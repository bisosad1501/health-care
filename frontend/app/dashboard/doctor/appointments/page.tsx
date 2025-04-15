"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { format, addDays, parseISO } from "date-fns"
import { vi } from "date-fns/locale"
import { CalendarDays, Clock, Plus, Search, Filter, RefreshCw, FileText } from "lucide-react"

import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { DashboardCalendar } from "@/components/dashboard/dashboard-calendar"
import { DataTable } from "@/components/ui/data-table"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

import appointmentService from "@/lib/api/appointment-service"
import { DoctorAvailability, TimeSlot, AppointmentWithDetails } from "@/lib/api/appointment-service"

// Schema cho form tạo lịch làm việc
const availabilityFormSchema = z.object({
  weekday: z.string().min(1, { message: "Vui lòng chọn ngày trong tuần" }),
  start_time: z.string().min(1, { message: "Vui lòng nhập giờ bắt đầu" }),
  end_time: z.string().min(1, { message: "Vui lòng nhập giờ kết thúc" }),
  is_available: z.boolean().default(true),
})

// Schema cho form tạo khung giờ từ lịch làm việc
const timeSlotFormSchema = z.object({
  start_date: z.date({ required_error: "Vui lòng chọn ngày bắt đầu" }),
  end_date: z.date({ required_error: "Vui lòng chọn ngày kết thúc" }),
  slot_duration: z.string().min(1, { message: "Vui lòng chọn thời lượng khung giờ" }),
})

// Schema cho form tạo khung giờ cho ngày cụ thể
const specificDateFormSchema = z.object({
  date: z.date({ required_error: "Vui lòng chọn ngày" }),
  start_time: z.string().min(1, { message: "Vui lòng nhập giờ bắt đầu" }),
  end_time: z.string().min(1, { message: "Vui lòng nhập giờ kết thúc" }),
  slot_duration: z.string().min(1, { message: "Vui lòng chọn thời lượng khung giờ" }),
})

