"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Rocket, AlertCircle } from "lucide-react"
import { SegmentedControl } from "@/components/segmented-control"
import { api, type ParsingRun } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function ManualParsingPage() {
  const router = useRouter()
  const { toast } = useToast()
  
  const [keyword, setKeyword] = useState("")
  const [depth, setDepth] = useState([10])
  const [source, setSource] = useState<"google" | "yandex" | "both">("both")
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const [recentRuns, setRecentRuns] = useState<ParsingRun[]>([])
  const [loadingRuns, setLoadingRuns] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRecentRuns()
  }, [])

  const loadRecentRuns = async () => {
    try {
      setLoadingRuns(true)
      setError(null)
      const response = await api.getParsingRuns({ limit: 5 })
      setRecentRuns(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setLoadingRuns(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const response = await api.startParsing(1, {
        depth: depth[0],
        source,
      })
      
      toast({
        title: "Парсинг запущен",
        description: `Run ID: ${response.runId}`,
      })
      
      router.push("/parsing-runs")
    } catch (err) {
      toast({
        title: "Ошибка",
        description: err instanceof Error ? err.message : 'Не удалось запустить парсинг',
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-semibold tracking-tight text-balance">Ручной парсинг</h1>
          <p className="text-muted-foreground text-base">Запустите парсинг для любого домена</p>
        </div>

        <Card className="p-8 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-3">
              <label className="text-sm font-medium">Ключ</label>
              <Input
                placeholder="Кирпич"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="h-11 text-base bg-background/50"
                required
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Глубина парсинга</label>
                <span className="text-sm text-muted-foreground font-mono">{depth[0]}</span>
              </div>
              <Slider value={depth} onValueChange={setDepth} min={1} max={100} step={1} className="py-4" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Минимум</span>
                <span>Максимум</span>
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium">Источник данных</label>
              <SegmentedControl
                value={source}
                onValueChange={setSource}
                options={[
                  { value: "google", label: "Google" },
                  { value: "yandex", label: "Yandex" },
                  { value: "both", label: "Оба" },
                ]}
              />
            </div>

            <Button type="submit" size="lg" className="w-full h-12 text-base font-medium gap-2" disabled={isSubmitting}>
              <Rocket className="w-4 h-4" />
              {isSubmitting ? "Запуск..." : "Начать парсинг"}
            </Button>
          </form>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <h3 className="text-lg font-semibold mb-4">Последние запуски</h3>
          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          {loadingRuns ? (
            <div className="text-center py-8 text-muted-foreground">Загрузка...</div>
          ) : recentRuns.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">Пока нет запусков</div>
          ) : (
            <div className="overflow-hidden rounded-lg border border-white/[0.08]">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/[0.08] bg-muted/30">
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Run ID</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Дата</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Глубина</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Источник</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRuns.map((run) => (
                    <tr
                      key={run.runId}
                      className="border-b border-white/[0.05] hover:bg-accent/50 transition-colors duration-200 cursor-pointer"
                      onClick={() => router.push(`/parsing-runs/${run.runId}`)}
                    >
                      <td className="py-3 px-4 text-sm font-mono">{run.runId.slice(0, 8)}...</td>
                      <td className="py-3 px-4 text-sm">{new Date(run.createdAt).toLocaleString('ru-RU')}</td>
                      <td className="py-3 px-4 text-sm font-mono">{run.depth || '-'}</td>
                      <td className="py-3 px-4 text-sm">{run.source || '-'}</td>
                      <td className="py-3 px-4">
                        <StatusBadge status={run.status} />
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
