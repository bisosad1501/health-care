import apiClient from "./api-client"

// Định nghĩa các interface dựa trên cấu trúc API thực tế
export interface MedicalRecord {
  id: number
  patient_id: number
  created_at: string
  updated_at: string
  encounters: Encounter[]
  allergies: Allergy[]
  medical_histories: any[]
}

export interface Encounter {
  id: number
  diagnoses: Diagnosis[]
  immunizations: any[]
  medications: Medication[]
  vital_signs: VitalSign[]
  lab_tests: LabTest[]
  encounter_date: string
  doctor_id: number
  appointment_id: number | null
  chief_complaint: string
  encounter_type: string
  notes: string
  created_at: string
  updated_at: string
  medical_record: number
}

export interface Diagnosis {
  id: number
  treatments: any[]
  doctor_id: number
  diagnosis_code: string
  diagnosis_description: string
  diagnosis_date: string
  notes: string
  prescription_ids: any[]
  created_at: string
  updated_at: string
  encounter: number
}

export interface Medication {
  id: number
  medication_name: string
  dosage: string
  frequency: string
  route: string
  start_date: string
  end_date: string | null
  prescribed_by: number
  reason: string
  notes: string | null
  created_at: string
  updated_at: string
  encounter: number
}

export interface VitalSign {
  id: number
  vital_type: string
  value: string
  unit: string
  recorded_by: number
  recorded_at: string
  notes: string
  created_at: string
  updated_at: string
  encounter: number
}

export interface Allergy {
  id: number
  allergen: string
  reaction: string
  severity: string
  onset_date: string
  notes: string
  created_at: string
  updated_at: string
  medical_record: number
}

export interface LabTest {
  id: number
  results: LabResult[]
  ordered_by: number
  ordered_at: string
  test_name: string
  test_code: string | null
  status: string
  collection_date: string | null
  notes: string
  lab_service_id: number | null
  created_at: string
  updated_at: string
  encounter: number
}

export interface LabResult {
  id: number
  performed_by: number
  performed_at: string
  result_value: string
  unit: string
  reference_range: string
  is_abnormal: boolean
  notes: string
  created_at: string
  updated_at: string
  lab_test: number
}

