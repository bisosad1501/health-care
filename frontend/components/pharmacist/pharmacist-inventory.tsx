import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { AlertTriangle, Calendar, Plus, ShoppingCart } from "lucide-react"

export default function PharmacistInventory() {
  const inventory = [
    {
      id: 1,
      name: "Lisinopril 10mg",
      category: "Antihypertensive",
      currentStock: 120,
      minStock: 50,
      maxStock: 200,
      expirationDate: "Dec 15, 2025",
      status: "Normal",
      stockPercentage: 60,
    },
    {
      id: 2,
      name: "Metformin 500mg",
      category: "Antidiabetic",
      currentStock: 35,
      minStock: 40,
      maxStock: 150,
      expirationDate: "Nov 30, 2025",
      status: "Low",
      stockPercentage: 23,
    },
    {
      id: 3,
      name: "Atorvastatin 20mg",
      category: "Statin",
      currentStock: 85,
      minStock: 30,
      maxStock: 120,
      expirationDate: "Jun 10, 2025",
      status: "Expiring Soon",
      stockPercentage: 71,
    },
    {
      id: 4,
      name: "Amoxicillin 500mg",
      category: "Antibiotic",
      currentStock: 15,
      minStock: 30,
      maxStock: 100,
      expirationDate: "Sep 20, 2025",
      status: "Critical",
      stockPercentage: 15,
    },
    {
      id: 5,
      name: "Ibuprofen 200mg",
      category: "NSAID",
      currentStock: 200,
      minStock: 50,
      maxStock: 200,
      expirationDate: "Oct 05, 2025",
      status: "Overstocked",
      stockPercentage: 100,
    },
  ]

  return (
    <div className="space-y-4">
      {inventory.map((item) => (
        <div key={item.id} className="rounded-lg border p-4">
          <div className="flex flex-col justify-between gap-2 sm:flex-row">
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{item.name}</h4>
                <Badge
                  variant={
                    item.status === "Critical" || item.status === "Low"
                      ? "destructive"
                      : item.status === "Expiring Soon"
                        ? "outline"
                        : item.status === "Overstocked"
                          ? "secondary"
                          : "default"
                  }
                  className={
                    item.status === "Expiring Soon"
                      ? "bg-amber-50 text-amber-700 hover:bg-amber-50 hover:text-amber-700"
                      : ""
                  }
                >
                  {item.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{item.category}</p>
            </div>
            <div className="flex items-center gap-2">
              {(item.status === "Critical" || item.status === "Low") && (
                <Button variant="outline" size="sm" className="gap-1">
                  <ShoppingCart className="h-3.5 w-3.5" />
                  Order
                </Button>
              )}
              <Button variant="outline" size="sm" className="gap-1">
                <Plus className="h-3.5 w-3.5" />
                Add Stock
              </Button>
            </div>
          </div>
          <div className="mt-4">
            <div className="mb-1 flex items-center justify-between text-sm">
              <span>
                Stock: {item.currentStock} / {item.maxStock}
              </span>
              <span className="text-muted-foreground">Min: {item.minStock}</span>
            </div>
            <Progress
              value={item.stockPercentage}
              className={
                item.status === "Critical" || item.status === "Low"
                  ? "bg-red-100"
                  : item.status === "Expiring Soon"
                    ? "bg-amber-100"
                    : "bg-gray-100"
              }
            />
          </div>
          <div className="mt-2 flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              <span>Expires: {item.expirationDate}</span>
            </div>
            {item.status === "Expiring Soon" && (
              <div className="flex items-center gap-1 text-amber-600">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>Check expiration</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
