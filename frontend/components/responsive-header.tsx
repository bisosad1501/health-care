"use client"

import type React from "react"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Bell, HeartPulse, LogOut, MessageSquare, Settings, User } from "lucide-react"
import MobileSidebar from "@/components/layout/mobile-sidebar"
import { useAuth } from "@/providers/auth-provider"

interface ResponsiveHeaderProps {
  menuItems: {
    href: string
    label: string
    icon: React.ReactNode
  }[]
}

export default function ResponsiveHeader({ menuItems }: ResponsiveHeaderProps) {
  const { user, logout } = useAuth()

  const logoutItem = {
    href: "/login",
    label: "Logout",
    icon: <LogOut className="h-4 w-4" />,
  }

  return (
    <header className="sticky top-0 z-10 border-b bg-background">
      <div className="container flex h-16 items-center justify-between py-4">
        <div className="flex items-center gap-2">
          <MobileSidebar
            title="Healthcare System"
            avatar={"/placeholder.svg?height=32&width=32"}
            avatarFallback={user?.firstName?.[0] + user?.lastName?.[0] || "U"}
            userName={user?.firstName + " " + user?.lastName || "User"}
            userRole={user?.role || ""}
            menuItems={menuItems}
            logoutItem={logoutItem}
          />
          <HeartPulse className="h-6 w-6 text-teal-600" />
          <h1 className="text-xl font-bold">Healthcare System</h1>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="hidden md:flex">
            <MessageSquare className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="hidden md:flex">
            <Bell className="h-5 w-5" />
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/placeholder.svg?height=32&width=32" alt="User" />
                  <AvatarFallback>{user?.firstName?.[0] + user?.lastName?.[0] || "U"}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.firstName + " " + user?.lastName || "User"}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user?.email || ""}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/dashboard/profile">
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/dashboard/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-red-600"
                onClick={() => {
                  logout()
                }}
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
