"use client"
import { useState } from "react"
import type React from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiFetch, APIError } from "@/lib/api"
import type { StartParsingResponseDTO } from "@/lib/types"
import { useRouter } from "next/navigation"
import { ErrorState } from "@/components/error-state"
import { Loader2 } from "lucide-react"
import { useI18n } from "@/lib/i18n/i18n-context"

export default function ManualParsingPage() {
  const { t } = useI18n()
  const router = useRouter()
  const [keyword, setKeyword] = useState("")
  const [depth, setDepth] = useState("10")
  const [source, setSource] = useState<"google" | "yandex" | "both">("both")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const response = await apiFetch<StartParsingResponseDTO>("/moderator/manual-parsing", {
        method: "POST",
        body: JSON.stringify({
          keyword: keyword.trim(),
          depth: Number.parseInt(depth, 10),
          source,
        }),
      })

      // Redirect to the parsing run details page
      router.push(`/parsing-runs/${response.runId}`)
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 503) {
          setError("Parser service is currently unavailable. Please try again later.")
        } else {
          setError(err.message)
        }
      } else {
        setError("An unexpected error occurred. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("manualParsingTitle")}</h1>
        <p className="text-muted-foreground">{t("manualParsingSubtitle")}</p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>{t("startNewParsing")}</CardTitle>
          <CardDescription>{t("enterKeywordAndConfigure")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="keyword">{t("keywordLabel")}</Label>
              <Input
                id="keyword"
                placeholder={t("keywordPlaceholder")}
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                required
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="depth">{t("depthLabel")}</Label>
                <Input
                  id="depth"
                  type="number"
                  min="1"
                  max="50"
                  value={depth}
                  onChange={(e) => setDepth(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground">{t("depthDescription")}</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="source">{t("sourceLabel")}</Label>
                <Select value={source} onValueChange={(value) => setSource(value as typeof source)}>
                  <SelectTrigger id="source">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="google">Google</SelectItem>
                    <SelectItem value="yandex">Yandex</SelectItem>
                    <SelectItem value="both">{t("both")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error && <ErrorState message={error} />}

            <Button type="submit" disabled={isLoading || !keyword.trim()} className="w-full">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isLoading ? t("starting") : t("startParsing")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
