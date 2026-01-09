import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Web3Provider } from "@/components/Web3Provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "V-Inference | Decentralized AI Inference with ZKML",
  description:
    "A decentralized AI inference network using Zero-Knowledge Proofs to ensure accurate computations. Upload models, run verified inference, and trade on the marketplace.",
  keywords: [
    "AI",
    "Machine Learning",
    "Zero Knowledge",
    "ZKML",
    "Decentralized",
    "Blockchain",
    "Inference",
    "DePIN",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased grid-pattern`}>
        <Web3Provider>{children}</Web3Provider>
      </body>
    </html>
  );
}
