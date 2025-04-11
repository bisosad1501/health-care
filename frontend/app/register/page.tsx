"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { HeartPulse } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/providers/auth-provider"

export default function RegisterPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { register } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [role, setRole] = useState("")

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget)
    const firstName = formData.get("firstName") as string
    const lastName = formData.get("lastName") as string
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const confirmPassword = formData.get("confirmPassword") as string
    const selectedRole = role || (formData.get("role") as string)

    try {
      // Validate passwords match
      if (password !== confirmPassword) {
        throw new Error("Passwords do not match")
      }

      // Call register function from auth provider
      await register(firstName, lastName, email, password, selectedRole)

      toast({
        title: "Registration successful",
        description: "Your account has been created successfully.",
      })

      // Redirect is handled in the auth provider
    } catch (error) {
      toast({
        title: "Registration failed",
        description: error instanceof Error ? error.message : "An error occurred during registration",
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
          <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
          <CardDescription>Enter your information to create an account</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input id="firstName" name="firstName" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input id="lastName" name="lastName" required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" placeholder="name@example.com" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input id="confirmPassword" name="confirmPassword" type="password" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select name="role" value={role} onValueChange={setRole}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PATIENT">Patient</SelectItem>
                  <SelectItem value="DOCTOR">Doctor</SelectItem>
                  <SelectItem value="NURSE">Nurse</SelectItem>
                  <SelectItem value="ADMIN">Administrator</SelectItem>
                  <SelectItem value="PHARMACIST">Pharmacist</SelectItem>
                  <SelectItem value="INSURANCE">Insurance Provider</SelectItem>
                  <SelectItem value="LAB_TECH">Laboratory Technician</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? "Creating account..." : "Create account"}
            </Button>
            <div className="text-center text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-primary hover:underline">
                Login
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
