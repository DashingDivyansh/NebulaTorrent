import { create } from 'zustand'
import type { PluginHealth, PluginStatus, TorrentResult } from '../types/torrent'
import { API_BASE_URL } from '../constants'

interface SearchState {
  // Data
  results: TorrentResult[]
  filteredResults: TorrentResult[]
  loading: boolean
  error: string | null
  pluginHealth: PluginHealth[]
  selectedResult: TorrentResult | null
  
  // Search Context
  query: string
  category: string
  
  // Filters
  minSeeders: number
  maxSize: number // in GB
  minSize: number // in GB
  
  // Sorting
  sortBy: keyof TorrentResult
  sortOrder: 'asc' | 'desc'
  
  // Actions
  setQuery: (query: string) => void
  setCategory: (category: string) => void
  setMinSeeders: (val: number) => void
  setMinSize: (val: number) => void
  setMaxSize: (val: number) => void
  setSort: (sortBy: keyof TorrentResult) => void
  search: () => Promise<void>
  applyFilters: () => void
  resetFilters: () => void
  setSelectedResult: (result: TorrentResult | null) => void
  setPluginHealth: (plugins: PluginHealth[]) => void
  addPluginResultCount: (plugin: string, count: number) => void
  setPluginStatus: (plugin: string, status: PluginStatus, message?: string) => void
}

