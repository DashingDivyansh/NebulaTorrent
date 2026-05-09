import React from 'react';
import { Copy, Download, Hash, Info, X } from 'lucide-react';

import { useSearchStore } from '../store/useSearchStore';

const formatSize = (bytes: number) => {
  if (!bytes) return 'N/A';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${parseFloat((bytes / Math.pow(1024, index)).toFixed(2))} ${units[index]}`;
};

export const DetailsPanel: React.FC = () => {
  const { selectedResult, setSelectedResult } = useSearchStore();

  if (!selectedResult) {
    return (
      <aside className="hidden xl:flex w-80 border-l border-gray-800 bg-gray-900/60 p-5 text-gray-500">
        <div className="m-auto flex flex-col items-center gap-3 text-center text-sm">
          <Info size={28} />
          <span>Select a result to inspect it.</span>
        </div>
      </aside>
    );
  }

  return (
    <aside className="hidden xl:flex w-80 border-l border-gray-800 bg-gray-900/60 p-5 flex-col gap-5 overflow-y-auto">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-blue-400 font-bold mb-2">Torrent Details</div>
          <h2 className="text-base font-bold text-white leading-snug">{selectedResult.title}</h2>
        </div>
        <button
          type="button"
          title="Close details"
          onClick={() => setSelectedResult(null)}
          className="p-2 rounded-lg text-gray-500 hover:text-white hover:bg-gray-800"
        >
          <X size={16} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Metric label="Seeders" value={selectedResult.seeders.toLocaleString()} tone="text-green-400" />
        <Metric label="Peers" value={selectedResult.leechers.toLocaleString()} tone="text-red-300" />
        <Metric label="Size" value={formatSize(selectedResult.size)} />
        <Metric label="Added" value={selectedResult.age || 'Unknown'} />
      </div>

      <div>
        <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-2">Sources</div>
        <div className="flex flex-wrap gap-1.5">
          {selectedResult.source.split(', ').map((source) => (
            <span key={source} className="px-2 py-1 rounded-md bg-gray-800 border border-gray-700 text-xs text-gray-300">
              {source}
            </span>
          ))}
        </div>
      </div>

      {selectedResult.infoHash && (
        <div>
          <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-2">Info Hash</div>
          <div className="flex items-center gap-2 rounded-lg bg-gray-950 border border-gray-800 p-3 text-xs font-mono text-gray-400 break-all">
            <Hash size={14} className="shrink-0 text-gray-500" />
            {selectedResult.infoHash}
          </div>
        </div>
      )}

      <div className="mt-auto grid gap-2">
        <button
          type="button"
          onClick={() => navigator.clipboard.writeText(selectedResult.magnet)}
          className="flex items-center justify-center gap-2 rounded-lg bg-gray-800 px-4 py-2.5 text-sm font-bold text-gray-200 hover:bg-gray-700"
        >
          <Copy size={16} />
          Copy Magnet
        </button>
        <a
          href={selectedResult.magnet}
          className="flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-blue-500"
        >
          <Download size={16} />
          Open Magnet
        </a>
      </div>
    </aside>
  );
};

const Metric = ({ label, value, tone = 'text-gray-200' }: { label: string; value: string; tone?: string }) => (
  <div className="rounded-lg bg-gray-950/80 border border-gray-800 p-3">
    <div className="text-[10px] uppercase tracking-widest text-gray-600 font-bold mb-1">{label}</div>
    <div className={`text-sm font-bold ${tone}`}>{value}</div>
  </div>
);
