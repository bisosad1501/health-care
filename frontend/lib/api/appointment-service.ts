import apiClient from "./api-client"

export interface AppointmentWithDetails {
  id: number
  patient: {
    id: number
    first_name: string
    last_name: string
    email: string
  }
  doctor: {
    id: number
    first_name: string
    last_name: string
    email: string
    specialty: string
  }
  appointment_date: string
  start_time: string
  end_time: string
  reason: string
  notes: string
  status: string
  location?: string
  created_at: string
  updated_at: string
}

export interface Appointment {
  id: number
  patient_id: number
  doctor_id: number
  time_slot?: number
  appointment_date: string
  start_time: string
  end_time: string
  reason: string
  notes: string
  status: string
  created_at: string
  updated_at: string
}

export interface DoctorAvailability {
  id: number
  doctor_id: number
  weekday: number
  start_time: string
  end_time: string
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface TimeSlot {
  id: number
  doctor_id: number
  date: string
  start_time: string
  end_time: string
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface AppointmentReminder {
  id: number
  appointment: number
  reminder_type: string
  scheduled_time: string
  message: string
  is_sent: boolean
  sent_at: string
  created_at: string
  updated_at: string
}

const AppointmentService = {
  async getAllAppointments(): Promise<AppointmentWithDetails[]> {
    const response = await apiClient.get("/api/appointments/")
    return response.data
  },

  async createAppointment(data: Partial<Appointment>): Promise<Appointment> {
    const response = await apiClient.post("/api/appointments/", data)
    return response.data
  },

  async getAppointmentById(id: number): Promise<AppointmentWithDetails> {
    const response = await apiClient.get(`/api/appointments/${id}/`)
    return response.data
  },

  async updateAppointment(id: number, data: Partial<Appointment>): Promise<Appointment> {
    const response = await apiClient.put(`/api/appointments/${id}/`, data)
    return response.data
  },

  async updateAppointmentStatus(id: number, status: string): Promise<Appointment> {
    const response = await apiClient.patch(`/api/appointments/${id}/`, { status })
    return response.data
  },

  async deleteAppointment(id: number): Promise<void> {
    await apiClient.delete(`/api/appointments/${id}/`)
  },

  async getUpcomingAppointments(): Promise<AppointmentWithDetails[]> {
    // Lưu ý: baseURL đã được sửa thành http://localhost:4000 nên cần thêm /api/ vào đầu
    const response = await apiClient.get("/api/appointments/upcoming/")
    return response.data
  },

  async getPatientAppointments(): Promise<AppointmentWithDetails[]> {
    try {
      // Sử dụng đường dẫn đã được xác định là hoạt động
      console.log("Calling appointments API");
      const response = await apiClient.get("/api/appointments/");
      console.log("Appointments API response:", response.data);

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        return response.data.results;
      }

      // Nếu không có trường results, trả về dữ liệu nguyên bản
      return response.data;
    } catch (error: any) {
      console.error("Error getting patient appointments:", error.response?.status, error.response?.data);

      // Trả về mảng rỗng để hiển thị thông báo không có cuộc hẹn
      return [];
    }
  },

  async getDoctorAppointments(doctorId: number): Promise<AppointmentWithDetails[]> {
    try {
      // Lấy danh sách lịch hẹn của bác sĩ
      const response = await apiClient.get(`/api/appointments/?doctor_id=${doctorId}`);

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        return response.data.results;
      }

      // Nếu không có trường results, trả về dữ liệu nguyên bản
      return response.data;
    } catch (error: any) {
      console.error("Error getting doctor appointments:", error.response?.status, error.response?.data);

      // Trả về mảng rỗng để hiển thị thông báo không có cuộc hẹn
      return [];
    }
  },

  // Doctor availabilities
  async getDoctorAvailabilities(doctorId: number): Promise<DoctorAvailability[]> {
    try {
      console.log(`Fetching doctor availabilities for doctor ${doctorId}`);
      const response = await apiClient.get(`/api/doctor-availabilities/?doctor_id=${doctorId}`)
      console.log("Doctor availabilities response:", response.data);

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        return response.data.results;
      }

      // Nếu không có trường results, trả về dữ liệu nguyên bản
      return response.data;
    } catch (error: any) {
      console.error("Error getting doctor availabilities:", error.response?.status, error.response?.data);
      return [];
    }
  },

  async createDoctorAvailability(data: Partial<DoctorAvailability>): Promise<DoctorAvailability> {
    const response = await apiClient.post("/api/doctor-availabilities/", data)
    return response.data
  },

  async updateDoctorAvailability(id: number, data: Partial<DoctorAvailability>): Promise<DoctorAvailability> {
    const response = await apiClient.put(`/api/doctor-availabilities/${id}/`, data)
    return response.data
  },

  async deleteDoctorAvailability(id: number): Promise<void> {
    await apiClient.delete(`/api/doctor-availabilities/${id}/`)
  },

  // Time slots
  async getAvailableTimeSlots(doctorId: number, startDate: string, endDate: string): Promise<TimeSlot[]> {
    try {
      // Sử dụng tham số is_available=true để lọc các khung giờ trống
      console.log(`Fetching time slots for doctor ${doctorId} from ${startDate} to ${endDate}`);
      const response = await apiClient.get(
        `/api/time-slots/?doctor_id=${doctorId}&start_date=${startDate}&end_date=${endDate}&is_available=true`,
      )

      console.log("Time slots API response:", response.data);

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        return response.data.results;
      }

      // Nếu không có trường results, trả về dữ liệu nguyên bản
      return response.data;
    } catch (error: any) {
      console.error("Error getting available time slots:", error.response?.status, error.response?.data);
      return [];
    }
  },

  // Generate time slots from doctor availability
  async generateTimeSlots(data: { doctor_id: number, start_date: string, end_date: string, slot_duration: number }): Promise<TimeSlot[]> {
    try {
      console.log("Generating time slots with data:", data);
      const response = await apiClient.post("/api/doctor-availabilities/generate_time_slots/", data);
      console.log("Generate time slots response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Error generating time slots:", error.response?.status, error.response?.data);
      throw error; // Re-throw to allow handling in the component
    }
  },

  // Appointment reminders
  async getAppointmentReminders(): Promise<AppointmentReminder[]> {
    const response = await apiClient.get("/api/appointment-reminders/")
    return response.data
  },

  async createAppointmentReminder(data: Partial<AppointmentReminder>): Promise<AppointmentReminder> {
    const response = await apiClient.post("/api/appointment-reminders/", data)
    return response.data
  },

  async getPendingReminders(): Promise<AppointmentReminder[]> {
    const response = await apiClient.get("/api/appointment-reminders/pending/")
    return response.data
  },
}

export default AppointmentService
