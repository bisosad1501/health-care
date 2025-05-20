"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, UserPlus, Loader2 } from "lucide-react"
import Link from "next/link"
import { DataTable } from "@/components/ui/data-table"
import { StatusBadge } from "@/components/ui/status-badge"
import { PageHeader } from "@/components/layout/page-header"
import { toast } from "sonner"
import patientService from "@/lib/api/patient-service"

// Định nghĩa interface cho dữ liệu bệnh nhân
interface Patient {
  id: string | number
  first_name: string
  last_name: string
  gender?: string
  date_of_birth?: string
  phone?: string
  email?: string
  last_visit_date?: string
  status?: string
}

export default function DoctorPatientsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [patients, setPatients] = useState<Patient[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Tính tuổi từ ngày sinh
  const calculateAge = (dateOfBirth: string | undefined): number => {
    if (!dateOfBirth) return 0
    const today = new Date()
    const birthDate = new Date(dateOfBirth)
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    return age
  }

  // Format ngày tháng
  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return "Chưa có"
    const date = new Date(dateString)
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  // Lấy danh sách bệnh nhân từ API
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setIsLoading(true)
        const response = await patientService.getPatients()
        console.log("Patients data:", response)

        // Chuyển đổi dữ liệu từ API sang định dạng hiển thị
        const formattedPatients = Array.isArray(response.data)
          ? response.data.map((patient: any) => ({
              id: patient.id,
              first_name: patient.first_name || "",
              last_name: patient.last_name || "",
              gender: patient.gender || "Không xác định",
              date_of_birth: patient.date_of_birth || patient.dateOfBirth,
              phone: patient.phone || patient.phone_number || "Chưa cập nhật",
              email: patient.email || "Chưa cập nhật",
              last_visit_date: patient.last_visit_date || "Chưa có",
              status: patient.status || "ACTIVE"
            }))
          : []

        setPatients(formattedPatients)
      } catch (error) {
        console.error("Error fetching patients:", error)
        toast.error("Không thể tải danh sách bệnh nhân. Vui lòng thử lại sau.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchPatients()
  }, [])

  const columns = [
    {
      key: "name",
      header: "Họ tên",
      cell: (patient: Patient) => (
        <Link href={`/dashboard/doctor/patients/${patient.id}`} className="font-medium hover:underline">
          {`${patient.first_name} ${patient.last_name}`}
        </Link>
      ),
    },
    {
      key: "gender",
      header: "Giới tính",
      cell: (patient: Patient) => patient.gender || "Không xác định",
    },
    {
      key: "age",
      header: "Tuổi",
      cell: (patient: Patient) => calculateAge(patient.date_of_birth),
    },
    {
      key: "phone",
      header: "Số điện thoại",
      cell: (patient: Patient) => patient.phone || "Chưa cập nhật",
    },
    {
      key: "lastVisit",
      header: "Lần khám gần nhất",
      cell: (patient: Patient) => formatDate(patient.last_visit_date),
    },
    {
      key: "status",
      header: "Trạng thái",
      cell: (patient: Patient) => <StatusBadge status={patient.status || "ACTIVE"} />,
    },
    {
      key: "actions",
      header: "",
      cell: (patient: Patient) => (
        <div className="flex justify-end">
          <Link href={`/dashboard/doctor/examination?patient=${patient.id}`}>
            <Button size="sm" variant="outline">
              Khám bệnh
            </Button>
          </Link>
        </div>
      ),
    },
  ]

  // Lọc bệnh nhân theo từ khóa tìm kiếm
  const filteredPatients = patients.filter((patient) => {
    const fullName = `${patient.first_name} ${patient.last_name}`.toLowerCase()
    return fullName.includes(searchQuery.toLowerCase()) ||
           (patient.phone && patient.phone.includes(searchQuery)) ||
           (patient.email && patient.email.toLowerCase().includes(searchQuery.toLowerCase()))
  })

  return (
    <div className="space-y-6">
      <PageHeader title="Bệnh nhân" description="Quản lý danh sách bệnh nhân của bạn">
        <Link href="/dashboard/doctor/patients/new">
          <Button size="sm">
            <UserPlus className="mr-2 h-4 w-4" />
            Thêm bệnh nhân
          </Button>
        </Link>
      </PageHeader>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Tìm kiếm bệnh nhân..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
              <p className="text-muted-foreground">Đang tải danh sách bệnh nhân...</p>
            </div>
          ) : (
            <DataTable
              columns={columns}
              data={filteredPatients}
              keyField="id"
              emptyState={
                <div className="flex flex-col items-center justify-center py-8">
                  <p className="text-muted-foreground">
                    {searchQuery ? "Không tìm thấy bệnh nhân phù hợp với từ khóa tìm kiếm" : "Chưa có bệnh nhân nào"}
                  </p>
                </div>
              }
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
