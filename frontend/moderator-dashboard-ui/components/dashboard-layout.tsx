"use client"

import { type ReactNode, useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, History, Layers, Key, Users, Pencil, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { ThemeToggle } from "@/components/theme-toggle"

interface DashboardLayoutProps {
  children: ReactNode
}

const navigation = [
  { name: "Панель", href: "/dashboard", icon: LayoutDashboard },
  { name: "История запусков", href: "/parsing-runs", icon: History },
  { name: "Очередь доменов", href: "/domains/queue", icon: Layers },
  { name: "База ключей", href: "/keywords", icon: Key },
  { name: "Поставщики", href: "/suppliers", icon: Users },
  { name: "Ручной парсинг", href: "/manual-parsing", icon: Pencil },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#020617] to-[#020617] dark:from-[#020617] dark:to-[#020617] bg-white relative">
      {/* Subtle noise texture */}
      <div
        className="fixed inset-0 opacity-[0.015] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' /%3E%3C/svg%3E")`,
        }}
      />

      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} className="h-10 w-10">
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </Button>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-200 ease-out lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="h-full bg-[#0a0f1e]/80 dark:bg-[#0a0f1e]/80 bg-slate-50/80 backdrop-blur-xl border-r border-white/[0.08] dark:border-white/[0.08] border-slate-200">
          <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="px-6 py-6 border-b border-white/[0.08] dark:border-white/[0.08] border-slate-200 flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold tracking-tight">Модератор</div>
                <div className="text-xs text-muted-foreground mt-1">B2B Parsing Platform</div>
              </div>
              {/* Theme Toggle */}
              <ThemeToggle />
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-white/[0.05] dark:hover:bg-white/[0.05] hover:bg-slate-100 hover:text-foreground",
                    )}
                  >
                    <item.icon className="w-4 h-4 shrink-0" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* User section */}
            <div className="px-6 py-4 border-t border-white/[0.08] dark:border-white/[0.08] border-slate-200">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-xs font-semibold text-white">
                  МД
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">Модератор</div>
                  <div className="text-xs text-muted-foreground">moderator@domain.ru</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main content */}
      <main className="lg:pl-64">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">{children}</div>
      </main>
    </div>
  )
}
