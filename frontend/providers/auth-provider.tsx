"use client"

import type React from "react"

import { createContext, useContext, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import AuthService from "@/lib/api/auth-service"

export interface User {
  id: string
  first_name: string
  last_name: string
  email: string
  role: "PATIENT" | "DOCTOR" | "NURSE" | "ADMIN" | "PHARMACIST" | "INSURANCE" | "LAB_TECH"
  permissions?: string[]
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string, role?: string) => Promise<void>
  register: (firstName: string, lastName: string, email: string, password: string, role: string) => Promise<void>
  logout: () => Promise<void>
  hasPermission: (permission: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Kiểm tra xem người dùng đã đăng nhập chưa
    const checkAuth = async () => {
      console.log('Running checkAuth...')
      try {
        // Kiểm tra token trong localStorage (chỉ ở phía client)
        const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null
        console.log('Token from localStorage:', token ? 'exists' : 'not found')

        if (token) {
          try {
            // Gọi API để lấy thông tin người dùng hiện tại
            const currentUser = await AuthService.getCurrentUser()

            // Chuyển đổi dữ liệu người dùng
            const user: User = {
              id: currentUser.id,
              first_name: currentUser.first_name,
              last_name: currentUser.last_name,
              email: currentUser.email,
              role: currentUser.role as User["role"],
            }

            setUser(user)
          } catch (error) {
            console.error("Failed to get current user:", error)
            if (typeof window !== 'undefined') {
              localStorage.removeItem("token")
              localStorage.removeItem("refreshToken")
            }
          }
        }
      } catch (error) {
        console.error("Auth check failed:", error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string, role?: string) => {
    setIsLoading(true)
    try {
      // Gọi API đăng nhập thật
      const response = await AuthService.login({ email, password, role })
      console.log('Login response in auth provider:', response)

      // Kiểm tra token đã được lưu chưa
      if (typeof window !== 'undefined') {
        const savedToken = localStorage.getItem('token')
        console.log('Token in localStorage after login:', savedToken ? 'exists' : 'not found')
      }

      // Chuyển đổi dữ liệu người dùng từ API
      const userData = response.user || {}

      const user: User = {
        id: userData.id,
        first_name: userData.first_name,
        last_name: userData.last_name,
        email: userData.email,
        role: userData.role as User["role"],
      }

      // Lưu token đã được xử lý trong AuthService

      setUser(user)

      // Redirect based on role
      if (role) {
        const dashboardPath = role.toLowerCase()
        // Xử lý các trường hợp đặc biệt
        let redirectPath = "/dashboard/"

        switch(dashboardPath) {
          case "administrator":
            redirectPath += "admin"
            break
          case "insurance provider":
            redirectPath += "insurance"
            break
          case "laboratory technician":
            redirectPath += "lab-tech"
            break
          default:
            redirectPath += dashboardPath
        }

        router.push(redirectPath)
      } else {
        router.push("/dashboard")
      }
    } catch (error) {
      console.error("Login failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (firstName: string, lastName: string, email: string, password: string, role: string) => {
    setIsLoading(true)
    try {
      // Gọi API đăng ký thật
      const response = await AuthService.register({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        password_confirm: password, // Yêu cầu xác nhận mật khẩu
        role
      })

      // Chuyển đổi dữ liệu người dùng từ API
      const userData = response.user || {}

      const user: User = {
        id: userData.id,
        first_name: userData.first_name,
        last_name: userData.last_name,
        email: userData.email,
        role: userData.role as User["role"],
      }

      // Lưu token đã được xử lý trong AuthService

      setUser(user)

      // Redirect based on role
      router.push(`/dashboard/${role.toLowerCase()}`)
    } catch (error) {
      console.error("Registration failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      // Gọi API đăng xuất thật
      await AuthService.logout()

      // Xóa trạng thái người dùng
      setUser(null)

      // Chuyển hướng đến trang đăng nhập
      router.push("/login")
    } catch (error) {
      console.error("Logout failed:", error)

      // Ngay cả khi đăng xuất thất bại, vẫn xóa trạng thái người dùng và chuyển hướng
      setUser(null)
      router.push("/login")
    }
  }

  const hasPermission = (permission: string) => {
    if (!user) return false
    if (user.role === "ADMIN") return true
    return user.permissions?.includes(permission) || false
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
