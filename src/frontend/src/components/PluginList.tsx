import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Box, CheckCircle2, Clock3, Loader2 } from 'lucide-react';

import { API_BASE_URL } from '../constants';
import { useSearchStore } from '../store/useSearchStore';
import type { PluginHealth, PluginStatus } from '../types/torrent';

const statusStyles: Record<PluginStatus, string> = {
  idle: 'text-gray-500 bg-gray-800/40 border-gray-700/30',
  loading: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  healthy: 'text-green-400 bg-green-500/10 border-green-500/30',
  cached: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  degraded: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  error: 'text-red-400 bg-red-500/10 border-red-500/30',
};

const StatusIcon = ({ status }: { status: PluginStatus }) => {
  if (status === 'loading') return <Loader2 size={12} className="animate-spin" />;
  if (status === 'healthy' || status === 'cached') return <CheckCircle2 size={12} />;
  if (status === 'degraded' || status === 'error') return <AlertTriangle size={12} />;
  return <Clock3 size={12} />;
};

export const PluginList: React.FC = () => {
  const { pluginHealth, setPluginHealth } = useSearchStore();
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/plugins`)
      .then(res => setPluginHealth(res.data))
      .catch(err => {
        console.error('Failed to load plugins', err);
        setLoadError('Plugin health unavailable');
      });
  }, [setPluginHealth]);

  const plugins: PluginHealth[] = pluginHealth;

  return (
    <div className="w-full max-w-4xl mx-auto p-4 bg-gray-900/30 rounded-lg mt-4 border border-gray-800/50 shadow-lg">
      <div className="flex items-center gap-2 mb-3">
        <Box size={16} className="text-blue-500" />
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Indexer Health</h2>
      </div>
      <div className="flex flex-wrap gap-2">
        {plugins.map((plugin) => (
          <div
            key={plugin.name}
            title={plugin.lastError || `${plugin.name} ${plugin.version}`}
            className={`flex items-center gap-2 px-2 py-1 rounded-md border transition-all ${statusStyles[plugin.status] || statusStyles.idle}`}
          >
            <StatusIcon status={plugin.status} />
            <span className="text-xs font-medium">{plugin.name}</span>
            <span className="text-[9px] uppercase opacity-70">{plugin.status}</span>
            {(plugin.resultCount ?? 0) > 0 && (
              <span className="text-[9px] rounded bg-white/10 px-1.5 py-0.5">{plugin.resultCount}</span>
            )}
            {plugin.sandboxed && <span className="text-[9px] uppercase opacity-60">Sandbox</span>}
          </div>
        ))}
        {plugins.length === 0 && !loadError && (
          <div className="py-1 text-gray-600 text-[10px] italic">
            No plugins loaded.
          </div>
        )}
        {loadError && <div className="py-1 text-red-400 text-[10px]">{loadError}</div>}
      </div>
    </div>
  );
};
