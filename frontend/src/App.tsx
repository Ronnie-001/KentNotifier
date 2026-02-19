import { Route, Routes } from "react-router-dom"
import SignIn from "./SignIn"
import Register from "./Register"
import Home from "./Home"

export default function App() {
    return (
        <Routes>
            {/* The registration routes*/}
            <Route path="/" element={ <SignIn /> } />
            <Route path="/register" element={ <Register /> } />

            {/* Main pages of the website*/}
            <Route path="/home" element={ <Home /> } />
            <Route path="/results" element={ <Register /> } />
        </Routes>
    )
}