export default function DoctorAppointmentsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("schedule")
  const [availabilities, setAvailabilities] = useState<DoctorAvailability[]>([])
  const safeAvailabilities = Array.isArray(availabilities) ? availabilities : []
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([])
  const [appointments, setAppointments] = useState<AppointmentWithDetails[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [userId, setUserId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [selectedAppointment, setSelectedAppointment] = useState<AppointmentWithDetails | null>(null)

  // Form cho lịch làm việc
  const availabilityForm = useForm<z.infer<typeof availabilityFormSchema>>({
    resolver: zodResolver(availabilityFormSchema),
    defaultValues: {
      weekday: "",
      start_time: "",
      end_time: "",
      is_available: true,
    },
  })

  // Form cho tạo khung giờ từ lịch làm việc
  const timeSlotForm = useForm<z.infer<typeof timeSlotFormSchema>>({
    resolver: zodResolver(timeSlotFormSchema),
    defaultValues: {
      start_date: new Date(),
      end_date: addDays(new Date(), 7),
      slot_duration: "30",
    },
  })

  // Form cho tạo khung giờ cho ngày cụ thể
  const specificDateForm = useForm<z.infer<typeof specificDateFormSchema>>({
    resolver: zodResolver(specificDateFormSchema),
    defaultValues: {
      date: new Date(),
      start_time: "08:00",
      end_time: "17:00",
      slot_duration: "30",
    },
  })

  // Lấy ID của bác sĩ đang đăng nhập
  useEffect(() => {
    const userJson = localStorage.getItem("user")
    if (userJson) {
      try {
        const user = JSON.parse(userJson)
        setUserId(user.id)
      } catch (error) {
        console.error("Error parsing user data:", error)
      }
    }
  }, [])

  // Lấy danh sách lịch làm việc của bác sĩ
  const fetchAvailabilities = async () => {
    if (!userId) return

    setIsLoading(true)
    try {
      const data = await appointmentService.getDoctorAvailabilities(userId)
      setAvailabilities(data)
    } catch (error) {
      console.error("Error fetching availabilities:", error)
      toast.error("Không thể tải lịch làm việc. Vui lòng thử lại sau.")
    } finally {
      setIsLoading(false)
    }
  }

  // Lấy danh sách khung giờ của bác sĩ
  const fetchTimeSlots = async () => {
    if (!userId) return

    setIsLoading(true)
    try {
      // Lấy khung giờ trong 30 ngày tới
      const today = format(new Date(), "yyyy-MM-dd")
      const nextMonth = format(addDays(new Date(), 30), "yyyy-MM-dd")

      console.log("Fetching time slots for doctor ID:", userId);
      console.log("Date range:", today, "to", nextMonth);

      const data = await appointmentService.getAvailableTimeSlots(userId, today, nextMonth)
      console.log("Fetched time slots:", data);

      if (Array.isArray(data)) {
        setTimeSlots(data)
      } else {
        console.error("Unexpected response format:", data);
        setTimeSlots([])
        toast.error("Dữ liệu khung giờ không đúng định dạng. Vui lòng thử lại sau.")
      }
    } catch (error: any) {
      console.error("Error fetching time slots:", error)
      toast.error(`Không thể tải khung giờ: ${error.message || 'Lỗi không xác định'}`)
    } finally {
      setIsLoading(false)
    }
  }

  // Lấy danh sách lịch hẹn của bác sĩ
  const fetchAppointments = async () => {
    if (!userId) return

    setIsLoading(true)
    try {
      const data = await appointmentService.getDoctorAppointments(userId)
      setAppointments(data)
    } catch (error) {
      console.error("Error fetching appointments:", error)
      toast.error("Không thể tải lịch hẹn. Vui lòng thử lại sau.")
    } finally {
      setIsLoading(false)
    }
  }

  // Cập nhật trạng thái lịch hẹn
  const handleUpdateAppointmentStatus = async (appointmentId: number, newStatus: string) => {
    setIsLoading(true)
    try {
      await appointmentService.updateAppointmentStatus(appointmentId, newStatus)
      toast.success("Cập nhật trạng thái lịch hẹn thành công!")
      fetchAppointments() // Tải lại danh sách lịch hẹn
    } catch (error) {
      console.error("Error updating appointment status:", error)
      toast.error("Không thể cập nhật trạng thái lịch hẹn. Vui lòng thử lại sau.")
    } finally {
      setIsLoading(false)
    }
  }

  // Tải dữ liệu khi component được mount hoặc khi userId thay đổi
  useEffect(() => {
    if (userId) {
      fetchAvailabilities()
      fetchTimeSlots()
      fetchAppointments()
    }
  }, [userId])

  // State để lưu trữ ID của ca làm việc đang được chỉnh sửa
  const [editingAvailabilityId, setEditingAvailabilityId] = useState<number | null>(null);

  // Xử lý tạo lịch làm việc mới
  const handleCreateAvailability = async (values: z.infer<typeof availabilityFormSchema>) => {
    if (!userId) {
      toast.error("Không tìm thấy thông tin bác sĩ. Vui lòng đăng nhập lại.")
      return
    }

    // Kiểm tra thời gian bắt đầu và kết thúc
    const startTime = values.start_time;
    const endTime = values.end_time;

    if (startTime >= endTime) {
      toast.error("Giờ kết thúc phải sau giờ bắt đầu.")
      return
    }

    // Kiểm tra chồng chéo với các ca làm việc hiện có
    const weekday = parseInt(values.weekday);
    const overlappingSchedules = safeAvailabilities.filter(schedule => {
      // Nếu đang chỉnh sửa, bỏ qua ca hiện tại khi kiểm tra chồng chéo
      if (editingAvailabilityId && schedule.id === editingAvailabilityId) {
        return false;
      }

      // Chỉ kiểm tra các ca cùng ngày
      if (schedule.weekday !== weekday) return false;

      // Kiểm tra chồng chéo thời gian
      // Ca mới bắt đầu trong khoảng thời gian của ca hiện có
      const startsWithinExisting = startTime >= schedule.start_time && startTime < schedule.end_time;
      // Ca mới kết thúc trong khoảng thời gian của ca hiện có
      const endsWithinExisting = endTime > schedule.start_time && endTime <= schedule.end_time;
      // Ca mới bao trùm ca hiện có
      const containsExisting = startTime <= schedule.start_time && endTime >= schedule.end_time;

      return startsWithinExisting || endsWithinExisting || containsExisting;
    });

    if (overlappingSchedules.length > 0) {
      toast.error("Ca làm việc mới chồng chéo với ca làm việc đã tồn tại. Vui lòng chọn thời gian khác.")
      return
    }

    setIsLoading(true)
    try {
      const data = {
        doctor_id: userId,
        weekday: weekday,
        start_time: startTime,
        end_time: endTime,
        is_available: values.is_available,
      }

      if (editingAvailabilityId) {
        // Cập nhật ca làm việc hiện có
        await appointmentService.updateDoctorAvailability(editingAvailabilityId, data)
        toast.success("Cập nhật ca làm việc thành công!")
        setEditingAvailabilityId(null); // Reset ID đang chỉnh sửa
      } else {
        // Tạo ca làm việc mới
        await appointmentService.createDoctorAvailability(data)
        toast.success("Tạo lịch làm việc thành công!")
      }

      const dialog = document.getElementById("add-schedule-dialog");
      if (dialog) dialog.classList.add("hidden");
      availabilityForm.reset()
      fetchAvailabilities()
    } catch (error: any) {
      console.error("Error creating/updating availability:", error)
      const errorMessage = error.response?.data?.detail || "Không thể tạo/cập nhật lịch làm việc. Vui lòng thử lại sau."
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  // Xử lý chỉnh sửa ca làm việc
  const handleEditAvailability = (schedule: DoctorAvailability) => {
    // Cập nhật form với dữ liệu của ca làm việc cần chỉnh sửa
    availabilityForm.reset({
      weekday: schedule.weekday.toString(),
      start_time: schedule.start_time,
      end_time: schedule.end_time,
      is_available: schedule.is_available,
    });

    // Lưu ID của ca làm việc đang chỉnh sửa
    setEditingAvailabilityId(schedule.id);

    // Cập nhật tiêu đề dialog
    const dialogTitle = document.querySelector("#add-schedule-dialog h3");
    if (dialogTitle) {
      dialogTitle.textContent = "Chỉnh sửa ca làm việc";
    }

    // Hiển thị dialog
    const dialog = document.getElementById("add-schedule-dialog");
    if (dialog) dialog.classList.remove("hidden");
  }

  // Xử lý xóa ca làm việc
  const handleDeleteAvailability = async (id: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa ca làm việc này không?")) {
      return;
    }

    setIsLoading(true);
    try {
      await appointmentService.deleteDoctorAvailability(id);
      toast.success("Xóa ca làm việc thành công!");

      // Làm mới danh sách lịch làm việc
      fetchAvailabilities();
    } catch (error) {
      console.error("Error deleting availability:", error);
      toast.error("Không thể xóa ca làm việc. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  }

  // Xử lý tạo khung giờ từ lịch làm việc
  const handleGenerateTimeSlots = async (values: z.infer<typeof timeSlotFormSchema>) => {
    if (!userId) {
      toast.error("Không tìm thấy thông tin bác sĩ. Vui lòng đăng nhập lại.")
      return
    }

    if (availabilities.length === 0) {
      toast.error("Bạn cần tạo lịch làm việc trước khi tạo khung giờ.")
      return
    }

    setIsLoading(true)
    try {
      const data = {
        doctor_id: userId,
        start_date: format(values.start_date, "yyyy-MM-dd"),
        end_date: format(values.end_date, "yyyy-MM-dd"),
        slot_duration: parseInt(values.slot_duration),
      }

      console.log("Generating time slots with data:", data);

      // Gọi API để tạo khung giờ
      await appointmentService.generateTimeSlots(data)
      toast.success("Tạo khung giờ thành công!")

      // Làm mới danh sách khung giờ
      fetchTimeSlots()

      // Reset form
      timeSlotForm.reset({
        start_date: new Date(),
        end_date: addDays(new Date(), 7),
        slot_duration: "30",
      })
    } catch (error) {
      console.error("Error generating time slots:", error)
      toast.error("Không thể tạo khung giờ. Vui lòng thử lại sau.")
    } finally {
      setIsLoading(false)
    }
  }

  // Xử lý tạo khung giờ cho ngày cụ thể
  const handleGenerateSpecificDateTimeSlots = async (values: z.infer<typeof specificDateFormSchema>) => {
    if (!userId) {
      toast.error("Không tìm thấy thông tin bác sĩ. Vui lòng đăng nhập lại.")
      return
    }

    setIsLoading(true)
    try {
      const specificDates = [
        {
          date: format(values.date, "yyyy-MM-dd"),
          start_time: values.start_time,
          end_time: values.end_time
        }
      ]

      const data = {
        doctor_id: userId,
        slot_duration: parseInt(values.slot_duration),
        specific_dates: specificDates
      }

      console.log("Generating specific date time slots with data:", data);

      // Gọi API để tạo khung giờ
      await appointmentService.generateTimeSlots(data)
      toast.success("Tạo khung giờ cho ngày cụ thể thành công!")

      // Làm mới danh sách khung giờ
      fetchTimeSlots()

      // Reset form
      specificDateForm.reset({
        date: new Date(),
        start_time: "08:00",
        end_time: "17:00",
        slot_duration: "30",
      })
    } catch (error) {
      console.error("Error generating specific date time slots:", error)
      toast.error("Không thể tạo khung giờ. Vui lòng thử lại sau.")
    } finally {
      setIsLoading(false)
    }
  }

  // Chuyển đổi dữ liệu lịch làm việc cho bảng
  const availabilityColumns = [
    {
      key: "weekday_name",
      header: "Ngày trong tuần",
      cell: (item: any) => <div>{item.weekday_name}</div>,
    },
    {
      key: "start_time",
      header: "Giờ bắt đầu",
      cell: (item: any) => {
        return <div>{item.start_time.substring(0, 5)}</div>
      },
    },
    {
      key: "end_time",
      header: "Giờ kết thúc",
      cell: (item: any) => {
        return <div>{item.end_time.substring(0, 5)}</div>
      },
    },
    {
      key: "is_available",
      header: "Trạng thái",
      cell: (item: any) => {
        return (
          <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            item.is_available ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          }`}>
            {item.is_available ? "Có làm việc" : "Không làm việc"}
          </div>
        )
      },
    },
  ]

  // Chuyển đổi dữ liệu khung giờ cho bảng
  const timeSlotColumns = [
    {
      key: "date",
      header: "Ngày",
      cell: (item: any) => {
        return <div>{format(new Date(item.date), "dd/MM/yyyy")}</div>
      },
    },
    {
      key: "start_time",
      header: "Giờ bắt đầu",
      cell: (item: any) => {
        return <div>{item.start_time.substring(0, 5)}</div>
      },
    },
    {
      key: "end_time",
      header: "Giờ kết thúc",
      cell: (item: any) => {
        return <div>{item.end_time.substring(0, 5)}</div>
      },
    },
    {
      key: "is_available",
      header: "Trạng thái",
      cell: (item: any) => {
        return (
          <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            item.is_available ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"
          }`}>
            {item.is_available ? "Còn trống" : "Đã đặt"}
          </div>
        )
      },
    },
  ]

  // Lọc khung giờ theo ngày đã chọn
  const filteredTimeSlots = selectedDate
    ? timeSlots.filter(slot => {
        const slotDate = new Date(slot.date)
        return (
          slotDate.getDate() === selectedDate.getDate() &&
          slotDate.getMonth() === selectedDate.getMonth() &&
          slotDate.getFullYear() === selectedDate.getFullYear()
        )
      })
    : timeSlots

  // Tạo dữ liệu sự kiện cho lịch
  const calendarEvents = timeSlots.map(slot => ({
    id: slot.id,
    title: `${slot.start_time.substring(0, 5)} - ${slot.end_time.substring(0, 5)}`,
    date: new Date(slot.date),
    status: slot.is_available ? "available" : "booked",
  }))

  return (
    <div className="space-y-6">
      <PageHeader title="Quản lý lịch hẹn" description="Tạo và quản lý lịch làm việc, khung giờ và lịch hẹn">
        <Button variant="outline" size="sm" className="h-9" onClick={() => fetchAvailabilities()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Làm mới
        </Button>
      </PageHeader>

      <div className="mb-6 rounded-lg border border-blue-100 bg-blue-50 p-4">
        <h3 className="mb-2 text-lg font-medium text-blue-800">Hướng dẫn tạo lịch làm việc</h3>
        <ol className="ml-6 list-decimal space-y-1 text-blue-700">
          <li><strong>Bước 1:</strong> Tạo ca làm việc cho các ngày trong tuần (ví dụ: Thứ 2 từ 8:00-12:00)</li>
          <li><strong>Bước 2:</strong> Chuyển sang tab "Khung giờ" và tạo các khung giờ khám bệnh từ ca làm việc</li>
          <li><strong>Bước 3:</strong> Xem và quản lý các lịch hẹn tại tab "Lịch hẹn"</li>
        </ol>
        <p className="mt-2 text-sm text-blue-600">Lưu ý: Bạn cần tạo ca làm việc trước khi có thể tạo khung giờ khám bệnh.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="schedule">Lịch làm việc</TabsTrigger>
          <TabsTrigger value="timeslots">Khung giờ</TabsTrigger>
          <TabsTrigger value="appointments">Lịch hẹn</TabsTrigger>
        </TabsList>

        {/* Tab Lịch làm việc */}
        <TabsContent value="schedule" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Form tạo lịch làm việc */}
            <Card>
              <CardHeader>
                <CardTitle>Lịch làm việc hàng tuần</CardTitle>
                <CardDescription>Thiết lập thời gian làm việc của bạn cho từng ngày trong tuần</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Bảng lịch làm việc theo ngày */}
                  <div className="grid gap-4">
                    {[
                      { id: 0, name: "Thứ Hai" },
                      { id: 1, name: "Thứ Ba" },
                      { id: 2, name: "Thứ Tư" },
                      { id: 3, name: "Thứ Năm" },
                      { id: 4, name: "Thứ Sáu" },
                      { id: 5, name: "Thứ Bảy" },
                      { id: 6, name: "Chủ Nhật" },
                    ].map((day) => {
                      // Tìm lịch làm việc hiện tại của ngày này (nếu có)
                      const dayAvailabilities = safeAvailabilities.filter(
                        (a) => a.weekday === day.id
                      );

                      return (
                        <div key={day.id} className="rounded-lg border p-4 bg-white shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-2">
                              <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                                {day.id + 1}
                              </div>
                              <div>
                                <div className="font-medium text-lg">{day.name}</div>
                                {dayAvailabilities.length > 0 && dayAvailabilities.some(a => a.is_available) ? (
                                  <div className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full inline-block mt-1">
                                    Có làm việc
                                  </div>
                                ) : (
                                  <div className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full inline-block mt-1">
                                    Không làm việc
                                  </div>
                                )}
                              </div>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              className="bg-primary/5 hover:bg-primary/10 border-primary/20"
                              onClick={() => {
                                // Reset form với giá trị mặc định cho ngày được chọn
                                availabilityForm.reset({
                                  weekday: day.id.toString(),
                                  start_time: "",
                                  end_time: "",
                                  is_available: true,
                                });

                                // Reset ID đang chỉnh sửa
                                setEditingAvailabilityId(null);

                                // Cập nhật tiêu đề dialog
                                const dialogTitle = document.querySelector("#add-schedule-dialog h3");
                                if (dialogTitle) {
                                  dialogTitle.textContent = "Thêm ca làm việc mới";
                                }

                                // Hiển thị dialog
                                const dialog = document.getElementById("add-schedule-dialog");
                                if (dialog) dialog.classList.remove("hidden");
                              }}
                            >
                              <Plus className="h-4 w-4 mr-1" />
                              Thêm ca
                            </Button>
                          </div>

                          {dayAvailabilities.length > 0 ? (
                            <div className="space-y-2">
                              {dayAvailabilities
                                // Sắp xếp theo thời gian bắt đầu
                                .sort((a, b) => a.start_time.localeCompare(b.start_time))
                                .map((schedule) => (
                                <div
                                  key={schedule.id}
                                  className={`flex items-center justify-between p-2 rounded mb-2 ${schedule.is_available ? 'bg-blue-50 border border-blue-100 hover:bg-blue-100' : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'} transition-colors`}
                                >
                                  <div className="flex items-center space-x-2">
                                    <Clock className="h-4 w-4 text-gray-500" />
                                    <span className="font-medium">
                                      {schedule.start_time.substring(0, 5)} - {schedule.end_time.substring(0, 5)}
                                    </span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <div className={`text-xs px-2 py-1 rounded-full ${schedule.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                      {schedule.is_available ? "Có làm việc" : "Không làm việc"}
                                    </div>
                                    <Button
                                      variant="ghost"
                                      size="icon"
                                      className="h-6 w-6 text-blue-600 hover:text-blue-800 hover:bg-blue-100"
                                      onClick={() => handleEditAvailability(schedule)}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                      </svg>
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="icon"
                                      className="h-6 w-6 text-red-600 hover:text-red-800 hover:bg-red-100"
                                      onClick={() => handleDeleteAvailability(schedule.id)}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                      </svg>
                                    </Button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-8 border border-dashed rounded-md bg-gray-50">
                              <Clock className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                              <p className="text-gray-500">Chưa có lịch làm việc</p>
                              <p className="text-xs text-gray-400 mt-1">Nhấn "Thêm ca" để tạo lịch làm việc</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Dialog thêm lịch làm việc */}
                <div id="add-schedule-dialog" className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
                  <div className="relative bg-white rounded-lg shadow-lg w-full max-w-md mx-auto p-6">
                    <div className="flex items-center justify-between mb-4 border-b pb-3">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <CalendarDays className="mr-2 h-5 w-5 text-primary" />
                        Thêm ca làm việc mới
                      </h3>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={() => {
                          const dialog = document.getElementById("add-schedule-dialog");
                          if (dialog) dialog.classList.add("hidden");
                        }}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <span className="sr-only">Close</span>
                      </Button>
                    </div>

                    <div className="bg-blue-50 p-3 rounded-md border border-blue-100 mb-4">
                      <p className="text-sm text-blue-800 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <span>
                          <strong>Hướng dẫn:</strong> Tạo ca làm việc cho ngày trong tuần. Sau khi tạo ca làm việc, bạn có thể tạo các khung giờ khám bệnh từ tab "Khung giờ".
                        </span>
                      </p>
                    </div>

                    <div className="bg-blue-50 p-3 rounded-md border border-blue-100 mb-4">
                      <p className="text-sm text-blue-800 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <span>
                          <strong>Hướng dẫn:</strong> Tạo ca làm việc cho ngày trong tuần. Sau khi tạo ca làm việc, bạn có thể tạo các khung giờ khám bệnh từ tab "Khung giờ".
                        </span>
                      </p>
                    </div>

                    <Form {...availabilityForm}>
                      <form onSubmit={availabilityForm.handleSubmit(handleCreateAvailability)} className="space-y-5">
                        <div className="bg-blue-50 p-3 rounded-md border border-blue-100 mb-4">
                          <p className="text-sm text-blue-800 flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                            Thêm ca làm việc cho ngày đã chọn
                          </p>
                        </div>

                        <FormField
                          control={availabilityForm.control}
                          name="weekday"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-sm font-medium">Ngày trong tuần</FormLabel>
                              <Select onValueChange={field.onChange} value={field.value}>
                                <FormControl>
                                  <SelectTrigger className="bg-gray-50 border-gray-200">
                                    <SelectValue placeholder="Chọn ngày trong tuần" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  <SelectItem value="0">Thứ Hai</SelectItem>
                                  <SelectItem value="1">Thứ Ba</SelectItem>
                                  <SelectItem value="2">Thứ Tư</SelectItem>
                                  <SelectItem value="3">Thứ Năm</SelectItem>
                                  <SelectItem value="4">Thứ Sáu</SelectItem>
                                  <SelectItem value="5">Thứ Bảy</SelectItem>
                                  <SelectItem value="6">Chủ Nhật</SelectItem>
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <div className="grid grid-cols-2 gap-4">
                          <FormField
                            control={availabilityForm.control}
                            name="start_time"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-sm font-medium">Giờ bắt đầu</FormLabel>
                                <div className="relative">
                                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                                  <FormControl>
                                    <Input type="time" className="pl-10 bg-gray-50 border-gray-200" {...field} />
                                  </FormControl>
                                </div>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={availabilityForm.control}
                            name="end_time"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-sm font-medium">Giờ kết thúc</FormLabel>
                                <div className="relative">
                                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                                  <FormControl>
                                    <Input type="time" className="pl-10 bg-gray-50 border-gray-200" {...field} />
                                  </FormControl>
                                </div>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>

                        <FormField
                          control={availabilityForm.control}
                          name="is_available"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 bg-gray-50">
                              <FormControl>
                                <Checkbox
                                  checked={field.value}
                                  onCheckedChange={field.onChange}
                                  className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                                />
                              </FormControl>
                              <div className="space-y-1 leading-none">
                                <FormLabel className="text-sm font-medium">Có làm việc</FormLabel>
                                <FormDescription className="text-xs">
                                  Chọn nếu bạn làm việc vào ca này
                                </FormDescription>
                              </div>
                            </FormItem>
                          )}
                        />

                        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                              const dialog = document.getElementById("add-schedule-dialog");
                              if (dialog) dialog.classList.add("hidden");
                            }}
                            className="px-4"
                          >
                            Hủy
                          </Button>
                          <Button
                            type="submit"
                            disabled={isLoading}
                            className="px-4 bg-primary hover:bg-primary/90"
                          >
                            {isLoading ? (
                              <>
                                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Đang xử lý...
                              </>
                            ) : (
                              <>
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Lưu lịch làm việc
                              </>
                            )}
                          </Button>
                        </div>
                      </form>
                    </Form>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Hướng dẫn tạo khung giờ */}
            <Card>
              <CardHeader>
                <CardTitle>Quy trình làm việc chuyên nghiệp</CardTitle>
                <CardDescription>Hướng dẫn quản lý lịch làm việc và lịch hẹn</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <AlertTitle>Quy trình quản lý lịch hẹn chuyên nghiệp</AlertTitle>
                  <AlertDescription className="space-y-2">
                    <p>1. Thiết lập lịch làm việc cố định hàng tuần</p>
                    <p>2. Tạo các khung giờ khám bệnh từ lịch làm việc</p>
                    <p>3. Quản lý và xác nhận các lịch hẹn từ bệnh nhân</p>
                    <p>4. Thực hiện khám bệnh và cập nhật trạng thái lịch hẹn</p>
                  </AlertDescription>
                </Alert>

                <div className="rounded-lg border p-4 bg-blue-50">
                  <h3 className="font-medium mb-2 text-blue-800">Bước 1: Thiết lập lịch làm việc</h3>
                  <ol className="list-decimal pl-5 space-y-1 text-blue-700">
                    <li>Chọn ngày trong tuần bạn muốn làm việc</li>
                    <li>Nhấn nút "Thêm ca" để mở form tạo ca làm việc</li>
                    <li>Nhập giờ bắt đầu và giờ kết thúc ca làm việc</li>
                    <li>Lưu lại lịch làm việc - đây là lịch cố định hàng tuần</li>
                  </ol>
                </div>

                <div className="rounded-lg border p-4 bg-green-50">
                  <h3 className="font-medium mb-2 text-green-800">Bước 2: Tạo khung giờ khám bệnh</h3>
                  <ol className="list-decimal pl-5 space-y-1 text-green-700">
                    <li>Chuyển sang tab "Khung giờ"</li>
                    <li>Chọn khoảng thời gian muốn tạo khung giờ (ví dụ: 2 tuần tới)</li>
                    <li>Chọn thời lượng mỗi ca khám (30 phút là thông dụng)</li>
                    <li>Nhấn "Tạo khung giờ" để hệ thống tự động tạo các khung giờ</li>
                    <li>Hệ thống sẽ tạo các khung giờ dựa trên lịch làm việc đã thiết lập</li>
                  </ol>
                </div>

                <div className="rounded-lg border p-4 bg-purple-50">
                  <h3 className="font-medium mb-2 text-purple-800">Bước 3: Quản lý lịch hẹn</h3>
                  <ol className="list-decimal pl-5 space-y-1 text-purple-700">
                    <li>Chuyển sang tab "Lịch hẹn" để xem các lịch hẹn từ bệnh nhân</li>
                    <li>Xác nhận hoặc từ chối các lịch hẹn mới</li>
                    <li>Khi hoàn thành khám bệnh, cập nhật trạng thái lịch hẹn thành "Hoàn thành"</li>
                    <li>Nhấn nút "Khám bệnh" để chuyển đến trang khám bệnh và ghi chép hồ sơ y tế</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab Khung giờ */}
        <TabsContent value="timeslots" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Form tạo khung giờ */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Tạo khung giờ khám bệnh</CardTitle>
                  <CardDescription>Tạo các khung giờ khám bệnh từ lịch làm việc đã thiết lập</CardDescription>
                </div>
                <div className="rounded-full bg-blue-100 p-2">
                  <CalendarDays className="h-5 w-5 text-blue-600" />
                </div>
              </CardHeader>
              <CardContent>
                {safeAvailabilities.length === 0 ? (
                  <Alert className="bg-amber-50 border-amber-200">
                    <AlertTitle className="text-amber-800 flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Chưa có lịch làm việc
                    </AlertTitle>
                    <AlertDescription className="text-amber-700 pl-7">
                      <p className="mb-2"><strong>Bước 1:</strong> Bạn cần thiết lập lịch làm việc trước khi tạo khung giờ khám bệnh.</p>
                      <div className="flex justify-center mt-4">
                        <Button
                          variant="outline"
                          className="bg-amber-100 border-amber-300 text-amber-800 hover:bg-amber-200"
                          onClick={() => setActiveTab("schedule")}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.707-10.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L9.414 11H13a1 1 0 100-2H9.414l1.293-1.293z" clipRule="evenodd" />
                          </svg>
                          Chuyển đến tab Lịch làm việc
                        </Button>
                      </div>
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="space-y-6">
                    <div className="bg-blue-50 p-5 rounded-lg border border-blue-100 mb-6">
                      <h3 className="text-blue-800 font-medium mb-3 flex items-center text-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        Tạo khung giờ khám bệnh từ lịch làm việc
                      </h3>
                      <div className="text-blue-700 text-sm pl-8 space-y-2">
                        <p className="font-medium">Quy trình tạo khung giờ:</p>
                        <p>1. Hệ thống sẽ tạo các khung giờ dựa trên <strong>lịch làm việc hàng tuần</strong> bạn đã thiết lập ở tab "Lịch làm việc"</p>
                        <p>2. Ví dụ: Nếu bạn đã thiết lập làm việc vào Thứ 2 từ 8:00-12:00, hệ thống sẽ tạo các khung giờ 30 phút (8:00-8:30, 8:30-9:00, v.v.) cho tất cả các ngày Thứ 2 trong khoảng thời gian bạn chọn</p>
                        <p>3. Bạn cần chọn <strong>khoảng thời gian</strong> muốn tạo khung giờ (từ ngày nào đến ngày nào)</p>
                        <p>4. Chọn <strong>thời lượng</strong> cho mỗi ca khám (30 phút là thông dụng)</p>
                        <p>5. Nhấn "Tạo khung giờ khám bệnh" để hệ thống tự động tạo các khung giờ</p>
                        <p className="mt-4 pt-2 border-t border-blue-200"><strong>Tính năng mới:</strong> Bạn cũng có thể tạo khung giờ cho ngày cụ thể bằng cách gọi API <code>/api/doctor-availabilities/generate_time_slots/</code> với tham số <code>specific_dates</code>. Điều này cho phép tạo khung giờ cho các ngày đặc biệt không nằm trong lịch làm việc thường.</p>
                      </div>
                    </div>

                    {/* Hiển thị lịch làm việc hiện tại */}
                    <div className="bg-white p-4 rounded-lg border mb-6">
                      <h3 className="text-lg font-medium mb-3 flex items-center">
                        <CalendarDays className="mr-2 h-5 w-5 text-primary" />
                        Lịch làm việc hiện tại của bạn
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {[0, 1, 2, 3, 4, 5, 6].map(dayIndex => {
                          const dayName = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][dayIndex];
                          const daySchedules = safeAvailabilities.filter(a => parseInt(a.weekday.toString()) === dayIndex);

                          return (
                            <div key={dayIndex} className="border rounded p-3 bg-gray-50">
                              <div className="font-medium mb-2">{dayName}</div>
                              {daySchedules.length > 0 ? (
                                <div className="space-y-1">
                                  {daySchedules
                                    .sort((a, b) => a.start_time.localeCompare(b.start_time))
                                    .map(schedule => (
                                      <div key={schedule.id} className="text-sm flex items-center">
                                        <Clock className="h-3 w-3 mr-1 text-gray-500" />
                                        <span>{schedule.start_time.substring(0, 5)} - {schedule.end_time.substring(0, 5)}</span>
                                        {schedule.is_available && (
                                          <span className="ml-2 text-xs px-1.5 py-0.5 bg-green-100 text-green-800 rounded-full">Có làm việc</span>
                                        )}
                                      </div>
                                    ))
                                  }
                                </div>
                              ) : (
                                <div className="text-sm text-gray-500 italic">Không có lịch làm việc</div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-4 text-sm text-center text-blue-600">
                        <Button
                          variant="link"
                          className="p-0 h-auto"
                          onClick={() => setActiveTab("schedule")}
                        >
                          Chỉnh sửa lịch làm việc
                        </Button>
                      </div>
                    </div>

                    <Form {...timeSlotForm}>
                      <form onSubmit={timeSlotForm.handleSubmit(handleGenerateTimeSlots)} className="space-y-5">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                          <FormField
                            control={timeSlotForm.control}
                            name="start_date"
                            render={({ field }) => (
                              <FormItem className="flex flex-col">
                                <FormLabel className="text-base font-medium mb-1.5">Ngày bắt đầu</FormLabel>
                                <Popover>
                                  <PopoverTrigger asChild>
                                    <FormControl>
                                      <Button
                                        variant={"outline"}
                                        className={cn(
                                          "w-full pl-3 text-left font-normal border-gray-300 hover:bg-gray-50",
                                          !field.value && "text-muted-foreground"
                                        )}
                                      >
                                        {field.value ? (
                                          format(field.value, "dd/MM/yyyy")
                                        ) : (
                                          <span>Chọn ngày bắt đầu</span>
                                        )}
                                        <CalendarDays className="ml-auto h-4 w-4 opacity-50" />
                                      </Button>
                                    </FormControl>
                                  </PopoverTrigger>
                                  <PopoverContent className="w-auto p-0" align="start">
                                    <Calendar
                                      mode="single"
                                      selected={field.value}
                                      onSelect={field.onChange}
                                      disabled={(date) => date < new Date()}
                                      initialFocus
                                    />
                                  </PopoverContent>
                                </Popover>
                                <FormDescription className="text-xs">
                                  Ngày bắt đầu tạo khung giờ (thường là ngày hôm nay)
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={timeSlotForm.control}
                            name="end_date"
                            render={({ field }) => (
                              <FormItem className="flex flex-col">
                                <FormLabel className="text-base font-medium mb-1.5">Ngày kết thúc</FormLabel>
                                <Popover>
                                  <PopoverTrigger asChild>
                                    <FormControl>
                                      <Button
                                        variant={"outline"}
                                        className={cn(
                                          "w-full pl-3 text-left font-normal border-gray-300 hover:bg-gray-50",
                                          !field.value && "text-muted-foreground"
                                        )}
                                      >
                                        {field.value ? (
                                          format(field.value, "dd/MM/yyyy")
                                        ) : (
                                          <span>Chọn ngày kết thúc</span>
                                        )}
                                        <CalendarDays className="ml-auto h-4 w-4 opacity-50" />
                                      </Button>
                                    </FormControl>
                                  </PopoverTrigger>
                                  <PopoverContent className="w-auto p-0" align="start">
                                    <Calendar
                                      mode="single"
                                      selected={field.value}
                                      onSelect={field.onChange}
                                      disabled={(date) => {
                                        const startDate = timeSlotForm.getValues("start_date")
                                        return date < startDate || date > addDays(startDate, 90)
                                      }}
                                      initialFocus
                                    />
                                  </PopoverContent>
                                </Popover>
                                <FormDescription className="text-xs">
                                  Ngày kết thúc tạo khung giờ (nên chọn 2-4 tuần tới)
                                </FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>

                        <FormField
                          control={timeSlotForm.control}
                          name="slot_duration"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-base font-medium mb-1.5">Thời lượng mỗi ca khám</FormLabel>
                              <div className="grid grid-cols-4 gap-3 mt-1">
                                {["15", "30", "45", "60"].map((duration) => (
                                  <div key={duration} className={`border rounded-md p-3 text-center cursor-pointer transition-colors ${field.value === duration ? 'bg-primary/10 border-primary' : 'hover:bg-gray-50'}`} onClick={() => field.onChange(duration)}>
                                    <div className="font-medium">{duration}</div>
                                    <div className="text-xs text-muted-foreground">phút</div>
                                  </div>
                                ))}
                              </div>
                              <FormDescription className="text-xs mt-2">
                                Thời lượng mỗi ca khám (30 phút là thông dụng cho hầu hết các ca khám)
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <Button type="submit" className="w-full mt-6 py-6 text-base" disabled={isLoading}>
                          {isLoading ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Đang tạo khung giờ khám bệnh...
                            </>
                          ) : (
                            <>
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
                              </svg>
                              Tạo khung giờ khám bệnh
                            </>
                          )}
                        </Button>
                      </form>
                    </Form>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Lịch khung giờ */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Lịch khung giờ khám bệnh</CardTitle>
                  <CardDescription>Xem tổng quan các khung giờ đã tạo theo lịch</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={() => fetchTimeSlots()}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Làm mới
                </Button>
              </CardHeader>
              <CardContent>
                <DashboardCalendar
                  title=""
                  events={calendarEvents}
                  onDateSelect={(date) => setSelectedDate(date)}
                />

                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-sm">Còn trống</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span className="text-sm">Đã đặt</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Bảng khung giờ */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Danh sách khung giờ chi tiết</CardTitle>
                <CardDescription>
                  {selectedDate
                    ? `Khung giờ ngày ${format(selectedDate, "dd/MM/yyyy")}`
                    : "Tất cả khung giờ khám bệnh"}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Tìm kiếm..."
                  className="max-w-[180px]"
                  onChange={(e) => setSearchQuery(e.target.value)}
                  value={searchQuery}
                />
                {selectedDate && (
                  <Button variant="ghost" size="sm" onClick={() => setSelectedDate(null)}>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Xóa bộ lọc
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {timeSlots.length === 0 ? (
                <Alert className="bg-amber-50 border-amber-200">
                  <AlertTitle className="text-amber-800 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Chưa có khung giờ khám bệnh
                  </AlertTitle>
                  <AlertDescription className="text-amber-700 pl-7">
                    Bước 2: Bạn cần tạo khung giờ khám bệnh. Vui lòng sử dụng form tạo khung giờ ở bên trái.
                  </AlertDescription>
                </Alert>
              ) : filteredTimeSlots.length === 0 ? (
                <Alert className="bg-blue-50 border-blue-200">
                  <AlertTitle className="text-blue-800">
                    Không tìm thấy khung giờ nào
                  </AlertTitle>
                  <AlertDescription className="text-blue-700">
                    Không có khung giờ nào phù hợp với bộ lọc hiện tại. Vui lòng thử lại với bộ lọc khác.
                  </AlertDescription>
                </Alert>
              ) : (
                <div>
                  <div className="rounded-md border overflow-hidden">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="h-10 px-4 text-left align-middle font-medium">Ngày</th>
                          <th className="h-10 px-4 text-left align-middle font-medium">Giờ bắt đầu</th>
                          <th className="h-10 px-4 text-left align-middle font-medium">Giờ kết thúc</th>
                          <th className="h-10 px-4 text-left align-middle font-medium">Trạng thái</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredTimeSlots.map((slot) => (
                          <tr key={slot.id} className="border-b transition-colors hover:bg-muted/25">
                            <td className="p-4 align-middle">{format(new Date(slot.date), "dd/MM/yyyy")}</td>
                            <td className="p-4 align-middle">{slot.start_time.substring(0, 5)}</td>
                            <td className="p-4 align-middle">{slot.end_time.substring(0, 5)}</td>
                            <td className="p-4 align-middle">
                              <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                slot.is_available ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"
                              }`}>
                                {slot.is_available ? "Còn trống" : "Đã đặt"}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-4 text-sm text-muted-foreground text-center">
                    Hiển thị {filteredTimeSlots.length} khung giờ {selectedDate ? `cho ngày ${format(selectedDate, "dd/MM/yyyy")}` : ""}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Lịch hẹn */}
        <TabsContent value="appointments" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Lịch hẹn của bạn</CardTitle>
                <CardDescription>Danh sách các cuộc hẹn với bệnh nhân</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={fetchAppointments}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Làm mới
              </Button>
            </CardHeader>
            <CardContent>
              {appointments.length === 0 ? (
                <Alert>
                  <AlertTitle>Chưa có lịch hẹn</AlertTitle>
                  <AlertDescription>
                    Bạn chưa có lịch hẹn nào. Lịch hẹn sẽ được tạo khi bệnh nhân đặt lịch khám với bạn.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-4">
                  {/* Bộ lọc và tìm kiếm */}
                  <div className="flex flex-col sm:flex-row gap-4 mb-6">
                    <div className="relative flex-1">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="search"
                        placeholder="Tìm kiếm theo tên bệnh nhân..."
                        className="pl-8"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    <Select
                      defaultValue="all"
                      value={statusFilter}
                      onValueChange={setStatusFilter}
                    >
                      <SelectTrigger className="w-full sm:w-[180px]">
                        <SelectValue placeholder="Trạng thái" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Tất cả trạng thái</SelectItem>
                        <SelectItem value="PENDING">Chờ xác nhận</SelectItem>
                        <SelectItem value="CONFIRMED">Xác nhận</SelectItem>
                        <SelectItem value="COMPLETED">Hoàn thành</SelectItem>
                        <SelectItem value="CANCELLED">Hủy</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Danh sách lịch hẹn */}
                  <div className="space-y-4">
                    {appointments
                      .filter(appointment => {
                        // Lọc theo trạng thái
                        if (statusFilter !== "all" && appointment.status !== statusFilter) {
                          return false;
                        }

                        // Lọc theo tìm kiếm
                        if (searchQuery && !`${appointment.patient.first_name} ${appointment.patient.last_name}`
                          .toLowerCase()
                          .includes(searchQuery.toLowerCase())
                        ) {
                          return false;
                        }

                        return true;
                      })
                      .map((appointment) => (
                      <div
                        key={appointment.id}
                        className="flex flex-col rounded-lg border p-4 md:flex-row md:items-center md:justify-between"
                      >
                        <div className="flex items-start gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                            <CalendarDays className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{appointment.patient.first_name} {appointment.patient.last_name}</h4>
                              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                                {appointment.status === 'PENDING' && 'Chờ xác nhận'}
                                {appointment.status === 'CONFIRMED' && 'Xác nhận'}
                                {appointment.status === 'COMPLETED' && 'Hoàn thành'}
                                {appointment.status === 'CANCELLED' && 'Hủy'}
                              </span>
                            </div>
                            <p className="text-sm">{appointment.reason}</p>
                            <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                              <Clock className="h-3.5 w-3.5" />
                              <span>
                                {format(new Date(appointment.appointment_date), "dd/MM/yyyy")} ({appointment.start_time.substring(0, 5)} - {appointment.end_time.substring(0, 5)})
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 flex items-center gap-2 md:mt-0">
                          {appointment.status === 'PENDING' && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                className="gap-1"
                                onClick={() => handleUpdateAppointmentStatus(appointment.id, 'CONFIRMED')}
                              >
                                Xác nhận
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="gap-1 text-red-500 border-red-200 hover:bg-red-50"
                                onClick={() => handleUpdateAppointmentStatus(appointment.id, 'CANCELLED')}
                              >
                                Từ chối
                              </Button>
                            </>
                          )}
                          {appointment.status === 'CONFIRMED' && (
                            <Button
                              variant="default"
                              size="sm"
                              onClick={() => handleUpdateAppointmentStatus(appointment.id, 'COMPLETED')}
                            >
                              Hoàn thành
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-1"
                            onClick={() => router.push(`/dashboard/doctor/examination?appointment=${appointment.id}`)}
                          >
                            <FileText className="h-3.5 w-3.5" />
                            Khám bệnh
                          </Button>
                        </div>
                      </div>
                    ))}
                    {appointments.length > 0 &&
                      appointments.filter(appointment => {
                        if (statusFilter !== "all" && appointment.status !== statusFilter) {
                          return false;
                        }
                        if (searchQuery && !`${appointment.patient.first_name} ${appointment.patient.last_name}`
                          .toLowerCase()
                          .includes(searchQuery.toLowerCase())
                        ) {
                          return false;
                        }
                        return true;
                      }).length === 0 && (
                        <Alert>
                          <AlertTitle>Không tìm thấy lịch hẹn</AlertTitle>
                          <AlertDescription>
                            Không có lịch hẹn nào phù hợp với bộ lọc hiện tại.
                          </AlertDescription>
                        </Alert>
                      )
                    }
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
