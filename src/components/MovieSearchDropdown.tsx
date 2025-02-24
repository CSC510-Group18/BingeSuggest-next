import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";

const API_BASE_URL = "http://127.0.0.1:5000";

interface MovieSearchDropdownProps {
  placeholder?: string;
  onSelect: (movie: string) => void;
  className?: string;
}

const MovieSearchDropdown: React.FC<MovieSearchDropdownProps> = ({
  placeholder,
  onSelect,
  className,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<string[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleSearch = async (term: string) => {
    if (term.length < 3) {
      setResults([]);
      setIsDropdownOpen(false);
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `q=${encodeURIComponent(term)}`,
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data);
        setIsDropdownOpen(true);
      } else {
        setResults([]);
        setIsDropdownOpen(false);
      }
    } catch (err) {
      setResults([]);
      setIsDropdownOpen(false);
    }
  };

  useEffect(() => {
    handleSearch(query);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className || ""}`} ref={containerRef}>
      <Input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        autoComplete="off"
      />
      {isDropdownOpen && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          <ul>
            {results.map((movie, index) => (
              <li
                key={index}
                className="p-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => {
                  onSelect(movie);
                  setQuery(movie); // set input with selected suggestion
                  setResults([]);
                  setIsDropdownOpen(false);
                }}
              >
                {movie}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MovieSearchDropdown;
