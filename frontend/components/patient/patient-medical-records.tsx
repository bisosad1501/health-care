"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Download, ExternalLink, FileText, User, AlertCircle } from "lucide-react"
import MedicalRecordService from "@/lib/api/medical-record-service"
import { format, parseISO } from "date-fns"
import { vi } from "date-fns/locale"
import { Skeleton } from "@/components/ui/skeleton"

// Interface cho dữ liệu hiển thị
interface FormattedMedicalRecord {
  id: number
  title: string
  doctor: string
  specialty: string
  date: string
  type: string
  summary: string
  hasAttachments: boolean
  recordId: number
  encounterId: number
}

export default function PatientMedicalRecords() {
  const [records, setRecords] = useState<FormattedMedicalRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMedicalRecords = async () => {
      try {
        setLoading(true)

        // Lấy danh sách hồ sơ y tế
        const response = await MedicalRecordService.getPatientMedicalRecords()
        console.log("Medical records response:", response)

        if (!response || !response.results || response.results.length === 0) {
          setRecords([])
          setLoading(false)
          return
        }

        // Lấy chi tiết của hồ sơ y tế đầu tiên
        const recordDetails = await MedicalRecordService.getMedicalRecordById(response.results[0].id)
        console.log("Medical record details:", recordDetails)

        if (!recordDetails || !recordDetails.encounters || recordDetails.encounters.length === 0) {
          setRecords([])
          setLoading(false)
          return
        }

        // Xử lý dữ liệu để hiển thị
        const formattedRecords = await Promise.all(recordDetails.encounters.map(async (encounter: any) => {
          // Lấy thông tin bác sĩ
          let doctorName = `Bác sĩ #${encounter.doctor_id}`
          let specialty = "Chưa xác định"

          try {
            const doctorInfo = await MedicalRecordService.getDoctorInfo(encounter.doctor_id)
            if (doctorInfo) {
              doctorName = `BS. ${doctorInfo.first_name} ${doctorInfo.last_name}`
              specialty = doctorInfo.doctor_profile?.specialization || "Chưa xác định"
            }
          } catch (error) {
            console.error("Error fetching doctor info:", error)
          }

          // Lấy chẩn đoán đầu tiên nếu có
          const diagnosis = encounter.diagnoses && encounter.diagnoses.length > 0
            ? encounter.diagnoses[0].diagnosis_description
            : "Không có chẩn đoán"

          // Định dạng ngày tháng
          const date = encounter.encounter_date
            ? format(parseISO(encounter.encounter_date), 'dd/MM/yyyy', { locale: vi })
            : "Không xác định"

          // Xác định loại khám
          const type = encounter.encounter_type === "OUTPATIENT"
            ? "Khám ngoại trú"
            : encounter.encounter_type === "INPATIENT"
              ? "Nội trú"
              : encounter.encounter_type

          return {
            id: encounter.id,
            title: encounter.chief_complaint || "Khám bệnh",
            doctor: doctorName,
            specialty: specialty,
            date: date,
            type: type,
            summary: encounter.notes || diagnosis,
            hasAttachments: encounter.lab_tests && encounter.lab_tests.length > 0,
            recordId: recordDetails.id,
            encounterId: encounter.id
          }
        }))

        setRecords(formattedRecords)
      } catch (error: any) {
        console.error("Error fetching medical records:", error)
        setError("Không thể tải hồ sơ y tế. Vui lòng thử lại sau.")
      } finally {
        setLoading(false)
      }
    }

    fetchMedicalRecords()
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

  if (records.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
        <FileText className="h-10 w-10 text-muted-foreground" />
        <h3 className="mt-2 text-lg font-medium">Không có hồ sơ y tế</h3>
        <p className="mt-1 text-sm text-muted-foreground">Bạn chưa có hồ sơ y tế nào.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {records.map((record) => (
        <div key={record.id} className="flex items-start justify-between rounded-lg border p-4">
          <div className="flex items-start gap-3">
            <div className="rounded-md bg-primary/10 p-2">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h4 className="font-medium">{record.title}</h4>
              <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{record.doctor}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{record.date}</span>
                </div>
                <Badge variant="outline">{record.type}</Badge>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{record.summary}</p>
            </div>
          </div>
          <div className="flex gap-2">
            {record.hasAttachments && (
              <Button variant="outline" size="sm" className="gap-1">
                <Download className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Tải xuống</span>
              </Button>
            )}
            <Button
              variant="default"
              size="sm"
              className="gap-1"
              onClick={() => window.location.href = `/dashboard/patient/records/${record.recordId}/encounters/${record.encounterId}`}
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
