"use client"

import { useState, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Clock, MapPin, MoreHorizontal, Video, AlertCircle } from "lucide-react"
import AppointmentService from "@/lib/api/appointment-service"
import { format, isTomorrow, isToday } from "date-fns"
import { vi } from "date-fns/locale"
import { Skeleton } from "@/components/ui/skeleton"

// Helper function để định dạng ngày
const formatAppointmentDate = (dateString: string) => {
  const date = new Date(dateString)
  if (isToday(date)) return "Hôm nay"
  if (isTomorrow(date)) return "Ngày mai"
  return format(date, 'dd/MM/yyyy', { locale: vi })
}

// Interface cho hiển thị
interface FormattedAppointment {
  id: number
  doctor: string
  specialty: string
  date: string
  time: string
  duration: string
  location: string
  type: "Trực tiếp" | "Video"
  status: string
  avatar?: string
}

export default function PatientAppointmentsList() {
  const [appointments, setAppointments] = useState<FormattedAppointment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        // Lấy token từ localStorage
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');

        // Nếu không có token, thử lấy lại sau 1 giây
        // Đây là giải pháp tạm thời để đảm bảo token được lấy sau khi đăng nhập
        if (!token || !userStr) {
          setTimeout(() => {
            const retryToken = localStorage.getItem('token');
            const retryUserStr = localStorage.getItem('user');

            if (retryToken && retryUserStr) {
              // Nếu lấy được token sau khi thử lại, gọi lại hàm fetchAppointments
              fetchAppointments();
            } else {
              console.error('Không có token hoặc thông tin người dùng');
              setError("Không có token hoặc thông tin người dùng. Vui lòng đăng nhập lại.");
              setLoading(false);
            }
          }, 1000);
          return;
        }

        let userRoleConfirmed = false;
        let userInfo = null;

        // Lấy thông tin người dùng từ localStorage
        try {
          if (userStr) {
            userInfo = JSON.parse(userStr);

            // Kiểm tra vai trò từ localStorage
            if (userInfo.role && userInfo.role.toUpperCase() !== 'PATIENT') {
              console.warn("Vai trò người dùng không phải PATIENT, nhưng vẫn tiếp tục");
            }

            userRoleConfirmed = true;
          } else {
            console.error('Không có thông tin người dùng trong localStorage');
          }
        } catch (userError) {
          console.error('Lỗi khi xử lý thông tin người dùng:', userError);
        }

        // Nếu không thể xác nhận vai trò từ API, kiểm tra từ localStorage
        if (!userRoleConfirmed) {
          console.log('DEBUG MODE: Using user info from localStorage');

          try {
            userInfo = JSON.parse(userStr);
            console.log('User info from localStorage:', userInfo);
          } catch (e) {
            console.error('Error parsing user info from localStorage:', e);
          }
        }

        setLoading(true);

        try {
          // Gọi API appointments với token đã lấy từ localStorage
          console.log('DEBUG MODE: Calling getPatientAppointments');
          console.log('DEBUG MODE: Token:', localStorage.getItem('token'));
          const data = await AppointmentService.getPatientAppointments();
          console.log('DEBUG MODE: Appointments data received:', data);

          // Kiểm tra xem data có phải là mảng hay không
          if (Array.isArray(data)) {
            if (data.length > 0) {
              // Format dữ liệu để hiển thị
              const formattedData = data.map(appointment => {
                // Tính khoảng thời gian của cuộc hẹn
                const startTime = new Date(`2000-01-01T${appointment.start_time}`)
                const endTime = new Date(`2000-01-01T${appointment.end_time}`)
                const diffInMinutes = Math.round((endTime.getTime() - startTime.getTime()) / 60000)

                return {
                  id: appointment.id,
                  doctor: `Bác sĩ ${appointment.doctor.first_name} ${appointment.doctor.last_name}`,
                  specialty: appointment.doctor.specialty || "Chưa xác định",
                  date: formatAppointmentDate(appointment.appointment_date),
                  time: appointment.start_time.substring(0, 5), // Lấy chỉ giờ:phút
                  duration: `${diffInMinutes} phút`,
                  location: appointment.location || "Chưa xác định",
                  // Đảm bảo type luôn là một trong hai giá trị hợp lệ
                  type: appointment.location?.toLowerCase().includes("trực tuyến") ? "Video" : "Trực tiếp" as "Video" | "Trực tiếp",
                  status: appointment.status === "confirmed" ? "Đã xác nhận" :
                        appointment.status === "scheduled" ? "Đã lên lịch" :
                        appointment.status === "completed" ? "Hoàn thành" :
                        appointment.status === "cancelled" ? "Đã hủy" : "Chưa xác định",
                  avatar: appointment.doctor.id ? `/avatars/doctor-${appointment.doctor.id}.jpg` : "/placeholder.svg"
                }
              });

              setAppointments(formattedData);
              setError(null);
            } else {
              console.log('DEBUG MODE: Empty appointments array');
              setAppointments([]);
            }
          } else if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
            // Xử lý dữ liệu dạng phân trang
            if (data.results.length > 0) {
              // Format dữ liệu để hiển thị
              const formattedData = data.results.map((appointment: any) => {
                // Tính khoảng thời gian của cuộc hẹn
                const startTime = new Date(`2000-01-01T${appointment.start_time}`)
                const endTime = new Date(`2000-01-01T${appointment.end_time}`)
                const diffInMinutes = Math.round((endTime.getTime() - startTime.getTime()) / 60000)

                return {
                  id: appointment.id,
                  doctor: `Bác sĩ ${appointment.doctor.first_name} ${appointment.doctor.last_name}`,
                  specialty: appointment.doctor.specialty || "Chưa xác định",
                  date: formatAppointmentDate(appointment.appointment_date),
                  time: appointment.start_time.substring(0, 5), // Lấy chỉ giờ:phút
                  duration: `${diffInMinutes} phút`,
                  location: appointment.location || "Chưa xác định",
                  // Đảm bảo type luôn là một trong hai giá trị hợp lệ
                  type: appointment.location?.toLowerCase().includes("trực tuyến") ? "Video" : "Trực tiếp" as "Video" | "Trực tiếp",
                  status: appointment.status === "confirmed" ? "Đã xác nhận" :
                        appointment.status === "scheduled" ? "Đã lên lịch" :
                        appointment.status === "completed" ? "Hoàn thành" :
                        appointment.status === "cancelled" ? "Đã hủy" : "Chưa xác định",
                  avatar: appointment.doctor.id ? `/avatars/doctor-${appointment.doctor.id}.jpg` : "/placeholder.svg"
                }
              });

              setAppointments(formattedData);
              setError(null);
            } else {
              console.log('DEBUG MODE: Empty results array in paginated data');
              setAppointments([]);
            }
          } else {
            console.log('DEBUG MODE: No appointments data or invalid format', data);
            setAppointments([]);
          }
        } catch (apiError: any) {
          console.error("DEBUG MODE: Lỗi khi tải danh sách cuộc hẹn:", apiError);
          console.error("Error details:", {
            status: apiError.response?.status,
            data: apiError.response?.data,
            message: apiError.message
          });

          // KHÔNG ĐĂNG XUẤT, CHỈ HIỂN THỊ THÔNG BÁO LỖI
          if (apiError.response?.status === 403) {
            setError(`Lỗi quyền truy cập: Bạn không có quyền xem danh sách cuộc hẹn. Chi tiết: ${JSON.stringify(apiError.response?.data || {})}`);
          } else if (apiError.response?.status === 404) {
            setError(`Không tìm thấy API: Đường dẫn API không tồn tại hoặc chưa được cấu hình. Chi tiết: ${apiError.message}`);
          } else if (apiError.response?.status === 401) {
            setError(`Lỗi xác thực: Phiên đăng nhập của bạn đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.`);
          } else {
            setError(`Lỗi khi tải danh sách cuộc hẹn: ${apiError.message}. Mã lỗi: ${apiError.response?.status || 'Không xác định'}`);
          }
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-start gap-4">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-[150px]" />
                <Skeleton className="h-3 w-[100px]" />
                <div className="flex gap-4 pt-1">
                  <Skeleton className="h-3 w-[80px]" />
                  <Skeleton className="h-3 w-[120px]" />
                  <Skeleton className="h-3 w-[150px]" />
                </div>
              </div>
            </div>
            <div className="mt-4 md:mt-0">
              <Skeleton className="h-6 w-[100px]" />
              <div className="flex gap-2 mt-2">
                <Skeleton className="h-8 w-[80px]" />
                <Skeleton className="h-8 w-8 rounded" />
              </div>
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

  if (appointments.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
        <Calendar className="h-10 w-10 text-muted-foreground" />
        <h3 className="mt-2 text-lg font-medium">Không có lịch hẹn nào</h3>
        <p className="mt-1 text-sm text-muted-foreground">Bạn chưa có lịch hẹn khám bệnh nào.</p>
        <p className="text-xs text-muted-foreground mt-1 mb-2">
          (Lưu ý: Nếu bạn vừa đặt lịch, có thể cần chờ API Gateway cập nhật hoặc có vấn đề về kết nối)
        </p>
        <Button className="mt-2" asChild>
          <a href="/dashboard/patient/appointments/new">Đặt lịch hẹn ngay</a>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {appointments.map((appointment) => (
        <div
          key={appointment.id}
          className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
        >
          <div className="flex items-start gap-4">
            <Avatar className="hidden md:block">
              <AvatarImage src={appointment.avatar || "/placeholder.svg"} alt={appointment.doctor} />
              <AvatarFallback>
                {appointment.doctor
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <h4 className="font-medium">{appointment.doctor}</h4>
              <p className="text-sm text-muted-foreground">{appointment.specialty}</p>
              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{appointment.date}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>
                    {appointment.time} ({appointment.duration})
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {appointment.type === "Video" ? (
                    <Video className="h-3.5 w-3.5 text-muted-foreground" />
                  ) : (
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  <span>{appointment.location}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between md:mt-0 md:flex-col md:items-end">
            <Badge
              variant={
                appointment.status === "Đã xác nhận" ? "default" :
                appointment.status === "Hoàn thành" ? "outline" :
                appointment.status === "Đã hủy" ? "destructive" : "outline"
              }
              className={
                appointment.status === "Đã xác nhận" ? "bg-green-100 text-green-800 hover:bg-green-100" :
                appointment.status === "Hoàn thành" ? "bg-blue-100 text-blue-800 hover:bg-blue-100" :
                ""
              }
            >
              {appointment.status}
            </Badge>
            <div className="flex items-center gap-2 mt-2">
              {appointment.status !== "Hoàn thành" && appointment.status !== "Đã hủy" && (
                <Button variant="outline" size="sm" asChild>
                  <a href={`/dashboard/patient/appointments/${appointment.id}/edit`}>Đổi lịch</a>
                </Button>
              )}
              <Button variant="ghost" size="icon" asChild>
                <a href={`/dashboard/patient/appointments/${appointment.id}`}>
                  <MoreHorizontal className="h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
