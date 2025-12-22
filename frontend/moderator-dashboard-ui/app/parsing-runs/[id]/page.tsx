"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Plus, Ban, Clock } from "lucide-react"

interface Domain {
  domain: string
  status: "supplier" | "reseller" | "blacklist" | "pending"
  urls: Array<{
    title: string
    url: string
    source: string
    keyword: string
  }>
}

interface LogEntry {
  timestamp: string
  level: "INFO" | "WARN" | "ERROR"
  message: string
}

export default function ParsingRunDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const [filter, setFilter] = useState("all")

  const domains: Domain[] = [
    {
      domain: "metallpro.ru",
      status: "supplier",
      urls: [
        {
          title: "Металлопрокат оптом - главная",
          url: "https://metallpro.ru",
          source: "Google",
          keyword: "металлопрокат москва",
        },
        {
          title: "Каталог продукции",
          url: "https://metallpro.ru/catalog",
          source: "Google",
          keyword: "металлопрокат москва",
        },
      ],
    },
    {
      domain: "steelmarket.com",
      status: "pending",
      urls: [
        {
          title: "Steel Market - B2B marketplace",
          url: "https://steelmarket.com",
          source: "Yandex",
          keyword: "металлопрокат москва",
        },
      ],
    },
  ]

  const logs: LogEntry[] = [
    {
      timestamp: "14:35:01",
      level: "INFO",
      message: 'Запуск парсинга для ключа "металлопрокат москва"',
    },
    {
      timestamp: "14:35:05",
      level: "INFO",
      message: "Получено 45 результатов из Google",
    },
    {
      timestamp: "14:35:12",
      level: "INFO",
      message: "Получено 38 результатов из Yandex",
    },
    {
      timestamp: "14:35:20",
      level: "WARN",
      message: "Домен example.com недоступен (timeout)",
    },
    {
      timestamp: "14:36:45",
      level: "INFO",
      message: "Парсинг завершен. Обработано доменов: 12",
    },
  ]

  const handleAction = async (domain: string, action: string) => {
    console.log("[v0] Action:", action, "for domain:", domain)
    // API call would go here
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-balance">Результаты запуска</h1>
          <p className="text-muted-foreground mt-2">Run ID: {params.id}</p>
        </div>

        <Tabs defaultValue="results" className="space-y-6">
          <TabsList className="bg-card/50 backdrop-blur-sm border border-white/[0.08]">
            <TabsTrigger value="results">Результаты</TabsTrigger>
            <TabsTrigger value="logs">Логи</TabsTrigger>
          </TabsList>

          <TabsContent value="results" className="space-y-4">
            <div className="flex gap-2">
              <Button variant={filter === "all" ? "secondary" : "ghost"} size="sm" onClick={() => setFilter("all")}>
                Все
              </Button>
              <Button
                variant={filter === "pending" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setFilter("pending")}
              >
                Очередь
              </Button>
              <Button
                variant={filter === "supplier" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setFilter("supplier")}
              >
                Поставщики
              </Button>
              <Button
                variant={filter === "reseller" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setFilter("reseller")}
              >
                Реселлеры
              </Button>
              <Button
                variant={filter === "blacklist" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setFilter("blacklist")}
              >
                Blacklist
              </Button>
            </div>

            <Accordion type="single" collapsible className="space-y-3">
              {domains.map((domain, i) => (
                <AccordionItem key={i} value={`domain-${i}`} className="border-none">
                  <Card className="overflow-hidden bg-card/50 backdrop-blur-sm border-white/[0.08]">
                    <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-accent/30 transition-colors duration-200">
                      <div className="flex items-center gap-4 flex-1 text-left">
                        <span className="text-base font-semibold">{domain.domain}</span>
                        <DomainStatusBadge status={domain.status} />
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-6 pb-4">
                      <div className="space-y-4 pt-2">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-1.5 h-8 text-xs bg-transparent"
                            onClick={() => handleAction(domain.domain, "supplier")}
                          >
                            <Plus className="w-3.5 h-3.5" />
                            Поставщик
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-1.5 h-8 text-xs bg-transparent"
                            onClick={() => handleAction(domain.domain, "reseller")}
                          >
                            <Plus className="w-3.5 h-3.5" />
                            Реселлер
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-1.5 h-8 text-xs bg-transparent"
                            onClick={() => handleAction(domain.domain, "blacklist")}
                          >
                            <Ban className="w-3.5 h-3.5" />
                            Blacklist
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-1.5 h-8 text-xs bg-transparent"
                            onClick={() => handleAction(domain.domain, "pending")}
                          >
                            <Clock className="w-3.5 h-3.5" />В очереди
                          </Button>
                        </div>

                        <div className="overflow-hidden rounded-lg border border-white/[0.08]">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b border-white/[0.08] bg-muted/30">
                                <th className="text-left py-2 px-3 text-xs font-medium text-muted-foreground">
                                  Заголовок
                                </th>
                                <th className="text-left py-2 px-3 text-xs font-medium text-muted-foreground">URL</th>
                                <th className="text-left py-2 px-3 text-xs font-medium text-muted-foreground">
                                  Источник
                                </th>
                                <th className="text-left py-2 px-3 text-xs font-medium text-muted-foreground">Ключ</th>
                              </tr>
                            </thead>
                            <tbody>
                              {domain.urls.map((url, j) => (
                                <tr key={j} className="border-b border-white/[0.05] last:border-0">
                                  <td className="py-2 px-3">{url.title}</td>
                                  <td className="py-2 px-3 font-mono text-xs text-muted-foreground">{url.url}</td>
                                  <td className="py-2 px-3">{url.source}</td>
                                  <td className="py-2 px-3 text-xs">{url.keyword}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </AccordionContent>
                  </Card>
                </AccordionItem>
              ))}
            </Accordion>
          </TabsContent>

          <TabsContent value="logs">
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
              <h3 className="text-lg font-semibold mb-4">Логи парсинга</h3>
              <div className="space-y-2">
                {logs.map((log, i) => (
                  <div
                    key={i}
                    className="flex gap-4 py-2 px-3 rounded hover:bg-accent/30 transition-colors duration-200"
                  >
                    <span className="text-xs font-mono text-muted-foreground shrink-0">{log.timestamp}</span>
                    <LogLevelBadge level={log.level} />
                    <span className="text-sm font-mono">{log.message}</span>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function DomainStatusBadge({ status }: { status: string }) {
  const styles = {
    supplier: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    reseller: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    blacklist: "bg-red-500/10 text-red-400 border-red-500/20",
    pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  }

  const labels = {
    supplier: "Поставщик",
    reseller: "Реселлер",
    blacklist: "Blacklist",
    pending: "Очередь",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${styles[status as keyof typeof styles]}`}
    >
      {labels[status as keyof typeof labels]}
    </span>
  )
}

function LogLevelBadge({ level }: { level: string }) {
  const styles = {
    INFO: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    WARN: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    ERROR: "bg-red-500/10 text-red-400 border-red-500/20",
  }

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-mono font-medium border shrink-0 ${styles[level as keyof typeof styles]}`}
    >
      {level}
    </span>
  )
}
