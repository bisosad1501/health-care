import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Calendar, Clock, ExternalLink, Pill, RefreshCw, User, AlertCircle } from "lucide-react"
import { useEffect, useState } from "react"
import PharmacyService, { PrescriptionWithDetails, PrescriptionItem } from "@/lib/api/pharmacy-service"
import MedicalRecordService from "@/lib/api/medical-record-service"
import { format } from "date-fns"
import { vi } from "date-fns/locale"
import { toast } from "sonner"
import { Skeleton } from "@/components/ui/skeleton"

// Định nghĩa interface cho dữ liệu hiển thị
interface MedicationDisplay {
  id: number
  name: string
  dosage: string
  frequency: string
  instructions: string
  prescribed: string
  doctor: string
  refills: number
  status: string
  expirationDate: string
  prescriptionId: number
  medicationDetails: any
}

export default function PatientPrescriptions() {
  const [medications, setMedications] = useState<MedicationDisplay[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingRefill, setLoadingRefill] = useState<number | null>(null)

  useEffect(() => {
    fetchPrescriptions()
  }, [])

  const fetchPrescriptions = async () => {
    try {
      setLoading(true)
      const prescriptions = await PharmacyService.getPatientPrescriptions()
      console.log("Fetched prescriptions:", prescriptions)

      // Chuyển đổi dữ liệu từ API sang định dạng hiển thị
      const medicationsData: MedicationDisplay[] = []

      for (const prescription of prescriptions) {
        // Lấy thông tin bác sĩ
        let doctorName = "Bác sĩ"
        try {
          const doctorInfo = await MedicalRecordService.getDoctorInfo(prescription.doctor_id)
          if (doctorInfo) {
            doctorName = `${doctorInfo.first_name} ${doctorInfo.last_name}`
          }
        } catch (error) {
          console.error(`Error fetching doctor info for doctor ${prescription.doctor_id}:`, error)
        }

        // Xử lý các item trong đơn thuốc
        if (prescription.items && prescription.items.length > 0) {
          for (const item of prescription.items) {
            const medication: MedicationDisplay = {
              id: item.id,
              name: item.medication_details?.name || "Thuốc không xác định",
              dosage: item.dosage || "",
              frequency: item.frequency || "",
              instructions: item.instructions || "",
              prescribed: formatDate(prescription.date_prescribed),
              doctor: doctorName,
              refills: 2, // Giả định số lần cấp lại
              status: getStatusDisplay(prescription.status),
              expirationDate: calculateExpirationDate(prescription.date_prescribed),
              prescriptionId: prescription.id,
              medicationDetails: item.medication_details
            }
            medicationsData.push(medication)
          }
        }
      }

      setMedications(medicationsData)
    } catch (error) {
      console.error("Error fetching prescriptions:", error)
      toast.error("Không thể tải thông tin đơn thuốc. Vui lòng thử lại sau.")
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return ""
    try {
      return format(new Date(dateString), "dd/MM/yyyy", { locale: vi })
    } catch (error) {
      console.error("Error formatting date:", error)
      return dateString
    }
  }

  const calculateExpirationDate = (dateString: string) => {
    if (!dateString) return ""
    try {
      const date = new Date(dateString)
      date.setMonth(date.getMonth() + 6) // Giả định đơn thuốc hết hạn sau 6 tháng
      return format(date, "dd/MM/yyyy", { locale: vi })
    } catch (error) {
      console.error("Error calculating expiration date:", error)
      return ""
    }
  }

  const getStatusDisplay = (status: string) => {
    switch (status?.toUpperCase()) {
      case "PENDING":
        return "Chờ xử lý"
      case "PROCESSING":
        return "Đang xử lý"
      case "DISPENSED":
        return "Đã cấp phát"
      case "CANCELLED":
        return "Đã hủy"
      case "EXPIRED":
        return "Hết hạn"
      default:
        return "Đang hoạt động"
    }
  }

  const handleRequestRefill = async (prescriptionId: number) => {
    try {
      setLoadingRefill(prescriptionId)
      await PharmacyService.requestRefill(prescriptionId)
      toast.success("Yêu cầu cấp lại thuốc đã được gửi thành công!")
      // Cập nhật lại danh sách đơn thuốc
      await fetchPrescriptions()
    } catch (error) {
      console.error("Error requesting refill:", error)
      toast.error("Không thể gửi yêu cầu cấp lại thuốc. Vui lòng thử lại sau.")
    } finally {
      setLoadingRefill(null)
    }
  }

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="w-full">
                  <Skeleton className="h-6 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
              <div className="mt-4 flex gap-2">
                <Skeleton className="h-8 w-full" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (medications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">Không có đơn thuốc</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Bạn chưa có đơn thuốc nào. Đơn thuốc sẽ xuất hiện ở đây sau khi bác sĩ kê đơn cho bạn.
        </p>
      </div>
    )
  }

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
                    className={
                      medication.status === "Đang hoạt động" || medication.status === "Đã cấp phát"
                        ? "bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
                        : "bg-gray-50 text-gray-700 hover:bg-gray-50 hover:text-gray-700"
                    }
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
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{medication.doctor}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{medication.prescribed}</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Hết hạn: {medication.expirationDate}</span>
                <span className="font-medium">Cấp lại: {medication.refills}</span>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              {(medication.status === "Đang hoạt động" || medication.status === "Đã cấp phát") && medication.refills > 0 && (
                <Button
                  className="w-full gap-1"
                  variant="outline"
                  size="sm"
                  onClick={() => handleRequestRefill(medication.prescriptionId)}
                  disabled={loadingRefill === medication.prescriptionId}
                >
                  {loadingRefill === medication.prescriptionId ? (
                    <span className="animate-spin">⏳</span>
                  ) : (
                    <RefreshCw className="h-3.5 w-3.5" />
                  )}
                  Yêu cầu cấp lại
                </Button>
              )}
              <Button className="w-full gap-1" variant="default" size="sm">
                <ExternalLink className="h-3.5 w-3.5" />
                Chi tiết
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
