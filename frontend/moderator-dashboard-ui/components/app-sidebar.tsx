"use client"
import { LayoutDashboard, Search, History, Database, Building2, Clock, Shield } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { ThemeToggle } from "@/components/theme-toggle"
import { LanguageToggle } from "@/components/language-toggle"
import { useI18n } from "@/lib/i18n/i18n-context"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar"

const navigationItems = [
  {
    key: "dashboard" as const,
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    key: "manualParsing" as const,
    url: "/manual-parsing",
    icon: Search,
  },
  {
    key: "parsingRuns" as const,
    url: "/parsing-runs",
    icon: History,
  },
  {
    key: "pendingDomains" as const,
    url: "/domains/queue",
    icon: Clock,
  },
]

const databaseItems = [
  {
    key: "keywords" as const,
    url: "/keywords",
    icon: Database,
  },
  {
    key: "suppliers" as const,
    url: "/suppliers",
    icon: Building2,
  },
  {
    key: "blacklist" as const,
    url: "/blacklist",
    icon: Shield,
  },
]

export function AppSidebar() {
  const pathname = usePathname()
  const { t } = useI18n()

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-sm font-bold">M</span>
          </div>
          <div>
            <p className="text-sm font-semibold">{t("moderator")}</p>
            <p className="text-xs text-muted-foreground">{t("dashboard")}</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Main</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.key}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{t(item.key)}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Databases</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {databaseItems.map((item) => (
                <SidebarMenuItem key={item.key}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{t(item.key)}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">{t("theme")}</p>
          <ThemeToggle />
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">{t("language")}</p>
          <LanguageToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
