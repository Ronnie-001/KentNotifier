import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Lock, ShieldCheck, Loader2 } from "lucide-react"
import { useNavigate } from "react-router-dom"
import Navbar from "./components/ui/navbar"

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    // Grab the token
    const token = localStorage.getItem("token");

    if (!token) {
        console.error("No token found");
        return;
    }

    const handleScrape = async () => {
        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 3000));
        console.log("Scraping started for:", email);
        
        fetch("http://localhost:8080/scraping-service/v1/get-login-details", {
            method: "POST",
            body: JSON.stringify({ email: email, password: password }),
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        setLoading(false);
        await new Promise(resolve => setTimeout(resolve, 1000));

        console.log("Navigating to the /mfa page")        

        // Navigate to the page where the MFA code will be displayed
        navigate("/mfa");
    }

    return (
        <div className="min-h-screen bg-slate-50 font-sans">
            <Navbar />
            {/* 2. Main Content Area */}
            <div className="flex flex-col items-center justify-center mt-12 px-4">

                <div className="text-center mb-8 space-y-2">
                    <h1 className="text-3xl font-bold text-slate-900">Welcome to KentNotifier</h1>
                    <p className="text-slate-500 max-w-lg">
                        To start receiving notifications, we need to sync with your university timetable.
                        Please enter your KentVision credentials below.
                    </p>
                </div>

                {/* 3. The "Connect KentVision" Card */}
                <Card className="w-full max-w-md shadow-lg border-t-4 border-t-blue-600">
                    <CardHeader>
                        <div className="flex items-center gap-2 mb-1">
                            <ShieldCheck className="w-5 h-5 text-blue-600" />
                            <span className="text-sm font-bold text-blue-600 uppercase tracking-wider">Secure Connection</span>
                        </div>
                        <CardTitle className="text-xl">Connect KentVision</CardTitle>
                        <CardDescription>
                            We use these details <strong>once</strong> to fetch your schedule.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="kv-email">Kent Email</Label>
                            <Input
                                id="kv-email"
                                placeholder="ab123@kent.ac.uk"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="kv-password">Password</Label>
                            <div className="relative">
                                <Input
                                    id="kv-password"
                                    type="password"
                                    className="pl-10" // Add padding for the icon
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                            </div>
                        </div>
                    </CardContent>

                    <CardFooter className="flex flex-col gap-4 bg-slate-50/50 p-6 rounded-b-lg">
                        <Button
                            className="w-full bg-blue-900 hover:bg-blue-800"
                            onClick={handleScrape}
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Syncing Timetable...
                                </>
                            ) : (
                                "Link Account & Sync"
                            )}
                        </Button>
                        <p className="text-xs text-center text-slate-400">
                            Your credentials are sent securely and are not stored in plain text.
                        </p>
                    </CardFooter>
                </Card>

            </div>
        </div>
    )
}
