export default function LoginPage() {
    return (
        <div>
            <h1>KentNotifer Login Page</h1>
            <LoginCard />
        </div>
    );
} 

function LoginCard() {
    return (
        <div>
            <SignUpButton />
            <SignInButton />
        </div>
    );
}

function SignUpButton() {
    return (
        <button>
            Sign Up
        </button>
    );
}

function SignInButton() {
    return (
        <button>
            Sign In
        </button>
    );
}
