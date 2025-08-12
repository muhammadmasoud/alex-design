import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { lazy, Suspense } from "react";

const Input = lazy(() => import("@/components/ui/input"));
const Button = lazy(() => import("@/components/ui/button"));
const SEO = lazy(() => import("@/components/SEO"));

import { useNavigate } from "react-router-dom";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

const schema = z.object({
  username: z.string().min(2, "Min 2 chars"),
  email: z.string().email(),
  password: z.string().min(6, "Minimum 6 characters"),
  confirm: z.string().min(6, "Minimum 6 characters"),
}).refine((d) => d.password === d.confirm, {
  message: "Passwords must match",
  path: ["confirm"],
});

type Values = z.infer<typeof schema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: Values) => {
    try {
      const { data } = await api.post(endpoints.auth.register, {
        username: values.username,
        email: values.email,
        password: values.password,
        confirm_password: values.confirm,
      });
      const token = data?.token || data?.access || data?.key;
      const user = data?.user;
      
      if (token && user) {
        login(token, user);
        toast({ title: `Welcome, ${user.username}!`, description: "Registration successful" });
        navigate("/");
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (e: any) {
      console.error("Registration error:", e.response?.data);
      const errorMessage = e?.response?.data?.non_field_errors?.[0] || 
                          e?.response?.data?.detail || 
                          e?.response?.data?.message ||
                          Object.values(e?.response?.data || {}).flat().join(", ") ||
                          e?.message || 
                          "Registration failed";
      toast({ title: "Registration failed", description: errorMessage });
    }
  };

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="container py-10 max-w-md">
        <SEO title="Register | Studio Arc" description="Create your Studio Arc account." canonical="/register" />
        <h1 className="font-heading text-3xl mb-6">Create account</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm">Username</label>
            <Input {...register("username")} placeholder="johndoe" />
            {errors.username && <p className="text-sm text-destructive mt-1">{errors.username.message}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm">Email</label>
            <Input type="email" {...register("email")} placeholder="you@example.com" />
            {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm">Password</label>
            <Input type="password" {...register("password")} />
            {errors.password && <p className="text-sm text-destructive mt-1">{errors.password.message}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm">Confirm Password</label>
            <Input type="password" {...register("confirm")} />
            {errors.confirm && <p className="text-sm text-destructive mt-1">{errors.confirm.message}</p>}
          </div>
          <Button type="submit" disabled={isSubmitting} className="w-full">{isSubmitting ? "Creating..." : "Create account"}</Button>
        </form>
      </div>
    </Suspense>
  );
}
