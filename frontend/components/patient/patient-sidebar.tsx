import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Activity, Calendar, FileText, Home, LogOut, Pill, Settings, User } from "lucide-react"

export default function PatientSidebar() {
  return (
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
  )
}
