import { Route, Routes } from "react-router-dom"
import SignIn from "./SignIn"
import Register from "./Register"

export default function App() {
    return (
        <Routes>
            {/* The registration routes*/}
            <Route path="/" element={ <SignIn /> } />
            <Route path="/register" element={ <Register /> } />

            {/* Main pages of the website*/}
            <Route path="/home" element={ <Register /> } />
            <Route path="/results" element={ <Register /> } />

        </Routes>
    )
}

