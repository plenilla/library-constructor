"use client"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import useMyAxios from "@/composables/useMyAxios"
import Image from "next/image"
import qs from "qs"

export function RegisterForm({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  const { request } = useMyAxios()
  const [username, setUserName] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if(password !== confirmPassword){
      setError('Пароли не совпадают')
      return
    }

    try {
      await request("/users/register", 'POST', qs.stringify({
        username,
        password,
        password_confirm: confirmPassword
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      router.push("/auth/login")
    } catch (error) {
      const errorMessage = error?.response ? error?.response?.data.message : "Ошибка регистрации";
      setError(errorMessage)
    }
  }

  return (
    <div className="min-h-screen flex justify-center px-4">
      <div className="md:min-w-[800px] w-full max-w-5xl" {...props}>
        <Card className="overflow-hidden">
          <div className="flex flex-col md:flex-row">
            {/* Левая часть - форма */}
            <div className="flex-1 flex flex-col p-6 md:min-w-[400px]">
              <CardHeader className="px-0 pt-0 pb-4">
                <CardTitle className="md:text-4xl md:py-5 text-[1.2em] md:text-center">Создайте учетную запись</CardTitle>
                <CardDescription>
                  Заполните форму для регистрации
                </CardDescription>
              </CardHeader>
              
              <form onSubmit={handleSubmit} className="flex-1 flex flex-col gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Логин</Label>
                  <Input
                    id="username"
                    type="text"
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder="Введите логин"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">Пароль</Label>
                  <Input 
                    id="password" 
                    type="password"
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Введите пароль" 
                    required 
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
                  <Input 
                    id="confirmPassword" 
                    type="password"
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Повторите пароль" 
                    required 
                  />
                </div>
                
                {error && <p className="text-red-500">{error}</p>}

                <div className="mt-auto space-y-4">
                  <Button type="submit" className="w-full" size="lg">
                    Зарегистрироваться
                  </Button>
                  <p className="text-center text-sm">
                    Уже есть аккаунт?{" "}
                    <Link href="/auth/login" className="font-bold underline">
                      Войти
                    </Link>
                  </p>
                </div>
              </form>
            </div>
            
            {/* Правая часть - изображение (только на десктопах) */}
            <div className="hidden lg:block flex-1 relative min-w-[400px] max-w-[500px]">
              <Image 
                src="/register.png" 
                alt="Иллюстрация регистрации"
                width={500}
                height={667}
                className="object-cover rounded-2xl w-full h-auto"
                priority 
              />
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
