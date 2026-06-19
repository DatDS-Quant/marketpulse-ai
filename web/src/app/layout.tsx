import type { Metadata } from "next";
import "./globals.css";
import { SidebarNav } from "@/components/dashboard/SidebarNav";

export const metadata: Metadata = {
  title: "MarketPulse AI | Intelligence Console",
  description: "Automated market intelligence and AI insight dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="antialiased font-sans bg-slate-950 text-slate-200 selection:bg-blue-500/30">
        <div className="flex min-h-screen">
          <SidebarNav />
          <main className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 min-h-full">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
