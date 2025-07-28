import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock AI Agent - Alert Management",
  description: "Create and manage stock alerts with AI-powered analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
