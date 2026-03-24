import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Loader2, Copy, Check, KeyRound } from "lucide-react"
import { useNavigate } from "react-router-dom"
import Navbar from "@/components/ui/navbar"
import { jwtDecode } from "jwt-decode"

export default function Mfa() {
    
    const [status, setStatus] = useState("scraping");
    const [mfaCode, setMfaCode] = useState("");
    const [copied, setCopied] = useState(false);
    const navigate = useNavigate();

    // Define an interface to define our own custom JWT payload
    interface customJwtPayload  {
        sub?: string;
        ID?: number;
        aud?: string[] | string;
        iat?: number;
        exp?: number;
    }

    // Grab the user id from the JWT token
    const token = localStorage.getItem("token");
    const decoded = token != null ? jwtDecode<customJwtPayload>(token) : null;

    useEffect(() => {        
        const pollForMfa = async () => {
            try {
                const response = await fetch(`http://localhost:8080/scraping-service/v1/login-status/${decoded?.ID}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();

                    console.log("PRINTING THE DATA: " + data);

                    if (data.status == "MFA_WAITING") {
                        setStatus("waiting");
                        setMfaCode(data.mfa_code);
                    }

                    if (data.status == "SUCCESS") {
                        setStatus("success");
                        setMfaCode(data.mfa_code);
                        return;
                    }

                    if (data.status == "FAILED") {
                        console.log("MFA code retreival failed! redirecting back to /sync");
                        navigate("/sync");
                        return;
                    }
                }

            } catch (error) {
                console.log("Error when polling for the MFA code!: " + error);
                alert("Polling error");
                return;
            }
        }
        
        const intervalId = setInterval(pollForMfa, 3000);
        
        return () => clearInterval(intervalId);
    }, [])

    const handleCopy = () => {
        navigator.clipboard.writeText(mfaCode.replace(/\s/g, '')); // Remove spaces for copy
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    return (
        <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
            <Navbar />
            <div className="flex-1 flex justify-center items-center p-4">
                <Card className="w-full max-w-sm shadow-xl border-t-4 border-t-blue-600">
                    
                    <CardHeader className="text-center pb-2">
                        <div className="mx-auto bg-blue-50 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                            <KeyRound className="w-6 h-6 text-blue-600" />
                        </div>
                        <CardTitle className="text-2xl font-bold text-slate-900">
                            {status === 'scraping' ? 'Retrieving Code...' : 'MFA Code Received'}
                        </CardTitle>
                        <CardDescription>
                            {status === 'scraping' 
                                ? "Please wait while we fetch the verification code from your account." 
                                : "Use this code to complete your login."}
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="flex flex-col items-center justify-center py-6 space-y-6">
                        {status === 'scraping' ? (
                            <div className="flex flex-col items-center gap-4">
                                <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
                                <p className="text-sm text-slate-500 animate-pulse">Scraping email inbox...</p>
                            </div>
                        ) : (
                            <div className="w-full space-y-4">
                                {/* The Big Code Display */}
                                <div className="bg-slate-100 border-2 border-slate-200 rounded-lg p-6 text-center">
                                    <span className="text-4xl font-mono font-bold tracking-widest text-slate-800">
                                        {mfaCode}
                                    </span>
                                </div>

                                <Button 
                                    className="w-full bg-blue-900 hover:bg-blue-800 h-12 text-base gap-2"
                                    onClick={handleCopy}
                                >
                                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    {copied ? "Copied to Clipboard" : "Copy Code"}
                                </Button>
                            </div>
                        )}

                    </CardContent>

                    <CardFooter className="bg-slate-50/50 p-6 rounded-b-lg border-t flex justify-center">
                         {/*TODO: if the MFA code is visible on the screen, grey out the "Skip to Dashboard button
                            and replace the text with: Enter the provided MFA code"*/}
                         {status === 'success' && (
                             <Button variant="link" onClick={() => navigate("/home")} className="text-slate-500">
                                 Move to Dashboard
                             </Button>
                         )}
                    </CardFooter>
                </Card>
            </div>
        </div>
    )
}
