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
  reason_text?: string
  reason_category?: number
  reason_category_details?: any
  notes?: string
  status: string
  status_name?: string
  appointment_type?: string
  appointment_type_name?: string
  priority?: number
  priority_name?: string
  is_recurring?: boolean
  recurrence_pattern?: string
  recurrence_end_date?: string
  is_follow_up?: boolean
  follow_up_to?: number
  location?: string
  medical_record_id?: number
  insurance_id?: string
  billing_id?: number
  prescription_id?: number
  lab_request_id?: number
  reminders?: AppointmentReminder[]
  visit_data?: PatientVisit
  created_at: string
  updated_at: string
  created_by?: number
}

export interface DoctorAvailability {
  id: number
  doctor_id: number
  weekday: number
  weekday_name?: string
  start_time: string
  end_time: string
  is_available: boolean
  schedule_type?: 'REGULAR' | 'TEMPORARY' | 'DAY_OFF'
  effective_date?: string
  location?: string
  department?: string
  room?: string
  slot_duration?: number
  max_patients_per_slot?: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface TimeSlot {
  id: number
  doctor_id: number
  doctor_info?: {
    id: number
    first_name?: string
    last_name?: string
    specialty?: string
    profile_image?: string
    department?: string
    name?: string
  }
  date: string
  start_time: string
  end_time: string
  is_available: boolean
  status?: 'AVAILABLE' | 'BOOKED' | 'CANCELLED'
  availability_id?: number
  location?: string
  department?: string
  room?: string
  duration?: number
  max_patients?: number
  current_patients?: number
  created_at: string
  updated_at: string
}

export interface AppointmentReminder {
  id: number
  appointment: number
  reminder_type: string
  reminder_type_name?: string
  scheduled_time: string
  status: string
  status_name?: string
  sent_at?: string
  message: string
  created_at: string
  updated_at: string
}

export interface PatientVisit {
  id: number
  appointment: number
  status: string
  status_name?: string
  checked_in_at: string
  checked_in_by?: number
  nurse_id?: number
  vitals_recorded: boolean
  vitals_recorded_at?: string
  doctor_start_time?: string
  doctor_end_time?: string
  waiting_time?: number
  waiting_time_display?: string
  notes?: string
  created_at: string
  updated_at: string
}

const AppointmentService = {
  async getAllAppointments(): Promise<AppointmentWithDetails[]> {
    const response = await apiClient.get("/api/appointments/")
    return response.data
  },

  async createAppointment(data: Partial<Appointment>): Promise<Appointment> {
    try {
      console.log("Creating appointment with data:", data);

      // Chuẩn bị dữ liệu gửi đi theo đúng cấu trúc API backend
      const appointmentData: any = {
        patient_id: data.patient_id,
        // Sử dụng time_slot_id hoặc time_slot tùy theo API backend yêu cầu
        time_slot_id: data.time_slot_id || data.time_slot,
        reason_text: data.reason_text || "",
        appointment_type: data.appointment_type || "REGULAR",
        priority: data.priority !== undefined ? data.priority : 0,
        notes: data.notes || "",
        created_by: data.created_by || data.patient_id
      };

      // Thêm doctor_id nếu có
      if (data.doctor_id) {
        appointmentData.doctor_id = data.doctor_id;
      }

      // Đảm bảo time_slot_id là số
      if (typeof appointmentData.time_slot_id === 'string') {
        appointmentData.time_slot_id = parseInt(appointmentData.time_slot_id);
      }

      // Nếu có reason_category, thêm vào dữ liệu
      if (data.reason_category) {
        appointmentData.reason_category = data.reason_category;
      }

      // Nếu có thông tin bảo hiểm, thêm vào dữ liệu
      if (data.insurance_id) {
        appointmentData.insurance_id = data.insurance_id;
      }

      // Nếu là lịch hẹn tái khám, thêm thông tin
      if (data.is_follow_up) {
        appointmentData.is_follow_up = true;
        if (data.follow_up_to) {
          appointmentData.follow_up_to = data.follow_up_to;
        }
      }

      console.log("Sending appointment data:", appointmentData);
      const response = await apiClient.post("/api/appointments/", appointmentData);
      console.log("Create appointment response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Error creating appointment:", error.response?.status, error.response?.data);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
        console.error("Response headers:", error.response.headers);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      throw error;
    }
  },

  async cancelAppointment(id: number, notes: string): Promise<Appointment> {
    try {
      console.log(`Cancelling appointment ${id} with notes: ${notes}`);
      const response = await apiClient.post(`/api/appointments/${id}/cancel/`, { notes });
      console.log("Cancel appointment response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Error cancelling appointment ${id}:`, error);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);

        // Kiểm tra các lỗi cụ thể
        if (error.response.status === 400 && error.response.data.error === 'Cannot cancel appointment within 24 hours') {
          throw new Error('Không thể hủy lịch hẹn trong vòng 24 giờ trước giờ hẹn.');
        } else if (error.response.data.detail) {
          throw new Error(error.response.data.detail);
        }
      }

      // Nếu không có lỗi cụ thể, ném lỗi chung
      throw error;
    }
  },

  async rescheduleAppointment(id: number, timeSlotId: number, notes: string): Promise<Appointment> {
    try {
      console.log(`Rescheduling appointment ${id} to time slot ${timeSlotId} with notes: ${notes}`);
      const response = await apiClient.post(`/api/appointments/${id}/reschedule/`, {
        time_slot_id: timeSlotId,
        notes
      });
      console.log("Reschedule appointment response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Error rescheduling appointment ${id}:`, error);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);

        // Kiểm tra các lỗi cụ thể
        if (error.response.data.detail) {
          throw new Error(error.response.data.detail);
        } else if (error.response.data.time_slot_id) {
          throw new Error(`Lỗi khung giờ: ${error.response.data.time_slot_id}`);
        } else if (error.response.data.error) {
          throw new Error(error.response.data.error);
        }
      }

      // Nếu không có lỗi cụ thể, ném lỗi chung
      throw error;
    }
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
      // Lấy thông tin người dùng từ localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error("User information not found in localStorage");
        return [];
      }

      const user = JSON.parse(userStr);
      const patientId = user.id;

      // Sử dụng đường dẫn API với filter theo patient_id
      console.log(`Calling appointments API for patient ${patientId}`);
      const response = await apiClient.get(`/api/appointments/?patient_id=${patientId}`);
      console.log("Appointments API response:", response.data);

      // Kiểm tra dữ liệu trả về có hợp lệ không
      if (!response.data) {
        console.error("API response data is null or undefined");
        return [];
      }

      // Xử lý dữ liệu trả về
      let appointments: any[] = [];

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        appointments = response.data.results;
      }
      // Nếu không có trường results, trả về dữ liệu nguyên bản
      else if (Array.isArray(response.data)) {
        appointments = response.data;
      }
      // Nếu là một đối tượng đơn lẻ
      else if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
        appointments = [response.data];
      }
      else {
        console.error("API response data is not in expected format", response.data);
        return [];
      }

      // Lấy danh sách doctor_id từ các lịch hẹn
      const doctorIds = appointments
        .map(appointment => appointment.doctor_id)
        .filter((id, index, self) => id && self.indexOf(id) === index); // Lọc các ID duy nhất và loại bỏ null/undefined

      console.log("Doctor IDs from appointments:", doctorIds);

      // Lấy thông tin chi tiết của các bác sĩ
      let doctorsMap: Record<number, any> = {};

      if (doctorIds.length > 0) {
        try {
          // Lấy thông tin người dùng của bác sĩ
          const usersResponse = await apiClient.get('/api/users/');
          console.log("Users API response:", usersResponse.data);

          if (Array.isArray(usersResponse.data)) {
            // Tạo map từ ID người dùng đến thông tin người dùng
            const userMap: Record<number, any> = {};
            usersResponse.data.forEach(user => {
              if (user.id) {
                userMap[user.id] = user;
              }
            });

            // Lấy danh sách tất cả bác sĩ
            const doctorsResponse = await apiClient.get('/api/doctors/');
            console.log("Doctors API response:", doctorsResponse.data);

            if (Array.isArray(doctorsResponse.data)) {
              // Tạo map từ ID bác sĩ đến thông tin chi tiết
              doctorsResponse.data.forEach(doctor => {
                if (doctor.id) {
                  // Lấy thông tin người dùng tương ứng
                  const user = userMap[doctor.user] || {};

                  doctorsMap[doctor.id] = {
                    ...doctor,
                    first_name: user.first_name || "",
                    last_name: user.last_name || "",
                    email: user.email || "",
                    specialty: doctor.specialization || ""
                  };
                }
              });
            }

            // Thêm các bác sĩ không có trong doctorsResponse nhưng có trong userResponse
            usersResponse.data.forEach(user => {
              if (user.role === 'DOCTOR' && user.id && doctorIds.includes(user.id) && !doctorsMap[user.id]) {
                doctorsMap[user.id] = {
                  id: user.id,
                  first_name: user.first_name || "",
                  last_name: user.last_name || "",
                  email: user.email || "",
                  specialty: user.doctor_profile?.specialization || ""
                };
              }
            });
          }
        } catch (error) {
          console.error("Error fetching doctors information:", error);
        }
      }

      console.log("Doctors map:", doctorsMap);

      // Chuẩn hóa dữ liệu
      return appointments.map((appointment: any) => {
        // Lấy thông tin bác sĩ từ map nếu có
        let doctorInfo = appointment.doctor || {};

        if (appointment.doctor_id && doctorsMap[appointment.doctor_id]) {
          doctorInfo = {
            ...doctorInfo,
            id: appointment.doctor_id,
            first_name: doctorsMap[appointment.doctor_id].first_name || "",
            last_name: doctorsMap[appointment.doctor_id].last_name || "",
            email: doctorsMap[appointment.doctor_id].email || "",
            specialty: doctorsMap[appointment.doctor_id].specialization || doctorsMap[appointment.doctor_id].specialty || ""
          };
        } else if (!appointment.doctor) {
          // Nếu không có thông tin bác sĩ, tạo một đối tượng mặc định
          doctorInfo = {
            id: appointment.doctor_id || null,
            first_name: "",
            last_name: "",
            email: "",
            specialty: ""
          };
        }

        // Đảm bảo các trường cần thiết luôn tồn tại
        return {
          ...appointment,
          appointment_date: appointment.appointment_date || appointment.date || new Date().toISOString().split('T')[0],
          start_time: appointment.start_time || "00:00:00",
          end_time: appointment.end_time || "00:30:00",
          status: appointment.status || "PENDING",
          location: appointment.location || "Chưa xác định",
          reason_text: appointment.reason_text || "",
          appointment_type: appointment.appointment_type || "REGULAR",
          doctor: doctorInfo
        };
      });
    } catch (error: any) {
      console.error("Error getting patient appointments:", error);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      // Trả về mảng rỗng để hiển thị thông báo không có cuộc hẹn
      return [];
    }
  },

  async getDoctorAppointments(doctorId: number): Promise<AppointmentWithDetails[]> {
    try {
      // Lấy danh sách lịch hẹn của bác sĩ
      const response = await apiClient.get(`/api/appointments/?doctor_id=${doctorId}`);
      console.log("Doctor appointments API response:", response.data);

      // Kiểm tra dữ liệu trả về có hợp lệ không
      if (!response.data) {
        console.error("API response data is null or undefined");
        return [];
      }

      // Xử lý dữ liệu trả về
      let appointments: any[] = [];

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        appointments = response.data.results;
      }
      // Nếu không có trường results, trả về dữ liệu nguyên bản
      else if (Array.isArray(response.data)) {
        appointments = response.data;
      }
      // Nếu là một đối tượng đơn lẻ
      else if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
        appointments = [response.data];
      }
      else {
        console.error("API response data is not in expected format", response.data);
        return [];
      }

      // Lấy danh sách patient_id từ các lịch hẹn
      const patientIds = appointments
        .map(appointment => appointment.patient_id)
        .filter((id, index, self) => id && self.indexOf(id) === index); // Lọc các ID duy nhất và loại bỏ null/undefined

      console.log("Patient IDs from appointments:", patientIds);

      // Lấy thông tin chi tiết của các bệnh nhân
      let patientsMap: Record<number, any> = {};

      if (patientIds.length > 0) {
        try {
          // Lấy thông tin người dùng
          const usersResponse = await apiClient.get('/api/users/');
          console.log("Users API response:", usersResponse.data);

          if (Array.isArray(usersResponse.data)) {
            // Lọc người dùng là bệnh nhân và có ID trong danh sách patientIds
            usersResponse.data.forEach(user => {
              if (user.role === 'PATIENT' && user.id && patientIds.includes(user.id)) {
                patientsMap[user.id] = {
                  id: user.id,
                  first_name: user.first_name || "",
                  last_name: user.last_name || "",
                  email: user.email || ""
                };
              }
            });
          }
        } catch (error) {
          console.error("Error fetching patients information:", error);
        }
      }

      console.log("Patients map:", patientsMap);

      // Chuẩn hóa dữ liệu
      return appointments.map((appointment: any) => {
        // Lấy thông tin bệnh nhân từ map nếu có
        let patientInfo = appointment.patient || {};

        if (appointment.patient_id && patientsMap[appointment.patient_id]) {
          patientInfo = {
            ...patientInfo,
            id: appointment.patient_id,
            first_name: patientsMap[appointment.patient_id].first_name || "",
            last_name: patientsMap[appointment.patient_id].last_name || "",
            email: patientsMap[appointment.patient_id].email || ""
          };
        } else if (!appointment.patient) {
          // Nếu không có thông tin bệnh nhân, tạo một đối tượng mặc định
          patientInfo = {
            id: appointment.patient_id || null,
            first_name: "",
            last_name: "",
            email: ""
          };
        }

        // Đảm bảo các trường cần thiết luôn tồn tại
        return {
          ...appointment,
          appointment_date: appointment.appointment_date || appointment.date || new Date().toISOString().split('T')[0],
          start_time: appointment.start_time || "00:00:00",
          end_time: appointment.end_time || "00:30:00",
          status: appointment.status || "PENDING",
          location: appointment.location || "Chưa xác định",
          reason_text: appointment.reason_text || "",
          appointment_type: appointment.appointment_type || "REGULAR",
          patient: patientInfo
        };
      });
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
  async getAvailableTimeSlots(doctorId: number, date: string, endDate: string = "", filters: any = {}): Promise<TimeSlot[]> {
    try {
      // Xây dựng query string từ các filter
      let queryParams = `doctor_id=${doctorId}&is_available=true`;

      // Thêm date nếu có
      if (date) {
        queryParams += `&date=${date}`;
      }

      // Thêm các filter khác nếu có
      if (filters.specialty) {
        queryParams += `&specialty=${encodeURIComponent(filters.specialty)}`;
      }

      if (filters.department) {
        queryParams += `&department=${encodeURIComponent(filters.department)}`;
      }

      if (filters.location) {
        queryParams += `&location=${encodeURIComponent(filters.location)}`;
      }

      if (filters.weekday !== undefined) {
        queryParams += `&weekday=${filters.weekday}`;
      }

      console.log(`Fetching available time slots with query: ${queryParams}`);
      const response = await apiClient.get(`/api/time-slots/?${queryParams}`)

      console.log("Time slots API response:", response.data);

      // Kiểm tra cấu trúc dữ liệu trả về
      if (response.data && Array.isArray(response.data)) {
        return response.data;
      } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        // API trả về dữ liệu dạng phân trang (pagination)
        return response.data.results;
      } else if (response.data && typeof response.data === 'object') {
        // Nếu API trả về một đối tượng khác, thử chuyển đổi thành mảng
        console.warn("API returned unexpected format, attempting to convert:", response.data);
        return [response.data];
      }

      console.warn("No time slots available with the current filters");
      return [];
    } catch (error: any) {
      console.error("Error getting available time slots:", error.response?.status, error.response?.data);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      // Trả về mảng rỗng khi có lỗi để hiển thị thông báo phù hợp cho người dùng
      return [];
    }
  },

  // Xóa khung giờ
  async deleteTimeSlot(id: number): Promise<void> {
    try {
      await apiClient.delete(`/api/time-slots/${id}/`);
    } catch (error: any) {
      console.error("Error deleting time slot:", error.response?.status, error.response?.data);
      throw error; // Re-throw to allow handling in the component
    }
  },

  // Tạo lịch làm việc cho bác sĩ (API mới)
  async createSchedule(data: {
    doctor_id: number,
    schedule_type: 'REGULAR' | 'TEMPORARY' | 'DAY_OFF',
    weekdays?: number[],
    start_time?: string,
    end_time?: string,
    effective_date?: string,
    location?: string,
    department?: string,
    room?: string,
    slot_duration?: number,
    max_patients_per_slot?: number,
    notes?: string,
    auto_generate_slots?: boolean,
    start_date?: string,
    end_date?: string
  }): Promise<DoctorAvailability[]> {
    try {
      // Đảm bảo dữ liệu gửi đi đúng định dạng
      const cleanedData = {
        ...data,
        // Đảm bảo các trường số được gửi dưới dạng số
        slot_duration: typeof data.slot_duration === 'string' ? parseInt(data.slot_duration) : data.slot_duration,
        max_patients_per_slot: typeof data.max_patients_per_slot === 'string' ? parseInt(data.max_patients_per_slot) : data.max_patients_per_slot,
        // Đảm bảo weekdays là mảng số
        weekdays: data.weekdays?.map(day => typeof day === 'string' ? parseInt(day) : day),
        // Đảm bảo các trường không bị undefined
        location: data.location || "",
        department: data.department || "",
        room: data.room || "",
        notes: data.notes || ""
      };

      console.log("Creating doctor schedule with data:", cleanedData);

      // Gọi đến endpoint đúng cho việc tạo lịch và khung giờ tự động
      const response = await apiClient.post("/api/doctor-availabilities/create_schedule/", cleanedData);
      console.log("Create schedule response:", response.data);

      // Xử lý kết quả trả về
      if (response.data && response.data.schedules) {
        return Array.isArray(response.data.schedules) ? response.data.schedules : [response.data.schedules];
      } else if (response.data) {
        // Nếu không có trường schedules, có thể API trả về trực tiếp mảng lịch
        return Array.isArray(response.data) ? response.data : [response.data];
      }
      return [];
    } catch (error: any) {
      console.error("Error creating doctor schedule:", error.response?.status, error.response?.data);
      // Log chi tiết hơn để debug
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
        console.error("Response headers:", error.response.headers);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }
      throw error; // Re-throw to allow handling in the component
    }
  },

  // Generate time slots from doctor availability
  async generateTimeSlots(data: {
    doctor_id: number,
    start_date?: string,
    end_date?: string,
    slot_duration: number,
    specific_dates?: Array<{
      date: string,
      start_time: string,
      end_time: string
    }>,
    department?: string,
    location?: string,
    room?: string,
    max_patients?: number
  }): Promise<TimeSlot[]> {
    try {
      console.log("Generating time slots with data:", data);
      // Sử dụng endpoint đúng cho việc tạo khung giờ
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

  // Patient Visit
  async createPatientVisit(appointmentId: number, notes?: string): Promise<PatientVisit> {
    const response = await apiClient.post("/api/patient-visits/check_in/", {
      appointment_id: appointmentId,
      notes
    });
    return response.data;
  },

  async updatePatientVisitStatus(visitId: number, status: string, notes?: string): Promise<PatientVisit> {
    const response = await apiClient.post(`/api/patient-visits/${visitId}/update_status/`, {
      status,
      notes
    });
    return response.data;
  },

  async getPatientVisit(appointmentId: number): Promise<PatientVisit> {
    const response = await apiClient.get(`/api/patient-visits/?appointment=${appointmentId}`);
    return response.data.results && response.data.results.length > 0 ? response.data.results[0] : null;
  },

  // Transition appointment to a new status
  async transitionAppointmentStatus(appointmentId: number, newStatus: string, notes?: string): Promise<Appointment> {
    // Các trạng thái hợp lệ: 'PENDING', 'CONFIRMED', 'CHECKED_IN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW', 'RESCHEDULED'
    try {
      let endpoint = '';
      let data: any = { notes };

      switch(newStatus) {
        case 'CANCELLED':
          endpoint = `/api/appointments/${appointmentId}/cancel/`;
          break;
        case 'COMPLETED':
          endpoint = `/api/appointments/${appointmentId}/complete/`;
          break;
        case 'RESCHEDULED':
          // Đã có phương thức rescheduleAppointment riêng
          throw new Error("Please use rescheduleAppointment method instead");
        default:
          // Sử dụng updateAppointmentStatus cho các trạng thái khác
          return this.updateAppointmentStatus(appointmentId, newStatus);
      }

      const response = await apiClient.post(endpoint, data);
      return response.data;
    } catch (error: any) {
      console.error(`Error transitioning appointment ${appointmentId} to ${newStatus}:`, error.response?.status, error.response?.data);
      throw error;
    }
  },

  // Billing related methods
  async getBillingForAppointment(appointmentId: number): Promise<any> {
    try {
      const response = await apiClient.get(`/api/billings/by-appointment/${appointmentId}/`);
      return response.data;
    } catch (error: any) {
      console.error(`Error getting billing for appointment ${appointmentId}:`, error.response?.status, error.response?.data);
      return null;
    }
  },

  async updateBillingStatus(billingId: number, status: string): Promise<any> {
    try {
      const response = await apiClient.patch(`/api/billings/${billingId}/update-status/`, { status });
      return response.data;
    } catch (error: any) {
      console.error(`Error updating billing status for billing ${billingId}:`, error.response?.status, error.response?.data);
      throw error;
    }
  },

  // Health insurance related methods
  async verifyInsurance(insuranceId: string, patientId: number): Promise<any> {
    try {
      const response = await apiClient.post(`/api/billings/verify-insurance/`, {
        insurance_id: insuranceId,
        patient_id: patientId
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error verifying insurance ${insuranceId}:`, error.response?.status, error.response?.data);
      return {
        verified: false,
        message: error.response?.data?.message || "Could not verify insurance"
      };
    }
  },

  // Lấy khung giờ cho ngày cụ thể
  async getTimeSlotsForDate(doctorId: number, date: string): Promise<TimeSlot[]> {
    try {
      console.log(`Fetching time slots for doctor ${doctorId} on date ${date}`);
      const response = await apiClient.get(`/api/time-slots/?doctor_id=${doctorId}&date=${date}`);
      console.log(`Response for time slots on ${date}:`, response.data);

      // Kiểm tra cấu trúc dữ liệu trả về
      if (Array.isArray(response.data)) {
        return response.data;
      } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        // Nếu API trả về dạng paging
        return response.data.results;
      } else if (response.data && typeof response.data === 'object') {
        // Nếu API trả về một đối tượng khác, thử chuyển đổi thành mảng
        console.warn(`Unexpected response format for time slots on ${date}, attempting to convert:`, response.data);
        return [response.data];
      } else {
        console.warn(`Unexpected response format for time slots on ${date}:`, response.data);
        return [];
      }
    } catch (error: any) {
      console.error(`Error getting time slots for date ${date}:`, error.response?.status, error.response?.data);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      return [];
    }
  },

  // Lấy thông tin về các ngày bác sĩ có lịch làm việc
  async getDoctorWorkingDays(doctorId: number): Promise<{working_days: number[], available_dates: string[], availabilities: any[]}> {
    try {
      console.log(`Fetching working days for doctor ${doctorId}`);
      const response = await apiClient.get(`/api/doctor-working-days/?doctor_id=${doctorId}`);
      console.log(`Response for doctor working days:`, response.data);

      return {
        working_days: response.data.working_days || [],
        available_dates: response.data.available_dates || [],
        availabilities: response.data.availabilities || []
      };
    } catch (error: any) {
      console.error(`Error getting doctor working days:`, error.response?.status, error.response?.data);

      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      return { working_days: [], available_dates: [], availabilities: [] };
    }
  },

  // Tạo lịch làm việc mới với method và endpoint hỗ trợ tự động tạo khung giờ
  async createDoctorSchedule(data: {
    doctor_id: number,
    weekday: number,
    start_time: string,
    end_time: string,
    is_available: boolean,
    schedule_type: 'REGULAR' | 'TEMPORARY' | 'DAY_OFF',
    location?: string,
    department?: string,
    room?: string,
    slot_duration?: number,
    max_patients_per_slot?: number,
    auto_generate_slots?: boolean,
    start_date?: string,
    end_date?: string,
    notes?: string
  }): Promise<DoctorAvailability> {
    try {
      console.log("Creating doctor schedule with data:", data);
      const response = await apiClient.post('/api/doctor-availabilities/', data);
      console.log("Create schedule response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error creating doctor schedule:", error);
      throw error;
    }
  },

  // Tạo một khung giờ đơn lẻ
  async createTimeSlot(data: Partial<TimeSlot>): Promise<TimeSlot> {
    try {
      console.log("Creating time slot with data:", data);
      const response = await apiClient.post('/api/time-slots/', data);
      console.log("Create time slot response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error creating time slot:", error);
      throw error;
    }
  },

  // Lấy danh sách bác sĩ có lịch trống
  async getAvailableDoctors(startDate: string, endDate: string, filters: any = {}): Promise<any[]> {
    try {
      // Vì API /api/doctors/available/ không tồn tại, chúng ta sẽ sử dụng API /api/doctors/ và lọc dữ liệu
      console.log(`Fetching doctors with filters:`, filters);
      const response = await apiClient.get(`/api/doctors/`);

      console.log("Doctors API response:", response.data);

      // Kiểm tra cấu trúc dữ liệu trả về
      let doctors = [];
      if (response.data && Array.isArray(response.data)) {
        doctors = response.data;
      } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        doctors = response.data.results;
      } else if (response.data && typeof response.data === 'object') {
        // Nếu API trả về một đối tượng khác, thử chuyển đổi thành mảng
        console.warn("API returned unexpected format, attempting to convert:", response.data);
        doctors = [response.data];
      }

      // Tạo mảng các ngày cần kiểm tra
      const startDateObj = new Date(startDate);
      const endDateObj = new Date(endDate);
      const dateRange: string[] = [];

      // Thêm startDate vào mảng
      dateRange.push(startDate);

      // Thêm các ngày giữa startDate và endDate vào mảng
      let currentDate = new Date(startDateObj);
      currentDate.setDate(currentDate.getDate() + 1);

      while (currentDate <= endDateObj) {
        const formattedDate = currentDate.toISOString().split('T')[0];
        dateRange.push(formattedDate);
        currentDate.setDate(currentDate.getDate() + 1);
      }

      console.log(`Checking availability for date range:`, dateRange);

      // Sau khi lấy danh sách bác sĩ, chúng ta sẽ lấy thông tin khung giờ trống cho mỗi bác sĩ
      const doctorsWithAvailability = await Promise.all(
        doctors.map(async (doctor: any) => {
          try {
            // Lấy khung giờ trống cho bác sĩ cho mỗi ngày trong khoảng thời gian
            let allTimeSlots: any[] = [];
            let allAvailableDates: string[] = [];

            // Kiểm tra từng ngày trong khoảng thời gian
            for (const date of dateRange) {
              try {
                const timeSlotsForDate = await this.getTimeSlotsForDate(doctor.id, date);

                // Lọc các khung giờ còn trống
                const availableTimeSlotsForDate = timeSlotsForDate.filter((slot: any) =>
                  slot.is_available === true ||
                  slot.status === "AVAILABLE" ||
                  slot.status_name === "Còn trống"
                );

                console.log(`Tìm thấy ${availableTimeSlotsForDate.length} khung giờ trống cho bác sĩ ${doctor.id} vào ngày ${date}`);

                // Nếu có khung giờ trống, thêm ngày vào danh sách ngày có lịch trống
                if (availableTimeSlotsForDate.length > 0) {
                  allAvailableDates.push(date);
                  allTimeSlots = [...allTimeSlots, ...availableTimeSlotsForDate];
                }
              } catch (dateError) {
                console.error(`Error getting time slots for doctor ${doctor.id} on date ${date}:`, dateError);
                // Tiếp tục kiểm tra các ngày khác
              }
            }

            // Xác định khoa của bác sĩ
            let department = doctor.department;

            // Nếu có khung giờ, lấy khoa từ khung giờ đầu tiên
            if (allTimeSlots.length > 0 && allTimeSlots[0].department) {
              department = allTimeSlots[0].department;
            }

            // Thêm thông tin khung giờ trống vào thông tin bác sĩ
            return {
              ...doctor,
              available_dates: allAvailableDates,
              available_slots_count: allTimeSlots.length,
              // Thêm các thông tin khác nếu cần
              name: doctor.user ? `${doctor.user.first_name} ${doctor.user.last_name}` :
                    (doctor.first_name && doctor.last_name ? `${doctor.first_name} ${doctor.last_name}` :
                    `Bác sĩ (ID: ${doctor.id})`),
              specialty: doctor.specialization || doctor.specialty || "Chưa cập nhật",
              department: department || "Chưa cập nhật"
            };
          } catch (error) {
            console.error(`Error getting time slots for doctor ${doctor.id}:`, error);
            return {
              ...doctor,
              available_dates: [],
              available_slots_count: 0,
              name: doctor.user ? `${doctor.user.first_name} ${doctor.user.last_name}` :
                    (doctor.first_name && doctor.last_name ? `${doctor.first_name} ${doctor.last_name}` :
                    `Bác sĩ (ID: ${doctor.id})`),
              specialty: doctor.specialization || doctor.specialty || "Chưa cập nhật",
              department: doctor.department || "Chưa cập nhật"
            };
          }
        })
      );

      // Lọc bác sĩ theo các filter
      let filteredDoctors = doctorsWithAvailability;

      // Lọc theo chuyên khoa
      if (filters.specialty && filters.specialty !== 'all') {
        filteredDoctors = filteredDoctors.filter((doctor: any) =>
          doctor.specialty === filters.specialty ||
          doctor.specialization === filters.specialty
        );
      }

      // Lọc theo khoa
      if (filters.department && filters.department !== 'all') {
        filteredDoctors = filteredDoctors.filter((doctor: any) => {
          // Kiểm tra khoa của bác sĩ
          const doctorDepartment = doctor.department?.toUpperCase();
          const filterDepartment = filters.department.toUpperCase();

          // So sánh không phân biệt chữ hoa/thường
          return doctorDepartment === filterDepartment ||
                 doctorDepartment?.includes(filterDepartment) ||
                 filterDepartment?.includes(doctorDepartment);
        });
      }

      // Lọc theo tên
      if (filters.name) {
        const searchName = filters.name.toLowerCase();
        filteredDoctors = filteredDoctors.filter((doctor: any) =>
          doctor.name.toLowerCase().includes(searchName)
        );
      }

      // Lọc bác sĩ có lịch trống
      filteredDoctors = filteredDoctors.filter((doctor: any) =>
        doctor.available_slots_count > 0
      );

      console.log(`Found ${filteredDoctors.length} doctors with available slots`);
      return filteredDoctors;
    } catch (error: any) {
      console.error("Error getting available doctors:", error.response?.status, error.response?.data);

      // Log chi tiết hơn về lỗi
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      } else if (error.request) {
        console.error("No response received:", error.request);
      } else {
        console.error("Error message:", error.message);
      }

      // Trả về mảng rỗng thay vì dữ liệu giả
      return [];
    }
  },

  // Lấy danh sách chuyên khoa
  async getSpecialties(department?: string): Promise<any[]> {
    try {
      // Vì API /api/specialties/ không tồn tại, chúng ta sẽ trả về danh sách chuyên khoa mặc định
      console.log("Getting specialties for department:", department);

      // Danh sách chuyên khoa mặc định
      const defaultSpecialties = [
        { id: "CARDIOLOGY", name: "Tim mạch" },
        { id: "NEUROLOGY", name: "Thần kinh" },
        { id: "ORTHOPEDICS", name: "Chỉnh hình" },
        { id: "GASTROENTEROLOGY", name: "Tiêu hóa" },
        { id: "DERMATOLOGY", name: "Da liễu" },
        { id: "OPHTHALMOLOGY", name: "Mắt" },
        { id: "PEDIATRICS", name: "Nhi" },
        { id: "GYNECOLOGY", name: "Phụ khoa" },
        { id: "UROLOGY", name: "Tiết niệu" },
        { id: "ENT", name: "Tai Mũi Họng" },
        { id: "PSYCHIATRY", name: "Tâm thần" },
        { id: "DENTISTRY", name: "Nha khoa" }
      ];

      // Lọc chuyên khoa theo khoa nếu có
      if (department && department !== 'all') {
        // Trong thực tế, cần có logic lọc chuyên khoa theo khoa
        // Ở đây chỉ trả về tất cả chuyên khoa
        return defaultSpecialties;
      }

      return defaultSpecialties;
    } catch (error: any) {
      console.error("Error getting specialties:", error);
      return [];
    }
  },

  // Lấy danh sách khoa
  async getDepartments(): Promise<any[]> {
    try {
      // Vì API /api/departments/ không tồn tại, chúng ta sẽ trả về danh sách khoa mặc định
      console.log("Getting departments");

      // Danh sách khoa mặc định - đảm bảo ID khớp với backend
      const defaultDepartments = [
        { id: "CARDIOLOGY", name: "Khoa tim mạch" },
        { id: "NEUROLOGY", name: "Khoa thần kinh" },
        { id: "ORTHOPEDICS", name: "Khoa chỉnh hình" },
        { id: "GASTROENTEROLOGY", name: "Khoa tiêu hóa" },
        { id: "DERMATOLOGY", name: "Khoa da liễu" },
        { id: "OPHTHALMOLOGY", name: "Khoa mắt" },
        { id: "PEDIATRICS", name: "Khoa nhi" },
        { id: "OBSTETRICS", name: "Khoa sản" },
        { id: "GENERAL", name: "Khoa đa khoa" }
      ];

      return defaultDepartments;
    } catch (error: any) {
      console.error("Error getting departments:", error);
      return [];
    }
  },

  // Lấy thông tin bảo hiểm của bệnh nhân
  async getPatientInsurance(): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/patient-insurance/');
      console.log("Patient insurance API response:", response.data);
      return response.data || [];
    } catch (error: any) {
      console.error("Error getting patient insurance:", error.response?.status, error.response?.data);
      return [];
    }
  },

  // Xác minh bảo hiểm cho dịch vụ
  async verifyInsuranceForService(insuranceId: number, serviceCode: string, amount: number): Promise<any> {
    try {
      const response = await apiClient.post('/api/verify-insurance/', {
        insurance_id: insuranceId,
        service_code: serviceCode,
        amount: amount
      });
      console.log("Verify insurance API response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Error verifying insurance:", error.response?.status, error.response?.data);
      return null;
    }
  },

  // Tạo lịch hẹn tái khám
  async createFollowUpAppointment(appointmentId: number, data: any): Promise<Appointment> {
    try {
      const response = await apiClient.post(`/api/appointments/${appointmentId}/create_follow_up/`, data);
      console.log("Create follow-up appointment response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Error creating follow-up appointment:", error.response?.status, error.response?.data);
      throw error;
    }
  },


}

export default AppointmentService
