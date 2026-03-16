import { useState } from "react" 
import { Link, useNavigate } from "react-router-dom" 
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import Icon from "@/components/ui/icon"

export default function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirm, setPasswordConfirm] = useState("");
    const navigate = useNavigate(); 

    async function handleSignUp() {
        try {
            // Check if the 2 passwords were equal or not
            if (password != passwordConfirm) {
                console.log("The password entered in both feilds does not match!");
                alert("Invalid credentials!");
                return;
            }

            const response = await fetch("http://localhost:8080/login-service/auth/v1/signup", {
                method: "POST",
                body: JSON.stringify({ email: email, password: password }),
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {
                console.log("Error when trying to register a new user" + response.status);
                alert("Invalid credentials!");
                return;
            }

            const data = await response.json();
            console.log("Server response: ", data);

            localStorage.setItem("token", data.token);
            navigate("/sync");

        } catch (error) {
            alert("Could not connect to the server");
            console.log(error);
        }
    }

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
                        <Input 
                            id="email" 
                            type="email" 
                            placeholder="user@kent.ac.uk"
                            onChange={(e) => setEmail(e.target.value)}
                            />
                    </div>

                    {/* Password */}
                    <div className="space-y-2">
                        <Label htmlFor="password">Password</Label>
                        <Input 
                            id="password" 
                            type="password"
                            placeholder="set your password"
                            onChange={(e) => setPassword(e.target.value)} />
                    </div>

                    {/* Confirm Password */}
                    <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm Password</Label>
                        <Input 
                            id="confirm-password" 
                            type="password"
                            placeholder="confirm your password"
                            onChange={(e) => setPasswordConfirm(e.target.value)} />
                    </div>

                    {/* Buttons */}
                    <div className="pt-2 flex flex-col gap-3">
                        {/* Primary Action: Create Account */}
                        <Button onClick={handleSignUp} className="w-full bg-blue-900 hover:bg-blue-800">
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
