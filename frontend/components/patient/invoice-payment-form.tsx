"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { InvoiceWithDetails } from "@/lib/api/billing-service"
import BillingService from "@/lib/api/billing-service"
import { formatCurrency } from "@/lib/utils"
import { toast } from "sonner"
import { CreditCard, Banknote, Building, Wallet } from "lucide-react"

interface InvoicePaymentFormProps {
  invoice: InvoiceWithDetails
  onSuccess: () => void
  onCancel: () => void
}

const formSchema = z.object({
  payment_method: z.enum(["CREDIT_CARD", "DEBIT_CARD", "BANK_TRANSFER", "CASH", "MOBILE_PAYMENT"]),
  amount: z.coerce.number().positive("Số tiền phải lớn hơn 0"),
  transaction_id: z.string().optional(),
  notes: z.string().optional(),
})

export default function InvoicePaymentForm({ invoice, onSuccess, onCancel }: InvoicePaymentFormProps) {
  const [loading, setLoading] = useState(false)
  const remainingAmount = invoice.balance || (invoice.total_amount - (invoice.paid_amount || 0))

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      payment_method: "CREDIT_CARD",
      amount: remainingAmount,
      transaction_id: "",
      notes: "",
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setLoading(true)
    try {
      await BillingService.addPaymentToInvoice(invoice.id, {
        ...values,
        payment_date: new Date().toISOString(),
      })
      toast.success("Thanh toán thành công")
      onSuccess()
    } catch (error) {
      console.error("Error processing payment:", error)
      toast.error("Có lỗi xảy ra khi xử lý thanh toán")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="payment_method"
          render={({ field }) => (
            <FormItem className="space-y-3">
              <FormLabel>Phương thức thanh toán</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="grid grid-cols-2 gap-4 md:grid-cols-3"
                >
                  <FormItem>
                    <FormControl>
                      <RadioGroupItem
                        value="CREDIT_CARD"
                        id="credit_card"
                        className="peer sr-only"
                      />
                    </FormControl>
                    <label
                      htmlFor="credit_card"
                      className="flex cursor-pointer flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                    >
                      <CreditCard className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Thẻ tín dụng</span>
                    </label>
                  </FormItem>
                  <FormItem>
                    <FormControl>
                      <RadioGroupItem
                        value="DEBIT_CARD"
                        id="debit_card"
                        className="peer sr-only"
                      />
                    </FormControl>
                    <label
                      htmlFor="debit_card"
                      className="flex cursor-pointer flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                    >
                      <CreditCard className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Thẻ ghi nợ</span>
                    </label>
                  </FormItem>
                  <FormItem>
                    <FormControl>
                      <RadioGroupItem
                        value="BANK_TRANSFER"
                        id="bank_transfer"
                        className="peer sr-only"
                      />
                    </FormControl>
                    <label
                      htmlFor="bank_transfer"
                      className="flex cursor-pointer flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                    >
                      <Building className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Chuyển khoản</span>
                    </label>
                  </FormItem>
                  <FormItem>
                    <FormControl>
                      <RadioGroupItem
                        value="CASH"
                        id="cash"
                        className="peer sr-only"
                      />
                    </FormControl>
                    <label
                      htmlFor="cash"
                      className="flex cursor-pointer flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                    >
                      <Banknote className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Tiền mặt</span>
                    </label>
                  </FormItem>
                  <FormItem>
                    <FormControl>
                      <RadioGroupItem
                        value="MOBILE_PAYMENT"
                        id="mobile_payment"
                        className="peer sr-only"
                      />
                    </FormControl>
                    <label
                      htmlFor="mobile_payment"
                      className="flex cursor-pointer flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                    >
                      <Wallet className="mb-3 h-6 w-6" />
                      <span className="text-sm font-medium">Ví điện tử</span>
                    </label>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid gap-4 md:grid-cols-2">
          <FormField
            control={form.control}
            name="amount"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Số tiền thanh toán</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="Nhập số tiền"
                    {...field}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value)
                      if (!isNaN(value) && value > remainingAmount) {
                        form.setValue("amount", remainingAmount)
                      } else {
                        field.onChange(e)
                      }
                    }}
                  />
                </FormControl>
                <p className="text-xs text-muted-foreground">
                  Số tiền còn lại: {formatCurrency(remainingAmount)}
                </p>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="transaction_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Mã giao dịch (nếu có)</FormLabel>
                <FormControl>
                  <Input placeholder="Nhập mã giao dịch" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Ghi chú</FormLabel>
              <FormControl>
                <Textarea placeholder="Nhập ghi chú thanh toán (nếu có)" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Hủy
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Đang xử lý..." : "Xác nhận thanh toán"}
          </Button>
        </div>
      </form>
    </Form>
  )
}
