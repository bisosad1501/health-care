import apiClient from "./api-client"

export interface LabTest {
  id: string
  patientId: string
  doctorId: string
  technicianId?: string
  type: string
  status: "ordered" | "in-progress" | "completed" | "cancelled"
  orderedDate: string
  completedDate?: string
  results?: {
    [key: string]: any
  }
  notes?: string
  attachments?: string[]
  createdAt: string
  updatedAt: string
}

export interface LabTestWithDetails extends LabTest {
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
  technician?: {
    id: string
    firstName: string
    lastName: string
  }
}

export interface LabTestListParams {
  page?: number
  limit?: number
  patientId?: string
  doctorId?: string
  technicianId?: string
  status?: string
  type?: string
  startDate?: string
  endDate?: string
}

export interface LabTestListResponse {
  data: LabTestWithDetails[]
  total: number
  page: number
  limit: number
  totalPages: number
}

const LaboratoryService = {
  getLabTests: async (params: LabTestListParams = {}): Promise<LabTestListResponse> => {
    const response = await apiClient.get("/lab-tests", { params })
    return response.data
  },

  getLabTestById: async (id: string): Promise<LabTestWithDetails> => {
    const response = await apiClient.get(`/lab-tests/${id}`)
    return response.data
  },

  createLabTest: async (data: Omit<LabTest, "id" | "createdAt" | "updatedAt">): Promise<LabTest> => {
    const response = await apiClient.post("/lab-tests", data)
    return response.data
  },

  updateLabTest: async (id: string, data: Partial<LabTest>): Promise<LabTest> => {
    const response = await apiClient.put(`/lab-tests/${id}`, data)
    return response.data
  },

  cancelLabTest: async (id: string, reason?: string): Promise<LabTest> => {
    const response = await apiClient.post(`/lab-tests/${id}/cancel`, { reason })
    return response.data
  },

  assignTechnician: async (id: string, technicianId: string): Promise<LabTest> => {
    const response = await apiClient.post(`/lab-tests/${id}/assign`, { technicianId })
    return response.data
  },

  updateResults: async (id: string, results: any, notes?: string): Promise<LabTest> => {
    const response = await apiClient.post(`/lab-tests/${id}/results`, { results, notes })
    return response.data
  },

  completeLabTest: async (id: string): Promise<LabTest> => {
    const response = await apiClient.post(`/lab-tests/${id}/complete`)
    return response.data
  },

  uploadAttachment: async (testId: string, file: File): Promise<{ url: string }> => {
    const formData = new FormData()
    formData.append("file", file)

    const response = await apiClient.post(`/lab-tests/${testId}/attachments`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    return response.data
  },
}

export default LaboratoryService
