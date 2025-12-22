"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, ChevronRight, AlertCircle } from "lucide-react"
import Link from "next/link"
import { api, type ParsingRun } from "@/lib/api"

export default function ParsingRunsPage() {
  const [statusFilter, setStatusFilter] = useState("all")
  const [search, setSearch] = useState("")
  
  const [runs, setRuns] = useState<ParsingRun[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRuns()
  }, [statusFilter])

  const loadRuns = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.getParsingRuns({
        status: statusFilter === 'all' ? undefined : statusFilter,
        limit: 50,
      })
      setRuns(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  const filteredRuns = runs.filter(run => {
    if (!search) return true
    return run.runId.toLowerCase().includes(search.toLowerCase()) ||
           run.requestId.toString().includes(search)
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-balance">История запусков</h1>
        </div>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по ключу или задаче"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 h-10 bg-background/50"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[200px] h-10 bg-background/50">
                <SelectValue placeholder="Статус" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все</SelectItem>
                <SelectItem value="queued">В очереди</SelectItem>
                <SelectItem value="running">Выполняется</SelectItem>
                <SelectItem value="succeeded">Готово</SelectItem>
                <SelectItem value="failed">Ошибка</SelectItem>
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
          ) : filteredRuns.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">Пока нет запусков</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/[0.08] bg-muted/30">
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Run ID</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Request ID</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Глубина</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Источник</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Статус</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Создан</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRuns.map((run) => (
                    <tr
                      key={run.runId}
                      className="border-b border-white/[0.05] hover:bg-accent/50 transition-colors duration-200 cursor-pointer"
                    >
                      <td className="py-3 px-4 text-sm font-mono text-muted-foreground">
                        {run.runId.slice(0, 8)}...
                      </td>
                      <td className="py-3 px-4 text-sm font-mono text-muted-foreground">
                        {run.requestId}
                      </td>
                      <td className="py-3 px-4 text-sm font-mono">{run.depth || '-'}</td>
                      <td className="py-3 px-4 text-sm">{run.source || '-'}</td>
                      <td className="py-3 px-4">
                        <StatusBadge status={run.status} />
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {new Date(run.createdAt).toLocaleString('ru-RU')}
                      </td>
                      <td className="py-3 px-4">
                        <Link href={`/parsing-runs/${run.runId}`}>
                          <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs">
                            Подробнее
                            <ChevronRight className="w-3 h-3" />
                          </Button>
                        </Link>
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

function StatusBadge({ status }: { status: string }) {
  const styles = {
    succeeded: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    running: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    failed: "bg-red-500/10 text-red-400 border-red-500/20",
    queued: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  }

  const labels = {
    succeeded: "Готово",
    running: "Выполняется",
    failed: "Ошибка",
    queued: "В очереди",
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${styles[status as keyof typeof styles]}`}
    >
      {labels[status as keyof typeof labels]}
    </span>
  )
}
