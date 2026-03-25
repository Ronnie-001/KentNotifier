import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Loader2, Activity, Clock } from "lucide-react"
import Navbar from "@/components/ui/navbar"

export default function Home() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isScraping, setIsScraping] = useState(false);
    
    const token = localStorage.getItem("token");

    const handleScrape = async () => {
        setIsScraping(true);
        try {
            const response = await fetch("http://localhost:8080/scraping-service/v1/webscrape-timetable", {
                method: "POST",
                body: JSON.stringify({ email: email, password: password }),
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data);
            }

        } catch (error) {
            console.log("Error when trying to find the data")
            return;
        }
        setTimeout(() => setIsScraping(false), 2000); 
    };
    
    return (
        <div className="min-h-screen bg-[#f8f9fa] font-mono text-slate-800 flex flex-col">
            
            {/* Abstracted top navigation */}
            <Navbar />

            {/* Main Content Area */}
            <main className="flex-1 w-full max-w-2xl mx-auto px-8 py-16 flex flex-col items-center text-center">
                
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-4 tracking-tight">
                        Dashboard
                    </h1>
                    <p className="text-slate-500 text-sm leading-relaxed max-w-md mx-auto">
                        Your credentials are linked. Manually trigger a scrape to check for structural timetable updates.
                    </p>
                </header>

                {/* Action Card using your UI components */}
                <Card className="w-full text-left shadow-xl border-t-4 border-t-blue-500 rounded-xl">
                    
                    <CardHeader className="pb-4">
                        <div className="flex items-center gap-2 text-blue-600 text-xs font-bold tracking-widest uppercase mb-2">
                            <Activity className="w-4 h-4" />
                            <span>Sync Status</span>
                        </div>
                        <CardTitle className="text-xl font-bold text-slate-900">
                            Compare Timetable
                        </CardTitle>
                        <CardDescription className="text-sm text-slate-500 pt-2">
                            Enter your credentials below and click the button to initialize the webscraper. We will fetch your latest schedule and highlight any detected differences.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="pb-6 space-y-4">
                        
                        {/* Credentials Form */}
                        <div className="space-y-4 mb-6">
                            <div className="space-y-2">
                                <label htmlFor="email" className="text-sm font-medium text-slate-700">
                                    Kent Email
                                </label>
                                <input 
                                    type="email" 
                                    id="email"
                                    placeholder="ab123@kent.ac.uk"
                                    className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <label htmlFor="password" className="text-sm font-medium text-slate-700">
                                    Password
                                </label>
                                <input 
                                    type="password" 
                                    id="password"
                                    placeholder="••••••••"
                                    className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Action Button */}
                        <Button 
                            onClick={handleScrape}
                            disabled={isScraping}
                            className="w-full bg-blue-900 hover:bg-blue-800 h-12 text-base gap-2 transition-all"
                        >
                            {isScraping ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Scraping Timetable...
                                </>
                            ) : (
                                "Initiate Webscrape"
                            )}
                        </Button>
                    </CardContent>

                    <CardFooter className="flex justify-center border-t bg-slate-50/50 p-4 rounded-b-xl">
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            <Clock className="w-3.5 h-3.5" />
                            <span>Last checked: Never</span>
                        </div>
                    </CardFooter>

                </Card>
            </main>
        </div>
    );
}
