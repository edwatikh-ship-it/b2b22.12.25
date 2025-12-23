"use client"
import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { apiFetch, APIError } from "@/lib/api"
import type { KeywordsListResponseDTO } from "@/lib/types"
import { EmptyState } from "@/components/empty-state"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { StatusBadge } from "@/components/status-badge"
import { Database, Search, ArrowLeft, Home } from "lucide-react"
import { format } from "date-fns"
import { useDebouncedCallback } from "use-debounce"
import { useI18n } from "@/lib/i18n/i18n-context"
import { useRouter } from "next/navigation"
import Link from "next/link"

export function KeywordsClient() {
  const { t } = useI18n()
  const router = useRouter()
  const [data, setData] = useState<KeywordsListResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")

  const fetchKeywords = async (query: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({ limit: "50", offset: "0" })
      if (query) {
        params.append("q", query)
      }
      if (statusFilter !== "all") {
        params.append("status", statusFilter)
      }

      const response = await apiFetch<KeywordsListResponseDTO>(`/moderator/keywords?${params}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load keywords")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const debouncedFetch = useDebouncedCallback((query: string) => {
    fetchKeywords(query)
  }, 300)

  useEffect(() => {
    fetchKeywords(searchQuery)
  }, [statusFilter])

  useEffect(() => {
    debouncedFetch(searchQuery)
  }, [searchQuery])

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => router.back()} title={t("goBack")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <Link href="/dashboard">
              <Button variant="ghost" size="icon" title={t("goToHome")}>
                <Home className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{t("keywordsTitle")}</h1>
            <p className="text-muted-foreground">{t("keywordsSubtitle")}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={t("searchKeywords")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder={t("filterByStatus")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("allStatuses")}</SelectItem>
            <SelectItem value="pending">{t("pending")}</SelectItem>
            <SelectItem value="parsed">{t("parsed")}</SelectItem>
            <SelectItem value="failed">{t("failed")}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && <ErrorState message={error} />}

      {isLoading ? (
        <LoadingState message={t("loadingKeywords")} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Database}
          title={t("noKeywordsFound")}
          description={searchQuery ? t("noKeywordsMatchSearch") : t("noKeywordsInDatabase")}
        />
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            {t("showing")} {data.items.length} {t("of")} {data.total} {t("keywords")}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="p-3 text-left text-sm font-medium">{t("keyword")}</th>
                  <th className="p-3 text-left text-sm font-medium">{t("status")}</th>
                  <th className="p-3 text-left text-sm font-medium">{t("lastParsedAt")}</th>
                  <th className="p-3 text-left text-sm font-medium">{t("domainsFound")}</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((keyword) => (
                  <tr key={keyword.keyId} className="border-b transition-colors hover:bg-muted/30">
                    <td className="p-3 font-medium">{keyword.keyword}</td>
                    <td className="p-3">
                      {keyword.status ? (
                        <StatusBadge status={keyword.status as "pending" | "parsed" | "failed"} />
                      ) : (
                        <Badge variant="secondary">{t("unknown")}</Badge>
                      )}
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {keyword.lastRunAt ? format(new Date(keyword.lastRunAt), "PP") : "—"}
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {keyword.domainsFound ?? 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
