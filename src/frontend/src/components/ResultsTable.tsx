import React, { useEffect, useState } from 'react';
import { AlertCircle, Download, Hash, RefreshCcw, Search, Users } from 'lucide-react';

import { useSearchStore } from '../store/useSearchStore';
import type { TorrentResult } from '../types/torrent';

export const ResultsTable: React.FC = () => {
  const { filteredResults, results, loading, error, setSort, sortBy, sortOrder, search, setSelectedResult, query } = useSearchStore();
  const [activeRow, setActiveRow] = useState(0);

  useEffect(() => {
    setActiveRow(0);
  }, [filteredResults.length]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA') return;

      if (event.key === 'j') {
        event.preventDefault();
        setActiveRow((row) => Math.min(row + 1, Math.max(filteredResults.length - 1, 0)));
      }

      if (event.key === 'k') {
        event.preventDefault();
        setActiveRow((row) => Math.max(row - 1, 0));
      }

      if (event.key === 'Enter' && filteredResults[activeRow]?.magnet) {
        window.location.href = filteredResults[activeRow].magnet;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeRow, filteredResults]);

  const formatSize = (bytes: number) => {
    if (bytes === 0) return 'N/A';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  const SortIcon = ({ field }: { field: keyof TorrentResult }) => {
    if (sortBy !== field) return null;
    return <span className="ml-1 text-blue-500">{sortOrder === 'desc' ? 'v' : '^'}</span>;
  };

  if (error && results.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center animate-in fade-in zoom-in duration-300">
        <div className="bg-red-500/10 text-red-500 p-4 rounded-full mb-4 ring-1 ring-red-500/20 shadow-lg shadow-red-500/10">
          <AlertCircle size={32} />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Search Service Unavailable</h3>
        <p className="text-gray-400 max-w-md mb-6">{error}</p>
        <button
          type="button"
          onClick={search}
          className="flex items-center gap-2 px-6 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-all"
        >
          <RefreshCcw size={16} />
          Retry Connection
        </button>
      </div>
    );
  }

  if (!loading && results.length === 0) {
    if (query) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center opacity-60">
          <div className="bg-gray-800/50 text-gray-500 p-4 rounded-full mb-4">
            <Search size={32} />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Results Found</h3>
          <p className="text-gray-400 max-w-md text-sm">We couldn't find any torrents matching your search.</p>
        </div>
      );
    }
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center opacity-60">
        <div className="bg-gray-800/50 text-gray-500 p-4 rounded-full mb-4">
          <Search size={32} />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Ready to Search</h3>
        <p className="text-gray-400 max-w-md text-sm">Enter a keyword above to start indexing from 11 sources.</p>
      </div>
    );
  }

  return (
    <div className="h-[48vh] min-h-[420px] max-h-[620px] shrink-0 overflow-hidden flex flex-col bg-gray-900/40 rounded-lg border border-gray-800/50 shadow-2xl backdrop-blur-xl">
      <div className="overflow-auto flex-1 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
        <table className="w-full text-left border-separate border-spacing-0">
          <thead className="sticky top-0 bg-gray-950/90 backdrop-blur-md z-10">
            <tr>
              <th className="px-6 py-4 border-b border-gray-800/50 cursor-pointer hover:bg-gray-800/30 transition-colors text-[10px] font-black uppercase tracking-widest text-gray-500" onClick={() => setSort('title')}>
                <div className="flex items-center">Name <SortIcon field="title" /></div>
              </th>
              <th className="px-4 py-4 border-b border-gray-800/50 cursor-pointer hover:bg-gray-800/30 transition-colors text-[10px] font-black uppercase tracking-widest text-gray-500 w-24" onClick={() => setSort('size')}>
                <div className="flex items-center">Size <SortIcon field="size" /></div>
              </th>
              <th className="px-4 py-4 border-b border-gray-800/50 cursor-pointer hover:bg-gray-800/30 transition-colors text-[10px] font-black uppercase tracking-widest text-gray-500 w-24" onClick={() => setSort('seeders')}>
                <div className="flex items-center text-green-500/80"><Users size={12} className="mr-1.5" /> Seed <SortIcon field="seeders" /></div>
              </th>
              <th className="px-4 py-4 border-b border-gray-800/50 cursor-pointer hover:bg-gray-800/30 transition-colors text-[10px] font-black uppercase tracking-widest text-gray-500 w-20" onClick={() => setSort('leechers')}>
                <div className="flex items-center text-red-500/80">Peers <SortIcon field="leechers" /></div>
              </th>
              <th className="px-4 py-4 border-b border-gray-800/50 text-[10px] font-black uppercase tracking-widest text-gray-500 w-32">Added</th>
              <th className="px-4 py-4 border-b border-gray-800/50 cursor-pointer hover:bg-gray-800/30 transition-colors text-[10px] font-black uppercase tracking-widest text-gray-500 w-32" onClick={() => setSort('source')}>
                <div className="flex items-center">Source <SortIcon field="source" /></div>
              </th>
              <th className="px-6 py-4 border-b border-gray-800/50 text-right text-[10px] font-black uppercase tracking-widest text-gray-500 w-44">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {filteredResults.map((result, idx) => (
              <tr
                key={`${result.infoHash || result.magnet || result.title}-${idx}`}
                onClick={() => setSelectedResult(result)}
                className={`group hover:bg-blue-600/5 transition-colors ${idx === activeRow ? 'bg-blue-600/10 outline outline-1 outline-blue-500/20' : ''}`}
              >
                <td className="px-6 py-4 truncate max-w-xl" title={result.title}>
                  <div className="flex flex-col gap-0.5">
                    <span className="text-sm font-semibold text-gray-200 group-hover:text-blue-400 transition-colors truncate">
                      {result.title}
                    </span>
                    {result.infoHash && (
                      <span className="text-[10px] text-gray-600 font-mono flex items-center gap-1 group-hover:text-gray-500">
                        <Hash size={10} /> {result.infoHash.substring(0, 16)}...
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-400 font-medium">{formatSize(result.size)}</td>
                <td className="px-4 py-4 text-sm text-green-500 font-bold tabular-nums">{result.seeders.toLocaleString()}</td>
                <td className="px-4 py-4 text-sm text-red-500/60 font-medium tabular-nums">{result.leechers.toLocaleString()}</td>
                <td className="px-4 py-4 text-[11px] text-gray-500 whitespace-nowrap">{result.age || 'Unknown'}</td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-1">
                    {result.source.split(', ').map((source) => (
                      <span key={source} className="px-1.5 py-0.5 bg-gray-800/50 border border-gray-700/50 rounded text-[9px] text-gray-400 font-bold tracking-tight">
                        {source}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
                    <button
                      type="button"
                      className="p-2 bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white rounded-lg transition-all active:scale-90"
                      title="Copy magnet link"
                      onClick={() => navigator.clipboard.writeText(result.magnet)}
                    >
                      <Hash size={16} />
                    </button>
                    <a
                      href={result.magnet}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-black transition-all shadow-lg shadow-blue-600/20 active:scale-95"
                    >
                      <Download size={14} />
                      OPEN
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-3 bg-gray-950/40 border-t border-gray-800/50 flex justify-between items-center text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">
        <div className="flex items-center gap-4">
          <span>{filteredResults.length} Matched</span>
          <span className="w-1 h-1 rounded-full bg-gray-800" />
          <span className="text-gray-600">{results.length - filteredResults.length} Filtered</span>
        </div>
        {loading && (
          <div className="flex items-center gap-2 text-blue-500">
            <RefreshCcw size={10} className="animate-spin" />
            <span>Streaming</span>
          </div>
        )}
      </div>
    </div>
  );
};
