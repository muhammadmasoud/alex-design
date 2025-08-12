import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import { useNavigate } from "react-router-dom";
import { api, endpoints } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

const schema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(6, "Minimum 6 characters"),
});

type Values = z.infer<typeof schema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, checkAdminStatus } = useAuth();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: Values) => {
    try {
      const { data } = await api.post(endpoints.auth.login, {
        username: values.username,
        password: values.password,
      });
      const token = data?.token || data?.access || data?.key;
      const user = data?.user;
      
      if (token && user) {
        login(token, user);
        // Check admin status after login
        await checkAdminStatus();
        toast({ title: `Welcome back, ${user.username}!` });
        navigate("/");
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (e: any) {
      console.error("Login error:", e.response?.data);
      const errorMessage = e?.response?.data?.non_field_errors?.[0] || 
                          e?.response?.data?.detail || 
                          e?.response?.data?.message ||
                          Object.values(e?.response?.data || {}).flat().join(", ") ||
                          e?.message || 
                          "Login failed";
      toast({ title: "Login failed", description: errorMessage });
    }
  };

  return (
    <div className="container py-10 max-w-md">
      <SEO title="Login | Studio Arc" description="Log in to your Studio Arc account." canonical="/login" />
      <h1 className="font-heading text-3xl mb-6">Log in</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">Username</label>
          <Input {...register("username")} placeholder="Enter your username" />
          {errors.username && <p className="text-sm text-destructive mt-1">{errors.username.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Password</label>
          <Input type="password" {...register("password")} />
          {errors.password && <p className="text-sm text-destructive mt-1">{errors.password.message}</p>}
        </div>
        <Button type="submit" disabled={isSubmitting} className="w-full">{isSubmitting ? "Signing in..." : "Sign in"}</Button>
      </form>
    </div>
  );
}
