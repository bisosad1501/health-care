import apiClient from "./api-client"

export interface LoginRequest {
  email: string
  password: string
  role?: string
}

export interface RegisterRequest {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirm: string
  role: string
}

export interface AuthResponse {
  user: {
    id: string
    first_name: string
    last_name: string
    email: string
    role: string
  }
  access: string  // JWT access token
  refresh: string  // JWT refresh token
}

const AuthService = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    try {
      console.log('Calling login API with data:', data)
      const response = await apiClient.post("/auth/login/", data)
      console.log('Login API response:', response.data)

      // Lưu token vào localStorage (chỉ ở phía client)
      if (typeof window !== 'undefined') {
        console.log('Saving tokens to localStorage:', {
          access: response.data.access ? 'exists' : 'missing',
          refresh: response.data.refresh ? 'exists' : 'missing'
        })
        if (response.data.access) {
          localStorage.setItem("token", response.data.access)
          console.log('Access token saved to localStorage')
        } else {
          console.error('Access token missing in response')
        }

        if (response.data.refresh) {
          localStorage.setItem("refreshToken", response.data.refresh)
          console.log('Refresh token saved to localStorage')
        } else {
          console.error('Refresh token missing in response')
        }
      }

      return response.data
    } catch (error) {
      console.error('Login API error:', error)

      // Xử lý lỗi từ API
      if (error.response && error.response.data) {
        const errorData = error.response.data
        console.log('Error data from API:', errorData)

        // Kiểm tra lỗi đăng nhập
        if (errorData.detail) {
          throw new Error(errorData.detail)
        }

        if (errorData.non_field_errors) {
          throw new Error(errorData.non_field_errors.join(', '))
        }

        // Xử lý các lỗi khác
        const errorMessages = []
        for (const field in errorData) {
          if (Array.isArray(errorData[field])) {
            errorMessages.push(`${field}: ${errorData[field].join(', ')}`)
          } else if (typeof errorData[field] === 'string') {
            errorMessages.push(`${field}: ${errorData[field]}`)
          }
        }

        if (errorMessages.length > 0) {
          throw new Error(errorMessages.join('\n'))
        }
      }

      // Nếu không có thông tin lỗi cụ thể, sử dụng thông báo lỗi chung
      throw new Error('Lỗi đăng nhập. Vui lòng kiểm tra email và mật khẩu.')
    }
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    try {
      console.log('Calling register API with data:', data)
      const response = await apiClient.post("/auth/register/", data)
      console.log('Register API response:', response.data)

      // Lưu token vào localStorage (chỉ ở phía client)
      if (typeof window !== 'undefined') {
        console.log('Saving tokens to localStorage:', {
          access: response.data.access ? 'exists' : 'missing',
          refresh: response.data.refresh ? 'exists' : 'missing'
        })
        if (response.data.access) {
          localStorage.setItem("token", response.data.access)
          console.log('Access token saved to localStorage')
        } else {
          console.error('Access token missing in response')
        }

        if (response.data.refresh) {
          localStorage.setItem("refreshToken", response.data.refresh)
          console.log('Refresh token saved to localStorage')
        } else {
          console.error('Refresh token missing in response')
        }
      }

      return response.data
    } catch (error) {
      console.error('Register API error:', error)

      // Xử lý lỗi từ API
      if (error.response && error.response.data) {
        const errorData = error.response.data
        console.log('Error data from API:', errorData)

        // Kiểm tra lỗi email đã tồn tại
        if (errorData.email && Array.isArray(errorData.email) && errorData.email.some(msg => msg.includes('user with this email already exists'))) {
          throw new Error('Email đã được sử dụng. Vui lòng chọn email khác.')
        }

        // Xử lý các lỗi khác
        const errorMessages = []
        for (const field in errorData) {
          if (Array.isArray(errorData[field])) {
            errorMessages.push(`${field}: ${errorData[field].join(', ')}`)
          } else if (typeof errorData[field] === 'string') {
            errorMessages.push(`${field}: ${errorData[field]}`)
          }
        }

        if (errorMessages.length > 0) {
          throw new Error(errorMessages.join('\n'))
        }
      }

      // Nếu không có thông tin lỗi cụ thể, sử dụng thông báo lỗi chung
      throw new Error('Lỗi đăng ký tài khoản. Vui lòng thử lại sau.')
    }
  },

  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await apiClient.post("/auth/forgot-password/", { email })
    return response.data
  },

  resetPassword: async (token: string, password: string): Promise<{ message: string }> => {
    const response = await apiClient.post("/auth/reset-password/", { token, password })
    return response.data
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/auth/logout/")
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      // Luôn xóa token khỏi localStorage (chỉ ở phía client)
      if (typeof window !== 'undefined') {
        localStorage.removeItem("token")
        localStorage.removeItem("refreshToken")
      }
    }
  },

  getCurrentUser: async (): Promise<AuthResponse["user"]> => {
    try {
      console.log('Calling getCurrentUser API...')

      // Thay vì gọi API /users/me/, chúng ta sử dụng thông tin từ token JWT
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token')
        console.log('Token from localStorage:', token ? 'exists' : 'not found')

        if (token) {
          // Parse JWT token
          try {
            // Kiểm tra token có đúng định dạng JWT không (xxx.yyy.zzz)
            const parts = token.split('.')
            if (parts.length !== 3) {
              console.error('Invalid token format: token does not have 3 parts')
              throw new Error('Invalid token format')
            }

            const base64Url = parts[1]
            if (!base64Url) {
              console.error('Invalid token format: payload part is missing')
              throw new Error('Invalid token format')
            }

            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')

            // Sử dụng atob an toàn hơn với try-catch
            let decodedString
            try {
              decodedString = atob(base64)
            } catch (e) {
              console.error('Error decoding base64:', e)
              throw new Error('Invalid token encoding')
            }

            const jsonPayload = decodeURIComponent(
              decodedString.split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
              }).join('')
            )

            const payload = JSON.parse(jsonPayload)
            console.log('Token payload:', payload)

            // Trích xuất thông tin người dùng từ payload
            return {
              id: payload.user_id,
              first_name: payload.first_name,
              last_name: payload.last_name,
              email: payload.email,
              role: payload.role
            }
          } catch (parseError) {
            console.error('Error parsing JWT token:', parseError)
            throw new Error('Invalid token format')
          }
        }
      }

      throw new Error('No token available')
    } catch (error) {
      console.error('getCurrentUser error:', error)
      throw error
    }
  },
}

export default AuthService
