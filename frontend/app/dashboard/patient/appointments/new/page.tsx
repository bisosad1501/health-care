"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { format, addDays, isSameDay, parseISO } from "date-fns"
import { vi } from "date-fns/locale"
import { CalendarIcon, Clock, MapPin, User, FileText, ChevronLeft, Check, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { PageHeader } from "@/components/layout/page-header"
import { PageContainer } from "@/components/layout/page-container"
import appointmentService from "@/lib/api/appointment-service"
import userService from "@/lib/api/user-service"
import { TimeSlot } from "@/lib/api/appointment-service"

// Định nghĩa interface cho bác sĩ
interface Doctor {
  id: number
  name: string
  specialty: string
  avatar?: string
}

// Định nghĩa interface cho khung giờ hiển thị
interface DisplayTimeSlot {
  id: number
  time: string
  available: boolean
  date: string
  start_time: string
  end_time: string
  doctor_id: number
}

// Định nghĩa interface cho địa điểm
interface Location {
  id: number
  name: string
  address: string
}

// Dữ liệu các địa điểm
const locations: Location[] = [
  { id: 1, name: "Phòng khám chính", address: "Tầng 1, Tòa nhà A, 123 Đường ABC, Quận 1" },
  { id: 2, name: "Phòng khám chi nhánh 1", address: "Tầng 2, Tòa nhà B, 456 Đường XYZ, Quận 2" },
  { id: 3, name: "Phòng khám chi nhánh 2", address: "Tầng 3, Tòa nhà C, 789 Đường DEF, Quận 3" },
]

export default function NewAppointmentPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [date, setDate] = useState<Date>()
  const [selectedDoctor, setSelectedDoctor] = useState<string>("")
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<string>("")
  const [selectedLocation, setSelectedLocation] = useState<string>("")
  const [reason, setReason] = useState<string>("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  // State cho dữ liệu từ API
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [timeSlots, setTimeSlots] = useState<DisplayTimeSlot[]>([])
  const [availableDates, setAvailableDates] = useState<Date[]>([])
  const [isLoading, setIsLoading] = useState({
    doctors: false,
    timeSlots: false
  })

  // Lấy danh sách bác sĩ
  const fetchDoctors = async () => {
    setIsLoading(prev => ({ ...prev, doctors: true }))
    try {
      // Gọi API lấy danh sách bác sĩ
      const response = await userService.getDoctors()
      setDoctors(response.map(doctor => ({
        id: doctor.id,
        name: doctor.full_name || `BS. ${doctor.username}`,
        specialty: doctor.specialty || 'Chưa cập nhật',
        avatar: doctor.avatar || '/placeholder.svg?height=40&width=40'
      })))
    } catch (error) {
      console.error('Error fetching doctors:', error)
      toast.error('Không thể tải danh sách bác sĩ. Vui lòng thử lại sau.')
      setDoctors([])
    } finally {
      setIsLoading(prev => ({ ...prev, doctors: false }))
    }
  }

  // Lấy các khung giờ trống của bác sĩ
  const fetchTimeSlots = async () => {
    if (!selectedDoctor || !date) return

    setIsLoading(prev => ({ ...prev, timeSlots: true }))
    try {
      const doctorId = parseInt(selectedDoctor)
      const formattedDate = format(date, 'yyyy-MM-dd')
      // Lấy khung giờ trong 7 ngày từ ngày được chọn
      const endDate = format(addDays(date, 7), 'yyyy-MM-dd')

      // Gọi API lấy các khung giờ trống
      const response = await appointmentService.getAvailableTimeSlots(doctorId, formattedDate, endDate)

      // Chuyển đổi dữ liệu API thành dạng hiển thị
      const formattedTimeSlots: DisplayTimeSlot[] = response.map(slot => ({
        id: slot.id,
        time: `${slot.start_time.substring(0, 5)} - ${slot.end_time.substring(0, 5)}`,
        available: slot.is_available,
        date: slot.date,
        start_time: slot.start_time,
        end_time: slot.end_time,
        doctor_id: slot.doctor_id
      }))

      setTimeSlots(formattedTimeSlots)

      // Tạo danh sách các ngày có khung giờ trống
      const dates = [...new Set(formattedTimeSlots.map(slot => slot.date))]
        .map(dateStr => parseISO(dateStr))
      setAvailableDates(dates)
    } catch (error) {
      console.error('Error fetching time slots:', error)
      toast.error('Không thể tải khung giờ. Vui lòng thử lại sau.')
      setTimeSlots([])
      setAvailableDates([])
    } finally {
      setIsLoading(prev => ({ ...prev, timeSlots: false }))
    }
  }

  // Gọi API khi component mount để lấy danh sách bác sĩ
  useEffect(() => {
    fetchDoctors()
  }, [])

  // Gọi API khi người dùng chọn bác sĩ và ngày
  useEffect(() => {
    if (selectedDoctor && date) {
      fetchTimeSlots()
    }
  }, [selectedDoctor, date])

  // Lọc các khung giờ theo ngày được chọn
  const getTimeSlotsForSelectedDate = () => {
    if (!date) return []
    return timeSlots.filter(slot => {
      const slotDate = parseISO(slot.date)
      return isSameDay(slotDate, date)
    })
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      // Lấy thông tin khung giờ được chọn
      const timeSlot = timeSlots.find(slot => slot.id.toString() === selectedTimeSlot)
      if (!timeSlot) throw new Error('Không tìm thấy khung giờ đã chọn')

      // Lấy ID người dùng từ localStorage
      const userJson = localStorage.getItem('user')
      if (!userJson) throw new Error('Vui lòng đăng nhập lại')

      const user = JSON.parse(userJson)
      const patientId = user.id

      // Tạo dữ liệu để gọi API
      const appointmentData = {
        patient_id: patientId,
        doctor_id: parseInt(selectedDoctor),
        appointment_date: timeSlot.date,
        start_time: timeSlot.start_time,
        end_time: timeSlot.end_time,
        reason: reason,
        location_id: parseInt(selectedLocation)
      }

      // Gọi API để tạo lịch hẹn
      await appointmentService.createAppointment(appointmentData)
      toast.success('Đặt lịch hẹn thành công!')
      router.push('/dashboard/patient/appointments')
    } catch (error: any) {
      console.error('Error creating appointment:', error)
      toast.error(error.message || 'Không thể đặt lịch hẹn. Vui lòng thử lại sau.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNext = () => {
    setStep(step + 1)
  }

  const handleBack = () => {
    setStep(step - 1)
  }

  const isStepComplete = () => {
    switch (step) {
      case 1:
        return !!date && !!selectedDoctor
      case 2:
        return !!selectedTimeSlot && !!selectedLocation
      case 3:
        return !!reason
      default:
        return false
    }
  }

  const containerVariants = {
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
        title="Đặt lịch hẹn mới"
        description="Đặt lịch hẹn khám bệnh với bác sĩ"
        actions={
          <Button variant="outline" onClick={() => router.back()}>
            <ChevronLeft className="mr-2 h-4 w-4" />
            Quay lại
          </Button>
        }
      />

      <div className="mx-auto max-w-3xl">
        {/* Stepper */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4].map((stepNumber) => (
              <div key={stepNumber} className="flex flex-1 items-center">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{
                    scale: 1,
                    opacity: 1,
                    backgroundColor: step >= stepNumber ? "var(--primary)" : "var(--muted)",
                  }}
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-full text-sm font-medium",
                    step >= stepNumber ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground",
                  )}
                >
                  {step > stepNumber ? <Check className="h-5 w-5" /> : stepNumber}
                </motion.div>
                {stepNumber < 4 && (
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{
                      scaleX: 1,
                      backgroundColor: step > stepNumber ? "var(--primary)" : "var(--border)",
                    }}
                    className={cn("h-1 flex-1", step > stepNumber ? "bg-primary" : "bg-border")}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="mt-2 flex justify-between text-sm">
            <div className={cn("text-center", step >= 1 ? "text-foreground" : "text-muted-foreground")}>
              Chọn ngày và bác sĩ
            </div>
            <div className={cn("text-center", step >= 2 ? "text-foreground" : "text-muted-foreground")}>
              Chọn giờ và địa điểm
            </div>
            <div className={cn("text-center", step >= 3 ? "text-foreground" : "text-muted-foreground")}>Lý do khám</div>
            <div className={cn("text-center", step >= 4 ? "text-foreground" : "text-muted-foreground")}>Xác nhận</div>
          </div>
        </div>

        {/* Step 1: Chọn ngày và bác sĩ */}
        {step === 1 && (
          <motion.div variants={containerVariants} initial="hidden" animate="show">
            <Card>
              <CardHeader>
                <CardTitle>Chọn ngày và bác sĩ</CardTitle>
                <CardDescription>Chọn ngày bạn muốn đặt lịch và bác sĩ bạn muốn khám</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <motion.div variants={item} className="space-y-2">
                  <Label htmlFor="date">Ngày khám</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {date ? format(date, "PPP", { locale: vi }) : "Chọn ngày"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={date}
                        onSelect={setDate}
                        initialFocus
                        disabled={(date) => {
                          // Không cho phép chọn ngày trong quá khứ hoặc quá 3 tháng từ hiện tại
                          const isPastDate = date < new Date(new Date().setHours(0, 0, 0, 0))
                          const isTooFarInFuture = date > new Date(new Date().setMonth(new Date().getMonth() + 3))

                          // Nếu đã có danh sách ngày có sẵn, chỉ cho phép chọn những ngày đó
                          if (selectedDoctor && availableDates.length > 0) {
                            const isAvailableDate = availableDates.some(availableDate =>
                              isSameDay(availableDate, date)
                            )
                            return isPastDate || isTooFarInFuture || !isAvailableDate
                          }

                          return isPastDate || isTooFarInFuture
                        }}
                        modifiers={{
                          available: availableDates
                        }}
                        modifiersClassNames={{
                          available: "bg-green-50 text-green-600 font-medium"
                        }}
                      />
                    </PopoverContent>
                  </Popover>
                </motion.div>

                <motion.div variants={item} className="space-y-2">
                  <Label htmlFor="doctor">Bác sĩ</Label>
                  {isLoading.doctors ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      <span className="ml-2 text-sm text-muted-foreground">Đang tải danh sách bác sĩ...</span>
                    </div>
                  ) : doctors.length === 0 ? (
                    <div className="rounded-md border border-dashed p-8 text-center">
                      <div className="text-sm text-muted-foreground">Không tìm thấy bác sĩ nào</div>
                      <Button variant="outline" className="mt-4" onClick={fetchDoctors}>
                        Thử lại
                      </Button>
                    </div>
                  ) : (
                    <RadioGroup value={selectedDoctor} onValueChange={setSelectedDoctor} className="space-y-3">
                      {doctors.map((doctor) => (
                        <motion.div
                          key={doctor.id}
                          whileHover={{ scale: 1.02 }}
                          className={cn(
                            "flex items-center space-x-3 rounded-md border p-4 transition-colors",
                            selectedDoctor === doctor.id.toString() && "border-primary bg-primary/5",
                          )}
                        >
                          <RadioGroupItem value={doctor.id.toString()} id={`doctor-${doctor.id}`} />
                          <Label
                            htmlFor={`doctor-${doctor.id}`}
                            className="flex flex-1 cursor-pointer items-center justify-between"
                          >
                            <div className="flex items-center space-x-3">
                              <img
                                src={doctor.avatar || "/placeholder.svg"}
                                alt={doctor.name}
                                className="h-10 w-10 rounded-full object-cover"
                              />
                              <div>
                                <div className="font-medium">{doctor.name}</div>
                                <div className="text-sm text-muted-foreground">{doctor.specialty}</div>
                              </div>
                            </div>
                          </Label>
                        </motion.div>
                      ))}
                    </RadioGroup>
                  )}
                </motion.div>
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button onClick={handleNext} disabled={!isStepComplete()}>
                  Tiếp theo
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        )}

        {/* Step 2: Chọn giờ và địa điểm */}
        {step === 2 && (
          <motion.div variants={containerVariants} initial="hidden" animate="show">
            <Card>
              <CardHeader>
                <CardTitle>Chọn giờ và địa điểm</CardTitle>
                <CardDescription>Chọn khung giờ và địa điểm bạn muốn đặt lịch</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <motion.div variants={item} className="space-y-2">
                  <Label>Khung giờ</Label>
                  {isLoading.timeSlots ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      <span className="ml-2 text-sm text-muted-foreground">Đang tải khung giờ...</span>
                    </div>
                  ) : getTimeSlotsForSelectedDate().length === 0 ? (
                    <div className="rounded-md border border-dashed p-8 text-center">
                      <div className="text-sm text-muted-foreground">
                        {selectedDoctor && date
                          ? "Không có khung giờ trống cho ngày này. Vui lòng chọn ngày khác."
                          : "Vui lòng chọn bác sĩ và ngày khám trước"}
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
                      {getTimeSlotsForSelectedDate().map((slot) => (
                        <motion.div key={slot.id} whileHover={{ scale: slot.available ? 1.05 : 1 }}>
                          <Button
                            variant="outline"
                            className={cn(
                              "w-full justify-center",
                              selectedTimeSlot === slot.id.toString() && "border-primary bg-primary/5",
                              !slot.available && "cursor-not-allowed opacity-50",
                            )}
                            disabled={!slot.available}
                            onClick={() => setSelectedTimeSlot(slot.id.toString())}
                          >
                            <Clock className="mr-2 h-4 w-4" />
                            {slot.time}
                          </Button>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </motion.div>

                <motion.div variants={item} className="space-y-2">
                  <Label htmlFor="location">Địa điểm</Label>
                  <RadioGroup value={selectedLocation} onValueChange={setSelectedLocation} className="space-y-3">
                    {locations.map((location) => (
                      <motion.div
                        key={location.id}
                        whileHover={{ scale: 1.02 }}
                        className={cn(
                          "flex items-center space-x-3 rounded-md border p-4 transition-colors",
                          selectedLocation === location.id.toString() && "border-primary bg-primary/5",
                        )}
                      >
                        <RadioGroupItem value={location.id.toString()} id={`location-${location.id}`} />
                        <Label
                          htmlFor={`location-${location.id}`}
                          className="flex flex-1 cursor-pointer items-center justify-between"
                        >
                          <div>
                            <div className="font-medium">{location.name}</div>
                            <div className="flex items-center text-sm text-muted-foreground">
                              <MapPin className="mr-1 h-3.5 w-3.5" />
                              {location.address}
                            </div>
                          </div>
                        </Label>
                      </motion.div>
                    ))}
                  </RadioGroup>
                </motion.div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  Quay lại
                </Button>
                <Button onClick={handleNext} disabled={!isStepComplete()}>
                  Tiếp theo
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        )}

        {/* Step 3: Lý do khám */}
        {step === 3 && (
          <motion.div variants={containerVariants} initial="hidden" animate="show">
            <Card>
              <CardHeader>
                <CardTitle>Lý do khám</CardTitle>
                <CardDescription>Mô tả lý do bạn muốn đặt lịch khám</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <motion.div variants={item} className="space-y-2">
                  <Label htmlFor="reason">Lý do khám</Label>
                  <Textarea
                    id="reason"
                    placeholder="Mô tả triệu chứng, lý do khám hoặc các thông tin khác bạn muốn bác sĩ biết trước"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    className="min-h-32"
                  />
                </motion.div>

                <motion.div variants={item} className="space-y-2">
                  <Label htmlFor="type">Loại khám</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Chọn loại khám" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="regular">Khám thông thường</SelectItem>
                      <SelectItem value="followup">Tái khám</SelectItem>
                      <SelectItem value="emergency">Khám khẩn cấp</SelectItem>
                      <SelectItem value="consultation">Tư vấn</SelectItem>
                    </SelectContent>
                  </Select>
                </motion.div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  Quay lại
                </Button>
                <Button onClick={handleNext} disabled={!isStepComplete()}>
                  Tiếp theo
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        )}

        {/* Step 4: Xác nhận */}
        {step === 4 && (
          <motion.div variants={containerVariants} initial="hidden" animate="show">
            <Card>
              <CardHeader>
                <CardTitle>Xác nhận thông tin</CardTitle>
                <CardDescription>Vui lòng kiểm tra lại thông tin trước khi xác nhận</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <motion.div variants={item} className="space-y-4">
                  <div className="rounded-md border p-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Ngày khám</div>
                        <div className="flex items-center mt-1">
                          <CalendarIcon className="mr-2 h-4 w-4 text-primary" />
                          <span>{date ? format(date, "PPP", { locale: vi }) : ""}</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Giờ khám</div>
                        <div className="flex items-center mt-1">
                          <Clock className="mr-2 h-4 w-4 text-primary" />
                          <span>{timeSlots.find((slot) => slot.id.toString() === selectedTimeSlot)?.time}</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Bác sĩ</div>
                        <div className="flex items-center mt-1">
                          <User className="mr-2 h-4 w-4 text-primary" />
                          <span>{doctors.find((doctor) => doctor.id.toString() === selectedDoctor)?.name}</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Địa điểm</div>
                        <div className="flex items-center mt-1">
                          <MapPin className="mr-2 h-4 w-4 text-primary" />
                          <span>{locations.find((location) => location.id.toString() === selectedLocation)?.name}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-md border p-4">
                    <div className="text-sm font-medium text-muted-foreground">Lý do khám</div>
                    <div className="mt-1 flex items-start">
                      <FileText className="mr-2 h-4 w-4 text-primary mt-0.5" />
                      <span>{reason}</span>
                    </div>
                  </div>
                </motion.div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  Quay lại
                </Button>
                <Button onClick={handleSubmit} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                      Đang xử lý...
                    </>
                  ) : (
                    "Xác nhận đặt lịch"
                  )}
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </div>
    </PageContainer>
  )
}
