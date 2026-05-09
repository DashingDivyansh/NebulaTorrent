import React, { useEffect, useState } from 'react';
import { useSearchStore } from '../store/useSearchStore';
import axios from 'axios';
import { API_BASE_URL } from '../constants';
import { 
  Film, 
  Tv, 
  Gamepad2, 
  Cpu, 
  Music, 
  Book, 
  LayoutGrid,
  Filter,
  History,
  Search
} from 'lucide-react';

const categories = [
  { id: '', name: 'All', icon: LayoutGrid },
  { id: 'movies', name: 'Movies', icon: Film },
  { id: 'tv', name: 'TV Shows', icon: Tv },
  { id: 'games', name: 'Games', icon: Gamepad2 },
  { id: 'software', name: 'Software', icon: Cpu },
  { id: 'music', name: 'Music', icon: Music },
  { id: 'books', name: 'Books', icon: Book },
];

export const Sidebar: React.FC = () => {
  const { 
    category, 
    setCategory, 
    minSeeders, 
    setMinSeeders,
    minSize,
    setMinSize,
    maxSize,
    setMaxSize,
    setQuery,
    search
  } = useSearchStore();

  const [history, setHistory] = useState<{ query: string; category: string; timestamp: string }[]>([]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/history`);
      setHistory(res.data);
    } catch (e) {
      console.error('Failed to fetch history', e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [category]); // Refresh history when category changes (which happens on search)

  const handleHistoryClick = (q: string, cat: string) => {
    setQuery(q);
    setCategory(cat);
    // Wait for state updates to propagate before searching
    setTimeout(() => search(), 0);
  };

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Categories</h2>
        <nav className="space-y-1">
          {categories.map((cat) => {
            const Icon = cat.icon;
            return (
              <button
                key={cat.id}
                onClick={() => setCategory(cat.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  category === cat.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                }`}
              >
                <Icon size={18} />
                <span>{cat.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center space-x-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            <Filter size={14} />
            <span>Filters</span>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-xs text-gray-400 mb-2">Min Seeders: {minSeeders}</label>
              <input 
                type="range" 
                min="0" 
                max="1000" 
                step="10"
                value={minSeeders}
                onChange={(e) => setMinSeeders(parseInt(e.target.value))}
                className="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Min (GB)</label>
                <input 
                  type="number" 
                  value={minSize}
                  onChange={(e) => setMinSize(parseFloat(e.target.value) || 0)}
                  className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Max (GB)</label>
                <input 
                  type="number" 
                  value={maxSize}
                  onChange={(e) => setMaxSize(parseFloat(e.target.value) || 0)}
                  className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="p-4">
          <div className="flex items-center space-x-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            <History size={14} />
            <span>Search History</span>
          </div>
          <div className="space-y-1">
            {history.map((h, i) => (
              <button
                key={i}
                onClick={() => handleHistoryClick(h.query, h.category || '')}
                className="w-full text-left px-2 py-1.5 rounded hover:bg-gray-800 text-sm text-gray-400 hover:text-gray-200 truncate flex items-center gap-2"
                title={h.query}
              >
                <Search size={12} className="shrink-0" />
                <span className="truncate">{h.query}</span>
              </button>
            ))}
            {history.length === 0 && (
              <div className="text-xs text-gray-600 italic px-2">No history yet</div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};
