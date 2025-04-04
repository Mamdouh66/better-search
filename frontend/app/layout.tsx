import type { Metadata } from "next";
import { IBM_Plex_Sans_Arabic } from "next/font/google";
import "./globals.css";

const ibmPlexArabic = IBM_Plex_Sans_Arabic({
  weight: ["100", "200", "300", "400", "500", "600", "700"],
  subsets: ["arabic"],
  variable: "--font-ibm-plex-arabic",
  display: "swap",
  preload: true,
});

export const metadata: Metadata = {
  title: "Better Search - Podcast Search Engine",
  description:
    "Search through millions of podcast episodes using our intelligent search engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl" className={ibmPlexArabic.variable}>
      <body className="font-sans min-h-screen">{children}</body>
    </html>
  );
}
