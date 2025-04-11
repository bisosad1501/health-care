import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Calendar, FileText, MessageSquare, MoreHorizontal } from "lucide-react"

export default function DoctorPatients() {
  const patients = [
    {
      id: 1,
      name: "Robert Davis",
      age: 62,
      lastVisit: "Yesterday",
      diagnosis: "Coronary Artery Disease",
      nextAppointment: "May 15, 2025",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 2,
      name: "Jennifer Lee",
      age: 45,
      lastVisit: "2 days ago",
      diagnosis: "Hypertension, Type 2 Diabetes",
      nextAppointment: "June 3, 2025",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 3,
      name: "William Taylor",
      age: 58,
      lastVisit: "3 days ago",
      diagnosis: "Heart Failure (NYHA Class II)",
      nextAppointment: "May 20, 2025",
      avatar: "/placeholder.svg?height=40&width=40",
    },
  ]

  return (
    <div className="space-y-4">
      {patients.map((patient) => (
        <div
          key={patient.id}
          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
        >
          <div className="flex items-start gap-4">
            <Avatar>
              <AvatarImage src={patient.avatar} alt={patient.name} />
              <AvatarFallback>
                {patient.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{patient.name}</h4>
                <span className="text-sm text-muted-foreground">{patient.age} yrs</span>
              </div>
              <p className="text-sm">{patient.diagnosis}</p>
              <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                <span>Last visit: {patient.lastVisit}</span>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>Next: {patient.nextAppointment}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2 md:mt-0">
            <Button variant="outline" size="sm" className="gap-1">
              <FileText className="h-3.5 w-3.5" />
              Records
            </Button>
            <Button variant="outline" size="sm" className="gap-1">
              <MessageSquare className="h-3.5 w-3.5" />
              Message
            </Button>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
