"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Edit, MoreHorizontal, Search, Shield, Trash, UserPlus } from "lucide-react"

export default function AdminUsersList() {
  const [searchQuery, setSearchQuery] = useState("")

  const users = [
    {
      id: "1",
      name: "Dr. Sarah Johnson",
      email: "sarah.johnson@example.com",
      role: "DOCTOR",
      specialty: "Cardiology",
      status: "active",
      lastActive: "2 hours ago",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: "2",
      name: "John Doe",
      email: "john.doe@example.com",
      role: "PATIENT",
      status: "active",
      lastActive: "1 day ago",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: "3",
      name: "Emma Wilson",
      email: "emma.wilson@example.com",
      role: "NURSE",
      department: "Cardiology",
      status: "active",
      lastActive: "5 hours ago",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: "4",
      name: "Michael Chen",
      email: "michael.chen@example.com",
      role: "PHARMACIST",
      status: "inactive",
      lastActive: "2 weeks ago",
      avatar: "/placeholder.svg?height=40&width=40",
    },
    {
      id: "5",
      name: "Lisa Brown",
      email: "lisa.brown@example.com",
      role: "ADMINISTRATOR",
      status: "active",
      lastActive: "Just now",
      avatar: "/placeholder.svg?height=40&width=40",
    },
  ]

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.role.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search users..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button className="gap-1">
          <UserPlus className="h-4 w-4" />
          Add User
        </Button>
      </div>

      <div className="rounded-md border">
        <div className="grid grid-cols-12 border-b bg-muted/50 p-4 text-sm font-medium">
          <div className="col-span-4">User</div>
          <div className="col-span-3">Role</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2">Last Active</div>
          <div className="col-span-1 text-right">Actions</div>
        </div>

        {filteredUsers.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">No users found</div>
        ) : (
          filteredUsers.map((user) => (
            <div key={user.id} className="grid grid-cols-12 items-center border-b p-4 text-sm last:border-0">
              <div className="col-span-4 flex items-center gap-3">
                <Avatar>
                  <AvatarImage src={user.avatar} alt={user.name} />
                  <AvatarFallback>
                    {user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{user.name}</div>
                  <div className="text-xs text-muted-foreground">{user.email}</div>
                </div>
              </div>
              <div className="col-span-3">
                <Badge
                  variant="outline"
                  className={
                    user.role === "ADMINISTRATOR"
                      ? "bg-purple-50 text-purple-700 hover:bg-purple-50 hover:text-purple-700"
                      : user.role === "DOCTOR"
                        ? "bg-blue-50 text-blue-700 hover:bg-blue-50 hover:text-blue-700"
                        : user.role === "NURSE"
                          ? "bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
                          : user.role === "PHARMACIST"
                            ? "bg-amber-50 text-amber-700 hover:bg-amber-50 hover:text-amber-700"
                            : "bg-gray-50 text-gray-700 hover:bg-gray-50 hover:text-gray-700"
                  }
                >
                  {user.role}
                </Badge>
                {user.specialty && <div className="mt-1 text-xs text-muted-foreground">{user.specialty}</div>}
                {user.department && <div className="mt-1 text-xs text-muted-foreground">{user.department}</div>}
              </div>
              <div className="col-span-2">
                <Badge
                  variant="outline"
                  className={
                    user.status === "active"
                      ? "bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
                      : "bg-red-50 text-red-700 hover:bg-red-50 hover:text-red-700"
                  }
                >
                  {user.status}
                </Badge>
              </div>
              <div className="col-span-2 text-muted-foreground">{user.lastActive}</div>
              <div className="col-span-1 text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                      <span className="sr-only">Actions</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Shield className="mr-2 h-4 w-4" />
                      Permissions
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-red-600">
                      <Trash className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
