import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, Download, ExternalLink } from "lucide-react"

export default function PatientTestResults() {
  const testResults = [
    {
      id: 1,
      name: "Complete Blood Count (CBC)",
      date: "Apr 5, 2025",
      doctor: "Dr. Sarah Johnson",
      status: "Completed",
      isNew: true,
    },
    {
      id: 2,
      name: "Lipid Panel",
      date: "Mar 20, 2025",
      doctor: "Dr. Michael Chen",
      status: "Completed",
      isNew: false,
    },
    {
      id: 3,
      name: "Chest X-Ray",
      date: "Feb 15, 2025",
      doctor: "Dr. Sarah Johnson",
      status: "Completed",
      isNew: false,
    },
  ]

  return (
    <div className="space-y-4">
      {testResults.map((result) => (
        <div key={result.id} className="flex items-start justify-between rounded-lg border p-4">
          <div className="flex items-start gap-3">
            <div className="rounded-md bg-primary/10 p-2">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{result.name}</h4>
                {result.isNew && <Badge className="bg-green-100 text-green-800 hover:bg-green-100">New</Badge>}
              </div>
              <div className="mt-1 text-sm text-muted-foreground">
                <p>Date: {result.date}</p>
                <p>Ordered by: {result.doctor}</p>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-1">
              <Download className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Download</span>
            </Button>
            <Button variant="default" size="sm" className="gap-1">
              <ExternalLink className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">View</span>
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
