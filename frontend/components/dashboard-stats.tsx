import { Card, CardContent } from "@/components/ui/card"
import type { ReactNode } from "react"

interface DashboardStatsProps {
  title: string
  value: string
  trend: string
  icon: ReactNode
}

export default function DashboardStats({ title, value, trend, icon }: DashboardStatsProps) {
  const isPositive = trend.startsWith("+")

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
          {icon}
        </div>
        <div className="mt-2 flex items-baseline">
          <h3 className="text-2xl font-bold">{value}</h3>
          <span className={`ml-2 text-xs font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>{trend}</span>
        </div>
      </CardContent>
    </Card>
  )
}
