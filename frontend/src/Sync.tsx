import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { LogOut, Lock, ShieldCheck, Loader2 } from "lucide-react"
import Icon from "@/components/ui/icon" // Assuming this is your logo component

export default function Sync() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const handleScrape = async () => {
        setLoading(true)
        // Simulate a scraping delay (replace this with your real API call later)
        await new Promise(resolve => setTimeout(resolve, 2000))
        console.log("Scraping started for:", email)
        setLoading(false)
    }

    return (
        <div className="min-h-screen bg-slate-50 font-sans">

            {/* 1. Navbar */}
            <nav className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200 p-4 flex justify-between items-center px-6 md:px-10">
                <Icon />
                <div className="flex items-center gap-5">
                    <span className="text-sm font-medium text-slate-600 hidden sm:inline">
                        user@kent.ac.uk
                    </span>
                    <Button variant="ghost" size="sm" className="text-slate-600 hover:text-slate-900 hover:bg-slate-100">
                        <LogOut className="w-4 h-4 mr-2" />
                        Log Out
                    </Button>
                </div>
            </nav>

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
