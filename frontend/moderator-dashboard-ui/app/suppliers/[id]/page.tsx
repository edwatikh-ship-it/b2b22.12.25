"use client"
import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { apiFetch, APIError } from "@/lib/api"
import type { SupplierDTO } from "@/lib/types"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { Mail, Phone, Globe, Building2, Calendar, ArrowLeft } from "lucide-react"
import { format } from "date-fns"

export default function SupplierDetailPage() {
  const params = useParams()
  const router = useRouter()
  const supplierId = params.id as string

  const [data, setData] = useState<SupplierDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSupplier()
  }, [supplierId])

  const fetchSupplier = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await apiFetch<SupplierDTO>(`/moderator/suppliers/${supplierId}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load supplier details")
      }
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading supplier details..." />
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <ErrorState message={error || "Failed to load supplier"} />
        <Button onClick={() => router.back()} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button onClick={() => router.back()} variant="ghost" size="icon">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{data.name}</h1>
          <p className="text-muted-foreground">Supplier Details</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle>Company Information</CardTitle>
                  <CardDescription>Details about this {data.type}</CardDescription>
                </div>
                <Badge
                  className={
                    data.type === "supplier"
                      ? "bg-[var(--status-supplier)] hover:bg-[var(--status-supplier)]/90"
                      : "bg-[var(--status-reseller)] hover:bg-[var(--status-reseller)]/90"
                  }
                >
                  {data.type}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.inn && (
                <div className="flex items-start gap-3">
                  <Building2 className="mt-0.5 h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">INN</p>
                    <p className="font-medium">{data.inn}</p>
                  </div>
                </div>
              )}

              {data.domain && (
                <div className="flex items-start gap-3">
                  <Globe className="mt-0.5 h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Domain</p>
                    <p className="font-medium">{data.domain}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {(data.email || data.phone || data.website) && (
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.email && (
                  <div className="flex items-start gap-3">
                    <Mail className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Email</p>
                      <a href={`mailto:${data.email}`} className="font-medium text-primary hover:underline">
                        {data.email}
                      </a>
                    </div>
                  </div>
                )}

                {data.phone && (
                  <div className="flex items-start gap-3">
                    <Phone className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Phone</p>
                      <a href={`tel:${data.phone}`} className="font-medium text-primary hover:underline">
                        {data.phone}
                      </a>
                    </div>
                  </div>
                )}

                {data.website && (
                  <div className="flex items-start gap-3">
                    <Globe className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Website</p>
                      <a
                        href={data.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-primary hover:underline"
                      >
                        {data.website}
                      </a>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <Calendar className="mt-0.5 h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Created</p>
                  <p className="font-medium">{data.createdAt ? format(new Date(data.createdAt), "PPp") : "—"}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Building2 className="mt-0.5 h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">ID</p>
                  <p className="font-medium font-mono text-sm">{data.id}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
