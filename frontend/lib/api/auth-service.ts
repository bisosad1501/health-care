import apiClient from "./api-client"

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  role: string
  gender?: string
  phone_number?: string
  birth_date?: string
}

interface AuthResponse {
  access: string
  refresh: string
  user: {
    id: number
    email: string
    first_name: string
    last_name: string
    role: string
    gender?: string
    phone_number?: string
    birth_date?: string
  }
}

const AuthService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log("[DEBUG] Calling login API...");
      const response = await apiClient.post("/api/auth/login/", credentials);
      console.log("[DEBUG] Login API response:", {
        hasAccess: !!response.data.access,
        hasRefresh: !!response.data.refresh,
        hasUser: !!response.data.user
      });

      // Lưu token và thông tin người dùng
      if (response.data.access && response.data.refresh) {
        console.log("[DEBUG] Saving tokens to localStorage...");
        // Lưu trực tiếp vào localStorage
        if (typeof window !== "undefined") {
          localStorage.setItem("token", response.data.access);
          localStorage.setItem("refreshToken", response.data.refresh);
          localStorage.setItem("user", JSON.stringify(response.data.user));
          if (response.data.user?.role) {
            localStorage.setItem("userRole", response.data.user.role);
          }

          // Kiểm tra xem token đã được lưu chưa
          console.log("[DEBUG] Checking localStorage after saving:", {
            token: localStorage.getItem("token") ? "Saved" : "Not saved",
            refreshToken: localStorage.getItem("refreshToken") ? "Saved" : "Not saved",
            user: localStorage.getItem("user") ? "Saved" : "Not saved",
            userRole: localStorage.getItem("userRole")
          });
        }

        // Gọi các phương thức helper
        this.setTokens(response.data.access, response.data.refresh);
        this.saveUserInfo(response.data.user);
      } else {
        console.log("[DEBUG] No tokens in response");
      }

      return response.data;
    } catch (error: any) {
      console.error("Login error:", error.response?.data || error.message);
      throw error;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await apiClient.post("/api/auth/register/", data)
      // Lưu token và thông tin người dùng nếu đăng ký thành công
      if (response.data.access && response.data.refresh) {
        this.setTokens(response.data.access, response.data.refresh)
        this.saveUserInfo(response.data.user)
      }
      return response.data
    } catch (error: any) {
      console.error("Register error:", error.response?.data || error.message)
      throw error
    }
  },

  async logout(refreshToken: string): Promise<void> {
    // Xóa token trước tiên để đảm bảo người dùng luôn được đăng xuất
    this.clearTokens()
    console.log("Tokens cleared successfully")

    // Nếu không có refresh token, không cần gọi API
    if (!refreshToken || refreshToken === "mock_refresh_token") {
      return
    }

    try {
      // Gọi API đăng xuất để blacklist token trên server
      // Thử cả hai cách gọi API
      try {
        // Cách 1: Sử dụng refresh_token
        await apiClient.post("/api/auth/logout/", { refresh_token: refreshToken })
        console.log("Logout API call successful with refresh_token parameter")
        return
      } catch (error1) {
        console.log("First logout attempt failed, trying with refresh parameter")

        try {
          // Cách 2: Sử dụng refresh
          await apiClient.post("/api/auth/logout/", { refresh: refreshToken })
          console.log("Logout API call successful with refresh parameter")
        } catch (error2: any) {
          // Nếu cả hai cách đều thất bại, ghi log lỗi
          console.error("Logout API error:",
            error2.response?.data || error2.message || "Unknown error")
        }
      }
    } catch (error: any) {
      // Xử lý lỗi chung
      console.error("Logout error:", error.message || "Unknown error")
    }
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    try {
      const response = await apiClient.post("/api/auth/token/refresh/", { refresh: refreshToken })
      return response.data
    } catch (error: any) {
      console.error("Token refresh error:", error.response?.data || error.message)
      throw error
    }
  },

  async validateToken(): Promise<{ valid: boolean; user: any }> {
    try {
      // Kiểm tra xem có token trong localStorage không
      const token = this.getToken();
      if (!token) {
        return { valid: false, user: null };
      }

      // Gọi API để xác thực token
      const response = await apiClient.get("/api/auth/validate-token/");

      // API Gateway trả về thông tin người dùng nếu token hợp lệ, hoặc các trường null nếu token không hợp lệ
      if (response.data && response.data.id && response.data.email && response.data.role) {
        // Trả về thông tin người dùng với valid=true
        return {
          valid: true,
          user: {
            id: response.data.id,
            email: response.data.email,
            role: response.data.role,
            first_name: response.data.first_name,
            last_name: response.data.last_name
          }
        };
      } else {
        // Nếu API không trả về thông tin người dùng hợp lệ, thử lấy từ localStorage
        const savedUser = this.getUserInfo();
        if (savedUser) {
          return { valid: true, user: savedUser };
        }
      }

      // Nếu không có thông tin người dùng hợp lệ, trả về token không hợp lệ
      return { valid: false, user: null };
    } catch (error: any) {
      console.error("Token validation error:", error.response?.data || error.message);

      // Nếu gặp lỗi khi gọi API, thử lấy thông tin người dùng từ localStorage
      try {
        const savedUser = this.getUserInfo();
        if (savedUser) {
          return { valid: true, user: savedUser };
        }
      } catch (localStorageError) {
        console.error("Lỗi khi lấy thông tin người dùng từ localStorage:", localStorageError);
      }

      return { valid: false, user: null };
    }
  },

  getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("token")
    }
    return null
  },

  getRefreshToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("refreshToken")
    }
    return null
  },

  setTokens(access: string, refresh: string): void {
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem("token", access);
        localStorage.setItem("refreshToken", refresh);
      } catch (error) {
        console.error("Lỗi khi lưu token vào localStorage:", error);
      }
    }
  },

  clearTokens(): void {
    if (typeof window !== "undefined") {
      try {
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("user");
        localStorage.removeItem("userRole");
      } catch (error) {
        console.error("Lỗi khi xóa token:", error);
      }
    }
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  },

  saveUserInfo(user: any): void {
    if (typeof window !== "undefined") {
      try {
        const userJson = JSON.stringify(user);
        localStorage.setItem("user", userJson);

        if (user.role) {
          localStorage.setItem("userRole", user.role);
        }
      } catch (error) {
        console.error("Lỗi khi lưu thông tin người dùng vào localStorage:", error);
      }
    }
  },

  getUserInfo(): any {
    if (typeof window !== "undefined") {
      const userJson = localStorage.getItem("user")
      if (userJson) {
        try {
          return JSON.parse(userJson)
        } catch (error) {
          console.error("Lỗi khi phân tích thông tin người dùng:", error)
          return null
        }
      }
    }
    return null
  },

  getUserRole(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("userRole")
    }
    return null
  }
}

export default AuthService
