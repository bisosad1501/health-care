import apiClient from "./api-client"

export interface Appointment {
  id: string
  patientId: string
  doctorId: string
  date: string
  startTime: string
  endTime: string
  status: "scheduled" | "completed" | "cancelled" | "no-show"
  type: string
  reason: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface AppointmentWithDetails extends Appointment {
  patient: {
    id: string
    firstName: string
    lastName: string
    email: string
    phone: string
  }
  doctor: {
    id: string
    firstName: string
    lastName: string
    specialty: string
  }
}

export interface AppointmentListParams {
  page?: number
  limit?: number
  patientId?: string
  doctorId?: string
  status?: string
  startDate?: string
  endDate?: string
}

export interface AppointmentListResponse {
  data: AppointmentWithDetails[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface CreateAppointmentRequest {
  patientId: string
  doctorId: string
  date: string
  startTime: string
  endTime: string
  type: string
  reason: string
  notes?: string
}

const AppointmentService = {
  getAppointments: async (params: AppointmentListParams = {}): Promise<AppointmentListResponse> => {
    const response = await apiClient.get("/appointments", { params })
    return response.data
  },

  getAppointmentById: async (id: string): Promise<AppointmentWithDetails> => {
    const response = await apiClient.get(`/appointments/${id}`)
    return response.data
  },

  createAppointment: async (data: CreateAppointmentRequest): Promise<Appointment> => {
    const response = await apiClient.post("/appointments", data)
    return response.data
  },

  updateAppointment: async (id: string, data: Partial<Appointment>): Promise<Appointment> => {
    const response = await apiClient.put(`/appointments/${id}`, data)
    return response.data
  },

  cancelAppointment: async (id: string, reason?: string): Promise<Appointment> => {
    const response = await apiClient.post(`/appointments/${id}/cancel`, { reason })
    return response.data
  },

  completeAppointment: async (id: string, notes?: string): Promise<Appointment> => {
    const response = await apiClient.post(`/appointments/${id}/complete`, { notes })
    return response.data
  },

  getAvailableSlots: async (doctorId: string, date: string): Promise<{ startTime: string; endTime: string }[]> => {
    const response = await apiClient.get(`/appointments/available-slots`, {
      params: { doctorId, date },
    })
    return response.data
  },
}

export default AppointmentService
