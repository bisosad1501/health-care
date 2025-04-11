import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Activity,
  Bell,
  FileText,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Settings,
  Shield,
  User,
  Users,
} from "lucide-react"
import AdminUsersList from "@/components/admin/admin-users-list"
import AdminStats from "@/components/admin/admin-stats"
import AdminActivityLog from "@/components/admin/admin-activity-log"

export default function AdminDashboard() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="h-6 w-6 text-teal-600" />
            <h1 className="text-xl font-bold">Healthcare System</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <MessageSquare className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Avatar>
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Admin" />
              <AvatarFallback>AD</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Admin" />
                <AvatarFallback>AD</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Admin User</p>
                <p className="text-xs text-muted-foreground">Administrator</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/admin">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/admin/users">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Users className="h-4 w-4" />
                  User Management
                </Button>
              </Link>
              <Link href="/dashboard/admin/roles">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Shield className="h-4 w-4" />
                  Roles & Permissions
                </Button>
              </Link>
              <Link href="/dashboard/admin/logs">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Activity className="h-4 w-4" />
                  System Logs
                </Button>
              </Link>
              <Link href="/dashboard/admin/reports">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Reports
                </Button>
              </Link>
              <Link href="/dashboard/admin/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/admin/settings">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Settings className="h-4 w-4" />
                  Settings
                </Button>
              </Link>
            </nav>
            <div className="mt-auto">
              <Link href="/login">
                <Button variant="ghost" className="w-full justify-start gap-2 text-red-500 hover:text-red-500">
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </Link>
            </div>
          </div>
        </aside>
        <main className="flex-1">
          <div className="container py-6">
            <h2 className="mb-6 text-3xl font-bold">Admin Dashboard</h2>

            <AdminStats />

            <div className="mt-6">
              <Tabs defaultValue="users">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="users">User Management</TabsTrigger>
                  <TabsTrigger value="activity">Activity Log</TabsTrigger>
                </TabsList>
                <TabsContent value="users" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>User Management</CardTitle>
                      <CardDescription>Manage users and their roles in the system</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <AdminUsersList />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="activity" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Activity Log</CardTitle>
                      <CardDescription>Recent system activities and events</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <AdminActivityLog />
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
      </div>
      <footer className="border-t bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <p className="text-sm text-muted-foreground">© 2025 Healthcare System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
