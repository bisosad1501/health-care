import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Activity,
  Calendar,
  FileText,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Pill,
  Settings,
  User,
} from "lucide-react"
import PatientAppointments from "@/components/patient/patient-appointments"
import PatientMedications from "@/components/patient/patient-medications"
import PatientTestResults from "@/components/patient/patient-test-results"

export default function PatientDashboard() {
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
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Patient" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Patient" />
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">John Doe</p>
                <p className="text-xs text-muted-foreground">Patient</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/patient">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/patient/appointments">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Calendar className="h-4 w-4" />
                  Appointments
                </Button>
              </Link>
              <Link href="/dashboard/patient/records">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Medical Records
                </Button>
              </Link>
              <Link href="/dashboard/patient/prescriptions">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Pill className="h-4 w-4" />
                  Prescriptions
                </Button>
              </Link>
              <Link href="/dashboard/patient/tests">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Activity className="h-4 w-4" />
                  Test Results
                </Button>
              </Link>
              <Link href="/dashboard/patient/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/patient/settings">
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
            <h2 className="mb-6 text-3xl font-bold">Patient Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Upcoming Appointments</span>
                    <Calendar className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">2</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">Next: Tomorrow, 10:00 AM</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Active Prescriptions</span>
                    <Pill className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">3</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">Refill in 5 days</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Recent Test Results</span>
                    <Activity className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">1</h3>
                    <span className="ml-2 text-xs font-medium text-green-600">New result available</span>
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
                    <h3 className="text-2xl font-bold">5</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">2 unread</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="appointments">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="appointments">Upcoming Appointments</TabsTrigger>
                  <TabsTrigger value="medications">Current Medications</TabsTrigger>
                  <TabsTrigger value="results">Recent Test Results</TabsTrigger>
                </TabsList>
                <TabsContent value="appointments" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Upcoming Appointments</CardTitle>
                      <CardDescription>Your scheduled appointments for the next 30 days</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PatientAppointments />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="medications" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Current Medications</CardTitle>
                      <CardDescription>Your active prescriptions and medication schedule</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PatientMedications />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="results" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Test Results</CardTitle>
                      <CardDescription>Your latest laboratory and diagnostic test results</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PatientTestResults />
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

function Bell(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </svg>
  )
}
