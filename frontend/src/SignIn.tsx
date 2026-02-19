import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Link, useNavigate } from "react-router-dom" 
import { useState } from "react"
import logo from "@/assets/logo.jpg" 

export default function SignIn() {

    // Login Hooks
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const navigate = useNavigate();
    
    async function handleLogin() {
        try {
            const response = await fetch("http://localhost:8080/login-service/auth/v1/signin", {
               method: "POST",
               body: JSON.stringify({email: email, password: password}),
               headers: {
                   "Content-Type": "application/json"
               },
            });
            
            // Postman being used for testing; Check for 401 errors
            if (!response.ok) {
                console.log("Error trying to login: " + response.status);
                alert("Invalid credentials!");
                return;
            }

            const data = await response.json();
            console.log("Server response: ", data);

            // Navigate and go to the home page
            navigate("/home")
            
            localStorage.setItem("token", data.token);
           
        } catch (error) {
            alert("Could not connect to the server")            
            console.log(error)
        }
    }

  return (
    <div className="relative flex justify-center items-center h-screen bg-gray-50">
      
      {/* 1. Logo in Top-Left Corner */}
        <div className="absolute top-6 left-6 flex items-center gap-2">
        <img src={logo} alt="Kent Notifier Logo" className="w-10 h-auto" />
        <span className="font-bold text-xl text-blue-900">KentNotifier</span>
      </div>

      {/* 2. Login Card */}
      <Card className="w-full max-w-sm shadow-xl border-t-4 border-t-blue-600">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold">Sign In</CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          
          {/* Username */}
          <div className="space-y-2">
            <Label htmlFor="username">Email Address</Label>
            <Input id="username" 
                   placeholder="user@kent.ac.uk" 
                   onChange={(e) => setEmail(e.target.value)}/>
          </div>
            
          {/* Password Section */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label htmlFor="password">Password</Label>
              <a href="#" className="text-xs text-blue-600 hover:underline">
                Forgot password?
              </a>
            </div>
            <Input id="password"
                   type="password"
                   onChange={(e) => setPassword(e.target.value)}/>
          </div>

          {/* Buttons */}
          <div className="pt-2 flex flex-col gap-3">
            <Button onClick={handleLogin} className="w-full bg-blue-900 hover:bg-blue-800">
              Sign In
            </Button>
            
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or
              </span>
            </div>

            <Button variant="outline" asChild className="w-full">
              <Link to="/register"> 
                Create an Account
              </Link>
            </Button>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
