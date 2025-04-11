import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent } from "@/components/ui/card"
import { Clock } from "lucide-react"

export default function PatientAppointmentCalendar() {
  // Sample appointments data
  const appointments = [
    {
      id: 1,
      doctor: "Dr. Sarah Johnson",
      specialty: "Cardiology",
      date: new Date(2025, 4, 10), // May 10, 2025
      time: "10:00 AM",
      duration: "30 min",
    },
    {
      id: 2,
      doctor: "Dr. Michael Chen",
      specialty: "General Practice",
      date: new Date(2025, 4, 15), // May 15, 2025
      time: "2:30 PM",
      duration: "45 min",
    },
    {
      id: 3,
      doctor: "Dr. Emily Rodriguez",
      specialty: "Dermatology",
      date: new Date(2025, 4, 22), // May 22, 2025
      time: "11:15 AM",
      duration: "30 min",
    },
  ]

  // Function to check if a date has appointments
  const hasAppointment = (date: Date) => {
    return appointments.some(
      (appointment) =>
        appointment.date.getDate() === date.getDate() &&
        appointment.date.getMonth() === date.getMonth() &&
        appointment.date.getFullYear() === date.getFullYear(),
    )
  }

  // Function to get appointments for a specific date
  const getAppointmentsForDate = (date: Date) => {
    return appointments.filter(
      (appointment) =>
        appointment.date.getDate() === date.getDate() &&
        appointment.date.getMonth() === date.getMonth() &&
        appointment.date.getFullYear() === date.getFullYear(),
    )
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      <div className="lg:w-1/2">
        <Calendar
          mode="single"
          selected={new Date(2025, 4, 10)} // May 10, 2025
          className="rounded-md border"
          modifiers={{
            appointment: (date) => hasAppointment(date),
          }}
          modifiersClassNames={{
            appointment: "bg-teal-100 font-bold text-teal-900",
          }}
        />
      </div>
      <div className="lg:w-1/2">
        <h3 className="mb-4 text-lg font-medium">Appointments on May 10, 2025</h3>
        <div className="space-y-3">
          {getAppointmentsForDate(new Date(2025, 4, 10)).map((appointment) => (
            <Card key={appointment.id}>
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{appointment.doctor}</h4>
                    <p className="text-sm text-muted-foreground">{appointment.specialty}</p>
                    <div className="mt-2 flex items-center gap-1 text-sm">
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                      <span>
                        {appointment.time} ({appointment.duration})
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
