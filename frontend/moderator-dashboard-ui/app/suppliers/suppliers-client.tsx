"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { apiFetch, APIError } from "@/lib/api"
import type { SuppliersListResponseDTO } from "@/lib/types"
import { EmptyState } from "@/components/empty-state"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { Building2, Search, ExternalLink, Mail, Phone, Globe, ArrowLeft, Home } from "lucide-react"
import { format } from "date-fns"
import Link from "next/link"
import { useDebouncedCallback } from "use-debounce"
import { useI18n } from "@/lib/i18n/i18n-context"
import { useRouter } from "next/navigation"

export function SuppliersClient() {
  const { t } = useI18n()
  const router = useRouter()
  const [data, setData] = useState<SuppliersListResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState<string>("all")

  const fetchSuppliers = async (query: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({ limit: "50", offset: "0" })
      if (query) {
        params.append("q", query)
      }
      if (typeFilter !== "all") {
        params.append("type", typeFilter)
      }

      const response = await apiFetch<SuppliersListResponseDTO>(`/moderator/suppliers?${params}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load suppliers")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const debouncedFetch = useDebouncedCallback((query: string) => {
    fetchSuppliers(query)
  }, 300)

  useEffect(() => {
    fetchSuppliers(searchQuery)
  }, [typeFilter])

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
            <h1 className="text-3xl font-bold tracking-tight">{t("suppliersTitle")}</h1>
            <p className="text-muted-foreground">{t("suppliersSubtitle")}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={t("searchSuppliers")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder={t("filterByType")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("allTypes")}</SelectItem>
            <SelectItem value="supplier">{t("suppliers")}</SelectItem>
            <SelectItem value="reseller">{t("resellers")}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && <ErrorState message={error} />}

      {isLoading ? (
        <LoadingState message={t("loadingSuppliers")} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Building2}
          title={t("noSuppliersFound")}
          description={searchQuery ? t("noSuppliersMatchSearch") : t("noSuppliersInDatabase")}
        />
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            {t("showing")} {data.items.length} {t("of")} {data.total} {t("suppliers")}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {data.items.map((supplier) => (
              <Card key={supplier.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-base">{supplier.name}</CardTitle>
                      {supplier.domain && <CardDescription>{supplier.domain}</CardDescription>}
                    </div>
                    <Badge
                      className={
                        supplier.type === "supplier"
                          ? "bg-[var(--status-supplier)] hover:bg-[var(--status-supplier)]/90"
                          : "bg-[var(--status-reseller)] hover:bg-[var(--status-reseller)]/90"
                      }
                    >
                      {supplier.type}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    {supplier.inn && (
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">INN:</span>
                        <span className="font-medium">{supplier.inn}</span>
                      </div>
                    )}

                    {supplier.email && (
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <a href={`mailto:${supplier.email}`} className="text-primary hover:underline">
                          {supplier.email}
                        </a>
                      </div>
                    )}

                    {supplier.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <a href={`tel:${supplier.phone}`} className="text-primary hover:underline">
                          {supplier.phone}
                        </a>
                      </div>
                    )}

                    {supplier.website && (
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 text-muted-foreground" />
                        <a
                          href={supplier.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                        >
                          Visit Website
                        </a>
                      </div>
                    )}

                    {supplier.createdAt && (
                      <div className="pt-2 text-xs text-muted-foreground">
                        {t("added")} {format(new Date(supplier.createdAt), "PPp")}
                      </div>
                    )}

                    <Button asChild variant="outline" size="sm" className="mt-2 w-full bg-transparent">
                      <Link href={`/suppliers/${supplier.id}`}>
                        {t("viewDetails")}
                        <ExternalLink className="ml-2 h-3 w-3" />
                      </Link>
                    </Button>
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
