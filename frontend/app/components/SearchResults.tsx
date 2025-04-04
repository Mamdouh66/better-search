"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Clock, User, Tag } from "lucide-react";

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

interface SearchResultsProps {
  results: SearchResult[];
}

export default function SearchResults({ results }: SearchResultsProps) {
  return (
    <div className="grid gap-6" dir="rtl">
      {results.map((result, index) => (
        <motion.div
          key={result.episode_id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          className="bg-[#4B4C51]/40 backdrop-blur-sm rounded-xl overflow-hidden 
            transition-all duration-300 ease-in-out hover:scale-[1.01] 
            border border-[#BCBCBE]/10 hover:border-[#BCBCBE]/20
            hover:bg-[#4B4C51]/50"
        >
          <div className="flex flex-col md:flex-row-reverse h-full">
            <div className="w-full md:w-[180px] relative bg-[#060606] shrink-0 aspect-square md:aspect-[4/3]">
              {result.episode_image && (
                <Image
                  src={result.episode_image}
                  alt={result.episode_title}
                  fill
                  sizes="(max-width: 768px) 100vw, 180px"
                  className="object-cover opacity-90 hover:opacity-100 transition-opacity"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = "none";
                  }}
                />
              )}
            </div>
            <div className="p-4 md:p-5 flex-1 flex flex-col justify-between">
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-3 text-sm text-[#BCBCBE]/70 flex-row-reverse">
                  <div className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" />
                    <span className="truncate max-w-[200px]">
                      {result.podcast_author}
                    </span>
                  </div>
                  {result.duration_formatted && (
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{result.duration_formatted}</span>
                    </div>
                  )}
                </div>

                <h3 className="text-lg font-medium text-[#F3F3F3] line-clamp-1">
                  {result.episode_title}
                </h3>
                <p className="text-[#BCBCBE]/80 text-sm line-clamp-2">
                  {result.episode_description}
                </p>

                <div className="flex items-center gap-2 mt-1 text-sm flex-row-reverse">
                  <Tag className="w-3.5 h-3.5 text-[#BCBCBE]/70" />
                  <span className="text-[#BCBCBE]/70 line-clamp-1 max-w-[300px]">
                    {result.podcast_title}
                  </span>
                </div>

                <div className="flex flex-wrap gap-2 mt-2 flex-row-reverse">
                  {result.podcast_categoires?.slice(0, 3).map((category, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-0.5 text-xs rounded-full bg-[#060606]/50 text-[#BCBCBE]/90
                        border border-[#BCBCBE]/10"
                    >
                      {category}
                    </span>
                  ))}
                  {result.podcast_categoires?.length > 3 && (
                    <span className="text-xs text-[#BCBCBE]/50">
                      +{result.podcast_categoires.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