const MedicalRecordService = {
  // Lấy danh sách hồ sơ y tế của bệnh nhân hiện tại
  async getPatientMedicalRecords(): Promise<any> {
    try {
      // Lấy thông tin người dùng từ localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error("User information not found in localStorage");
        return { results: [] };
      }

      const user = JSON.parse(userStr);
      const patientId = user.id;

      // Thứ tự ưu tiên API endpoint:
      // 1. /api/medical-records/patient/{patientId}/ - Endpoint chuyên biệt cho bệnh nhân
      // 2. /api/medical-records/?patient_id={patientId} - Endpoint với query parameter
      // 3. /api/encounters/ - Endpoint thay thế để lấy hồ sơ y tế qua cuộc gặp

      // Phương pháp 1: Thử lấy hồ sơ y tế của bệnh nhân qua endpoint chuyên biệt
      try {
        console.log(`Fetching medical records for patient ${patientId} via patient endpoint`);
        const response = await apiClient.get(`/api/medical-records/patient/${patientId}/`);
        console.log("Medical records response from patient endpoint:", response.data);
        return response.data;
      } catch (patientEndpointError: any) {
        console.log(`Could not get medical records from /api/medical-records/patient/${patientId}/, trying with query parameter`);

        // Phương pháp 2: Thử lấy danh sách hồ sơ y tế với query parameter
        try {
          console.log(`Fetching medical records for patient ${patientId} via query parameter`);
          const response = await apiClient.get(`/api/medical-records/?patient_id=${patientId}`);
          console.log("Medical records response from query parameter:", response.data);
          return response.data;
        } catch (listError: any) {
          console.log("Could not get medical records list, trying alternative method");

          // Phương pháp 3: Lấy danh sách cuộc gặp và từ đó lấy hồ sơ y tế
          try {
            console.log("Fetching encounters to find medical record ID");
            const encountersResponse = await apiClient.get('/api/encounters/');

            if (encountersResponse.data &&
                encountersResponse.data.results &&
                encountersResponse.data.results.length > 0) {

              const medicalRecordId = encountersResponse.data.results[0].medical_record;
              console.log(`Found medical record ID: ${medicalRecordId}`);

              // Lấy chi tiết hồ sơ y tế
              const recordResponse = await apiClient.get(`/api/medical-records/${medicalRecordId}/`);

              // Định dạng kết quả để phù hợp với cấu trúc mong đợi
              return {
                count: 1,
                next: null,
                previous: null,
                results: [recordResponse.data]
              };
            }
          } catch (encounterError: any) {
            console.error("Error fetching encounters:", encounterError);
          }

          // Nếu tất cả phương pháp đều thất bại, trả về mảng rỗng
          return { results: [] };
        }
      }
    } catch (error: any) {
      console.error("Error fetching patient medical records:", error);
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      }
      return { results: [] };
    }
  },

  // Lấy chi tiết hồ sơ y tế
  async getMedicalRecordById(id: number): Promise<MedicalRecord> {
    try {
      console.log(`Fetching medical record details for record ${id}`);
      const response = await apiClient.get(`/api/medical-records/${id}/`);
      console.log("Medical record details response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Error fetching medical record ${id}:`, error);
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  },

  // Lấy danh sách kết quả xét nghiệm của bệnh nhân hiện tại
  async getPatientLabTests(): Promise<any> {
    try {
      // Lấy thông tin người dùng từ localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error("User information not found in localStorage");
        return { results: [] };
      }

      const user = JSON.parse(userStr);
      const patientId = user.id;

      console.log(`Fetching lab tests for patient ${patientId}`);
      const response = await apiClient.get(`/api/lab-tests/?patient_id=${patientId}`);
      console.log("Lab tests response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Error fetching patient lab tests:", error);
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      }
      return { results: [] };
    }
  },

  // Lấy chi tiết kết quả xét nghiệm
  async getLabTestById(id: number): Promise<LabTest> {
    try {
      console.log(`Fetching lab test details for test ${id}`);
      const response = await apiClient.get(`/api/lab-tests/${id}/`);
      console.log("Lab test details response:", response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Error fetching lab test ${id}:`, error);
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  },

  // Lấy thông tin bác sĩ
  async getDoctorInfo(doctorId: number): Promise<any> {
    try {
      console.log(`Fetching doctor info for doctor ${doctorId}`);

      // Thứ tự ưu tiên API endpoint:
      // 1. /api/users/doctors/{doctorId}/ - Endpoint đồng bộ với medical-record-service
      // 2. /api/users/{doctorId}/ - Endpoint chung cho tất cả người dùng
      // 3. /api/doctor-profile/{doctorId}/ - Endpoint cho profile bác sĩ
      // 4. /api/doctors/{doctorId}/ - Endpoint danh sách bác sĩ

      // Thử lấy thông tin từ API users/doctors (đồng bộ với medical-record-service)
      try {
        const response = await apiClient.get(`/api/users/doctors/${doctorId}/`);
        console.log("Doctor info response from users/doctors API:", response.data);
        return response.data;
      } catch (doctorsError) {
        console.log(`Could not get doctor info from /api/users/doctors/${doctorId}/, trying /api/users/`);

        // Thử lấy thông tin từ API users
        try {
          const userResponse = await apiClient.get(`/api/users/${doctorId}/`);
          console.log("Doctor info response from users API:", userResponse.data);
          return userResponse.data;
        } catch (userError) {
          console.log(`Could not get doctor info from /api/users/${doctorId}/, trying /api/doctor-profile/`);

          // Thử lấy thông tin từ API doctor-profile
          try {
            const profileResponse = await apiClient.get(`/api/doctor-profile/${doctorId}/`);
            console.log("Doctor profile response:", profileResponse.data);

            // Nếu API trả về thông tin profile, cần định dạng lại để phù hợp với cấu trúc mong đợi
            if (profileResponse.data && profileResponse.data.user_id) {
              return {
                id: profileResponse.data.user_id,
                first_name: profileResponse.data.first_name || "Bác sĩ",
                last_name: profileResponse.data.last_name || `#${doctorId}`,
                doctor_profile: profileResponse.data
              };
            }

            return profileResponse.data;
          } catch (profileError) {
            console.log(`Could not get doctor info from /api/doctor-profile/${doctorId}/, trying /api/doctors/`);

            // Thử lấy thông tin từ API doctors
            try {
              const doctorResponse = await apiClient.get(`/api/doctors/${doctorId}/`);
              console.log("Doctor info response from doctors API:", doctorResponse.data);
              return doctorResponse.data;
            } catch (doctorError) {
              // Nếu tất cả API đều không hoạt động, trả về thông tin giả
              console.log("Could not get doctor info from any API, using fallback data");

              // Dữ liệu giả cho bác sĩ - Mở rộng danh sách
              const doctorNames: Record<number, { first_name: string, last_name: string, specialization?: string }> = {
                1: { first_name: "Quản trị", last_name: "Viên" },
                2: { first_name: "Admin", last_name: "User" },
                3: { first_name: "Minh", last_name: "Nguyễn", specialization: "Nội tổng quát" },
                4: { first_name: "Thắng", last_name: "Nguyễn" },
                5: { first_name: "Hương", last_name: "Trần", specialization: "Tim mạch" },
                6: { first_name: "Hải", last_name: "Lê", specialization: "Nhi khoa" },
                7: { first_name: "Lan", last_name: "Phạm", specialization: "Da liễu" },
                8: { first_name: "Tuấn", last_name: "Vũ", specialization: "Thần kinh" },
                9: { first_name: "Mai", last_name: "Hoàng", specialization: "Sản phụ khoa" },
                10: { first_name: "Dũng", last_name: "Trần", specialization: "Chấn thương chỉnh hình" }
              };

              const doctorInfo = doctorNames[doctorId] || { first_name: "Bác sĩ", last_name: `#${doctorId}` };

              // Định dạng dữ liệu giả để phù hợp với cấu trúc mong đợi
              return {
                id: doctorId,
                first_name: doctorInfo.first_name,
                last_name: doctorInfo.last_name,
                doctor_profile: {
                  specialization: doctorInfo.specialization || "Đa khoa"
                }
              };
            }
          }
        }
      }
    } catch (error: any) {
      console.error(`Error fetching doctor info ${doctorId}:`, error);

      // Trả về dữ liệu giả với định dạng phù hợp
      return {
        id: doctorId,
        first_name: "Bác sĩ",
        last_name: `#${doctorId}`,
        doctor_profile: {
          specialization: "Đa khoa"
        }
      };
    }
  },

  // Lấy tất cả hồ sơ y tế (chỉ dành cho admin)
  async getAllMedicalRecords(): Promise<any> {
    try {
      const response = await apiClient.get("/api/medical-records/");
      return response.data;
    } catch (error) {
      console.error("Error fetching all medical records:", error);
      return { results: [] };
    }
  },

  // Lấy tất cả kết quả xét nghiệm (chỉ dành cho admin)
  async getAllLabTests(): Promise<any> {
    try {
      const response = await apiClient.get("/api/lab-tests/");
      return response.data;
    } catch (error) {
      console.error("Error fetching all lab tests:", error);
      return { results: [] };
    }
  },

  // Lấy danh sách cuộc gặp của bệnh nhân hiện tại
  async getPatientEncounters(): Promise<Encounter[]> {
    try {
      // Lấy thông tin người dùng từ localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error("User information not found in localStorage");
        return [];
      }

      const user = JSON.parse(userStr);
      const patientId = user.id;

      console.log(`Fetching encounters for patient ${patientId}`);
      const response = await apiClient.get(`/api/encounters/?patient_id=${patientId}`);
      console.log("Encounters response:", response.data);

      // Xử lý dữ liệu trả về
      let encounters: Encounter[] = [];

      // API trả về dữ liệu dạng phân trang (pagination)
      if (response.data && response.data.results) {
        encounters = response.data.results;
      }
      // Nếu không có trường results, trả về dữ liệu nguyên bản
      else if (Array.isArray(response.data)) {
        encounters = response.data;
      }

      return encounters;
    } catch (error: any) {
      console.error("Error fetching patient encounters:", error);
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response data:", error.response.data);
      }
      return [];
    }
  }
}

export default MedicalRecordService
