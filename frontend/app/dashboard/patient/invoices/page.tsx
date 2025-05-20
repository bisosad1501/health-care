"use client"

import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import PatientInvoices from "@/components/patient/patient-invoices"

export default function PatientInvoicesPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Hóa đơn" description="Xem và thanh toán hóa đơn của bạn" />

      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">Tất cả</TabsTrigger>
          <TabsTrigger value="pending">Chờ thanh toán</TabsTrigger>
          <TabsTrigger value="paid">Đã thanh toán</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="mt-4">
          <Card>
            <CardContent className="p-6">
              <PatientInvoices filter="all" />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="pending" className="mt-4">
          <Card>
            <CardContent className="p-6">
              <PatientInvoices filter="pending" />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="paid" className="mt-4">
          <Card>
            <CardContent className="p-6">
              <PatientInvoices filter="paid" />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
