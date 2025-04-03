"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Loader2 } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      onSubmit={handleSubmit}
      className="w-full relative"
      dir="rtl"
    >
      <div
        className={`relative flex items-center group backdrop-blur-sm
          ${isFocused ? "shadow-lg" : "shadow-md"}`}
      >
        <div className="absolute inset-0 bg-[#4B4C51]/30 rounded-xl" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Search for podcasts, episodes, or topics..."
          className="w-full pr-6 pl-14 py-4 text-base md:text-lg bg-transparent rounded-xl
            focus:outline-none relative z-10 text-right
            text-[#F3F3F3] placeholder-[#BCBCBE]/70
            transition-all duration-300 ease-in-out"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="absolute left-4 p-2 text-[#BCBCBE]/70 hover:text-[#F3F3F3] 
            transition-colors disabled:opacity-50 disabled:hover:text-[#BCBCBE]/70
            z-10"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Search className="w-5 h-5" />
          )}
        </button>
      </div>
      <div
        className={`absolute inset-0 -z-10 transition-opacity duration-300
          opacity-${isFocused ? "100" : "0"}`}
        style={{
          background:
            "radial-gradient(circle at center, rgba(188,188,190,0.1) 0%, transparent 70%)",
          transform: "translateY(2px)",
          filter: "blur(8px)",
        }}
      />
    </motion.form>
  );
}
