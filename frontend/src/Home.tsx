import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Loader2, Activity, Clock } from "lucide-react"
import Navbar from "@/components/ui/navbar"

export default function Home() {
    const [isScraping, setIsScraping] = useState(false);

    const handleScrape = async () => {
        setIsScraping(true);
        // TODO: Await your backend scraping trigger here
        // await fetch('/api/scrape', { method: 'POST' });
        
        // Mock delay for UI testing
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
                            Click the button below to initialize the webscraper. We will fetch your latest schedule and highlight any detected differences.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="pb-6">
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
