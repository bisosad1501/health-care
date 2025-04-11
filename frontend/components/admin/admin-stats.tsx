import { Card, CardContent } from "@/components/ui/card"
import { AlertTriangle, CheckCircle, Clock, Users } from "lucide-react"

export default function AdminStats() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Total Users</span>
            <Users className="h-5 w-5 text-teal-600" />
          </div>
          <div className="mt-2 flex items-baseline">
            <h3 className="text-2xl font-bold">1,248</h3>
            <span className="ml-2 text-xs font-medium text-green-600">+24 this week</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            <span className="font-medium">Active:</span> 1,156 (92.6%)
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">System Status</span>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <div className="mt-2 flex items-baseline">
            <h3 className="text-2xl font-bold">99.9%</h3>
            <span className="ml-2 text-xs font-medium text-green-600">Uptime</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            <span className="font-medium">Last incident:</span> 15 days ago
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">Pending Approvals</span>
            <Clock className="h-5 w-5 text-amber-600" />
          </div>
          <div className="mt-2 flex items-baseline">
            <h3 className="text-2xl font-bold">18</h3>
            <span className="ml-2 text-xs font-medium text-amber-600">Require attention</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            <span className="font-medium">Oldest:</span> 2 days ago
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">System Alerts</span>
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <div className="mt-2 flex items-baseline">
            <h3 className="text-2xl font-bold">3</h3>
            <span className="ml-2 text-xs font-medium text-red-600">Active alerts</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            <span className="font-medium">Critical:</span> 1 alert
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
