import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Link } from "react-router-dom"
import Icon from "@/components/ui/icon"

export default function Register() {
    return (
        <div className="relative flex justify-center items-center h-screen bg-gray-50">

            <div className="absolute top-6 left-6 flex items-center gap-2">
                <Icon />
            </div>

            <Card className="w-full max-w-sm shadow-xl border-t-4 border-t-blue-600">
                <CardHeader>
                    <CardTitle className="text-center text-2xl font-bold">Create Account</CardTitle>
                    <CardDescription className="text-center">
                        Enter your details to get started
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">

                    {/* Full Name */}
                    <div className="space-y-2">
                        <Label htmlFor="name">Full Name</Label>
                        <Input id="name" placeholder="John Doe" />
                    </div>

                    {/* Email */}
                    <div className="space-y-2">
                        <Label htmlFor="email">Email Address</Label>
                        <Input id="email" type="email" placeholder="user@kent.ac.uk" />
                    </div>

                    {/* Password */}
                    <div className="space-y-2">
                        <Label htmlFor="password">Password</Label>
                        <Input id="password" type="password" />
                    </div>

                    {/* Confirm Password */}
                    <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm Password</Label>
                        <Input id="confirm-password" type="password" />
                    </div>

                    {/* Buttons */}
                    <div className="pt-2 flex flex-col gap-3">
                        {/* Primary Action: Create Account */}
                        <Button className="w-full bg-blue-900 hover:bg-blue-800">
                            Create Account
                        </Button>

                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-background px-2 text-muted-foreground">
                                Already have an account?
                            </span>
                        </div>

                        {/* Secondary Action: Go back to Sign In */}
                        <Button variant="outline" asChild className="w-full">
                            <Link to="/">
                                Sign In
                            </Link>
                        </Button>
                    </div>

                </CardContent>
            </Card>
        </div>
    )
}
