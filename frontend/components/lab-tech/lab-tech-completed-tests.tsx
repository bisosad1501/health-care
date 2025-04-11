import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Download, FileText, MoreHorizontal, User } from "lucide-react"

export default function LabTechCompletedTests() {
  const completedTests = [
    {
      id: 1,
      patient: "Robert Davis",
      patientId: "P-1008",
      testType: "Complete Blood Count (CBC)",
      doctor: "Dr. Sarah Johnson",
      completedDate: "Today",
      completedTime: "11:30 AM",
      status: "Completed",
      result: "Normal",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 2,
      patient: "Jennifer Lee",
      patientId: "P-1012",
      testType: "Thyroid Function Test",
      doctor: "Dr. Michael Chen",
      completedDate: "Today",
      completedTime: "09:45 AM",
      status: "Completed",
      result: "Abnormal",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 3,
      patient: "Michael Brown",
      patientId: "P-1002",
      testType: "Lipid Panel",
      doctor: "Dr. Sarah Johnson",
      completedDate: "Yesterday",
      completedTime: "03:15 PM",
      status: "Completed",
      result: "Normal",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: 4,
      patient: "Olivia Martinez",
      patientId: "P-1005",
      testType: "Urinalysis",
      doctor: "Dr. Michael Chen",
      completedDate: "Yesterday",
      completedTime: "01:30 PM",
      status: "Completed",
      result: "Normal",
      avatar: "/placeholder.svg?height=40&width=40",
    },
  ]

  return (
    <div className="space-y-4">
      {completedTests.map((test) => (
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
                  <span>
                    {test.completedDate}, {test.completedTime}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between md:mt-0 md:flex-col md:items-end">
            <Badge
              variant={test.result === "Normal" ? "outline" : "secondary"}
              className={
                test.result === "Normal"
                  ? "bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
                  : "bg-amber-50 text-amber-700 hover:bg-amber-50 hover:text-amber-700"
              }
            >
              {test.result}
            </Badge>
            <div className="flex items-center gap-2 mt-2">
              <Button variant="outline" size="sm" className="gap-1">
                <Download className="h-3.5 w-3.5" />
                Export
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
