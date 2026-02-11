import { 
    Card,
    CardHeader,
    CardTitle,
    CardContent,
} from "@/components/ui/card"

import {
    Input
} from "@/components/ui/input"

import {
    Button
} from "@/components/ui/button"

import {
    Label
} from "@/components/ui/label"

export default function SignIn() {
    return (
        <div className="flex justify-center items-center h-screen">
            <Card className="w-full max-w-sm shadow-lg border-2 rounded-sm"> 
                <CardHeader>
                    <CardTitle className="text-center">Sign in</CardTitle>
                </CardHeader>
                <CardContent>
                    <Label htmlFor="username">email address:</Label>
                    <Input></Input>
                    <br></br>
                    <div className="flex justify-between items-center mb-2">
                        <Label htmlFor="password">password:</Label>
                        <a href="#" className="text-sm">Forgot password?</a>
                    </div>
                        <Input></Input>
                    <br></br>
                    <Button className="w-full">sign in</Button>
                </CardContent>
            </Card>
        </div>
    )
}
