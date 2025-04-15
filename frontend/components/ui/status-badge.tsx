"use client"

import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type StatusType = "success" | "warning" | "error" | "info" | "default"

interface StatusBadgeProps {
  status: StatusType
  text: string
  className?: string
  animate?: boolean
}

export function StatusBadge({ status, text, className, animate = true }: StatusBadgeProps) {
  const getStatusClass = () => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-800 hover:bg-green-100 hover:text-green-800"
      case "warning":
        return "bg-amber-100 text-amber-800 hover:bg-amber-100 hover:text-amber-800"
      case "error":
        return "bg-red-100 text-red-800 hover:bg-red-100 hover:text-red-800"
      case "info":
        return "bg-blue-100 text-blue-800 hover:bg-blue-100 hover:text-blue-800"
      default:
        return "bg-gray-100 text-gray-800 hover:bg-gray-100 hover:text-gray-800"
    }
  }

  const BadgeContent = () => (
    <span className="flex items-center gap-1">
      {status === "success" && <span className="h-1.5 w-1.5 rounded-full bg-green-600"></span>}
      {status === "warning" && <span className="h-1.5 w-1.5 rounded-full bg-amber-600"></span>}
      {status === "error" && <span className="h-1.5 w-1.5 rounded-full bg-red-600"></span>}
      {status === "info" && <span className="h-1.5 w-1.5 rounded-full bg-blue-600"></span>}
      {status === "default" && <span className="h-1.5 w-1.5 rounded-full bg-gray-600"></span>}
      {text}
    </span>
  )

  if (animate) {
    return (
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        <Badge className={cn(getStatusClass(), className)}>
          <BadgeContent />
        </Badge>
      </motion.div>
    )
  }

  return (
    <Badge className={cn(getStatusClass(), className)}>
      <BadgeContent />
    </Badge>
  )
}
