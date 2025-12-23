"use client"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiFetch, APIError } from "@/lib/api"
import type {
  ParsingResultsResponseDTO,
  ParsingRunDTO,
  ParsingRunLogResponseDTO,
  ParsingRunsListResponseDTO,
} from "@/lib/types"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { StatusBadge } from "@/components/status-badge"
import { DomainResultsAccordion } from "@/components/domain-results-accordion"
import { RefreshCw, ArrowLeft, Home, CheckCircle2, AlertTriangle, XCircle, Copy } from "lucide-react"
import { format } from "date-fns"
import { useI18n } from "@/lib/i18n/i18n-context"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import Link from "next/link"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function ParsingRunDetailPage() {
  const { t } = useI18n()
  const router = useRouter()
  const { toast } = useToast()
  const params = useParams()
  const runId = params.runId as string

  const [run, setRun] = useState<ParsingRunDTO | null>(null)
  const [results, setResults] = useState<ParsingResultsResponseDTO | null>(null)
  const [logs, setLogs] = useState<ParsingRunLogResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const [processingDomain, setProcessingDomain] = useState<string | null>(null)
  const [showSupplierDialog, setShowSupplierDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<{domain: string, action: "supplier" | "reseller"} | null>(null)
  const [supplierName, setSupplierName] = useState("")
  const [supplierInn, setSupplierInn] = useState("")
  const [supplierEmail, setSupplierEmail] = useState("")

  const copyLogsToClipboard = () => {
    if (!logs || !logs.events) return
    const rawLogs = JSON.stringify(logs.events, null, 2)
    navigator.clipboard.writeText(rawLogs)
    toast({
      title: t("logsCopied"),
      description: t("logsCopiedDescription"),
    })
  }

  useEffect(() => {
    fetchRunDetails()
  }, [runId])

  useEffect(() => {
    // Auto-refresh if status is queued or running
    // Also refresh once after status changes to check for completion
    if (run?.status === "queued" || run?.status === "running") {
      const interval = setInterval(() => {
        setIsPolling(true)
        fetchRunDetails()
      }, 3000) // Reduced to 3 seconds for faster status updates

      return () => clearInterval(interval)
    } else if (run?.status && (run.status === "succeeded" || run.status === "failed")) {
      // If status changed to succeeded/failed, refresh once more to ensure UI is updated
      setIsPolling(true)
      fetchRunDetails()
      setTimeout(() => setIsPolling(false), 1000)
    } else {
      setIsPolling(false)
    }
  }, [run?.status, runId])

  const fetchRunDetails = async () => {
    if (!runId) return

    try {
      // Fetch run details (which includes results) and logs in parallel
      const [resultsResponse, logsResponse] = await Promise.all([
        apiFetch<ParsingResultsResponseDTO>(`/moderator/parsing-runs/${runId}`),
        apiFetch<ParsingRunLogResponseDTO>(`/moderator/parsing-runs/${runId}/logs`).catch(() => null),
      ])

      // Extract run info from results
      // Try to get run status from list endpoint
      try {
        const runsList = await apiFetch<ParsingRunsListResponseDTO>(`/moderator/parsing-runs?limit=100`)
        const matchingRun = runsList.items.find((r) => r.runId === runId)
        if (matchingRun) {
          setRun(matchingRun)
        } else {
          // Fallback: create minimal run info from results
          setRun({
            runId: resultsResponse.runId,
            requestId: resultsResponse.requestId,
            status: resultsResponse.results.length > 0 ? "succeeded" : "running",
          })
        }
      } catch {
        // Fallback: create minimal run info from results
        setRun({
          runId: resultsResponse.runId,
          requestId: resultsResponse.requestId,
          status: resultsResponse.results.length > 0 ? "succeeded" : "running",
        })
      }
      setResults(resultsResponse)

      if (logsResponse) {
        setLogs(logsResponse)
      } else {
        setLogs(null)
      }

      setError(null)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load parsing run details")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleDomainAction = async (domain: string, action: "supplier" | "reseller" | "blacklist" | "pending") => {
    if (processingDomain === domain) return
    
    if (action === "supplier" || action === "reseller") {
      // Show dialog for required fields
      setPendingAction({ domain, action })
      setSupplierName("")
      setSupplierInn("")
      setSupplierEmail("")
      setShowSupplierDialog(true)
      return
    }
    
    setProcessingDomain(domain)
    
    try {
      if (action === "blacklist") {
        // Add to blacklist
        await apiFetch("/moderator/blacklist/domains", {
          method: "POST",
          body: JSON.stringify({
            domain: domain,
            comment: `Added from parsing run ${runId}`,
          }),
        })
        toast({
          title: t("success"),
          description: t("domainAddedToBlacklist").replace("{domain}", domain),
        })
      } else if (action === "pending") {
        // Keep pending - no action needed, just show message
        toast({
          title: t("info"),
          description: t("domainKeptPending").replace("{domain}", domain),
        })
      }
      
      // Refresh results to show updated status
      await fetchRunDetails()
    } catch (err) {
      if (err instanceof APIError) {
        toast({
          title: t("error"),
          description: err.message,
          variant: "destructive",
        })
      } else {
        toast({
          title: t("error"),
          description: t("failedToProcessDomain"),
          variant: "destructive",
        })
      }
    } finally {
      setProcessingDomain(null)
    }
  }

  const handleSupplierSubmit = async () => {
    if (!pendingAction || !supplierName.trim() || !supplierInn.trim() || !supplierEmail.trim()) {
      toast({
        title: t("error"),
        description: t("allFieldsRequired"),
        variant: "destructive",
      })
      return
    }

    setProcessingDomain(pendingAction.domain)
    setShowSupplierDialog(false)
    
    try {
      await apiFetch("/moderator/suppliers", {
        method: "POST",
        body: JSON.stringify({
          name: supplierName.trim(),
          inn: supplierInn.trim(),
          email: supplierEmail.trim(),
          domain: pendingAction.domain,
          type: pendingAction.action,
        }),
      })
      const typeText = pendingAction.action === "supplier" ? t("supplier") : t("reseller")
      toast({
        title: t("success"),
        description: t("domainAddedAsSupplier").replace("{domain}", pendingAction.domain).replace("{type}", typeText),
      })
      
      // Refresh results to show updated status
      await fetchRunDetails()
    } catch (err) {
      if (err instanceof APIError) {
        toast({
          title: t("error"),
          description: err.message,
          variant: "destructive",
        })
      } else {
        toast({
          title: t("error"),
          description: t("failedToProcessDomain"),
          variant: "destructive",
        })
      }
    } finally {
      setProcessingDomain(null)
      setPendingAction(null)
      setSupplierName("")
      setSupplierInn("")
      setSupplierEmail("")
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading parsing run details..." />
  }

  if (error || !run) {
    return (
      <div className="space-y-4">
        <ErrorState message={error || "Failed to load parsing run"} />
        <Button onClick={() => window.history.back()} variant="outline">
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
              title={t("goBack")}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <Link href="/dashboard">
              <Button variant="ghost" size="icon" title={t("goToHome")}>
                <Home className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{t("runDetails")}</h1>
            <p className="text-muted-foreground">
              {results?.results?.[0]?.keyword 
                ? `${t("keyword")}: ${results?.results?.[0]?.keyword || ""}`
                : `${t("runId")}: ${runId.slice(0, 8)}`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isPolling && <span className="text-sm text-muted-foreground">{t("autoRefreshing")}</span>}
          <Button onClick={fetchRunDetails} variant="outline" size="icon" disabled={isPolling}>
            <RefreshCw className={`h-4 w-4 ${isPolling ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{t("runInformation")}</CardTitle>
              {run.requestId && <CardDescription>{t("requestId")}: {run.requestId}</CardDescription>}
            </div>
            <StatusBadge status={run.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {run.createdAt && (
              <div>
                <p className="text-sm text-muted-foreground">{t("createdAt")}</p>
                <p className="font-medium">{format(new Date(run.createdAt), "PPp")}</p>
              </div>
            )}
            {run.finishedAt && (
              <div>
                <p className="text-sm text-muted-foreground">{t("finishedAt")}</p>
                <p className="font-medium">{format(new Date(run.finishedAt), "PPp")}</p>
              </div>
            )}
            {run.depth !== undefined && (
              <div>
                <p className="text-sm text-muted-foreground">{t("depth")}</p>
                <p className="font-medium">{run.depth}</p>
              </div>
            )}
            {run.source && (
              <div>
                <p className="text-sm text-muted-foreground">{t("source")}</p>
                <p className="font-medium capitalize">{run.source}</p>
              </div>
            )}
            {run.totalKeys !== undefined && (
              <div>
                <p className="text-sm text-muted-foreground">{t("totalKeywords")}</p>
                <p className="font-medium">{run.totalKeys}</p>
              </div>
            )}
          </div>

          {run.errorMessage && (
            <div className="mt-4 rounded-md bg-destructive/10 p-4">
              <p className="text-sm font-medium text-destructive">Error</p>
              <p className="mt-1 text-sm text-destructive">{run.errorMessage}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="results" className="w-full">
        <TabsList>
          <TabsTrigger value="results">{t("results")}</TabsTrigger>
          <TabsTrigger value="logs">{t("logs")}</TabsTrigger>
        </TabsList>

        <TabsContent value="results" className="space-y-4">
          {results && results.results && results.results.length > 0 ? (
            <DomainResultsAccordion 
              results={results.results} 
              showActions={true}
              onDomainAction={handleDomainAction}
            />
          ) : (
            <Card>
              <CardContent className="py-8">
                <p className="text-center text-sm text-muted-foreground">
                  {run.status === "running" || run.status === "queued"
                    ? t("parsingInProgress")
                    : t("noResultsAvailable")}
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{t("logs")}</CardTitle>
                  <CardDescription>{t("parsingLogsDescription")}</CardDescription>
                </div>
                {logs && logs.events && logs.events.length > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={copyLogsToClipboard}
                    className="gap-2"
                  >
                    <Copy className="h-4 w-4" />
                    {t("copyRawLogs")}
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {logs && logs.events && logs.events.length > 0 ? (
                <div className="space-y-1">
                  {logs.events.map((event, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 rounded-md px-3 py-2 text-sm hover:bg-muted/50 transition-colors"
                    >
                      {event.level === "error" ? (
                        <XCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                      ) : event.level === "warn" ? (
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 shrink-0" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-baseline gap-2 flex-wrap">
                          <span className="text-xs text-muted-foreground font-mono">
                            {format(new Date(event.timestamp), "HH:mm:ss")}
                          </span>
                          <span className={
                            event.level === "error" 
                              ? "text-destructive" 
                              : event.level === "warn"
                                ? "text-yellow-600"
                                : ""
                          }>
                            {event.message}
                          </span>
                        </div>
                        {event.context && Object.keys(event.context).length > 0 && (
                          <pre className="mt-1 overflow-auto rounded bg-muted p-2 text-xs text-muted-foreground">
                            {JSON.stringify(event.context, null, 2)}
                          </pre>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-sm text-muted-foreground">{t("noLogsAvailable")}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Supplier/Reseller Dialog */}
      <Dialog open={showSupplierDialog} onOpenChange={setShowSupplierDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {pendingAction?.action === "supplier" ? t("addSupplier") : t("addReseller")}
            </DialogTitle>
            <DialogDescription>
              {t("fillRequiredFields")} {pendingAction?.domain}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="supplier-name">{t("companyName")} *</Label>
              <Input
                id="supplier-name"
                placeholder={t("companyNamePlaceholder")}
                value={supplierName}
                onChange={(e) => setSupplierName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="supplier-inn">{t("inn")} *</Label>
              <Input
                id="supplier-inn"
                placeholder={t("innPlaceholder")}
                value={supplierInn}
                onChange={(e) => setSupplierInn(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="supplier-email">{t("salesEmail")} *</Label>
              <Input
                id="supplier-email"
                type="email"
                placeholder={t("salesEmailPlaceholder")}
                value={supplierEmail}
                onChange={(e) => setSupplierEmail(e.target.value)}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSupplierDialog(false)}>
              {t("cancel")}
            </Button>
            <Button onClick={handleSupplierSubmit} disabled={!supplierName.trim() || !supplierInn.trim() || !supplierEmail.trim()}>
              {t("save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
