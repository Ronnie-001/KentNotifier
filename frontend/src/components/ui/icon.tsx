import { BellRing } from "lucide-react"

// The main icon for KentNotifier
export default function Icon() {
    return (
        <div className="font-bold text-xl flex items-center gap-2 text-blue-900">
            <BellRing className="w-6 h-6 text-blue-600" />
            <span>Kent<span className="text-blue-600">Notifier</span></span>
        </div>
    )
}
