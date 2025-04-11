import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Clock, MapPin, MoreHorizontal, Video } from "lucide-react"

export default function PatientAppointmentsList() {
  const appointments = [
    {
      id: 1,
      doctor: "Dr. Sarah Johnson",
      specialty: "Cardiology",
      date: "Tomorrow",
      time: "10:00 AM",
      duration: "30 min",
      location: "Main Hospital, Room 305",
      type: "In-person",
      status: "Confirmed",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 2,
      doctor: "Dr. Michael Chen",
      specialty: "General Practice",
      date: "May 15, 2025",
      time: "2:30 PM",
      duration: "45 min",
      location: "Virtual Appointment",
      type: "Video",
      status: "Scheduled",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 3,
      doctor: "Dr. Emily Rodriguez",
      specialty: "Dermatology",
      date: "May 22, 2025",
      time: "11:15 AM",
      duration: "30 min",
      location: "North Clinic, Room 102",
      type: "In-person",
      status: "Scheduled",
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
            <Avatar className="hidden md:block">
              <AvatarImage src={appointment.avatar} alt={appointment.doctor} />
              <AvatarFallback>
                {appointment.doctor
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <h4 className="font-medium">{appointment.doctor}</h4>
              <p className="text-sm text-muted-foreground">{appointment.specialty}</p>
              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{appointment.date}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>
                    {appointment.time} ({appointment.duration})
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {appointment.type === "Video" ? (
                    <Video className="h-3.5 w-3.5 text-muted-foreground" />
                  ) : (
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  <span>{appointment.location}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between md:mt-0 md:flex-col md:items-end">
            <Badge
              variant={appointment.status === "Confirmed" ? "default" : "outline"}
              className={appointment.status === "Confirmed" ? "bg-green-100 text-green-800 hover:bg-green-100" : ""}
            >
              {appointment.status}
            </Badge>
            <div className="flex items-center gap-2 mt-2">
              <Button variant="outline" size="sm">
                Reschedule
              </Button>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
