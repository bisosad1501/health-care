import apiClient from "./api-client"

export interface MedicalRecord {
  id: string
  patientId: string
  doctorId: string
  date: string
  type: string
  diagnosis: string
  symptoms: string[]
  notes: string
  attachments?: string[]
  createdAt: string
  updatedAt: string
}

export interface MedicalRecordWithDetails extends MedicalRecord {
  patient: {
    id: string
    firstName: string
    lastName: string
  }
  doctor: {
    id: string
    firstName: string
    lastName: string
    specialty: string
  }
}

export interface MedicalRecordListParams {
  page?: number
  limit?: number
  patientId?: string
  doctorId?: string
  type?: string
  startDate?: string
  endDate?: string
}

export interface MedicalRecordListResponse {
  data: MedicalRecordWithDetails[]
  total: number
  page: number
  limit: number
  totalPages: number
}

const MedicalRecordService = {
  getMedicalRecords: async (params: MedicalRecordListParams = {}): Promise<MedicalRecordListResponse> => {
    const response = await apiClient.get("/medical-records", { params })
    return response.data
  },

  getMedicalRecordById: async (id: string): Promise<MedicalRecordWithDetails> => {
    const response = await apiClient.get(`/medical-records/${id}`)
    return response.data
  },

  createMedicalRecord: async (data: Omit<MedicalRecord, "id" | "createdAt" | "updatedAt">): Promise<MedicalRecord> => {
    const response = await apiClient.post("/medical-records", data)
    return response.data
  },

  updateMedicalRecord: async (id: string, data: Partial<MedicalRecord>): Promise<MedicalRecord> => {
    const response = await apiClient.put(`/medical-records/${id}`, data)
    return response.data
  },

  deleteMedicalRecord: async (id: string): Promise<void> => {
    await apiClient.delete(`/medical-records/${id}`)
  },

  uploadAttachment: async (recordId: string, file: File): Promise<{ url: string }> => {
    const formData = new FormData()
    formData.append("file", file)

    const response = await apiClient.post(`/medical-records/${recordId}/attachments`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    return response.data
  },
}

export default MedicalRecordService
