import { describe, it, expect } from 'vitest'
import { useSearchStore } from '../store/useSearchStore'

describe('SearchStore', () => {
  it('should initialize with default values', () => {
    const state = useSearchStore.getState()
    expect(state.results).toEqual([])
    expect(state.query).toBe('')
    expect(state.minSeeders).toBe(0)
  })

  it('should update query', () => {
    useSearchStore.getState().setQuery('test query')
    expect(useSearchStore.getState().query).toBe('test query')
  })

  it('should apply seeders filter', () => {
    const store = useSearchStore.getState()
    
    // Set mock results
    useSearchStore.setState({
      results: [
        { title: 'A', seeders: 10, size: 1000, leechers: 0, age: '', category: '', source: 'S', magnet: 'M' },
        { title: 'B', seeders: 100, size: 1000, leechers: 0, age: '', category: '', source: 'S', magnet: 'M' }
      ]
    })

    store.setMinSeeders(50)
    
    const filtered = useSearchStore.getState().filteredResults
    expect(filtered.length).toBe(1)
    expect(filtered[0].title).toBe('B')
  })
})
