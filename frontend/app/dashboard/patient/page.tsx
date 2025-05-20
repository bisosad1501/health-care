"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { StatusBadge } from "@/components/ui/status-badge"
import { StatCard } from "@/components/ui/stat-card"
import { PageHeader } from "@/components/layout/page-header"
import { PageContainer } from "@/components/layout/page-container"
import {
  Calendar,
  Clock,
  FileText,
  PlusCircle,
  Pill,
  FlaskRoundIcon as Flask,
  CalendarClock,
  Activity,
  ChevronRight,
} from "lucide-react"
import PatientAppointments from "@/components/patient/patient-appointments"
import { formatDate } from "@/lib/utils"
import appointmentService from "@/lib/api/appointment-service"
import PharmacyService, { PrescriptionWithDetails } from "@/lib/api/pharmacy-service"
import LaboratoryService, { LabTest } from "@/lib/api/laboratory-service"
import MedicalRecordService from "@/lib/api/medical-record-service"
import { toast } from "sonner"

export default function PatientDashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [appointments, setAppointments] = useState<any[]>([])
  const [prescriptions, setPrescriptions] = useState<any[]>([])
  const [labTests, setLabTests] = useState<any[]>([])
  const [stats, setStats] = useState({
    upcomingAppointments: 0,
    pendingPrescriptions: 0,
    pendingLabTests: 0,
    completedVisits: 0,
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)

      // Lấy dữ liệu cuộc hẹn từ API
      const appointmentsResponse = await appointmentService.getPatientAppointments()
      console.log('Appointments data from API:', appointmentsResponse)

      // Chuyển đổi dữ liệu từ API sang định dạng hiển thị
      const formattedAppointments = appointmentsResponse.map(appointment => {
        // Kiểm tra và log cấu trúc dữ liệu
        console.log('Appointment structure:', JSON.stringify(appointment, null, 2))

        // Xử lý thông tin bác sĩ
        let doctorInfo = {
          id: appointment.doctor_id || 0,
          first_name: '',
          last_name: '',
          specialty: '',
          email: ''
        }

        // Ưu tiên sử dụng doctor nếu có
        if (appointment.doctor && typeof appointment.doctor === 'object') {
          doctorInfo = {
            ...doctorInfo,
            ...appointment.doctor
          }
        }
        // Nếu không có doctor, thử sử dụng doctor_info
        else if (appointment.doctor_info && typeof appointment.doctor_info === 'object') {
          doctorInfo = {
            ...doctorInfo,
            first_name: appointment.doctor_info.first_name || '',
            last_name: appointment.doctor_info.last_name || '',
            specialty: appointment.doctor_info.specialty || '',
            email: appointment.doctor_info.email || ''
          }
        }

        // Xử lý ngày và giờ
        let appointmentDate = ''
        let startTime = ''
        let endTime = ''
        let location = 'Phòng khám chính'

        // Nếu có time_slot
        if (appointment.time_slot) {
          if (typeof appointment.time_slot === 'object') {
            appointmentDate = appointment.time_slot.date || ''
            startTime = appointment.time_slot.start_time?.substring(0, 5) || ''
            endTime = appointment.time_slot.end_time?.substring(0, 5) || ''
            location = appointment.time_slot.location || location
          }
        }
        // Nếu không có time_slot, sử dụng các trường trực tiếp
        else {
          appointmentDate = appointment.appointment_date || appointment.date || ''
          startTime = appointment.start_time?.substring(0, 5) || ''
          endTime = appointment.end_time?.substring(0, 5) || ''
          location = appointment.location || location
        }

        return {
          id: appointment.id,
          doctor: doctorInfo,
          appointment_date: appointmentDate,
          start_time: startTime,
          end_time: endTime,
          reason: appointment.reason_text || appointment.reason || '',
          status: appointment.status || 'PENDING',
          location: location,
        }
      })

      console.log('Formatted appointments:', formattedAppointments)
      setAppointments(formattedAppointments)

      // Lấy dữ liệu đơn thuốc từ API
      let formattedPrescriptions = []
      try {
        const prescriptionsResponse = await PharmacyService.getPatientPrescriptions()
        console.log('Prescriptions data from API:', prescriptionsResponse)

        // Chuyển đổi dữ liệu từ API sang định dạng hiển thị
        formattedPrescriptions = await Promise.all(prescriptionsResponse.map(async (prescription) => {
          // Lấy thông tin bác sĩ nếu cần
          let doctorInfo = {
            first_name: '',
            last_name: '',
            specialty: ''
          }

          try {
            if (prescription.doctor_id) {
              const doctorResponse = await MedicalRecordService.getDoctorInfo(prescription.doctor_id)
              if (doctorResponse) {
                doctorInfo = {
                  first_name: doctorResponse.first_name || '',
                  last_name: doctorResponse.last_name || '',
                  specialty: doctorResponse.doctor_profile?.specialty?.name || ''
                }
              }
            }
          } catch (error) {
            console.error(`Error fetching doctor info for prescription ${prescription.id}:`, error)
          }

          // Xử lý các item trong đơn thuốc
          const medications = prescription.items?.map(item => ({
            name: item.medication_details?.name || 'Thuốc không xác định',
            dosage: `${item.dosage || ''} - ${item.frequency || ''}`
          })) || []

          return {
            id: prescription.id,
            doctor: doctorInfo,
            prescription_date: prescription.date_prescribed || prescription.created_at,
            status: prescription.status || 'PENDING',
            medications: medications
          }
        }))

        console.log('Formatted prescriptions:', formattedPrescriptions)
        setPrescriptions(formattedPrescriptions)
      } catch (error) {
        console.error("Error fetching prescriptions:", error)
        toast.error("Không thể tải thông tin đơn thuốc")
        formattedPrescriptions = []
        setPrescriptions([])
      }

      // Lấy dữ liệu xét nghiệm từ API
      let formattedLabTests = []
      try {
        const labTestsResponse = await LaboratoryService.getPatientLabTests()
        console.log('Lab tests data from API:', labTestsResponse)

        // Chuyển đổi dữ liệu từ API sang định dạng hiển thị
        formattedLabTests = await Promise.all(labTestsResponse.map(async (test) => {
          // Lấy thông tin bác sĩ nếu cần
          let doctorInfo = {
            first_name: '',
            last_name: '',
            specialty: ''
          }

          try {
            if (test.ordered_by) {
              const doctorResponse = await MedicalRecordService.getDoctorInfo(test.ordered_by)
              if (doctorResponse) {
                doctorInfo = {
                  first_name: doctorResponse.first_name || '',
                  last_name: doctorResponse.last_name || '',
                  specialty: doctorResponse.doctor_profile?.specialty?.name || ''
                }
              }
            }
          } catch (error) {
            console.error(`Error fetching doctor info for lab test ${test.id}:`, error)
          }

          return {
            id: test.id,
            test_name: test.test_type_details?.name || 'Xét nghiệm không xác định',
            ordered_at: test.ordered_at || test.created_at,
            status: test.status || 'PENDING',
            doctor: doctorInfo
          }
        }))

        console.log('Formatted lab tests:', formattedLabTests)
        setLabTests(formattedLabTests)
      } catch (error) {
        console.error("Error fetching lab tests:", error)
        toast.error("Không thể tải thông tin xét nghiệm")
        formattedLabTests = []
        setLabTests([])
      }

      // Lấy số lần khám đã hoàn thành từ API
      let completedVisitsCount = 0
      try {
        const encounters = await MedicalRecordService.getPatientEncounters()
        completedVisitsCount = encounters.length
        console.log('Completed visits count:', completedVisitsCount)
      } catch (error) {
        console.error("Error fetching completed visits:", error)
        completedVisitsCount = 0
      }

      // Cập nhật thống kê
      setStats({
        upcomingAppointments: formattedAppointments.filter((a) => a.status === "CONFIRMED" || a.status === "SCHEDULED").length,
        pendingPrescriptions: formattedPrescriptions.filter((p) => p.status === "PENDING").length,
        pendingLabTests: formattedLabTests.filter((l) => l.status === "PENDING").length,
        completedVisits: completedVisitsCount
      })

      setLoading(false)
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
      toast.error("Không thể tải dữ liệu trang chủ")
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <StatusBadge status="success" text="Đã hoàn thành" />
      case "PENDING":
        return <StatusBadge status="warning" text="Đang chờ" />
      case "DISPENSED":
        return <StatusBadge status="info" text="Đã phát thuốc" />
      case "CONFIRMED":
        return <StatusBadge status="success" text="Đã xác nhận" />
      case "SCHEDULED":
        return <StatusBadge status="info" text="Đã lên lịch" />
      default:
        return <StatusBadge status="default" text={status} />
    }
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }

  return (
    <PageContainer>
      <PageHeader
        title="Trang chủ"
        description="Xin chào, chào mừng bạn đến với hệ thống quản lý y tế"
        actions={
          <Button onClick={() => router.push("/dashboard/patient/appointments/simple-booking")} className="group">
            <PlusCircle className="mr-2 h-4 w-4 transition-transform group-hover:rotate-90" />
            <span>Đặt lịch hẹn</span>
          </Button>
        }
      />

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
      >
        <motion.div variants={item}>
          <StatCard
            title="Lịch hẹn sắp tới"
            value={stats.upcomingAppointments.toString()}
            description="Cuộc hẹn đã xác nhận"
            icon={<CalendarClock className="h-5 w-5" />}
            trend="up"
            trendValue="5%"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            title="Đơn thuốc chờ xử lý"
            value={stats.pendingPrescriptions.toString()}
            description="Đơn thuốc cần lấy"
            icon={<Pill className="h-5 w-5" />}
            trend="neutral"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            title="Xét nghiệm chờ xử lý"
            value={stats.pendingLabTests.toString()}
            description="Xét nghiệm cần thực hiện"
            icon={<Flask className="h-5 w-5" />}
            trend="neutral"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatCard
            title="Lần khám đã hoàn thành"
            value={stats.completedVisits.toString()}
            description="Tổng số lần khám"
            icon={<Activity className="h-5 w-5" />}
            trend="up"
            trendValue="12%"
          />
        </motion.div>
      </motion.div>

      <Tabs defaultValue="appointments">
        <TabsList className="mb-4">
          <TabsTrigger value="appointments">Lịch hẹn sắp tới</TabsTrigger>
          <TabsTrigger value="prescriptions">Đơn thuốc gần đây</TabsTrigger>
          <TabsTrigger value="lab-tests">Xét nghiệm gần đây</TabsTrigger>
        </TabsList>

        {/* Không sử dụng AnimatePresence ở đây vì có nhiều phần tử con */}
          <TabsContent key="appointments" value="appointments">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Lịch hẹn sắp tới</CardTitle>
                      <CardDescription>Danh sách các cuộc hẹn sắp tới của bạn</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => router.push("/dashboard/patient/appointments")}
                      className="group"
                    >
                      <span>Xem tất cả</span>
                      <ChevronRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  ) : (
                    <PatientAppointments appointments={appointments} />
                  )}
                </CardContent>
                <CardFooter className="flex justify-center border-t pt-4">
                  <Button onClick={() => router.push("/dashboard/patient/appointments/simple-booking")} className="group">
                    <PlusCircle className="mr-2 h-4 w-4 transition-transform group-hover:rotate-90" />
                    <span>Đặt lịch hẹn</span>
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent key="prescriptions" value="prescriptions">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Đơn thuốc gần đây</CardTitle>
                      <CardDescription>Danh sách đơn thuốc gần đây của bạn</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => router.push("/dashboard/patient/prescriptions")}
                      className="group"
                    >
                      <span>Xem tất cả</span>
                      <ChevronRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  ) : prescriptions.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-center py-8 text-muted-foreground"
                    >
                      <Pill className="h-12 w-12 mx-auto mb-2 opacity-20" />
                      <p>Bạn chưa có đơn thuốc nào</p>
                    </motion.div>
                  ) : (
                    <motion.div variants={container} initial="hidden" animate="show" className="space-y-4">
                      {prescriptions.map((prescription, index) => (
                        <motion.div
                          key={prescription.id}
                          variants={item}
                          whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">Đơn thuốc #{prescription.id}</h4>
                              {getStatusBadge(prescription.status)}
                            </div>
                            <p className="text-sm text-muted-foreground">
                              BS. {prescription.doctor.first_name} {prescription.doctor.last_name} (
                              {prescription.doctor.specialty})
                            </p>
                            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                              <Calendar className="h-3.5 w-3.5" />
                              <span>{formatDate(prescription.prescription_date)}</span>
                            </div>
                            <div className="mt-2">
                              {prescription.medications.map((med: any, index: number) => (
                                <div key={index} className="text-sm">
                                  <span className="font-medium">{med.name}</span>: {med.dosage}
                                </div>
                              ))}
                            </div>
                          </div>
                          <div className="mt-4 flex items-center gap-2 md:mt-0">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => router.push(`/dashboard/patient/prescriptions/${prescription.id}`)}
                              className="group"
                            >
                              <FileText className="mr-2 h-3.5 w-3.5" />
                              <span>Chi tiết</span>
                              <ChevronRight className="ml-1 h-3.5 w-3.5 opacity-0 transition-all group-hover:ml-2 group-hover:opacity-100" />
                            </Button>
                          </div>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent key="lab-tests" value="lab-tests">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Xét nghiệm gần đây</CardTitle>
                      <CardDescription>Danh sách xét nghiệm gần đây của bạn</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => router.push("/dashboard/patient/records")}
                      className="group"
                    >
                      <span>Xem tất cả</span>
                      <ChevronRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  ) : labTests.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-center py-8 text-muted-foreground"
                    >
                      <Flask className="h-12 w-12 mx-auto mb-2 opacity-20" />
                      <p>Bạn chưa có xét nghiệm nào</p>
                    </motion.div>
                  ) : (
                    <motion.div variants={container} initial="hidden" animate="show" className="space-y-4">
                      {labTests.map((test, index) => (
                        <motion.div
                          key={test.id}
                          variants={item}
                          whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{test.test_name}</h4>
                              {getStatusBadge(test.status)}
                            </div>
                            <p className="text-sm text-muted-foreground">
                              BS. {test.doctor.first_name} {test.doctor.last_name} ({test.doctor.specialty})
                            </p>
                            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                              <Clock className="h-3.5 w-3.5" />
                              <span>Yêu cầu: {formatDate(test.ordered_at)}</span>
                            </div>
                          </div>
                          <div className="mt-4 flex items-center gap-2 md:mt-0">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => router.push(`/dashboard/patient/records/lab-tests/${test.id}`)}
                              className="group"
                            >
                              <FileText className="mr-2 h-3.5 w-3.5" />
                              <span>Xem kết quả</span>
                              <ChevronRight className="ml-1 h-3.5 w-3.5 opacity-0 transition-all group-hover:ml-2 group-hover:opacity-100" />
                            </Button>
                          </div>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        {/* Kết thúc các TabsContent */}
      </Tabs>
    </PageContainer>
  )
}
