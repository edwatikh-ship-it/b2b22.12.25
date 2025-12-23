"use client"
import { useEffect, useState } from "react"
import type React from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { apiFetch, APIError } from "@/lib/api"
import type { ModeratorBlacklistDomainListResponseDTO, ModeratorBlacklistDomainDTO } from "@/lib/types"
import { EmptyState } from "@/components/empty-state"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { Shield, Plus, Trash2, Loader2, ExternalLink, ArrowLeft, Home, ChevronDown, ChevronUp } from "lucide-react"
import { format } from "date-fns"
import { useToast } from "@/hooks/use-toast"
import { useI18n } from "@/lib/i18n/i18n-context"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function BlacklistPage() {
  const { t } = useI18n()
  const router = useRouter()
  const { toast } = useToast()
  const [data, setData] = useState<ModeratorBlacklistDomainListResponseDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deletingDomain, setDeletingDomain] = useState<string | null>(null)
  const [expandedUrls, setExpandedUrls] = useState<Set<string>>(new Set())
  const [expandAll, setExpandAll] = useState(false)

  // Form state
  const [domain, setDomain] = useState("")
  const [url, setUrl] = useState("")
  const [comment, setComment] = useState("")

  const toggleUrlExpansion = (domain: string) => {
    const newExpanded = new Set(expandedUrls)
    if (newExpanded.has(domain)) {
      newExpanded.delete(domain)
    } else {
      newExpanded.add(domain)
    }
    setExpandedUrls(newExpanded)
  }

  const toggleExpandAll = () => {
    if (expandAll) {
      setExpandedUrls(new Set())
    } else if (data) {
      setExpandedUrls(new Set(data.items.map(item => item.domain)))
    }
    setExpandAll(!expandAll)
  }

  const isUrlsExpanded = (domain: string, urlsCount: number) => {
    // Auto-expand if 1-3 URLs or expandAll is true
    return urlsCount <= 3 || expandAll || expandedUrls.has(domain)
  }

  useEffect(() => {
    fetchBlacklist()
  }, [])

  const fetchBlacklist = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({ limit: "50", offset: "0" })
      const response = await apiFetch<ModeratorBlacklistDomainListResponseDTO>(`/moderator/blacklist/domains?${params}`)
      setData(response)
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load blacklist")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddDomain = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      await apiFetch<ModeratorBlacklistDomainDTO>("/moderator/blacklist/domains", {
        method: "POST",
        body: JSON.stringify({
          domain: domain.trim(),
          url: url.trim() || undefined,
          comment: comment.trim() || undefined,
        }),
      })

      toast({
        title: "Domain Added",
        description: `${domain.trim()} has been added to the blacklist`,
      })

      // Reset form and close dialog
      setDomain("")
      setUrl("")
      setComment("")
      setIsDialogOpen(false)

      // Refresh list
      await fetchBlacklist()
    } catch (err) {
      if (err instanceof APIError) {
        toast({
          title: "Error",
          description: err.message,
          variant: "destructive",
        })
      } else {
        toast({
          title: "Error",
          description: "Failed to add domain to blacklist",
          variant: "destructive",
        })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteDomain = async (domainToDelete: string) => {
    if (!confirm(`Are you sure you want to remove ${domainToDelete} from the blacklist?`)) {
      return
    }

    setDeletingDomain(domainToDelete)

    try {
      await apiFetch(`/moderator/blacklist/domains/${encodeURIComponent(domainToDelete)}`, {
        method: "DELETE",
      })

      toast({
        title: "Domain Removed",
        description: `${domainToDelete} has been removed from the blacklist`,
      })

      // Refresh list
      await fetchBlacklist()
    } catch (err) {
      if (err instanceof APIError) {
        toast({
          title: "Error",
          description: err.message,
          variant: "destructive",
        })
      } else {
        toast({
          title: "Error",
          description: "Failed to remove domain from blacklist",
          variant: "destructive",
        })
      }
    } finally {
      setDeletingDomain(null)
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
            <h1 className="text-3xl font-bold tracking-tight">{t("blacklistTitle")}</h1>
            <p className="text-muted-foreground">{t("blacklistSubtitle")}</p>
          </div>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              {t("addDomain")}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleAddDomain}>
              <DialogHeader>
                <DialogTitle>Add Domain to Blacklist</DialogTitle>
                <DialogDescription>
                  Add a root domain (without scheme or path) to the global blacklist
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="domain">Domain *</Label>
                  <Input
                    id="domain"
                    placeholder="example.com"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">Enter root domain without https:// or www.</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="url">Source URL (Optional)</Label>
                  <Input
                    id="url"
                    type="url"
                    placeholder="https://example.com/page"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="comment">Comment (Optional)</Label>
                  <Textarea
                    id="comment"
                    placeholder="Reason for blacklisting"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting || !domain.trim()}>
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Add to Blacklist
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && <ErrorState message={error} />}

      {isLoading ? (
        <LoadingState message="Loading blacklist..." />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Shield}
          title="No Blacklisted Domains"
          description="No domains have been blacklisted yet. Add domains that should be excluded from parsing results."
          action={
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add First Domain
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {data.items.length} of {data.total} blacklisted domains
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleExpandAll}
              className="gap-2"
            >
              {expandAll ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  Collapse All
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  Expand All
                </>
              )}
            </Button>
          </div>

          <div className="grid gap-4">
            {data.items.map((item) => (
              <Card key={item.domain}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-base">{item.domain}</CardTitle>
                      <CardDescription>Added {format(new Date(item.createdat), "PPp")}</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDeleteDomain(item.domain)}
                      disabled={deletingDomain === item.domain}
                      className="border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
                    >
                      {deletingDomain === item.domain ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </CardHeader>
                {(item.comment || (item.urls && item.urls.length > 0)) && (
                  <CardContent className="space-y-3">
                    {item.comment && (
                      <div>
                        <p className="text-sm text-muted-foreground">Comment</p>
                        <p className="mt-1 text-sm">{item.comment}</p>
                      </div>
                    )}
                    {item.urls && item.urls.length > 0 && (
                      <div>
                        <button
                          onClick={() => toggleUrlExpansion(item.domain)}
                          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                        >
                          <span>Source URLs ({item.urls.length})</span>
                          {item.urls.length > 3 && (
                            isUrlsExpanded(item.domain, item.urls.length) ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <>
                                <ChevronDown className="h-4 w-4" />
                                <span className="text-xs truncate max-w-xs">{item.urls[0]?.url}</span>
                              </>
                            )
                          )}
                        </button>
                        {isUrlsExpanded(item.domain, item.urls.length) && (
                          <div className="mt-2 space-y-1">
                            {item.urls.map((urlItem, idx) => (
                              <div key={idx} className="flex items-center justify-between rounded-md bg-muted p-2">
                                <a
                                  href={urlItem.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1 text-sm text-primary hover:underline break-all"
                                >
                                  {urlItem.url}
                                  <ExternalLink className="h-3 w-3 shrink-0" />
                                </a>
                                {urlItem.comment && (
                                  <span className="text-xs text-muted-foreground">{urlItem.comment}</span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
