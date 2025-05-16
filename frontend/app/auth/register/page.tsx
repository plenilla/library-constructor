import { RegisterForm } from "@/components/ui/register-form";

const Register = () => {
  return (
    <div className="flex min-h-[80vh] w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-[70vh]">
        <RegisterForm />
      </div>
    </div>
  );
};
Register.displayName = 'Register';

export default Register;
