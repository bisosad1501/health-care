import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Bell,
  HeartPulse,
  Home,
  LogOut,
  MessageSquare,
  Package,
  Pill,
  Settings,
  ShoppingCart,
  User,
} from "lucide-react"
import PharmacistPrescriptions from "@/components/pharmacist/pharmacist-prescriptions"
import PharmacistInventory from "@/components/pharmacist/pharmacist-inventory"

export default function PharmacistDashboard() {
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
              <AvatarImage src="/placeholder.svg?height=32&width=32" alt="Pharmacist" />
              <AvatarFallback>PH</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r bg-background lg:block">
          <div className="flex h-full flex-col gap-2 p-4">
            <div className="flex items-center gap-2 px-2 py-4">
              <Avatar>
                <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Pharmacist" />
                <AvatarFallback>PH</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">Michael Chen</p>
                <p className="text-xs text-muted-foreground">Pharmacist</p>
              </div>
            </div>
            <nav className="grid gap-1 px-2 py-2">
              <Link href="/dashboard/pharmacist">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Home className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/pharmacist/prescriptions">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Pill className="h-4 w-4" />
                  Prescriptions
                </Button>
              </Link>
              <Link href="/dashboard/pharmacist/inventory">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <Package className="h-4 w-4" />
                  Inventory
                </Button>
              </Link>
              <Link href="/dashboard/pharmacist/orders">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <ShoppingCart className="h-4 w-4" />
                  Orders
                </Button>
              </Link>
              <Link href="/dashboard/pharmacist/profile">
                <Button variant="ghost" className="w-full justify-start gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Button>
              </Link>
              <Link href="/dashboard/pharmacist/settings">
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
            <h2 className="mb-6 text-3xl font-bold">Pharmacist Dashboard</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Pending Prescriptions</span>
                    <Pill className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">12</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">4 urgent</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Dispensed Today</span>
                    <Package className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">28</h3>
                    <span className="ml-2 text-xs font-medium text-green-600">+5 from yesterday</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Low Stock Items</span>
                    <ShoppingCart className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">7</h3>
                    <span className="ml-2 text-xs font-medium text-red-600">Reorder needed</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Expiring Soon</span>
                    <Calendar className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="mt-2 flex items-baseline">
                    <h3 className="text-2xl font-bold">15</h3>
                    <span className="ml-2 text-xs font-medium text-amber-600">Within 30 days</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6">
              <Tabs defaultValue="prescriptions">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="prescriptions">Pending Prescriptions</TabsTrigger>
                  <TabsTrigger value="inventory">Inventory Status</TabsTrigger>
                </TabsList>
                <TabsContent value="prescriptions" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Pending Prescriptions</CardTitle>
                      <CardDescription>Prescriptions waiting to be filled</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PharmacistPrescriptions />
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="inventory" className="mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Inventory Status</CardTitle>
                      <CardDescription>Current stock levels and alerts</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PharmacistInventory />
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

function Calendar(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M8 2v4" />
      <path d="M16 2v4" />
      <rect width="18" height="18" x="3" y="4" rx="2" />
      <path d="M3 10h18" />
    </svg>
  )
}
