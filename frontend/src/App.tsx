import { Route, Routes } from "react-router-dom"
import SignIn from "./SignIn"
import Register from "./Register"
import Sync from "./Sync"
import Mfa from "./Mfa"
import Home from "./Home"

export default function App() {
    return (
        <Routes>
            {/* The registration routes*/}
            <Route path="/" element={ <SignIn /> } />
            <Route path="/register" element={ <Register /> } />

            {/* Main pages of the website*/}
            <Route path="/sync" element={ <Sync /> } />
            <Route path="/results" element={ <Register /> } />
            <Route path="/mfa" element={ <Mfa /> } />
            <Route path="/home" element={ <Home /> } />
        </Routes>
    )
}
