"use client"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent } from "@/components/ui/card"
import { Clock } from "lucide-react"
import { useState } from "react"

export default function PatientAppointmentCalendar() {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date(2025, 4, 10))

  // Sample appointments data
  const appointments = [
    {
      id: 1,
      doctor: "Bác sĩ Nguyễn Thị Hương",
      specialty: "Tim mạch",
      date: new Date(2025, 4, 10), // May 10, 2025
      time: "10:00",
      duration: "30 phút",
    },
    {
      id: 2,
      doctor: "Bác sĩ Trần Văn Minh",
      specialty: "Đa khoa",
      date: new Date(2025, 4, 15), // May 15, 2025
      time: "14:30",
      duration: "45 phút",
    },
    {
      id: 3,
      doctor: "Bác sĩ Lê Thị Hoa",
      specialty: "Da liễu",
      date: new Date(2025, 4, 22), // May 22, 2025
      time: "11:15",
      duration: "30 phút",
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
  const getAppointmentsForDate = (date: Date | undefined) => {
    if (!date) return []

    return appointments.filter(
      (appointment) =>
        appointment.date.getDate() === date.getDate() &&
        appointment.date.getMonth() === date.getMonth() &&
        appointment.date.getFullYear() === date.getFullYear(),
    )
  }

  // Format date for display
  const formatDate = (date: Date | undefined) => {
    if (!date) return ""

    return new Intl.DateTimeFormat("vi-VN", {
      day: "numeric",
      month: "numeric",
      year: "numeric",
    }).format(date)
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      <div className="lg:w-1/2">
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={setSelectedDate}
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
        <h3 className="mb-4 text-lg font-medium">Lịch hẹn ngày {formatDate(selectedDate)}</h3>
        <div className="space-y-3">
          {getAppointmentsForDate(selectedDate).map((appointment) => (
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
                    Chi tiết
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
          {getAppointmentsForDate(selectedDate).length === 0 && (
            <p className="text-muted-foreground text-center py-4">Không có lịch hẹn vào ngày này</p>
          )}
        </div>
      </div>
    </div>
  )
}
