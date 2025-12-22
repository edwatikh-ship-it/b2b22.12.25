"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, ExternalLink, Plus, Ban, Clock } from "lucide-react"

interface DomainQueueItem {
  domain: string
  status: "pending" | "supplier" | "reseller" | "blacklist"
  lastKeyword: string
  hits: number
  lastSeen: string
}

export default function DomainQueuePage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState("domain")

  const domains: DomainQueueItem[] = [
    {
      domain: "metallpro.ru",
      status: "pending",
      lastKeyword: "металлопрокат москва",
      hits: 12,
      lastSeen: "2025-01-20 14:35",
    },
    {
      domain: "steelmarket.com",
      status: "pending",
      lastKeyword: "сталь оптом",
      hits: 8,
      lastSeen: "2025-01-20 13:22",
    },
    {
      domain: "supplier-one.ru",
      status: "supplier",
      lastKeyword: "стройматериалы",
      hits: 24,
      lastSeen: "2025-01-20 12:10",
    },
  ]

  const handleQuickAction = async (domain: string, action: string) => {
    console.log("[v0] Quick action:", action, "for domain:", domain)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-balance">Очередь доменов</h1>
          <p className="text-muted-foreground mt-2">Рабочий инбокс модератора</p>
        </div>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по домену"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 h-10 bg-background/50"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[180px] h-10 bg-background/50">
                <SelectValue placeholder="Статус" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="supplier">Поставщики</SelectItem>
                <SelectItem value="reseller">Реселлеры</SelectItem>
                <SelectItem value="blacklist">Blacklist</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-[180px] h-10 bg-background/50">
                <SelectValue placeholder="Сортировка" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="domain">По домену</SelectItem>
                <SelectItem value="date">По дате</SelectItem>
                <SelectItem value="hits">По хитам</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        <Card className="overflow-hidden bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/[0.08] bg-muted/30">
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Домен</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Статус</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Последний ключ</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Хитов</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Последнее появление</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Действия</th>
                </tr>
              </thead>
              <tbody>
                {domains.map((domain, i) => (
                  <tr
                    key={i}
                    className="border-b border-white/[0.05] hover:bg-accent/50 transition-colors duration-200 group"
                  >
                    <td className="py-3 px-4 text-sm font-medium">
                      <div className="flex items-center gap-2">
                        {domain.domain}
                        <ExternalLink className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <DomainStatusBadge status={domain.status} />
                    </td>
                    <td className="py-3 px-4 text-sm">{domain.lastKeyword}</td>
                    <td className="py-3 px-4 text-sm font-mono">{domain.hits}</td>
                    <td className="py-3 px-4 text-sm">{domain.lastSeen}</td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                          title="Поставщик"
                          onClick={() => handleQuickAction(domain.domain, "supplier")}
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                          title="Blacklist"
                          onClick={() => handleQuickAction(domain.domain, "blacklist")}
                        >
                          <Ban className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                          title="Очередь"
                          onClick={() => handleQuickAction(domain.domain, "pending")}
                        >
                          <Clock className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function DomainStatusBadge({ status }: { status: string }) {
  const styles = {
    supplier: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    reseller: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    blacklist: "bg-red-500/10 text-red-400 border-red-500/20",
    pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  }

  const labels = {
    supplier: "Поставщик",
    reseller: "Реселлер",
    blacklist: "Blacklist",
    pending: "Pending",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${styles[status as keyof typeof styles]}`}
    >
      {labels[status as keyof typeof labels]}
    </span>
  )
}
