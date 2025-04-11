"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { HeartPulse } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/providers/auth-provider"

export default function LoginPage() {
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [role, setRole] = useState(searchParams.get("role") || "")

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const selectedRole = role || (formData.get("role") as string)

    try {
      // Sử dụng hàm login từ AuthProvider
      await login(email, password, selectedRole)

      toast({
        title: "Đăng nhập thành công",
        description: `Chào mừng trở lại! Bạn đã đăng nhập với vai trò ${selectedRole}.`,
      })

      // Lưu ý: Không cần chuyển hướng ở đây vì login() trong AuthProvider đã xử lý việc này
    } catch (error) {
      toast({
        title: "Đăng nhập thất bại",
        description: error instanceof Error ? error.message : "Đã xảy ra lỗi trong quá trình đăng nhập",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <div className="mb-8 flex items-center gap-2">
        <HeartPulse className="h-8 w-8 text-teal-600" />
        <h1 className="text-2xl font-bold">Healthcare System</h1>
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription>Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" placeholder="name@example.com" required />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link href="/forgot-password" className="text-xs text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <Input id="password" name="password" type="password" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select name="role" value={role} onValueChange={setRole}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="patient">Patient</SelectItem>
                  <SelectItem value="doctor">Doctor</SelectItem>
                  <SelectItem value="nurse">Nurse</SelectItem>
                  <SelectItem value="administrator">Administrator</SelectItem>
                  <SelectItem value="pharmacist">Pharmacist</SelectItem>
                  <SelectItem value="insurance provider">Insurance Provider</SelectItem>
                  <SelectItem value="laboratory technician">Laboratory Technician</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>
            <div className="text-center text-sm">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="text-primary hover:underline">
                Register
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>

      <footer className="mt-8 text-center text-sm text-muted-foreground">
        <p>© 2025 Healthcare System. All rights reserved.</p>
      </footer>
    </div>
  )
}
