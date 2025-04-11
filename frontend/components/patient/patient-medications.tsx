import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Clock, Pill, RefreshCw } from "lucide-react"

export default function PatientMedications() {
  const medications = [
    {
      id: 1,
      name: "Lisinopril",
      dosage: "10mg",
      frequency: "Once daily",
      instructions: "Take in the morning with food",
      prescribed: "Apr 1, 2025",
      refills: 2,
      status: "Active",
    },
    {
      id: 2,
      name: "Atorvastatin",
      dosage: "20mg",
      frequency: "Once daily",
      instructions: "Take in the evening",
      prescribed: "Apr 1, 2025",
      refills: 5,
      status: "Active",
    },
    {
      id: 3,
      name: "Metformin",
      dosage: "500mg",
      frequency: "Twice daily",
      instructions: "Take with meals",
      prescribed: "Mar 15, 2025",
      refills: 1,
      status: "Active",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {medications.map((medication) => (
        <Card key={medication.id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">{medication.name}</h4>
                  <Badge
                    variant="outline"
                    className="bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
                  >
                    {medication.status}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{medication.dosage}</p>
              </div>
              <Pill className="h-5 w-5 text-teal-600" />
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span>{medication.frequency}</span>
              </div>
              <p className="text-sm">{medication.instructions}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Prescribed: {medication.prescribed}</span>
                <span className="font-medium">Refills: {medication.refills}</span>
              </div>
            </div>
            <Button className="mt-4 w-full gap-2" variant="outline" size="sm">
              <RefreshCw className="h-3.5 w-3.5" />
              Request Refill
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
