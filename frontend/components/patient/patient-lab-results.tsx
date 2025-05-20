"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Download, ExternalLink, FileText, User, AlertCircle, Beaker, TestTube } from "lucide-react"
import MedicalRecordService from "@/lib/api/medical-record-service"
import { format, parseISO } from "date-fns"
import { vi } from "date-fns/locale"
import { Skeleton } from "@/components/ui/skeleton"

// Interface cho dữ liệu hiển thị
interface FormattedLabTest {
  id: number
  name: string
  date: string
  doctor: string
  lab: string
  status: string
  summary: string
  isNew: boolean
  labTestId: number
}

// Hàm chuyển đổi trạng thái
const getStatusName = (status: string): string => {
  const statusMap: Record<string, string> = {
    'ORDERED': 'Đã yêu cầu',
    'COLLECTED': 'Đã lấy mẫu',
    'IN_PROGRESS': 'Đang xử lý',
    'COMPLETED': 'Hoàn thành',
    'CANCELLED': 'Đã hủy',
    'PENDING': 'Chờ xử lý'
  }
  return statusMap[status] || status
}

export default function PatientLabResults() {
  const [labResults, setLabResults] = useState<FormattedLabTest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchLabTests = async () => {
      try {
        setLoading(true)

        // Lấy danh sách hồ sơ y tế
        const medicalRecordsResponse = await MedicalRecordService.getPatientMedicalRecords()
        console.log("Medical records response:", medicalRecordsResponse)

        if (!medicalRecordsResponse || !medicalRecordsResponse.results || medicalRecordsResponse.results.length === 0) {
          setLabResults([])
          setLoading(false)
          return
        }

        // Lấy chi tiết của hồ sơ y tế đầu tiên
        const recordDetails = await MedicalRecordService.getMedicalRecordById(medicalRecordsResponse.results[0].id)
        console.log("Medical record details:", recordDetails)

        if (!recordDetails || !recordDetails.encounters || recordDetails.encounters.length === 0) {
          setLabResults([])
          setLoading(false)
          return
        }

        // Tạo danh sách tất cả các xét nghiệm từ tất cả các lần khám
        const allLabTests: any[] = []
        recordDetails.encounters.forEach(encounter => {
          if (encounter.lab_tests && encounter.lab_tests.length > 0) {
            encounter.lab_tests.forEach((labTest: any) => {
              allLabTests.push({
                ...labTest,
                encounterId: encounter.id,
                doctorId: encounter.doctor_id
              })
            })
          }
        })

        if (allLabTests.length === 0) {
          setLabResults([])
          setLoading(false)
          return
        }

        // Xử lý dữ liệu để hiển thị
        const formattedLabTests = await Promise.all(allLabTests.map(async (labTest: any) => {
          // Lấy thông tin bác sĩ
          let doctorName = `Bác sĩ #${labTest.doctorId}`

          try {
            const doctorInfo = await MedicalRecordService.getDoctorInfo(labTest.doctorId)
            if (doctorInfo) {
              doctorName = `BS. ${doctorInfo.first_name} ${doctorInfo.last_name}`
            }
          } catch (error) {
            console.error("Error fetching doctor info:", error)
          }

          // Tạo tóm tắt từ kết quả xét nghiệm
          let summary = labTest.notes || "Không có ghi chú"
          if (labTest.results && labTest.results.length > 0) {
            const abnormalResults = labTest.results.filter((result: any) => result.is_abnormal)
            if (abnormalResults.length > 0) {
              summary = `Có ${abnormalResults.length} kết quả bất thường. ${labTest.notes || ''}`
            } else {
              summary = `Tất cả kết quả trong giới hạn bình thường. ${labTest.notes || ''}`
            }
          }

          // Định dạng ngày tháng
          const date = labTest.ordered_at
            ? format(parseISO(labTest.ordered_at), 'dd/MM/yyyy', { locale: vi })
            : "Không xác định"

          // Xác định xét nghiệm mới (trong vòng 7 ngày)
          const isNew = labTest.ordered_at
            ? (new Date().getTime() - new Date(labTest.ordered_at).getTime()) / (1000 * 60 * 60 * 24) < 7
            : false

          return {
            id: labTest.id,
            name: labTest.test_name || "Xét nghiệm",
            date: date,
            doctor: doctorName,
            lab: "Phòng xét nghiệm bệnh viện",
            status: getStatusName(labTest.status),
            summary: summary,
            isNew: isNew,
            labTestId: labTest.id
          }
        }))

        // Sắp xếp theo ngày mới nhất
        formattedLabTests.sort((a: any, b: any) => {
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        })

        setLabResults(formattedLabTests)
      } catch (error: any) {
        console.error("Error fetching lab tests:", error)
        setError("Không thể tải kết quả xét nghiệm. Vui lòng thử lại sau.")
      } finally {
        setLoading(false)
      }
    }

    fetchLabTests()
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex items-start justify-between rounded-lg border p-4">
            <div className="flex items-start gap-3">
              <Skeleton className="h-10 w-10 rounded-md" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-[200px]" />
                <div className="flex gap-4">
                  <Skeleton className="h-3 w-[100px]" />
                  <Skeleton className="h-3 w-[80px]" />
                </div>
                <Skeleton className="h-3 w-[300px]" />
              </div>
            </div>
            <div className="flex gap-2">
              <Skeleton className="h-8 w-[100px]" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h3 className="mt-2 text-lg font-medium">Không thể tải dữ liệu</h3>
        <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        <Button className="mt-4" onClick={() => window.location.reload()}>
          Thử lại
        </Button>
      </div>
    )
  }

  if (labResults.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
        <TestTube className="h-10 w-10 text-muted-foreground" />
        <h3 className="mt-2 text-lg font-medium">Không có kết quả xét nghiệm</h3>
        <p className="mt-1 text-sm text-muted-foreground">Bạn chưa có kết quả xét nghiệm nào.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {labResults.map((result) => (
        <div key={result.id} className="flex items-start justify-between rounded-lg border p-4">
          <div className="flex items-start gap-3">
            <div className="rounded-md bg-primary/10 p-2">
              <TestTube className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{result.name}</h4>
                {result.isNew && <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Mới</Badge>}
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{result.date}</span>
                </div>
                <div className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Yêu cầu bởi: {result.doctor}</span>
                </div>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{result.summary}</p>
              <p className="mt-1 text-xs text-muted-foreground">Phòng xét nghiệm: {result.lab}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-1">
              <Download className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Tải xuống</span>
            </Button>
            <Button
              variant="default"
              size="sm"
              className="gap-1"
              onClick={() => window.location.href = `/dashboard/patient/records/lab-tests/${result.labTestId}`}
            >
              <ExternalLink className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Xem</span>
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
