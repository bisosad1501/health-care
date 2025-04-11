import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Clock, FileText, MoreHorizontal, User } from "lucide-react"

export default function LabTechPendingTests() {
  const pendingTests = [
    {
      id: 1,
      patient: "Emma Wilson",
      patientId: "P-1001",
      testType: "Complete Blood Count (CBC)",
      doctor: "Dr. Sarah Johnson",
      requestDate: "Today",
      requestTime: "09:15 AM",
      status: "Urgent",
      dueDate: "Today, 2:00 PM",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 2,
      patient: "James Rodriguez",
      patientId: "P-1008",
      testType: "Lipid Panel",
      doctor: "Dr. Michael Chen",
      requestDate: "Today",
      requestTime: "10:30 AM",
      status: "Routine",
      dueDate: "Tomorrow, 10:00 AM",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 3,
      patient: "Sophia Chen",
      patientId: "P-1003",
      testType: "Urinalysis",
      doctor: "Dr. Sarah Johnson",
      requestDate: "Today",
      requestTime: "11:45 AM",
      status: "Urgent",
      dueDate: "Today, 4:00 PM",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 4,
      patient: "William Taylor",
      patientId: "P-1006",
      testType: "Liver Function Test",
      doctor: "Dr. Michael Chen",
      requestDate: "Yesterday",
      requestTime: "03:30 PM",
      status: "Routine",
      dueDate: "Tomorrow, 12:00 PM",
      avatar: "/placeholder.svg?height=40&width=40",
    },
  ]

  return (
    <div className="space-y-4">
      {pendingTests.map((test) => (
        <div
          key={test.id}
          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
        >
          <div className="flex items-start gap-4">
            <Avatar>
              <AvatarImage src={test.avatar} alt={test.patient} />
              <AvatarFallback>
                {test.patient
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{test.patient}</h4>
                <span className="text-xs text-muted-foreground">{test.patientId}</span>
              </div>
              <p className="text-sm font-medium">{test.testType}</p>
              <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5" />
                  <span>{test.doctor}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>{test.requestDate}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{test.requestTime}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between md:mt-0 md:flex-col md:items-end">
            <Badge
              variant={test.status === "Urgent" ? "destructive" : "outline"}
              className={
                test.status === "Urgent" ? "" : "bg-blue-50 text-blue-700 hover:bg-blue-50 hover:text-blue-700"
              }
            >
              {test.status}
            </Badge>
            <div className="mt-1 text-xs text-muted-foreground">Due: {test.dueDate}</div>
            <div className="flex items-center gap-2 mt-2">
              <Button variant="default" size="sm">
                Process
              </Button>
              <Button variant="outline" size="sm" className="gap-1">
                <FileText className="h-3.5 w-3.5" />
                Details
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
