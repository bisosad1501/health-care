import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Calendar, FileText, HeartPulse, Pill, Stethoscope, Users } from "lucide-react"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="h-6 w-6 text-teal-600" />
            <h1 className="text-xl font-bold">Healthcare System</h1>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-sm font-medium text-primary">
              Home
            </Link>
            <Link href="/about" className="text-sm font-medium text-muted-foreground hover:text-primary">
              About
            </Link>
            <Link href="/services" className="text-sm font-medium text-muted-foreground hover:text-primary">
              Services
            </Link>
            <Link href="/contact" className="text-sm font-medium text-muted-foreground hover:text-primary">
              Contact
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/register" className="hidden md:block">
              <Button>Register</Button>
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-teal-50 to-white">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
              <div className="space-y-4">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Comprehensive Healthcare Management System
                </h1>
                <p className="text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  A complete solution for managing healthcare operations including patient management, appointment
                  scheduling, medical records, pharmacy, billing, and laboratory services.
                </p>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Link href="/register">
                    <Button size="lg">Get Started</Button>
                  </Link>
                  <Link href="/login">
                    <Button size="lg" variant="outline">
                      Login
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="flex justify-center">
                <img
                  src="/placeholder.svg?height=400&width=500"
                  alt="Healthcare System"
                  className="rounded-lg object-cover"
                  width={500}
                  height={400}
                />
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Key Features</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Our healthcare system provides a comprehensive set of features to streamline healthcare operations.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 mt-8">
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Users className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Patient Management</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Efficiently manage patient information, medical history, and personal details.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Calendar className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Appointment Scheduling</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Schedule, reschedule, and manage appointments with ease and efficiency.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <FileText className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Medical Records</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Securely store and access electronic health records for comprehensive patient care.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Pill className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Pharmacy Management</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Manage prescriptions, inventory, and dispensing of medications.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Activity className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Laboratory Services</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Track and manage medical tests, samples, and results efficiently.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Stethoscope className="h-8 w-8 text-teal-600" />
                  <div className="grid gap-1">
                    <CardTitle>Doctor Portal</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Specialized interface for doctors to manage patients, appointments, and medical records.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">User Roles</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Our system supports various user roles with specialized interfaces and permissions.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 mt-8">
              {[
                {
                  title: "Patient",
                  description: "Access medical records, schedule appointments, view prescriptions, and pay bills.",
                },
                {
                  title: "Doctor",
                  description: "Manage patient care, appointments, prescriptions, and medical records.",
                },
                {
                  title: "Nurse",
                  description: "Assist doctors, manage patient care, and update medical records.",
                },
                {
                  title: "Administrator",
                  description: "Manage users, system configuration, and overall operations.",
                },
                {
                  title: "Pharmacist",
                  description: "Manage prescriptions, medication inventory, and dispensing.",
                },
                {
                  title: "Insurance Provider",
                  description: "Process insurance claims, verify coverage, and manage policies.",
                },
                {
                  title: "Laboratory Technician",
                  description: "Manage lab tests, samples, and results reporting.",
                },
              ].map((role, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle>{role.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{role.description}</p>
                  </CardContent>
                  <CardFooter>
                    <Link href={`/login?role=${role.title.toLowerCase()}`}>
                      <Button variant="outline" size="sm">
                        Login as {role.title}
                      </Button>
                    </Link>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </section>
      </main>
      <footer className="border-t bg-background">
        <div className="container flex flex-col gap-4 py-10 md:flex-row md:gap-8 md:py-12">
          <div className="flex flex-col gap-2 md:gap-4 lg:gap-6">
            <div className="flex items-center gap-2">
              <HeartPulse className="h-6 w-6 text-teal-600" />
              <h2 className="text-xl font-bold">Healthcare System</h2>
            </div>
            <p className="text-sm text-muted-foreground md:max-w-xs">
              A comprehensive healthcare management system built with microservice architecture.
            </p>
          </div>
          <div className="grid flex-1 grid-cols-2 gap-8 sm:grid-cols-4">
            <div className="grid gap-2">
              <h3 className="text-sm font-medium">Product</h3>
              <nav className="grid gap-2">
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Features
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Pricing
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Documentation
                </Link>
              </nav>
            </div>
            <div className="grid gap-2">
              <h3 className="text-sm font-medium">Company</h3>
              <nav className="grid gap-2">
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  About
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Careers
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Contact
                </Link>
              </nav>
            </div>
            <div className="grid gap-2">
              <h3 className="text-sm font-medium">Legal</h3>
              <nav className="grid gap-2">
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Privacy
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Terms
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Compliance
                </Link>
              </nav>
            </div>
            <div className="grid gap-2">
              <h3 className="text-sm font-medium">Support</h3>
              <nav className="grid gap-2">
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Help Center
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  FAQs
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
                  Contact Support
                </Link>
              </nav>
            </div>
          </div>
        </div>
        <div className="container flex flex-col gap-4 border-t py-6 md:flex-row md:items-center md:justify-between md:py-8">
          <p className="text-sm text-muted-foreground">© 2025 Healthcare System. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
              Privacy Policy
            </Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
              Terms of Service
            </Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">
              Cookie Policy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
