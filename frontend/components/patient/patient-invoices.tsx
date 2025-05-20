"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, CreditCard, ExternalLink, FileText, AlertCircle } from "lucide-react"
import BillingService, { Invoice } from "@/lib/api/billing-service"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"

interface PatientInvoicesProps {
  filter?: "all" | "pending" | "paid"
}

export default function PatientInvoices({ filter = "all" }: PatientInvoicesProps) {
  const router = useRouter()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await BillingService.getAllInvoices()

        // Kiểm tra cấu trúc dữ liệu trả về
        console.log("API response:", response)

        // Xử lý dữ liệu trả về, có thể là mảng hoặc đối tượng có thuộc tính results
        let data = Array.isArray(response) ? response :
                  response && response.results ? response.results : []

        // Filter invoices based on the filter prop
        let filteredData = data
        if (filter === "pending") {
          filteredData = data.filter(invoice =>
            invoice.status === "PENDING" || invoice.status === "PARTIALLY_PAID" || invoice.status === "OVERDUE"
          )
        } else if (filter === "paid") {
          filteredData = data.filter(invoice => invoice.status === "PAID")
        }

        setInvoices(filteredData)
      } catch (error) {
        console.error("Error fetching invoices:", error)
        toast.error("Không thể tải danh sách hóa đơn")
        setInvoices([]) // Đặt mảng rỗng để tránh lỗi
      } finally {
        setLoading(false)
      }
    }

    fetchInvoices()
  }, [filter])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "PAID":
        return <Badge className="bg-green-500">Đã thanh toán</Badge>
      case "PARTIALLY_PAID":
        return <Badge className="bg-blue-500">Thanh toán một phần</Badge>
      case "PENDING":
        return <Badge className="bg-yellow-500">Chờ thanh toán</Badge>
      case "OVERDUE":
        return <Badge className="bg-red-500">Quá hạn</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-start justify-between rounded-lg border p-4">
            <div className="flex items-start gap-3">
              <Skeleton className="h-10 w-10 rounded-md" />
              <div>
                <Skeleton className="h-5 w-40" />
                <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </div>
            <Skeleton className="h-9 w-24" />
          </div>
        ))}
      </div>
    )
  }

  if (invoices.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-medium">Không có hóa đơn nào</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          {filter === "pending"
            ? "Bạn không có hóa đơn nào đang chờ thanh toán."
            : filter === "paid"
              ? "Bạn chưa có hóa đơn nào đã thanh toán."
              : "Bạn chưa có hóa đơn nào."}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {invoices.map((invoice) => (
        <div key={invoice.id} className="flex items-start justify-between rounded-lg border p-4">
          <div className="flex items-start gap-3">
            <div className="rounded-md bg-primary/10 p-2">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h4 className="font-medium">Hóa đơn #{invoice.id}</h4>
              <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Ngày tạo: {formatDate(invoice.invoice_date)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <CreditCard className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Số tiền: {formatCurrency(invoice.total_amount)}</span>
                </div>
                {getStatusBadge(invoice.status)}
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 gap-1"
            onClick={() => router.push(`/dashboard/patient/invoices/${invoice.id}`)}
          >
            <span>Chi tiết</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </Button>
        </div>
      ))}
    </div>
  )
}
