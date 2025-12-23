"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { apiFetch, APIError } from "@/lib/api"
import type { ParsingRunsListResponseDTO, ParsingRunDTO } from "@/lib/types"
import { EmptyState } from "@/components/empty-state"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { StatusBadge } from "@/components/status-badge"
import { History, ExternalLink } from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"
import { useI18n } from "@/lib/i18n/i18n-context"

export default function ParsingRunsPage() {
  const { t } = useI18n()
  const [data, setData] = useState<ParsingRunsListResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>("all")

  useEffect(() => {
    fetchRuns()
  }, [statusFilter])

  const fetchRuns = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({ limit: "50", offset: "0" })
      if (statusFilter !== "all") {
        params.append("status", statusFilter)
      }

      const response = await apiFetch<ParsingRunsListResponseDTO>(`/moderator/parsing-runs?${params}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load parsing runs")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t("parsingRunsTitle")}</h1>
          <p className="text-muted-foreground">{t("parsingRunsSubtitle")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder={t("filterByStatus")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allStatuses")}</SelectItem>
              <SelectItem value="queued">{t("queued")}</SelectItem>
              <SelectItem value="running">{t("running")}</SelectItem>
              <SelectItem value="succeeded">{t("succeeded")}</SelectItem>
              <SelectItem value="failed">{t("failed")}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && <ErrorState message={error} />}

      {isLoading ? (
        <LoadingState message={t("loading")} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={History}
          title={t("noParsingRuns")}
          description={t("noParsingRunsDesc")}
          action={
            <Button asChild>
              <Link href="/manual-parsing">{t("startParsing")}</Link>
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            {t("showing")} {data.items.length} {t("of")} {data.total} {t("runs")}
          </div>

          <div className="grid gap-4">
            {data.items.map((run) => (
              <ParsingRunCard key={run.runId} run={run} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ParsingRunCard({ run }: { run: ParsingRunDTO }) {
  const { t } = useI18n()
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base">{t("runId")}: {run.runId.slice(0, 8)}</CardTitle>
            {run.requestId && <CardDescription>{t("requestId")}: {run.requestId}</CardDescription>}
          </div>
          <StatusBadge status={run.status} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
            {run.createdAt && (
              <div>
                <span className="text-muted-foreground">{t("createdAt")}:</span>
                <p className="font-medium">{format(new Date(run.createdAt), "PPp")}</p>
              </div>
            )}
            {run.finishedAt && (
              <div>
                <span className="text-muted-foreground">{t("finishedAt")}:</span>
                <p className="font-medium">{format(new Date(run.finishedAt), "PPp")}</p>
              </div>
            )}
            {run.depth !== undefined && (
              <div>
                <span className="text-muted-foreground">{t("depth")}:</span>
                <p className="font-medium">{run.depth}</p>
              </div>
            )}
            {run.source && (
              <div>
                <span className="text-muted-foreground">{t("source")}:</span>
                <p className="font-medium capitalize">{run.source}</p>
              </div>
            )}
          </div>

          {run.totalKeys !== undefined && (
            <div className="text-sm">
              <span className="text-muted-foreground">{t("totalKeywords")}: </span>
              <Badge variant="secondary">{run.totalKeys}</Badge>
            </div>
          )}

          {run.errorMessage && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{run.errorMessage}</div>
          )}

          <Button asChild variant="outline" size="sm" className="w-full sm:w-auto bg-transparent">
            <Link href={`/parsing-runs/${run.runId}`}>
              {t("viewDetails")}
              <ExternalLink className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
