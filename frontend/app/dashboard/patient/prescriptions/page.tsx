import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Filter, HeartPulse, Search } from "lucide-react"
import PatientPrescriptions from "@/components/patient/patient-prescriptions"
import PatientSidebar from "@/components/patient/patient-sidebar"

export default function PatientPrescriptionsPage() {
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
                <h2 className="text-3xl font-bold">Prescriptions</h2>
                <p className="text-muted-foreground">View and manage your medications</p>
              </div>
            </div>

            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative max-w-sm">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input type="search" placeholder="Search medications..." className="pl-8 w-full sm:w-[300px]" />
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="gap-1">
                  <Filter className="h-3.5 w-3.5" />
                  Filter
                </Button>
              </div>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Current Medications</CardTitle>
                <CardDescription>Your active prescriptions and medication schedule</CardDescription>
              </CardHeader>
              <CardContent>
                <PatientPrescriptions />
              </CardContent>
            </Card>
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
