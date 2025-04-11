"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Menu } from "lucide-react"

interface MobileSidebarProps {
  title: string
  avatar: string
  avatarFallback: string
  userName: string
  userRole: string
  menuItems: {
    href: string
    label: string
    icon: React.ReactNode
  }[]
  logoutItem: {
    href: string
    label: string
    icon: React.ReactNode
  }
}

export default function MobileSidebar({
  title,
  avatar,
  avatarFallback,
  userName,
  userRole,
  menuItems,
  logoutItem,
}: MobileSidebarProps) {
  const [open, setOpen] = useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="p-0">
        <SheetHeader className="border-b p-4">
          <SheetTitle>{title}</SheetTitle>
        </SheetHeader>
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-2 border-b p-4">
            <Avatar>
              <AvatarImage src={avatar} alt={userName} />
              <AvatarFallback>{avatarFallback}</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{userName}</p>
              <p className="text-xs text-muted-foreground">{userRole}</p>
            </div>
          </div>
          <nav className="flex-1 overflow-auto p-4">
            <div className="grid gap-1">
              {menuItems.map((item, index) => (
                <Link key={index} href={item.href} onClick={() => setOpen(false)}>
                  <Button variant="ghost" className="w-full justify-start gap-2">
                    {item.icon}
                    {item.label}
                  </Button>
                </Link>
              ))}
            </div>
          </nav>
          <div className="border-t p-4">
            <Link href={logoutItem.href} onClick={() => setOpen(false)}>
              <Button variant="ghost" className="w-full justify-start gap-2 text-red-500 hover:text-red-500">
                {logoutItem.icon}
                {logoutItem.label}
              </Button>
            </Link>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
