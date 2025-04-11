import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Activity,
  Bell,
  Clipboard,
  FileText,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Settings,
  User,
  Users,
} from "lucide-react"
import NursePatientsList from "@/components/nurse/nurse-patients-list"
import NurseTasks from "@/components/nurse/nurse-tasks"

export default function NurseDashboard() {
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
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Nurse" />
              <AvatarFallback>NR</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Nurse" />
                <AvatarFallback>NR</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Emma Wilson</p>
                <p className="text-xs text-muted-foreground">Nurse</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/nurse">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/nurse/patients">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Users className="h-4 w-4" />
                  Patients
                </Button>
              </Link>
              <Link href="/dashboard/nurse/tasks">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Clipboard className="h-4 w-4" />
                  Tasks
                </Button>
              </Link>
              <Link href="/dashboard/nurse/records">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Medical Records
                </Button>
              </Link>
              <Link href="/dashboard/nurse/vitals">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Activity className="h-4 w-4" />
                  Vital Signs
                </Button>
              </Link>
              <Link href="/dashboard/nurse/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/nurse/settings">
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
            <h2 className="mb-6 text-3xl font-bold">Nurse Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Assigned Patients</span>
                    <Users className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">12</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">Current shift</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Tasks</span>
                    <Clipboard className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">8</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">3 urgent</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Vital Signs Due</span>
                    <Activity className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">5</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">Next: 30 min</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Messages</span>
                    <MessageSquare className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">7</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">2 unread</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="patients">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="patients">Assigned Patients</TabsTrigger>
                  <TabsTrigger value="tasks">Tasks</TabsTrigger>
                </TabsList>
                <TabsContent value="patients" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Assigned Patients</CardTitle>
                      <CardDescription>Patients under your care for the current shift</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <NursePatientsList />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="tasks" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Tasks</CardTitle>
                      <CardDescription>Your pending tasks and assignments</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <NurseTasks />
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
