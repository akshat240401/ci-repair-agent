import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic CI Repair",
  description: "Investigate failing CI, generate coordinated repairs, and verify them deterministically.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
