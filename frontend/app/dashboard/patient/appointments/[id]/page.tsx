"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { format } from "date-fns"
import { vi } from "date-fns/locale"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/use-toast"
import { CalendarIcon, Clock, MapPin, ArrowLeft, AlertCircle, FileText, MessageCircle, X } from "lucide-react"
import { PageHeader } from "@/components/layout/page-header"
import { PageContainer } from "@/components/layout/page-container"
import { StatusBadge } from "@/components/ui/status-badge"

export default function AppointmentDetailsPage() {
  const router = useRouter()
  const params = useParams()
  const appointmentId = params.id as string

  const [loading, setLoading] = useState(true)
  const [appointment, setAppointment] = useState<any>(null)
  const [cancelReason, setCancelReason] = useState("")
  const [showCancelDialog, setShowCancelDialog] = useState(false)

  useEffect(() => {
    fetchAppointmentDetails()
  }, [appointmentId])

  const fetchAppointmentDetails = async () => {
    try {
      setLoading(true)
      // Giả lập API call để lấy chi tiết lịch hẹn
      // Trong thực tế, sẽ gọi API từ AppointmentService.getAppointmentById(appointmentId)
      setTimeout(() => {
        const mockAppointment = {
          id: appointmentId,
          patient: {
            id: 1,
            first_name: "Nguyễn",
            last_name: "Văn Bệnh",
            email: "patient@example.com",
          },
          doctor: {
            id: 2,
            first_name: "Trần",
            last_name: "Thị B",
            email: "doctor@example.com",
            specialty: "Thần kinh",
            avatar: "/placeholder.svg?height=40&width=40",
          },
          appointment_date: "2025-05-15",
          start_time: "09:00",
          end_time: "09:30",
          reason: "Đau đầu, chóng mặt kéo dài 3 ngày",
          notes: "Bệnh nhân có tiền sử cao huyết áp",
          status: "CONFIRMED",
          location: "Phòng 203, Tầng 2, Tòa nhà A",
          created_at: "2025-05-01T10:00:00Z",
          updated_at: "2025-05-01T10:30:00Z",
          messages: [
            {
              id: 1,
              sender: "SYSTEM",
              content: "Lịch hẹn của bạn đã được xác nhận.",
              created_at: "2025-05-01T10:30:00Z",
            },
            {
              id: 2,
              sender: "DOCTOR",
              content: "Vui lòng mang theo kết quả xét nghiệm gần nhất nếu có.",
              created_at: "2025-05-02T14:20:00Z",
            },
          ],
        }
        setAppointment(mockAppointment)
        setLoading(false)
      }, 500)
    } catch (error) {
      console.error("Error fetching appointment details:", error)
      toast({
        title: "Lỗi",
        description: "Không thể tải thông tin lịch hẹn. Vui lòng thử lại sau.",
        variant: "destructive",
      })
      setLoading(false)
    }
  }

  const handleCancelAppointment = async () => {
    try {
      setLoading(true)
      // Giả lập API call để hủy lịch hẹn
      // Trong thực tế, sẽ gọi API từ AppointmentService.updateAppointment(appointmentId, { status: "CANCELLED", notes: cancelReason })
      setTimeout(() => {
        setAppointment({ ...appointment, status: "CANCELLED", notes: cancelReason })
        setLoading(false)
        setShowCancelDialog(false)
        toast({
          title: "Hủy lịch thành công",
          description: "Lịch hẹn của bạn đã được hủy thành công.",
        })
      }, 1000)
    } catch (error) {
      console.error("Error cancelling appointment:", error)
      toast({
        title: "Lỗi",
        description: "Không thể hủy lịch hẹn. Vui lòng thử lại sau.",
        variant: "destructive",
      })
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageContainer>
    )
  }

  if (!appointment) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center h-[60vh]">
          <AlertCircle className="h-12 w-12 text-destructive mb-4" />
          <h2 className="text-xl font-semibold mb-2">Không tìm thấy lịch hẹn</h2>
          <p className="text-muted-foreground mb-4">Lịch hẹn này không tồn tại hoặc đã bị xóa.</p>
          <Button onClick={() => router.push("/dashboard/patient/appointments")}>Quay lại danh sách</Button>
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <PageHeader
        title="Chi tiết lịch hẹn"
        description="Xem thông tin chi tiết lịch hẹn của bạn"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push("/dashboard/patient/appointments")}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Quay lại
            </Button>
            {appointment.status === "CONFIRMED" && (
              <Button variant="destructive" onClick={() => setShowCancelDialog(true)}>
                <X className="mr-2 h-4 w-4" />
                Hủy lịch
              </Button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Thông tin lịch hẹn</CardTitle>
                <StatusBadge status={appointment.status} />
              </div>
              <CardDescription>Mã lịch hẹn: APT-{appointment.id.toString().padStart(4, "0")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Bác sĩ</h3>
                  <div className="flex items-center gap-3 mt-2">
                    <Avatar>
                      <AvatarImage
                        src={appointment.doctor.avatar || "/placeholder.svg"}
                        alt={`${appointment.doctor.first_name} ${appointment.doctor.last_name}`}
                      />
                      <AvatarFallback>
                        {appointment.doctor.first_name[0]}
                        {appointment.doctor.last_name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium">
                        BS. {appointment.doctor.first_name} {appointment.doctor.last_name}
                      </p>
                      <p className="text-sm text-muted-foreground">{appointment.doctor.specialty}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Thời gian</h3>
                  <div className="flex items-center gap-2 mt-2">
                    <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                    <span>{format(new Date(appointment.appointment_date), "EEEE, dd/MM/yyyy", { locale: vi })}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>
                      {appointment.start_time} - {appointment.end_time}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Địa điểm</h3>
                <div className="flex items-center gap-2 mt-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span>{appointment.location}</span>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Lý do khám</h3>
                <p className="mt-2">{appointment.reason}</p>
              </div>

              {appointment.notes && (
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Ghi chú</h3>
                  <p className="mt-2">{appointment.notes}</p>
                </div>
              )}

              {appointment.status === "CANCELLED" && (
                <div className="rounded-md border border-destructive/20 bg-destructive/10 p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                    <div>
                      <h3 className="font-medium text-destructive">Lịch hẹn đã bị hủy</h3>
                      <p className="text-sm text-destructive/80 mt-1">
                        {appointment.notes || "Không có lý do được cung cấp"}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Tabs defaultValue="messages">
            <TabsList>
              <TabsTrigger value="messages">Tin nhắn</TabsTrigger>
              <TabsTrigger value="documents">Tài liệu</TabsTrigger>
            </TabsList>
            <TabsContent value="messages" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Tin nhắn</CardTitle>
                  <CardDescription>Trao đổi thông tin với bác sĩ</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {appointment.messages && appointment.messages.length > 0 ? (
                      appointment.messages.map((message: any) => (
                        <div
                          key={message.id}
                          className={`flex gap-3 ${message.sender === "PATIENT" ? "justify-end" : "justify-start"}`}
                        >
                          {message.sender !== "PATIENT" && (
                            <Avatar className="h-8 w-8">
                              {message.sender === "DOCTOR" ? (
                                <AvatarImage
                                  src={appointment.doctor.avatar || "/placeholder.svg"}
                                  alt={`${appointment.doctor.first_name} ${appointment.doctor.last_name}`}
                                />
                              ) : (
                                <AvatarImage src="/placeholder.svg" alt="System" />
                              )}
                              <AvatarFallback>
                                {message.sender === "DOCTOR"
                                  ? `${appointment.doctor.first_name[0]}${appointment.doctor.last_name[0]}`
                                  : "SYS"}
                              </AvatarFallback>
                            </Avatar>
                          )}
                          <div
                            className={`rounded-lg p-3 max-w-[80%] ${
                              message.sender === "PATIENT" ? "bg-primary text-primary-foreground" : "bg-muted"
                            }`}
                          >
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs mt-1 opacity-70">
                              {format(new Date(message.created_at), "HH:mm, dd/MM/yyyy")}
                            </p>
                          </div>
                          {message.sender === "PATIENT" && (
                            <Avatar className="h-8 w-8">
                              <AvatarImage
                                src="/placeholder.svg"
                                alt={`${appointment.patient.first_name} ${appointment.patient.last_name}`}
                              />
                              <AvatarFallback>
                                {appointment.patient.first_name[0]}
                                {appointment.patient.last_name[0]}
                              </AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-20" />
                        <p>Chưa có tin nhắn nào</p>
                      </div>
                    )}
                  </div>
                </CardContent>
                <CardFooter>
                  <div className="flex w-full gap-2">
                    <Textarea
                      placeholder="Nhập tin nhắn..."
                      className="flex-1"
                      disabled={appointment.status === "CANCELLED"}
                    />
                    <Button disabled={appointment.status === "CANCELLED"}>Gửi</Button>
                  </div>
                </CardFooter>
              </Card>
            </TabsContent>
            <TabsContent value="documents" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Tài liệu</CardTitle>
                  <CardDescription>Tài liệu liên quan đến lịch hẹn</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="h-12 w-12 mx-auto mb-2 opacity-20" />
                    <p>Chưa có tài liệu nào</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Hướng dẫn</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium">Trước khi đến khám</h3>
                  <ul className="mt-2 space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                        <CalendarIcon className="h-3 w-3 text-primary" />
                      </div>
                      <span>Đến trước giờ hẹn 15 phút để hoàn tất thủ tục đăng ký</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                        <FileText className="h-3 w-3 text-primary" />
                      </div>
                      <span>Mang theo CMND/CCCD và thẻ BHYT (nếu có)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                        <AlertCircle className="h-3 w-3 text-primary" />
                      </div>
                      <span>Nếu bạn không thể đến đúng hẹn, vui lòng hủy hoặc đổi lịch trước 24 giờ</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-medium">Chính sách hủy lịch</h3>
                  <p className="mt-2 text-sm">
                    Bạn có thể hủy lịch hẹn miễn phí trước 24 giờ. Nếu hủy trong vòng 24 giờ trước giờ hẹn, bạn có thể
                    phải chịu phí hủy lịch.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Liên hệ hỗ trợ</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <p>
                  <span className="font-medium">Hotline:</span> 1900 1234
                </p>
                <p>
                  <span className="font-medium">Email:</span> support@healthcare.com
                </p>
                <p>
                  <span className="font-medium">Giờ làm việc:</span> 7:00 - 20:00 (Thứ 2 - Chủ nhật)
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Hủy lịch hẹn</DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn hủy lịch hẹn này? Vui lòng cung cấp lý do hủy lịch.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <h3 className="text-sm font-medium">Lý do hủy lịch</h3>
              <Textarea
                placeholder="Nhập lý do hủy lịch..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCancelDialog(false)}>
              Hủy
            </Button>
            <Button variant="destructive" onClick={handleCancelAppointment} disabled={loading}>
              {loading ? "Đang xử lý..." : "Xác nhận hủy lịch"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PageContainer>
  )
}
