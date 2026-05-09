export interface TorrentResult {
  title: string
  size: number
  seeders: number
  leechers: number
  age: string
  category: string
  source: string
  magnet: string
  infoHash?: string
}

export type PluginStatus = 'idle' | 'loading' | 'healthy' | 'cached' | 'degraded' | 'error'

export interface PluginHealth {
  name: string
  version: string
  status: PluginStatus
  failures: number
  lastError?: string | null
  degradedUntil?: number | null
  rateLimit?: number
  sandboxed?: boolean
  resultCount?: number
}
