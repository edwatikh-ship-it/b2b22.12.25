"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Search, History, Clock, Database, Building2, Shield, ArrowRight } from "lucide-react"
import Link from "next/link"
import { useI18n } from "@/lib/i18n/i18n-context"

export default function DashboardPage() {
  const { t } = useI18n()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("dashboardTitle")}</h1>
        <p className="text-muted-foreground">{t("dashboardSubtitle")}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <Search className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("startNewParsing")}</CardTitle>
            <CardDescription>{t("startNewParsingDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/manual-parsing">
                {t("startParsing")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <History className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("viewParsingHistory")}</CardTitle>
            <CardDescription>{t("viewParsingHistoryDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/parsing-runs">
                {t("viewDetails")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <Clock className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("reviewPendingDomains")}</CardTitle>
            <CardDescription>{t("reviewPendingDomainsDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/domains/queue">
                {t("viewDetails")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <Database className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("manageKeywords")}</CardTitle>
            <CardDescription>{t("manageKeywordsDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/keywords">
                {t("viewDetails")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("manageSuppliersResellers")}</CardTitle>
            <CardDescription>{t("manageSuppliersResellersDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/suppliers">
                {t("viewDetails")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <Shield className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardTitle>{t("manageBlacklist")}</CardTitle>
            <CardDescription>{t("manageBlacklistDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/blacklist">
                {t("viewDetails")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
