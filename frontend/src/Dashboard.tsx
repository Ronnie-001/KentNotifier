import { PlusCircle, MinusCircle, Clock, MapPin, Activity } from "lucide-react"
import Navbar from "./components/ui/navbar";
import { jwtDecode } from "jwt-decode"
import { useEffect, useState } from "react";

// --- REUSABLE COMPONENTS ---

interface TimetableEvent {
    date: string;
    time: string;
    module: string;
    type: string;
    location: string;
    staff: string;
}

interface DifferenceState {
    added: TimetableEvent[];
    removed: TimetableEvent[];
}

export function RemovedEvent({ event }: { event: TimetableEvent }) {
    
    return (
        <div className="relative overflow-hidden bg-[#fffafa] border border-red-50 shadow-sm rounded-lg p-5 flex flex-col gap-3 transition-all hover:shadow-md border-l-4 border-l-red-500">
            {/* Top Row: Module & Type */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <MinusCircle className="w-5 h-5 text-red-600" strokeWidth={1.5} />
                    <span className="font-bold text-base tracking-tight text-red-800">
                        {event.module}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                        {event.type}
                    </span>
                </div>
                
                {/* Visual Badge */}
                <span className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md bg-red-100 text-red-700">
                    Removed
                </span>
            </div>

            {/* Bottom Row: Time & Location Details */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 text-sm text-slate-600 pl-8">
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-700">{event.date}</span>
                    <span>{event.time}</span>
                </div>
                <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span className="truncate">{event.location}</span>
                </div>
            </div>
        </div>
    );
}

export function AddedEvent({ event }: { event: TimetableEvent }) {
    return (
        <div className="relative overflow-hidden bg-[#f8fdf9] border border-green-50 shadow-sm rounded-lg p-5 flex flex-col gap-3 transition-all hover:shadow-md border-l-4 border-l-green-500">
            {/* Top Row: Module & Type */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <PlusCircle className="w-5 h-5 text-green-700" strokeWidth={1.5} />
                    <span className="font-bold text-base tracking-tight text-green-900">
                        {event.module}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                        {event.type}
                    </span>
                </div>
                
                {/* Visual Badge */}
                <span className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md bg-green-100 text-green-800">
                    Added
                </span>
            </div>

            {/* Bottom Row: Time & Location Details */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 text-sm text-slate-600 pl-8">
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-700">{event.date}</span>
                    <span>{event.time}</span>
                </div>
                <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span className="truncate">{event.location}</span>
                </div>
            </div>
        </div>
    );
}

// --- MAIN DASHBOARD COMPONENT ---
export default function Dashboard() {
    const [differences, setDifferences] = useState<DifferenceState>({
        added: [],
        removed: []
    });
    
     // Define an interface to define our own custom JWT payload
    interface customJwtPayload  {
        sub?: string;
        ID?: number;
        aud?: string[] | string;
        iat?: number;
        exp?: number;
    }

    const token = localStorage.getItem("token");
    const decoded = token != null ? jwtDecode<customJwtPayload>(token) : null;

    useEffect(() => {
        const grabUserData = async () => {
            try {
                const response = await fetch(`http://localhost:8080/scraping-service/v1/status/${decoded?.ID}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    }
                });
                
                if (response.ok) {

                    const data = await response.json();

                    let added = [];
                    let removed = [];
                    
                    try {
                        if (data.scraping_results) {
                            const parsed = JSON.parse(data.scraping_results);

                            for (const key in parsed) {
                                const nestedData = parsed[key];

                                if (Array.isArray(nestedData.added)) {
                                    added.push(...nestedData.added);
                                }

                                if (Array.isArray(nestedData.removed)) {
                                    removed.push(...nestedData.removed);
                                }
                            }        
                        }
                    } catch (error) {
                        console.error("Error when parsing the json data:" + error)
                    }

                    setDifferences({
                        added: added,
                        removed: removed
                    })                    
                }                     

            } catch (error) {
                console.error("Error when fetching user data from redis: " + error)
            }
        };

        grabUserData();        

    }, []);


    // Example data structure matching your Python backend
//     const differences = {
//         added: [
//             { day: "Monday", time: "11:00 - 12:00", module: "COMP5002", type: "LECTURE", location: "Jennison Lecture Theatre" }
//         ],
//         removed: [
//             { day: "Friday", time: "14:00 - 16:00", module: "COMP5003", type: "PC", location: "Cornwallis South PC room 1" }
//         ]
//     };

    return (
        <div className="min-h-screen bg-[#f8f9fa] font-mono text-slate-800 flex flex-col">

            {/* Top Navigation */}
            <Navbar />

            {/* Main Content Area */}
            <main className="flex-1 w-full max-w-3xl mx-auto px-6 py-16 flex flex-col">
                
                <div className="w-full bg-white text-left shadow-[0_8px_30px_rgb(0,0,0,0.04)] rounded-xl overflow-hidden flex flex-col font-mono border border-slate-100">
                    
                    <div className="p-6 md:p-8">
                        
                        {/* Header */}
                        <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-100">
                            <div>
                                <div className="flex items-center gap-2 text-blue-600 text-xs font-bold tracking-widest uppercase mb-2">
                                    <Activity className="w-4 h-4" />
                                    <span>Sync Complete</span>
                                </div>
                                <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Timetable Updates</h2>
                            </div>
                            <div className="text-right">
                                <span className="block text-3xl font-bold text-slate-900">
                                    {differences.added.length + differences.removed.length}
                                </span>
                                <span className="text-xs text-slate-500 uppercase tracking-widest font-bold">Changes</span>
                            </div>
                        </div>

                        {/* The Differences Lists */}
                        <div className="space-y-10">

                            {differences.added.length === 0 && differences.removed.length === 0 && (
                                <div className="text-center py-12 px-4">
                                    <p className="text-slate-500 font-medium">No timetable changes detected.</p>
                                    <p className="text-xs text-slate-400 mt-1">Your schedule is completely up to date.</p>
                                </div>
                            )}
                            
                            {differences.removed.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-red-500 uppercase tracking-widest flex items-center gap-2.5">
                                        <span className="w-2 h-2 rounded-full bg-red-400" />
                                        Removed from Schedule
                                    </h3>
                                    <div className="grid gap-3">
                                        {differences.removed.map(event => (
                                            <RemovedEvent key={`${event.date}-${event.time}-${event.module}`} event={event} />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {differences.added.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-green-600 uppercase tracking-widest flex items-center gap-2.5">
                                        <span className="w-2 h-2 rounded-full bg-green-500" />
                                        Added to Schedule
                                    </h3>
                                    <div className="grid gap-3">
                                        {differences.added.map(event => (
                                            <AddedEvent key={`${event.date}-${event.time}-${event.module}`} event={event} />
                                        ))}
                                    </div>
                                </div>
                            )}

                        </div>

                    </div>

                    {/* Footer Action */}
                    <div className="bg-slate-50/80 border-t border-slate-100 p-4 sm:p-6 flex justify-end">
                        <button className="w-full sm:w-auto bg-[#203682] hover:bg-[#1a2c6b] text-white px-8 py-2.5 rounded-md text-sm font-medium transition-all shadow-sm">
                            Acknowledge & Dismiss
                        </button>
                    </div>
                    
                </div>
            </main>
        </div>
    );
}
