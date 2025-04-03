"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import SearchResults from "./components/SearchResults";
import SearchBar from "./components/SearchBar";

interface SearchResult {
  episode_id: number;
  episode_title: string;
  episode_description: string;
  episode_image: string;
  podcast_title: string;
  podcast_author: string;
  duration_formatted: string;
  date_published: string;
  podcast_categoires: string[];
  sim_score: number;
}

interface ApiResponse {
  result: SearchResult[];
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/search?query=${encodeURIComponent(query)}`
      );
      const data: ApiResponse = await response.json();
      setResults(data.result || []);
    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main
      className="min-h-screen bg-[#060606] text-[#F3F3F3] relative overflow-x-hidden"
      dir="rtl"
    >
      {/* Grid Background */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `linear-gradient(to right, #F3F3F3 1px, transparent 1px),
            linear-gradient(to bottom, #F3F3F3 1px, transparent 1px)`,
          backgroundSize: "50px 50px",
          opacity: 0.03,
        }}
      />

      {/* Gradient overlay */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background:
            "radial-gradient(circle at 50% 0%, rgba(75,76,81,0.1) 0%, transparent 50%)",
        }}
      />

      <div className="relative z-10">
        <div className="container mx-auto px-4 min-h-screen flex flex-col">
          <div className="flex-grow flex flex-col items-center justify-center max-w-4xl mx-auto w-full py-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center mb-10 w-full"
            >
              <h1 className="text-4xl md:text-6xl font-bold mb-4 text-[#F3F3F3]">
                اكتشف بودكاستك
                <span className="block mt-2">المفضل القادم</span>
              </h1>
              <p className="text-[#BCBCBE]/70 text-base md:text-lg max-w-2xl mx-auto">
                ابحث في ملايين الحلقات باستخدام محرك البحث الذكي
              </p>
            </motion.div>

            <div className="w-full max-w-2xl mx-auto px-4">
              <SearchBar onSearch={handleSearch} isLoading={isLoading} />
            </div>
          </div>

          {results && results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="w-full max-w-4xl mx-auto pb-16 px-4"
            >
              <SearchResults results={results} />
            </motion.div>
          )}
        </div>
      </div>
    </main>
  );
}
