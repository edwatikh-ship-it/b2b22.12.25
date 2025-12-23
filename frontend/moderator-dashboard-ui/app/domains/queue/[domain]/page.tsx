"use client"
import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { apiFetch, APIError } from "@/lib/api"
import type { DomainDecisionRequestDTO } from "@/lib/types"
import { ErrorState } from "@/components/error-state"
import { LoadingState } from "@/components/loading-state"
import { Loader2 } from "lucide-react"
import { format } from "date-fns"
import { useToast } from "@/hooks/use-toast"

import type { PendingDomainDetailDTO } from "@/lib/types"

export default function DomainDetailPage() {
  const params = useParams()
  const router = useRouter()
  const domain = decodeURIComponent(params.domain as string)
  const { toast } = useToast()

  const [data, setData] = useState<PendingDomainDetailDTO | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Form state for supplier/reseller
  const [cardData, setCardData] = useState({
    inn: "",
    name: "",
    email: "",
    phone: "",
    website: "",
  })
  const [comment, setComment] = useState("")

  useEffect(() => {
    fetchDomainDetail()
  }, [domain])

  const fetchDomainDetail = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await apiFetch<PendingDomainDetailDTO>(`/moderator/pending-domains/${encodeURIComponent(domain)}`)
      setData(response)
      // Pre-fill website with domain
      setCardData((prev) => ({ ...prev, website: `https://${domain}` }))
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to load domain details")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleDecision = async (status: "supplier" | "reseller" | "blacklist" | "pending") => {
    setIsSubmitting(true)

    try {
      const body: DomainDecisionRequestDTO = {
        status,
        comment: comment.trim() || undefined,
      }

      // Only include carddata for supplier and reseller
      if (status === "supplier" || status === "reseller") {
        body.carddata = {
          inn: cardData.inn.trim() || undefined,
          name: cardData.name.trim() || undefined,
          email: cardData.email.trim() || undefined,
          phone: cardData.phone.trim() || undefined,
          website: cardData.website.trim() || undefined,
        }
      }

      await apiFetch(`/moderator/domains/${encodeURIComponent(domain)}/decision`, {
        method: "POST",
        body: JSON.stringify(body),
      })

      toast({
        title: "Decision Saved",
        description: `Domain marked as ${status}`,
      })

      // Navigate back to queue after a short delay
      setTimeout(() => {
        router.push("/domains/queue")
      }, 1000)
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
          description: "Failed to save decision",
          variant: "destructive",
        })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading domain details..." />
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <ErrorState message={error || "Failed to load domain"} />
        <Button onClick={() => router.back()} variant="outline">
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{data.domain}</h1>
        <p className="text-muted-foreground">Make a decision on this pending domain</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Domain Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Total Hits</p>
                  <Badge variant="secondary" className="mt-1">
                    {data.totalhits}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Unique URLs</p>
                  <Badge variant="secondary" className="mt-1">
                    {data.urlcount}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">First Seen</p>
                  <p className="mt-1 font-medium">{format(new Date(data.firstseenat), "PPp")}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Last Seen</p>
                  <p className="mt-1 font-medium">{format(new Date(data.lasthitat), "PPp")}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {data.urls && data.urls.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Found URLs</CardTitle>
                <CardDescription>{data.urls.length} URLs from this domain</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.urls.map((urlItem, idx) => (
                    <div key={idx} className="space-y-2 rounded-md bg-muted p-3">
                      <div className="flex items-center justify-between">
                        <a
                          href={urlItem.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="break-all text-sm text-primary hover:underline"
                        >
                          {urlItem.url}
                        </a>
                        <Badge variant="secondary">{urlItem.hitcount} hits</Badge>
                      </div>
                      {urlItem.keys && urlItem.keys.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {urlItem.keys.map((key, keyIdx) => (
                            <Badge key={keyIdx} variant="outline" className="text-xs">
                              {key}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Make Decision</CardTitle>
              <CardDescription>Choose action for this domain</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Company Name (Optional)</Label>
                <Input
                  id="name"
                  placeholder="Company name"
                  value={cardData.name}
                  onChange={(e) => setCardData({ ...cardData, name: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="inn">INN (Optional)</Label>
                <Input
                  id="inn"
                  placeholder="Tax identification number"
                  value={cardData.inn}
                  onChange={(e) => setCardData({ ...cardData, inn: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email (Optional)</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="contact@example.com"
                  value={cardData.email}
                  onChange={(e) => setCardData({ ...cardData, email: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone (Optional)</Label>
                <Input
                  id="phone"
                  placeholder="+1234567890"
                  value={cardData.phone}
                  onChange={(e) => setCardData({ ...cardData, phone: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="website">Website</Label>
                <Input
                  id="website"
                  placeholder="https://example.com"
                  value={cardData.website}
                  onChange={(e) => setCardData({ ...cardData, website: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="comment">Comment (Optional)</Label>
                <Textarea
                  id="comment"
                  placeholder="Add any notes about this decision"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="space-y-2 pt-4">
                <Button
                  className="w-full bg-[var(--status-supplier)] hover:bg-[var(--status-supplier)]/90"
                  onClick={() => handleDecision("supplier")}
                  disabled={isSubmitting}
                >
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Mark as Supplier
                </Button>
                <Button
                  className="w-full bg-[var(--status-reseller)] hover:bg-[var(--status-reseller)]/90"
                  onClick={() => handleDecision("reseller")}
                  disabled={isSubmitting}
                >
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Mark as Reseller
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-[var(--status-blacklist)] text-[var(--status-blacklist)] hover:bg-[var(--status-blacklist)] hover:text-white bg-transparent"
                  onClick={() => handleDecision("blacklist")}
                  disabled={isSubmitting}
                >
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Add to Blacklist
                </Button>
                <Button
                  variant="outline"
                  className="w-full bg-transparent"
                  onClick={() => handleDecision("pending")}
                  disabled={isSubmitting}
                >
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Keep Pending
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
