"use client"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { ParsingResultsByKeyDTO } from "@/lib/types"
import { ExternalLink, Shield, Building2, ShoppingCart, Clock, Key } from "lucide-react"
import { useI18n } from "@/lib/i18n/i18n-context"

interface DomainResultsAccordionProps {
  results: ParsingResultsByKeyDTO[]
  onDomainAction?: (domain: string, action: "supplier" | "reseller" | "blacklist" | "pending") => void
  showActions?: boolean
}

export function DomainResultsAccordion({ results, onDomainAction, showActions = true }: DomainResultsAccordionProps) {
  const { t } = useI18n()
  
  if (!results || results.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <p className="text-sm text-muted-foreground">{t("noResultsAvailable")}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {results.map((keyResult) => (
        <div key={keyResult.keyId} className="space-y-2">
          {keyResult.keyword && (
            <div className="flex items-center gap-2">
              <Badge variant="outline">Keyword: {keyResult.keyword}</Badge>
              <span className="text-sm text-muted-foreground">{keyResult.groups.length} domains</span>
            </div>
          )}

          <Accordion type="single" collapsible className="w-full">
            {keyResult.groups.map((group, idx) => {
              const domainUrl = `https://${group.domain.replace(/^www\./, "")}`
              const statusColor = group.status === "supplier" 
                ? "text-green-600 font-semibold" 
                : group.status === "reseller" 
                ? "text-blue-600 font-semibold" 
                : ""
              
              return (
              <AccordionItem key={`${group.domain}-${idx}`} value={`${group.domain}-${idx}`} className="border rounded-lg px-4">
                <div className="flex items-center justify-between gap-4 py-2">
                  <AccordionTrigger className="hover:no-underline flex-1 py-2">
                    <div className="flex items-center gap-2 text-left flex-wrap">
                      <a
                        href={domainUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className={`font-medium hover:underline ${statusColor}`}
                        title={t("openDomain")}
                      >
                        {group.domain}
                      </a>
                      <Badge variant="secondary" className="text-xs">
                        {group.urls.length} URLs
                      </Badge>
                      {group.source && (
                        <Badge variant="outline" className="text-xs">
                          {group.source}
                        </Badge>
                      )}
                      {keyResult.keyword && (
                        <Badge variant="outline" className="text-xs bg-muted/50">
                          <Key className="mr-1 h-3 w-3" />
                          {keyResult.keyword}
                        </Badge>
                      )}
                      {group.status === "supplier" && (
                        <Badge className="bg-green-600 text-white text-xs">
                          {t("supplier")}
                        </Badge>
                      )}
                      {group.status === "reseller" && (
                        <Badge className="bg-blue-600 text-white text-xs">
                          {t("reseller")}
                        </Badge>
                      )}
                    </div>
                  </AccordionTrigger>
                  
                  {showActions && onDomainAction && !group.status && (
                    <div className="flex flex-wrap gap-1.5 shrink-0">
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          onDomainAction(group.domain, "supplier")
                        }}
                        className="bg-green-600 hover:bg-green-700 text-white h-8 px-3"
                        title={t("markAsSupplier")}
                      >
                        <Building2 className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          onDomainAction(group.domain, "reseller")
                        }}
                        className="bg-blue-600 hover:bg-blue-700 text-white h-8 px-3"
                        title={t("markAsReseller")}
                      >
                        <ShoppingCart className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation()
                          onDomainAction(group.domain, "blacklist")
                        }}
                        className="border-red-600 text-red-600 hover:bg-red-600 hover:text-white h-8 px-3"
                        title={t("addToBlacklist")}
                      >
                        <Shield className="h-3.5 w-3.5" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={(e) => {
                          e.stopPropagation()
                          onDomainAction(group.domain, "pending")
                        }}
                        className="border-gray-400 text-gray-600 hover:bg-gray-100 h-8 px-3"
                        title={t("keepPending")}
                      >
                        <Clock className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  )}
                </div>
                
                <AccordionContent>
                  <div className="space-y-2 pb-4">
                    {group.urls.map((url, urlIdx) => (
                      <div
                        key={urlIdx}
                        className="group flex items-start justify-between gap-2 rounded-md bg-muted p-3 text-sm transition-colors hover:bg-muted/80"
                      >
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 break-all text-primary hover:underline"
                          title={url}
                        >
                          {url}
                        </a>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="shrink-0 text-primary opacity-0 transition-opacity group-hover:opacity-100"
                          title={t("openInNewTab")}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
              )
            })}
          </Accordion>
        </div>
      ))}
    </div>
  )
}
