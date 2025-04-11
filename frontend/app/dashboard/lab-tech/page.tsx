import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Activity,
  Bell,
  Beaker,
  FileText,
  FlaskRoundIcon as Flask,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Settings,
  User,
  Microscope,
} from "lucide-react"
import LabTechPendingTests from "@/components/lab-tech/lab-tech-pending-tests"
import LabTechCompletedTests from "@/components/lab-tech/lab-tech-completed-tests"

export default function LabTechDashboard() {
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
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Lab Tech" />
              <AvatarFallback>LT</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Lab Tech" />
                <AvatarFallback>LT</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Alex Thompson</p>
                <p className="text-xs text-muted-foreground">Laboratory Technician</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/lab-tech">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/tests">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Flask className="h-4 w-4" />
                  Test Requests
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/results">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Test Results
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/equipment">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Microscope className="h-4 w-4" />
                  Equipment
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/samples">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Beaker className="h-4 w-4" />
                  Sample Management
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/lab-tech/settings">
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
            <h2 className="mb-6 text-3xl font-bold">Laboratory Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Pending Tests</span>
                    <Flask className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">18</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">5 urgent</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Completed Today</span>
                    <Activity className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">12</h3>
                    <span className="ml-2 text-xs font-medium text-green-600">+3 from yesterday</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Sample Collection</span>
                    <Beaker className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">7</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">Awaiting collection</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Equipment Status</span>
                    <Microscope className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">95%</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">1 needs maintenance</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="pending">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="pending">Pending Tests</TabsTrigger>
                  <TabsTrigger value="completed">Recently Completed</TabsTrigger>
                </TabsList>
                <TabsContent value="pending" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Pending Test Requests</CardTitle>
                      <CardDescription>Tests awaiting processing or results</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <LabTechPendingTests />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="completed" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recently Completed Tests</CardTitle>
                      <CardDescription>Tests completed in the last 7 days</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <LabTechCompletedTests />
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
