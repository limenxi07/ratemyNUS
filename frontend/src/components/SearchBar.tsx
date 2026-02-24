'use client'

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface Module {
  code: string;
  name: string;
  comment_count: number;
  units: number;
  semesters: string[];
}

export default function SearchBar({ size = 'large' }: { size?: 'large' | 'small' }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Module[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    const searchModules = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        setResults(data);
        setShowDropdown(data.length > 0);
        setSelectedIndex(0);
      } catch (error) {
        console.error('Search failed:', error);
      }
    };

    const debounce = setTimeout(searchModules, 200);
    return () => clearTimeout(debounce);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown || results.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % results.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + results.length) % results.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      router.push(`/modules/${results[selectedIndex].code}`);
      setShowDropdown(false);
      setQuery('');
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSelect = (code: string) => {
    router.push(`/modules/${code}`);
    setShowDropdown(false);
    setQuery('');
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const inputSize = size === 'large' 
    ? 'text-lg py-4 px-6' 
    : 'text-base py-3 px-5';

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Search by module code or name..."
        className={`w-full ${inputSize} rounded-2xl border-2 border-outline-primary focus:border-outline-active focus:outline-none bg-surface transition`}
      />

      {showDropdown && results.length > 0 && (
        <div className="absolute top-full mt-2 w-full bg-surface border-2 border-outline-primary rounded-xl shadow-lg max-h-96 overflow-y-auto z-50">
          {results.map((module, index) => (
            <button
              key={module.code}
              onClick={() => handleSelect(module.code)}
              className={`w-full text-left px-5 py-3 hover:bg-navbar transition ${
                index === selectedIndex ? 'bg-outline-primary' : ''
              } ${index !== results.length - 1 ? 'border-b border-outline-primary/20' : ''} first:rounded-t-xl last:rounded-b-xl`}
            >
              <div className="font-semibold text-text-body">{module.code}</div>
              <div className="text-sm text-text-body/70">{module.name}</div>
              <div className="text-xs text-text-body/50 mt-1">
                {module.comment_count} reviews • {module.units} MCs • Sem {module.semesters.join(', ')}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}