import { Button } from "@/components/ui/button"
import { LogOut } from "lucide-react"
import Icon from "@/components/ui/icon"

export default function Navbar() {
    return (
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
    )
}
