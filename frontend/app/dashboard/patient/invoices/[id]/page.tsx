"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ChevronLeft, Download, CreditCard, FileText, Clock, CheckCircle, AlertCircle } from "lucide-react"
import BillingService, { InvoiceWithDetails } from "@/lib/api/billing-service"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import InvoicePaymentForm from "@/components/patient/invoice-payment-form"

export default function InvoiceDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [invoice, setInvoice] = useState<InvoiceWithDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [showPaymentForm, setShowPaymentForm] = useState(false)

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        const data = await BillingService.getInvoiceById(parseInt(params.id))
        console.log("Invoice details:", data)
        setInvoice(data)
      } catch (error) {
        console.error("Error fetching invoice:", error)
        toast.error("Không thể tải thông tin hóa đơn")
      } finally {
        setLoading(false)
      }
    }

    fetchInvoice()
  }, [params.id])

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

  const handleExportPdf = async () => {
    try {
      const pdfBlob = await BillingService.exportInvoicePdf(parseInt(params.id))

      // Tạo URL cho blob
      const url = window.URL.createObjectURL(pdfBlob)

      // Tạo link tạm thời và kích hoạt tải xuống
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `hoa-don-${invoice?.invoice_number || params.id}.pdf`)
      document.body.appendChild(link)
      link.click()

      // Dọn dẹp
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.success("Xuất hóa đơn PDF thành công")
    } catch (error) {
      console.error("Error exporting invoice to PDF:", error)
      toast.error("Không thể xuất hóa đơn PDF")
    }
  }

  const handleApplyInsurance = async () => {
    try {
      const updatedInvoice = await BillingService.applyInsurance(parseInt(params.id))
      setInvoice(updatedInvoice)
      toast.success("Đã áp dụng bảo hiểm thành công")
    } catch (error) {
      console.error("Error applying insurance:", error)
      toast.error("Không thể áp dụng bảo hiểm")
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Chi tiết hóa đơn" description="Đang tải..." />
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <Skeleton className="h-8 w-1/3" />
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-1/5" />
              <Separator className="my-4" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!invoice) {
    return (
      <div className="space-y-6">
        <PageHeader title="Chi tiết hóa đơn" description="Không tìm thấy hóa đơn" />
        <Card>
          <CardContent className="p-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
            <h3 className="mt-4 text-lg font-medium">Không tìm thấy hóa đơn</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Hóa đơn bạn đang tìm kiếm không tồn tại hoặc bạn không có quyền truy cập.
            </p>
            <Button className="mt-4" onClick={() => router.back()}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              Quay lại
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Hóa đơn #${invoice.id}`}
        description={`Ngày tạo: ${formatDate(invoice.issue_date)}`}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.back()}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              Quay lại
            </Button>
            <Button variant="outline" onClick={handleExportPdf}>
              <Download className="mr-2 h-4 w-4" />
              Tải PDF
            </Button>
            {invoice.status !== "PAID" && (
              <>
                <Button onClick={() => setShowPaymentForm(true)}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Thanh toán
                </Button>
                {invoice.insurance_claims?.length === 0 && (
                  <Button variant="secondary" onClick={handleApplyInsurance}>
                    <FileText className="mr-2 h-4 w-4" />
                    Áp dụng bảo hiểm
                  </Button>
                )}
              </>
            )}
          </div>
        }
      />

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Chi tiết hóa đơn</CardTitle>
            {getStatusBadge(invoice.status)}
          </div>
          <CardDescription>
            Hạn thanh toán: {formatDate(invoice.due_date)}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Thông tin bệnh nhân</h3>
                <div className="mt-2">
                  <p className="font-medium">{invoice.patient?.first_name} {invoice.patient?.last_name}</p>
                  <p className="text-sm text-muted-foreground">{invoice.patient?.email}</p>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">Thông tin thanh toán</h3>
                <div className="mt-2">
                  <p className="text-sm">Tổng tiền: <span className="font-medium">{formatCurrency(invoice.total_amount)}</span></p>
                  <p className="text-sm">Đã thanh toán: <span className="font-medium">{formatCurrency(invoice.paid_amount || 0)}</span></p>
                  <p className="text-sm">Còn lại: <span className="font-medium">{formatCurrency(invoice.balance || (invoice.total_amount - (invoice.paid_amount || 0)))}</span></p>
                </div>
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="mb-4 text-sm font-medium">Chi tiết các mục</h3>
              <div className="rounded-md border">
                <table className="min-w-full divide-y divide-border">
                  <thead>
                    <tr className="bg-muted/50">
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Mô tả</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground">Số lượng</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Đơn giá</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Thành tiền</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {invoice.items?.map((item) => (
                      <tr key={item.id}>
                        <td className="px-4 py-3 text-sm">{item.description}</td>
                        <td className="px-4 py-3 text-center text-sm">{item.quantity}</td>
                        <td className="px-4 py-3 text-right text-sm">{formatCurrency(item.unit_price)}</td>
                        <td className="px-4 py-3 text-right text-sm font-medium">{formatCurrency(item.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-muted/50">
                      <td colSpan={3} className="px-4 py-3 text-right text-sm font-medium">Tổng cộng</td>
                      <td className="px-4 py-3 text-right text-sm font-medium">{formatCurrency(invoice.total_amount)}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            {invoice.payments && invoice.payments.length > 0 && (
              <>
                <Separator />
                <div>
                  <h3 className="mb-4 text-sm font-medium">Lịch sử thanh toán</h3>
                  <div className="rounded-md border">
                    <table className="min-w-full divide-y divide-border">
                      <thead>
                        <tr className="bg-muted/50">
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Ngày</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Phương thức</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Trạng thái</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Số tiền</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {invoice.payments.map((payment) => (
                          <tr key={payment.id}>
                            <td className="px-4 py-3 text-sm">{formatDate(payment.payment_date)}</td>
                            <td className="px-4 py-3 text-sm">{payment.payment_method}</td>
                            <td className="px-4 py-3 text-sm">
                              {payment.status === "COMPLETED" ? (
                                <span className="inline-flex items-center text-green-600">
                                  <CheckCircle className="mr-1 h-3 w-3" />
                                  Hoàn thành
                                </span>
                              ) : (
                                <span className="inline-flex items-center text-yellow-600">
                                  <Clock className="mr-1 h-3 w-3" />
                                  Đang xử lý
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right text-sm font-medium">{formatCurrency(payment.amount)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {invoice.insurance_claims && invoice.insurance_claims.length > 0 && (
              <>
                <Separator />
                <div>
                  <h3 className="mb-4 text-sm font-medium">Yêu cầu bảo hiểm</h3>
                  <div className="rounded-md border">
                    <table className="min-w-full divide-y divide-border">
                      <thead>
                        <tr className="bg-muted/50">
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Mã yêu cầu</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Ngày gửi</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Trạng thái</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Số tiền yêu cầu</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Số tiền được duyệt</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {invoice.insurance_claims.map((claim) => (
                          <tr key={claim.id}>
                            <td className="px-4 py-3 text-sm">{claim.claim_number}</td>
                            <td className="px-4 py-3 text-sm">{formatDate(claim.submission_date)}</td>
                            <td className="px-4 py-3 text-sm">
                              <Badge variant="outline">{claim.status}</Badge>
                            </td>
                            <td className="px-4 py-3 text-right text-sm">{formatCurrency(claim.claim_amount)}</td>
                            <td className="px-4 py-3 text-right text-sm font-medium">
                              {claim.approved_amount ? formatCurrency(claim.approved_amount) : "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {invoice.notes && (
              <>
                <Separator />
                <div>
                  <h3 className="mb-2 text-sm font-medium">Ghi chú</h3>
                  <p className="text-sm text-muted-foreground">{invoice.notes}</p>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {showPaymentForm && (
        <Card>
          <CardHeader>
            <CardTitle>Thanh toán hóa đơn</CardTitle>
            <CardDescription>
              Vui lòng chọn phương thức thanh toán và nhập thông tin thanh toán
            </CardDescription>
          </CardHeader>
          <CardContent>
            <InvoicePaymentForm
              invoice={invoice}
              onSuccess={() => {
                setShowPaymentForm(false)
                // Reload invoice data
                BillingService.getInvoiceById(parseInt(params.id)).then(setInvoice)
              }}
              onCancel={() => setShowPaymentForm(false)}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
