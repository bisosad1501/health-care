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
  Settings,
  Stethoscope,
  User,
  Users,
} from "lucide-react"
import DoctorAppointments from "@/components/doctor/doctor-appointments"
import DoctorPatients from "@/components/doctor/doctor-patients"

export default function DoctorDashboard() {
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
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Doctor" />
              <AvatarFallback>DR</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Doctor" />
                <AvatarFallback>DR</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Dr. Sarah Johnson</p>
                <p className="text-xs text-muted-foreground">Cardiologist</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/doctor">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/doctor/appointments">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Calendar className="h-4 w-4" />
                  Appointments
                </Button>
              </Link>
              <Link href="/dashboard/doctor/patients">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Users className="h-4 w-4" />
                  Patients
                </Button>
              </Link>
              <Link href="/dashboard/doctor/records">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Medical Records
                </Button>
              </Link>
              <Link href="/dashboard/doctor/prescriptions">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Stethoscope className="h-4 w-4" />
                  Prescriptions
                </Button>
              </Link>
              <Link href="/dashboard/doctor/tests">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Activity className="h-4 w-4" />
                  Lab Orders
                </Button>
              </Link>
              <Link href="/dashboard/doctor/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/doctor/settings">
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
            <h2 className="mb-6 text-3xl font-bold">Doctor Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Today's Appointments</span>
                    <Calendar className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">8</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">Next: 10:30 AM</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Patients Seen Today</span>
                    <Users className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">3</h3>
                    <span className="ml-2 text-xs font-medium text-green-600">+1 from yesterday</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Pending Lab Results</span>
                    <Activity className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">5</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">2 urgent</span>
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
                    <h3 className="text-2xl font-bold">12</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">4 unread</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="appointments">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="appointments">Today's Schedule</TabsTrigger>
                  <TabsTrigger value="patients">Recent Patients</TabsTrigger>
                </TabsList>
                <TabsContent value="appointments" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Today's Schedule</CardTitle>
                      <CardDescription>Your appointments for today, {new Date().toLocaleDateString()}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DoctorAppointments />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="patients" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Patients</CardTitle>
                      <CardDescription>Patients you've seen in the last 7 days</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DoctorPatients />
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