export const useSearchStore = create<SearchState>((set, get) => ({
  results: [],
  filteredResults: [],
  loading: false,
  error: null,
  pluginHealth: [],
  selectedResult: null,
  query: '',
  category: '',
  minSeeders: 0,
  minSize: 0,
  maxSize: 0,
  sortBy: 'seeders',
  sortOrder: 'desc',

  setQuery: (query) => set({ query }),

  setSelectedResult: (selectedResult) => set({ selectedResult }),

  setPluginHealth: (pluginHealth) => {
    const existing = get().pluginHealth;
    set({
      pluginHealth: pluginHealth.map((plugin) => ({
        ...plugin,
        resultCount: existing.find((item) => item.name === plugin.name)?.resultCount ?? plugin.resultCount ?? 0,
      })),
    });
  },

  addPluginResultCount: (plugin, count) => {
    const current = get().pluginHealth
    const existing = current.find((p) => p.name === plugin)
    if (!existing) {
      set({
        pluginHealth: [
          ...current,
          { name: plugin, version: '', status: 'healthy', failures: 0, resultCount: count },
        ],
      })
      return
    }

    set({
      pluginHealth: current.map((p) =>
        p.name === plugin ? { ...p, resultCount: (p.resultCount ?? 0) + count } : p,
      ),
    })
  },

  setPluginStatus: (plugin, status, message) => {
    const current = get().pluginHealth
    const existing = current.find((p) => p.name === plugin)
    if (!existing) {
      set({
        pluginHealth: [
          ...current,
          { name: plugin, version: '', status, failures: status === 'error' ? 1 : 0, lastError: message },
        ],
      })
      return
    }

    set({
      pluginHealth: current.map((p) =>
        p.name === plugin
          ? {
              ...p,
              status,
              lastError: message ?? p.lastError,
              failures: status === 'error' ? p.failures + 1 : p.failures,
            }
          : p,
      ),
    })
  },
  
  setCategory: (category) => {
    set({ category })
    // If there's already a query, re-search automatically
    if (get().query) {
      get().search()
    }
  },

  setMinSeeders: (minSeeders) => {
    set({ minSeeders })
    get().applyFilters()
  },

  setMinSize: (minSize) => {
    set({ minSize })
    get().applyFilters()
  },

  setMaxSize: (maxSize) => {
    set({ maxSize })
    get().applyFilters()
  },

  resetFilters: () => {
    set({ minSeeders: 0, minSize: 0, maxSize: 0 })
    get().applyFilters()
  },

  applyFilters: () => {
    const { results, minSeeders, minSize, maxSize, sortBy, sortOrder } = get()
    
    let filtered = results.filter(r => {
      const sizeGB = r.size / (1024**3)
      if (r.seeders < minSeeders) return false
      if (minSize > 0 && sizeGB < minSize) return false
      if (maxSize > 0 && sizeGB > maxSize) return false
      return true
    })

    const sorted = [...filtered].sort((a, b) => {
      const valA = a[sortBy]
      const valB = b[sortBy]
      
      let comparison = 0
      if (typeof valA === 'number' && typeof valB === 'number') {
        comparison = valA - valB
      } else {
        comparison = String(valA).localeCompare(String(valB))
      }
      
      return sortOrder === 'desc' ? -comparison : comparison
    })

    set({ filteredResults: sorted })
  },

  setSort: (sortBy) => {
    const { sortBy: currentSortBy, sortOrder } = get()
    const newOrder = currentSortBy === sortBy && sortOrder === 'desc' ? 'asc' : 'desc'
    set({ sortBy, sortOrder: newOrder })
    get().applyFilters()
  },

  search: async () => {
    const { query, category } = get()
    const trimmedQuery = query.trim()
    if (!trimmedQuery) return

    // Initialize search state
    set({ 
      results: [], 
      filteredResults: [], 
      selectedResult: null,
      pluginHealth: get().pluginHealth.map((plugin) => ({ ...plugin, resultCount: 0 })),
      loading: true, 
      error: null 
    })
    
    const url = `${API_BASE_URL}/search?q=${encodeURIComponent(trimmedQuery)}${category ? `&category=${category}` : ''}`
    
    let eventSource: EventSource | null = null
    
    try {
      eventSource = new EventSource(url)

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          eventSource?.close()
          set({ loading: false })
          return
        }

        try {
          const payload = JSON.parse(event.data)

          if (payload.type === 'done') {
            eventSource?.close()
            set({ loading: false })
            return
          }

          if (payload.type === 'error') {
            set({ error: payload.message || 'Search failed', loading: false })
            eventSource?.close()
            return
          }

          if (payload.type === 'plugin_status') {
            get().setPluginStatus(payload.plugin, payload.status, payload.message)
            return
          }

          if (payload.type !== 'results') return

          const newBatch: TorrentResult[] = payload.results
          if (!Array.isArray(newBatch) || newBatch.length === 0) return
          get().addPluginResultCount(payload.plugin, newBatch.length)

          const currentResults = get().results
          const updatedResults = [...currentResults]
          
          newBatch.forEach(newRes => {
            // Helper to get reliable deduplication key
            const getHash = (r: TorrentResult) => (
              r.infoHash?.toLowerCase() || 
              r.magnet.match(/xt=urn:btih:([a-zA-Z0-9]+)/)?.[1]?.toLowerCase() || 
              r.title.toLowerCase()
            )
            
            const hash = getHash(newRes)
            const existingIdx = updatedResults.findIndex(r => getHash(r) === hash)

            if (existingIdx > -1) {
              const existing = updatedResults[existingIdx]
              // Merge sources
              const sources = new Set([...existing.source.split(', '), newRes.source])
              existing.source = Array.from(sources).join(', ')
              
              // Keep best metadata
              if (newRes.seeders > existing.seeders) {
                existing.seeders = newRes.seeders
                existing.leechers = newRes.leechers
              }
            } else {
              updatedResults.push(newRes)
            }
          })

          set({ results: updatedResults })
          get().applyFilters()
          if (!get().selectedResult && updatedResults.length > 0) {
            set({ selectedResult: updatedResults[0] })
          }
        } catch (parseErr) {
          console.error('Failed to parse search results batch:', parseErr)
        }
      }

      eventSource.onerror = () => {
        if (eventSource?.readyState === EventSource.CLOSED) {
          // If we got results, treat closure as success
          if (get().results.length > 0) {
            set({ loading: false })
          } else {
            set({ error: 'Failed to connect to search service', loading: false })
          }
        } else {
          // Actual interruption
          if (get().results.length === 0) {
            set({ error: 'Search connection lost', loading: false })
          } else {
            set({ loading: false })
          }
        }
        eventSource?.close()
      }
    } catch (criticalErr) {
      set({ error: 'Could not initialize search', loading: false })
      eventSource?.close()
    }
  }
}))
