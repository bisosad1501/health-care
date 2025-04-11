import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Calendar, ChevronLeft, ChevronRight, Filter, HeartPulse, Plus, Search } from "lucide-react"
import PatientAppointmentsList from "@/components/patient/patient-appointments-list"
import PatientAppointmentCalendar from "@/components/patient/patient-appointment-calendar"
import PatientSidebar from "@/components/patient/patient-sidebar"

export default function PatientAppointmentsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="h-6 w-6 text-teal-600" />
            <h1 className="text-xl font-bold">Healthcare System</h1>
          </div>
          <div className="flex items-center gap-4">
            <Avatar>
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Patient" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <PatientSidebar />
        <main className="flex-1">
          <div className="container py-6">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold">Appointments</h2>
                <p className="text-muted-foreground">Manage your upcoming and past appointments</p>
              </div>
              <Button className="gap-1">
                <Plus className="h-4 w-4" />
                Book Appointment
              </Button>
            </div>

            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative max-w-sm">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input type="search" placeholder="Search appointments..." className="pl-8 w-full sm:w-[300px]" />
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="gap-1">
                  <Filter className="h-3.5 w-3.5" />
                  Filter
                </Button>
                <div className="flex items-center rounded-md border bg-background">
                  <Button variant="ghost" size="icon" className="h-8 w-8 rounded-none rounded-l-md">
                    <ChevronLeft className="h-4 w-4" />
                    <span className="sr-only">Previous month</span>
                  </Button>
                  <div className="px-3 py-1 text-sm font-medium">May 2025</div>
                  <Button variant="ghost" size="icon" className="h-8 w-8 rounded-none rounded-r-md">
                    <ChevronRight className="h-4 w-4" />
                    <span className="sr-only">Next month</span>
                  </Button>
                </div>
              </div>
            </div>

            <Tabs defaultValue="list">
              <TabsList className="mb-4">
                <TabsTrigger value="list" className="gap-2">
                  <Calendar className="h-4 w-4" />
                  List View
                </TabsTrigger>
                <TabsTrigger value="calendar" className="gap-2">
                  <Calendar className="h-4 w-4" />
                  Calendar View
                </TabsTrigger>
              </TabsList>
              <TabsContent value="list">
                <Card>
                  <CardHeader>
                    <CardTitle>Upcoming Appointments</CardTitle>
                    <CardDescription>Your scheduled appointments for the next 30 days</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <PatientAppointmentsList />
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="calendar">
                <Card>
                  <CardHeader>
                    <CardTitle>Appointment Calendar</CardTitle>
                    <CardDescription>View your appointments in a calendar format</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <PatientAppointmentCalendar />
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
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
