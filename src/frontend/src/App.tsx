import { lazy, Suspense } from 'react'
import { SearchBar } from './components/SearchBar'
import { PluginList } from './components/PluginList'
import { Sidebar } from './components/Sidebar'
import { ErrorBoundary } from './components/ErrorBoundary'

const ResultsTable = lazy(() => import('./components/ResultsTable').then((module) => ({ default: module.ResultsTable })))
const DetailsPanel = lazy(() => import('./components/DetailsPanel').then((module) => ({ default: module.DetailsPanel })))

function App() {
  return (
    <div className="h-screen w-full bg-gray-950 text-white flex flex-col overflow-hidden">
      <header className="bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-blue-500 flex items-center gap-2">
          <span className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">N</span>
          NebulaTorrent
        </h1>
        <div className="text-gray-500 text-xs">Modern Decentralized Search</div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        
        <main className="flex-1 overflow-hidden flex">
          <div className="flex-1 overflow-y-auto p-4 flex flex-col">
            <SearchBar />
            <ErrorBoundary>
              <Suspense fallback={<div className="p-6 text-sm text-gray-500">Loading results...</div>}>
                <ResultsTable />
              </Suspense>
            </ErrorBoundary>
            <PluginList />
          </div>
          <ErrorBoundary>
            <Suspense fallback={null}>
              <DetailsPanel />
            </Suspense>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}

export default App
