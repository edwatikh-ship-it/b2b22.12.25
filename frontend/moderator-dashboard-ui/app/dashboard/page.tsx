"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Clock, CheckCircle2, XCircle, TrendingUp, Database } from "lucide-react"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Панель управления</h1>
          <p className="text-muted-foreground mt-2">Обзор активности платформы парсинга</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Активные запуски</CardTitle>
              <Activity className="w-4 h-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground mt-1">+2 за последний час</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">В очереди</CardTitle>
              <Clock className="w-4 h-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">847</div>
              <p className="text-xs text-muted-foreground mt-1">доменов ожидают обработки</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Успешных</CardTitle>
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,284</div>
              <p className="text-xs text-muted-foreground mt-1">за последние 24 часа</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Ошибок</CardTitle>
              <XCircle className="w-4 h-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">23</div>
              <p className="text-xs text-muted-foreground mt-1">требуют внимания</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
              <TrendingUp className="w-4 h-4 text-cyan-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">98.2%</div>
              <p className="text-xs text-muted-foreground mt-1">+0.5% от прошлой недели</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">База данных</CardTitle>
              <Database className="w-4 h-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">45.2K</div>
              <p className="text-xs text-muted-foreground mt-1">записей в системе</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="bg-card/50 backdrop-blur-sm border-white/[0.08]">
          <CardHeader>
            <CardTitle>Последняя активность</CardTitle>
            <CardDescription>Недавние события в системе парсинга</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  action: "Запуск парсинга завершен",
                  target: "example.com",
                  time: "2 минуты назад",
                  status: "success",
                },
                {
                  action: "Новый домен добавлен",
                  target: "newdomain.ru",
                  time: "15 минут назад",
                  status: "info",
                },
                {
                  action: "Ошибка парсинга",
                  target: "failed-site.com",
                  time: "32 минуты назад",
                  status: "error",
                },
                {
                  action: "Обновлены ключевые слова",
                  target: "База ключей",
                  time: "1 час назад",
                  status: "info",
                },
              ].map((activity, i) => (
                <div key={i} className="flex items-center gap-4 py-2 border-b border-white/[0.05] last:border-0">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      activity.status === "success"
                        ? "bg-green-500"
                        : activity.status === "error"
                          ? "bg-red-500"
                          : "bg-blue-500"
                    }`}
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.target}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
