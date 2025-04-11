import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Bell,
  Building,
  CreditCard,
  FileCheck,
  FileText,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Settings,
  ShieldCheck,
  User,
} from "lucide-react"
import InsuranceClaims from "@/components/insurance/insurance-claims"
import InsurancePolicies from "@/components/insurance/insurance-policies"

export default function InsuranceDashboard() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="h-6 w-6 text-teal-600" />
            <h1 className="text-xl font-bold">Healthcare System</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <MessageSquare className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Avatar>
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Insurance" />
              <AvatarFallback>IN</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Insurance" />
                <AvatarFallback>IN</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">David Wilson</p>
                <p className="text-xs text-muted-foreground">Insurance Provider</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/insurance">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/insurance/claims">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileCheck className="h-4 w-4" />
                  Claims
                </Button>
              </Link>
              <Link href="/dashboard/insurance/policies">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <ShieldCheck className="h-4 w-4" />
                  Policies
                </Button>
              </Link>
              <Link href="/dashboard/insurance/providers">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Building className="h-4 w-4" />
                  Providers
                </Button>
              </Link>
              <Link href="/dashboard/insurance/payments">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <CreditCard className="h-4 w-4" />
                  Payments
                </Button>
              </Link>
              <Link href="/dashboard/insurance/reports">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Reports
                </Button>
              </Link>
              <Link href="/dashboard/insurance/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/insurance/settings">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Settings className="h-4 w-4" />
                  Settings
                </Button>
              </Link>
            </nav>
            <div className="mt-auto">
              <Link href="/login">
                <Button variant="ghost" className="w-full justify-start gap-2 text-red-500 hover:text-red-500">
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </Link>
            </div>
          </div>
        </aside>
        <main className="flex-1">
          <div className="container py-6">
            <h2 className="mb-6 text-3xl font-bold">Insurance Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Pending Claims</span>
                    <FileCheck className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">24</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">8 require review</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Approved Today</span>
                    <ShieldCheck className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">16</h3>
                    <span className="ml-2 text-xs font-medium text-green-600">$12,450 total</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Active Policies</span>
                    <FileText className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">1,248</h3>
                    <span className="ml-2 text-xs font-medium text-muted-foreground">42 expiring soon</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Monthly Payout</span>
                    <CreditCard className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">$245,320</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">+12% from last month</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="claims">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="claims">Recent Claims</TabsTrigger>
                  <TabsTrigger value="policies">Expiring Policies</TabsTrigger>
                </TabsList>
                <TabsContent value="claims" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Claims</CardTitle>
                      <CardDescription>Claims submitted in the last 7 days</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <InsuranceClaims />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="policies" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Expiring Policies</CardTitle>
                      <CardDescription>Policies expiring in the next 30 days</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <InsurancePolicies />
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
      </div>
      <footer className="border-t bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <p className="text-sm text-muted-foreground">© 2025 Healthcare System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
