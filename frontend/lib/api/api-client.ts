import axios from "axios"

// Tạo instance axios với cấu hình mặc định
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api",
  headers: {
    "Content-Type": "application/json",
  },
})

// Thêm interceptor để xử lý token authentication
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem("token")
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Thêm interceptor để xử lý refresh token
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Nếu lỗi 401 (Unauthorized) và chưa thử refresh token
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Gọi API refresh token (chỉ ở phía client)
        let refreshToken = null
        if (typeof window !== 'undefined') {
          refreshToken = localStorage.getItem("refreshToken")
        }

        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api"}/auth/token/refresh/`, {
          refresh_token: refreshToken,
        })

        // Lưu token mới (chỉ ở phía client)
        const { access_token, refresh_token } = response.data
        if (typeof window !== 'undefined') {
          localStorage.setItem("token", access_token)
          localStorage.setItem("refreshToken", refresh_token || refreshToken)
          console.log('Tokens refreshed and saved to localStorage')
        }

        // Cập nhật header và thực hiện lại request
        apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Nếu refresh token thất bại, đăng xuất người dùng (chỉ ở phía client)
        if (typeof window !== 'undefined') {
          localStorage.removeItem("token")
          localStorage.removeItem("refreshToken")
          window.location.href = "/login"
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
