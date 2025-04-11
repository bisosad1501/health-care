"use client"

import React from "react"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "./auth-provider"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  )
}
