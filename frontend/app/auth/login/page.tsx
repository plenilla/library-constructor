
import { LoginForm } from "@/components/ui/login-form";

const Login = () => {
  return (
    <div className="flex w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-[70vh]">
        <LoginForm />
      </div>
    </div>
  );
};
Login.displayName = 'Login';
export default Login;
