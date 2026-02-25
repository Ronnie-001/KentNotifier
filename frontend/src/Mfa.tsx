import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { ShieldCheck, Loader2, ArrowLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"
import Navbar from "@/components/ui/navbar" 

export default function Mfa() {
    const [code, setCode] = useState("")
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const handleVerify = async () => {
        setLoading(true)
        await new Promise(resolve => setTimeout(resolve, 1500))
        setLoading(false)
        navigate("/home")
    }

    return (
        // 1. Change layout to 'flex-col' so Navbar sits on top
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">

            <Navbar />

            <div className="flex-1 flex justify-center items-center p-4">
                
                <Card className="w-full max-w-sm shadow-xl border-t-4 border-t-blue-600">
                    <CardHeader className="text-center pb-2">
                        <div className="mx-auto bg-blue-50 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                            <ShieldCheck className="w-6 h-6 text-blue-600" />
                        </div>
                        <CardTitle className="text-2xl font-bold text-slate-900">Authentication Required</CardTitle>
                        <CardDescription>
                            Please enter the 6-digit code sent to your email.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4 pt-4">
                        <div className="space-y-2">
                            <Label htmlFor="mfa-code" className="sr-only">MFA Code</Label>
                            <Input 
                                id="mfa-code" 
                                placeholder="000000" 
                                className="text-center text-2xl tracking-[0.5em] font-mono h-14" 
                                maxLength={6}
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                            />
                        </div>

                        <Button 
                            className="w-full bg-blue-900 hover:bg-blue-800 h-11 text-base" 
                            onClick={handleVerify}
                            disabled={loading || code.length < 6}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Verifying...
                                </>
                            ) : (
                                "Verify Identity"
                            )}
                        </Button>
                    </CardContent>

                    <CardFooter className="flex flex-col gap-4 bg-slate-50/50 p-6 rounded-b-lg border-t">
                        <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-600" onClick={() => navigate("/")}>
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back to Login
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        </div>
    )
}
