import apiClient from "./api-client"

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  date_joined: string
  last_login: string
}

export interface PatientProfile {
  id: number
  user: number
  date_of_birth: string
  gender: string
  blood_type: string
  height: number
  weight: number
  emergency_contact_name: string
  emergency_contact_phone: string
  medical_history: string
  allergies: string
  created_at: string
  updated_at: string
}

export interface DoctorProfile {
  id: number
  user: number
  specialty: string
  license_number: string
  education: string
  experience_years: number
  bio: string
  consultation_fee: number
  available_for_appointments: boolean
  created_at: string
  updated_at: string
}

export interface NurseProfile {
  id: number
  user: number
  department: string
  license_number: string
  education: string
  experience_years: number
  created_at: string
  updated_at: string
}

export interface Address {
  id: number
  user: number
  address_line1: string
  address_line2: string
  city: string
  state: string
  postal_code: string
  country: string
  is_primary: boolean
  created_at: string
  updated_at: string
}

export interface ContactInfo {
  id: number
  user: number
  phone_number: string
  alternative_email: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: number
  user: number
  document_type: string
  file: string
  description: string
  is_verified: boolean
  verification_notes: string
  uploaded_at: string
  verified_at: string
}

const UserService = {
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get("/api/users/me/")
    return response.data
  },

  async getAllUsers(): Promise<User[]> {
    const response = await apiClient.get("/api/users/")
    return response.data
  },

  async getUserById(id: number): Promise<User> {
    const response = await apiClient.get(`/api/users/${id}/`)
    return response.data
  },

  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await apiClient.put(`/api/users/${id}/`, data)
    return response.data
  },

  async deleteUser(id: number): Promise<void> {
    await apiClient.delete(`/api/users/${id}/`)
  },

  // Lấy danh sách bác sĩ
  async getDoctors(): Promise<User[]> {
    try {
      // Gọi API lấy danh sách người dùng có vai trò DOCTOR
      const response = await apiClient.get("/api/users/?role=DOCTOR")
      return response.data
    } catch (error) {
      console.error("Error fetching doctors:", error)
      return []
    }
  },

  // Patient profile
  async getPatientProfile(): Promise<PatientProfile> {
    const response = await apiClient.get("/api/patient-profile/")
    return response.data
  },

  async updatePatientProfile(data: Partial<PatientProfile>): Promise<PatientProfile> {
    const response = await apiClient.put("/api/patient-profile/", data)
    return response.data
  },

  // Doctor profile
  async getDoctorProfile(): Promise<DoctorProfile> {
    const response = await apiClient.get("/api/doctor-profile/")
    return response.data
  },

  async updateDoctorProfile(data: Partial<DoctorProfile>): Promise<DoctorProfile> {
    const response = await apiClient.put("/api/doctor-profile/", data)
    return response.data
  },

  // Nurse profile
  async getNurseProfile(): Promise<NurseProfile> {
    const response = await apiClient.get("/api/nurse-profile/")
    return response.data
  },

  async updateNurseProfile(data: Partial<NurseProfile>): Promise<NurseProfile> {
    const response = await apiClient.put("/api/nurse-profile/", data)
    return response.data
  },

  // Addresses
  async getAddresses(): Promise<Address[]> {
    const response = await apiClient.get("/api/addresses/")
    return response.data
  },

  async createAddress(data: Partial<Address>): Promise<Address> {
    const response = await apiClient.post("/api/addresses/", data)
    return response.data
  },

  async updateAddress(id: number, data: Partial<Address>): Promise<Address> {
    const response = await apiClient.put(`/api/addresses/${id}/`, data)
    return response.data
  },

  async deleteAddress(id: number): Promise<void> {
    await apiClient.delete(`/api/addresses/${id}/`)
  },

  // Contact info
  async getContactInfo(): Promise<ContactInfo> {
    const response = await apiClient.get("/api/contact-info/")
    return response.data
  },

  async updateContactInfo(data: Partial<ContactInfo>): Promise<ContactInfo> {
    const response = await apiClient.put("/api/contact-info/", data)
    return response.data
  },

  // Documents
  async getDocuments(): Promise<Document[]> {
    const response = await apiClient.get("/api/documents/")
    return response.data
  },

  async uploadDocument(formData: FormData): Promise<Document> {
    const response = await apiClient.post("/api/documents/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    return response.data
  },

  async verifyDocument(id: number, data: { is_verified: boolean; verification_notes: string }): Promise<Document> {
    const response = await apiClient.post(`/api/documents/${id}/verify/`, data)
    return response.data
  },

  // Admin endpoints
  async getAllPatientProfiles(): Promise<PatientProfile[]> {
    const response = await apiClient.get("/api/admin/patient-profiles/")
    return response.data
  },

  async getAllDoctorProfiles(): Promise<DoctorProfile[]> {
    const response = await apiClient.get("/api/admin/doctor-profiles/")
    return response.data
  },
}

export default UserService
