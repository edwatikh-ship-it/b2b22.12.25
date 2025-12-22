"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, AlertCircle } from "lucide-react"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { api, type Supplier } from "@/lib/api"

export default function SuppliersPage() {
  const [search, setSearch] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [sortBy, setSortBy] = useState("name")
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null)
  
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSuppliers()
  }, [])

  const loadSuppliers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.getSuppliers({
        q: search || undefined,
        limit: 100,
      })
      setSuppliers(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    loadSuppliers()
  }

  const filteredSuppliers = suppliers.filter(supplier => {
    if (!search) return true
    return supplier.name.toLowerCase().includes(search.toLowerCase()) ||
           supplier.domain?.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-balance">База поставщиков</h1>
        </div>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по названию или ИНН"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 h-10 bg-background/50"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={typeFilter === "all" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setTypeFilter("all")}
              >
                Все
              </Button>
              <Button
                variant={typeFilter === "supplier" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setTypeFilter("supplier")}
              >
                Поставщики
              </Button>
              <Button
                variant={typeFilter === "reseller" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setTypeFilter("reseller")}
              >
                Реселлеры
              </Button>
            </div>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-[200px] h-10 bg-background/50">
                <SelectValue placeholder="Сортировка" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">По имени (А–Я)</SelectItem>
                <SelectItem value="date">По дате добавления</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        {error && (
          <Card className="p-4 bg-red-500/10 border-red-500/20">
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          </Card>
        )}

        <Card className="overflow-hidden bg-card/50 backdrop-blur-sm border-white/[0.08]">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Загрузка...</div>
          ) : filteredSuppliers.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">Пока нет данных</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/[0.08] bg-muted/30">
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">ID</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Название</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Домен</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Email</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Телефон</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">Создан</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSuppliers.map((supplier) => (
                    <tr
                      key={supplier.id}
                      className="border-b border-white/[0.05] hover:bg-accent/50 transition-colors duration-200 cursor-pointer"
                      onClick={() => setSelectedSupplier(supplier)}
                    >
                      <td className="py-3 px-4 text-sm font-mono text-muted-foreground">{supplier.id}</td>
                      <td className="py-3 px-4 text-sm font-medium">{supplier.name}</td>
                      <td className="py-3 px-4 text-sm">{supplier.domain || '-'}</td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">{supplier.email || '-'}</td>
                      <td className="py-3 px-4 text-sm">{supplier.phone || '-'}</td>
                      <td className="py-3 px-4 text-sm">
                        {new Date(supplier.createdAt).toLocaleString('ru-RU')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      <Sheet open={!!selectedSupplier} onOpenChange={() => setSelectedSupplier(null)}>
        <SheetContent className="w-full sm:max-w-lg">
          {selectedSupplier && (
            <>
              <SheetHeader>
                <SheetTitle className="text-2xl">{selectedSupplier.name}</SheetTitle>
              </SheetHeader>
              <div className="mt-6 space-y-6">
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">ID</div>
                  <div className="text-base font-mono">{selectedSupplier.id}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Домен</div>
                  <div className="text-base">{selectedSupplier.domain || '-'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Email</div>
                  <div className="text-base">{selectedSupplier.email || '-'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Телефон</div>
                  <div className="text-base">{selectedSupplier.phone || '-'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Статус</div>
                  <div className="text-base">{selectedSupplier.status || '-'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Создан</div>
                  <div className="text-base">{new Date(selectedSupplier.createdAt).toLocaleString('ru-RU')}</div>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </DashboardLayout>
  )
}

function SupplierTypeBadge({ type }: { type: string }) {
  const styles = {
    supplier: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    reseller: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  }

  const labels = {
    supplier: "Поставщик",
    reseller: "Реселлер",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${styles[type as keyof typeof styles]}`}
    >
      {labels[type as keyof typeof labels]}
    </span>
  )
}
