"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { apiFetch, APIError } from "@/lib/api"
import type { PendingDomainListResponseDTO } from "@/lib/types"
import { EmptyState } from "@/components/empty-state"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { Clock, ArrowUpDown, ExternalLink, ArrowLeft, Home } from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"
import { useI18n } from "@/lib/i18n/i18n-context"
import { useRouter } from "next/navigation"

export default function PendingDomainsPage() {
  const { t } = useI18n()
  const router = useRouter()
  const [data, setData] = useState<PendingDomainListResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<"hits" | "createdat" | "domain">("hits")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [statusFilter, setStatusFilter] = useState<"all" | "pending">("pending")

  useEffect(() => {
    fetchDomains()
  }, [sortBy, sortOrder, statusFilter])

  const fetchDomains = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        limit: "50",
        offset: "0",
        sortBy,
        sortOrder,
      })

      const response = await apiFetch<PendingDomainListResponseDTO>(`/moderator/pending-domains?${params}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load pending domains")
      }
    } finally {
      setIsLoading(false)
    }
  }

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
            <h1 className="text-3xl font-bold tracking-tight">{t("pendingDomainsTitle")}</h1>
            <p className="text-muted-foreground">{t("pendingDomainsSubtitle")}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as typeof statusFilter)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder={t("status")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allStatuses")}</SelectItem>
              <SelectItem value="pending">{t("awaitingDecision")}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as typeof sortBy)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder={t("sortBy")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hits">{t("hits")}</SelectItem>
              <SelectItem value="createdat">{t("dateAdded")}</SelectItem>
              <SelectItem value="domain">{t("domain")}</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}>
            <ArrowUpDown className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {error && <ErrorState message={error} />}

      {isLoading ? (
        <LoadingState message={t("loadingPendingDomains")} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Clock}
          title={t("noPendingDomains")}
          description={t("noPendingDomainsDesc")}
        />
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            {t("showing")} {data.items.length} {t("of")} {data.total} {t("domains")}
            {statusFilter === "pending" && ` (${t("awaitingDecision")}: ${data.total})`}
          </div>

          <div className="grid gap-4">
            {data.items.map((domain) => (
              <Card key={domain.domain}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{domain.domain}</CardTitle>
                    <Button asChild variant="outline" size="sm">
                      <Link href={`/domains/queue/${encodeURIComponent(domain.domain)}`}>
                        {t("viewDetails")}
                        <ExternalLink className="ml-2 h-3 w-3" />
                      </Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
                    <div>
                      <p className="text-muted-foreground">Total Hits</p>
                      <Badge variant="secondary" className="mt-1">
                        {domain.totalhits}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Unique URLs</p>
                      <Badge variant="secondary" className="mt-1">
                        {domain.urlcount}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-muted-foreground">First Seen</p>
                      <p className="mt-1 font-medium">{format(new Date(domain.firstseenat), "PP")}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Last Seen</p>
                      <p className="mt-1 font-medium">{format(new Date(domain.lasthitat), "PP")}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
