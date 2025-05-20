import apiClient from "./api-client"

export interface Medication {
  id: number
  name: string
  generic_name: string
  brand_name: string
  manufacturer: string
  description: string
  dosage_form: string
  strength: string
  active_ingredients: string
  requires_prescription: boolean
  created_at: string
  updated_at: string
}

export interface Prescription {
  id: number
  patient_id: number
  doctor_id: number
  medical_record: number
  prescription_date: string
  status: string
  notes: string
  created_at: string
  updated_at: string
}

export interface PrescriptionWithDetails extends Prescription {
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
  items: PrescriptionItem[]
}

export interface PrescriptionItem {
  id: number
  prescription: number
  medication: number
  medication_details: Medication
  dosage: string
  frequency: string
  duration: number
  quantity: number
  instructions: string
  created_at: string
  updated_at: string
}

export interface InventoryItem {
  id: number
  medication: number
  medication_details: Medication
  batch_number: string
  expiry_date: string
  quantity: number
  unit_price: number
  location: string
  created_at: string
  updated_at: string
}

export interface Dispensing {
  id: number
  prescription: number
  patient_id: number
  pharmacist_id: number
  dispensing_date: string
  status: string
  notes: string
  created_at: string
  updated_at: string
}

export interface DispensingItem {
  id: number
  dispensing: number
  prescription_item: number
  inventory_item: number
  quantity: number
  notes: string
  created_at: string
  updated_at: string
}

const PharmacyService = {
  // Medications
  async getAllMedications(): Promise<Medication[]> {
    const response = await apiClient.get("/api/medications/")
    return response.data
  },

  async createMedication(data: Partial<Medication>): Promise<Medication> {
    const response = await apiClient.post("/api/medications/", data)
    return response.data
  },

  async getMedicationById(id: number): Promise<Medication> {
    const response = await apiClient.get(`/api/medications/${id}/`)
    return response.data
  },

  // Prescriptions
  async getAllPrescriptions(): Promise<PrescriptionWithDetails[]> {
    const response = await apiClient.get("/api/prescriptions/")
    return response.data
  },

  async createPrescription(data: Partial<Prescription>): Promise<Prescription> {
    const response = await apiClient.post("/api/prescriptions/", data)
    return response.data
  },

  async getPrescriptionById(id: number): Promise<PrescriptionWithDetails> {
    const response = await apiClient.get(`/api/prescriptions/${id}/`)
    return response.data
  },

  // Prescription items
  async getPrescriptionItems(prescriptionId: number): Promise<PrescriptionItem[]> {
    const response = await apiClient.get(`/api/prescription-items/?prescription=${prescriptionId}`)
    return response.data
  },

  async createPrescriptionItem(data: Partial<PrescriptionItem>): Promise<PrescriptionItem> {
    const response = await apiClient.post("/api/prescription-items/", data)
    return response.data
  },

  // Inventory
  async getAllInventoryItems(): Promise<InventoryItem[]> {
    const response = await apiClient.get("/api/inventory/")
    return response.data
  },

  async createInventoryItem(data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await apiClient.post("/api/inventory/", data)
    return response.data
  },

  // Dispensing
  async getAllDispensings(): Promise<Dispensing[]> {
    const response = await apiClient.get("/api/dispensings/")
    return response.data
  },

  async createDispensing(data: Partial<Dispensing>): Promise<Dispensing> {
    const response = await apiClient.post("/api/dispensings/", data)
    return response.data
  },

  async createDispensingItem(data: Partial<DispensingItem>): Promise<DispensingItem> {
    const response = await apiClient.post("/api/dispensing-items/", data)
    return response.data
  },

  // Lấy đơn thuốc của bệnh nhân hiện tại
  async getPatientPrescriptions(): Promise<PrescriptionWithDetails[]> {
    try {
      // Lấy thông tin người dùng từ localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error("User information not found in localStorage");
        return [];
      }

      const user = JSON.parse(userStr);
      const patientId = user.id;

      // Gọi API để lấy đơn thuốc của bệnh nhân
      console.log(`Fetching prescriptions for patient ${patientId}`);
      const response = await apiClient.get(`/api/prescriptions/?patient_id=${patientId}`);
      console.log("Prescriptions API response:", response.data);

      // Kiểm tra dữ liệu trả về có hợp lệ không
      if (!response.data) {
        console.error("API response data is null or undefined");
        return [];
      }

      // Xử lý dữ liệu trả về
      let prescriptions: PrescriptionWithDetails[] = [];

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        prescriptions = response.data.results;
      }
      // Nếu không có trường results, trả về dữ liệu nguyên bản
      else if (Array.isArray(response.data)) {
        prescriptions = response.data;
      }

      return prescriptions;
    } catch (error) {
      console.error("Error fetching patient prescriptions:", error);
      return [];
    }
  },

  // Yêu cầu cấp lại thuốc
  async requestRefill(prescriptionId: number): Promise<any> {
    try {
      const response = await apiClient.post(`/api/prescriptions/${prescriptionId}/refill/`);
      return response.data;
    } catch (error) {
      console.error(`Error requesting refill for prescription ${prescriptionId}:`, error);
      throw error;
    }
  },
}

export default PharmacyService
