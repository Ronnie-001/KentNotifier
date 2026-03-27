import { Route, Routes } from "react-router-dom"
import SignIn from "./SignIn"
import Register from "./Register"
import Sync from "./Sync"
import Mfa from "./Mfa"
import BeginSearch from "./BeginSearch"
import MfaSearch from "./MfaSearch"
import Dashboard from "./Dashboard"

export default function App() {
    return (
        <Routes>
            {/* The registration routes */}
            <Route path="/" element={ <SignIn /> } />
            <Route path="/register" element={ <Register /> } />

            {/* Scraping routes */}
            <Route path="/sync" element={ <Sync /> } />
            <Route path="/mfa" element={ <Mfa /> } />
            <Route path="/search" element={ <BeginSearch /> } />
            <Route path="/mfa-search" element={ <MfaSearch />} />
            
            {/* Dashboard routes */}
            <Route path="/dashboard" element={ <Dashboard /> } />
        </Routes>
    )
}
