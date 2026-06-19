"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, TrendingUp, ShieldCheck, FileText, Lightbulb, Activity } from "lucide-react";

export function SidebarNav() {
  const pathname = usePathname();

  const navItems = [
    { name: "Overview", href: "/", icon: LayoutDashboard },
    { name: "Trends", href: "/trends", icon: TrendingUp },
    { name: "Sources", href: "/sources", icon: ShieldCheck },
    { name: "Evidence", href: "/evidence", icon: FileText },
    { name: "Insights", href: "/insights", icon: Lightbulb },
    { name: "System", href: "/system", icon: Activity },
  ];

  return (
    <div className="w-64 shrink-0 border-r border-slate-800 bg-slate-950/50 hidden md:block">
      <div className="flex h-full flex-col px-4 py-8">
        <div className="mb-10 px-2">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            MarketPulse AI
          </h1>
          <p className="text-xs text-slate-500 font-medium tracking-wide uppercase mt-1">
            Intelligence Console
          </p>
        </div>
        
        <nav className="flex-1 space-y-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-blue-500/10 text-blue-400 shadow-sm ring-1 ring-blue-500/20"
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-blue-400" : "opacity-70"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto px-2 pt-6">
          <div className="rounded-lg bg-slate-900/50 p-4 border border-slate-800/50">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Workspace</h3>
            <p className="text-sm text-slate-300">Production Mode</p>
            <p className="text-xs text-slate-500 mt-1">Read-only dashboard</p>
          </div>
        </div>
      </div>
    </div>
  );
}
