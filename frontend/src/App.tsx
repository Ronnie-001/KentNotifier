import { Route, Routes } from "react-router-dom"
import SignIn from "./SignIn"
import Register from "./Register"

export default function App() {
    return (
        <Routes>
            {/* The registration routes*/}
            <Route path="/" element={ <SignIn /> } />
            <Route path="/register" element={ <Register /> } />

        </Routes>
    )
}

