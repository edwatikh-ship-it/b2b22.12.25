"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, AlertCircle } from "lucide-react"
import { api, type Keyword } from "@/lib/api"

export default function KeywordsPage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<"pending" | "parsed" | "failed" | "all">("all")
  const [sortBy, setSortBy] = useState<"keyword_asc" | "keyword_desc" | "created_at_desc" | "created_at_asc">("keyword_asc")
  
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadKeywords()
  }, [statusFilter, sortBy])

  const loadKeywords = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.getKeywords({
        q: search || undefined,
        status: statusFilter === 'all' ? undefined : statusFilter,
        sort: sortBy,
        limit: 100,
      })
      setKeywords(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    loadKeywords()
  }

  const filteredKeywords = keywords.filter(kw => {
    if (!search) return true
    return kw.keyword.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-balance">База ключей</h1>
        </div>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по ключу"
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
                <SelectItem value="parsed">Parsed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-[200px] h-10 bg-background/50">
                <SelectValue placeholder="Сортировка" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="keyword_asc">По алфавиту (А-Я)</SelectItem>
                <SelectItem value="keyword_desc">По алфавиту (Я-А)</SelectItem>
                <SelectItem value="created_at_desc">По дате (новые)</SelectItem>
                <SelectItem value="created_at_asc">По дате (старые)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        {error && (
          <Card className="p-4 bg-red-500/10 border-red-500/20">
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          </Card>
        )}

        <Card className="overflow-hidden bg-card/50 backdrop-blur-sm border-white/[0.08]">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Загрузка...</div>
          ) : filteredKeywords.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">Пока нет данных</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/[0.08] bg-muted/30">
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">ID</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Ключ</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Статус</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Создан</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredKeywords.map((keyword) => (
                    <tr
                      key={keyword.id}
                      className="border-b border-white/[0.05] hover:bg-accent/50 transition-colors duration-200"
                    >
                      <td className="py-3 px-4 text-sm font-mono text-muted-foreground">{keyword.id}</td>
                      <td className="py-3 px-4 text-sm font-medium">{keyword.keyword}</td>
                      <td className="py-3 px-4">
                        <KeywordStatusBadge status={keyword.status} />
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {new Date(keyword.createdAt).toLocaleString('ru-RU')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </DashboardLayout>
  )
}

function KeywordStatusBadge({ status }: { status: string }) {
  const styles = {
    parsed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    failed: "bg-red-500/10 text-red-400 border-red-500/20",
  }

  const labels = {
    parsed: "Parsed",
    pending: "Pending",
    failed: "Failed",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${styles[status as keyof typeof styles]}`}
    >
      {labels[status as keyof typeof labels]}
    </span>
  )
}

function RunStatusBadge({ status }: { status: string }) {
  const styles = {
    succeeded: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    running: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    failed: "bg-red-500/10 text-red-400 border-red-500/20",
  }

  const labels = {
    succeeded: "Готово",
    running: "Выполняется",
    failed: "Ошибка",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${styles[status as keyof typeof styles]}`}
    >
      {labels[status as keyof typeof labels]}
    </span>
  )
}
