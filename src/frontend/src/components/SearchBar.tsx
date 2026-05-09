import React, { useRef, useEffect } from 'react';
import { useSearchStore } from '../store/useSearchStore';
import { Search as SearchIcon } from 'lucide-react';

export const SearchBar: React.FC = () => {
  const { query, setQuery, search, loading } = useSearchStore();
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      search();
    }
  };

  // Focus search bar on '/' key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <form 
      onSubmit={handleSearch} 
      className="flex gap-2 w-full max-w-4xl mx-auto mb-6 sticky top-0 z-20 bg-gray-950/80 backdrop-blur-sm py-2"
    >
      <div className="relative flex-1 group">
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors">
          <SearchIcon size={18} />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for movies, games, software... (Press '/' to focus)"
          className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-700 bg-gray-900 text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 shadow-lg transition-all"
          aria-label="Search torrents"
        />
      </div>
      <button
        type="submit"
        disabled={loading || !query.trim()}
        className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800/50 disabled:text-white/50 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-lg transition-all active:scale-95 flex items-center gap-2 min-w-[140px] justify-center"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            <span>Searching</span>
          </>
        ) : (
          <span>Search</span>
        )}
      </button>
    </form>
  );
};
