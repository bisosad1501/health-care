import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Clock, FileText, MoreHorizontal } from "lucide-react"

export default function DoctorAppointments() {
  const appointments = [
    {
      id: 1,
      patient: "Emma Wilson",
      age: 42,
      reason: "Follow-up: Hypertension",
      time: "10:30 AM",
      duration: "30 min",
      status: "Upcoming",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 2,
      patient: "James Rodriguez",
      age: 65,
      reason: "Chest Pain Evaluation",
      time: "11:15 AM",
      duration: "45 min",
      status: "Upcoming",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 3,
      patient: "Sophia Chen",
      age: 38,
      reason: "Annual Physical",
      time: "1:00 PM",
      duration: "60 min",
      status: "Upcoming",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 4,
      patient: "Michael Brown",
      age: 55,
      reason: "Post-Surgery Follow-up",
      time: "2:15 PM",
      duration: "30 min",
      status: "Upcoming",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 5,
      patient: "Olivia Martinez",
      age: 29,
      reason: "Medication Review",
      time: "3:30 PM",
      duration: "30 min",
      status: "Upcoming",
      avatar: "/placeholder.svg?height=40&width=40",
    },
  ]

  return (
    <div className="space-y-4">
      {appointments.map((appointment) => (
        <div
          key={appointment.id}
          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
        >
          <div className="flex items-start gap-4">
            <Avatar>
              <AvatarImage src={appointment.avatar} alt={appointment.patient} />
              <AvatarFallback>
                {appointment.patient
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{appointment.patient}</h4>
                <span className="text-sm text-muted-foreground">{appointment.age} yrs</span>
              </div>
              <p className="text-sm">{appointment.reason}</p>
              <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                <span>
                  {appointment.time} ({appointment.duration})
                </span>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2 md:mt-0">
            <Button variant="outline" size="sm" className="gap-1">
              <FileText className="h-3.5 w-3.5" />
              Records
            </Button>
            <Button variant="default" size="sm">
              Start
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
