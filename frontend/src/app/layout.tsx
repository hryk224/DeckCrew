import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DeckCrew",
  description:
    "Autonomous AI DJs that debate, adapt, and direct real-time music generation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
