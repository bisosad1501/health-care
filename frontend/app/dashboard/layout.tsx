"use client"

import type React from "react"

import { usePathname } from "next/navigation"
import { useEffect } from "react"
import { useAuth } from "@/providers/auth-provider"

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const pathname = usePathname()
  const { user, isLoading, isAuthenticated } = useAuth()

  // Redirect logic based on authentication and role
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login if not authenticated
      window.location.href = "/login"
      return
    }

    if (!isLoading && isAuthenticated && user) {
      // Check if user is accessing a route they have permission for
      const role = user.role.toLowerCase()
      const currentPath = pathname.split("/")[2] // e.g., "patient" from "/dashboard/patient"

      if (currentPath && currentPath !== role) {
        // Redirect to their appropriate dashboard if they're trying to access another role's dashboard
        window.location.href = `/dashboard/${role}`
      }
    }
  }, [isLoading, isAuthenticated, user, pathname])

  // Show loading state while checking authentication
  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  // Show dashboard content if authenticated
  return <>{children}</>
}
