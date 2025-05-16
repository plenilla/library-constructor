'use client'
import { Button } from '@/components/ui/button'
import {
	Card,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import useMyAxios from '@/composables/useMyAxios'
import { cn } from '@/lib/utils'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import qs from 'qs'
import React, { useState } from 'react'

export function LoginForm({
	className,
	...props
}: React.ComponentPropsWithoutRef<'div'>) {
	const { request } = useMyAxios()
	const [username, setUserName] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState('')
	const router = useRouter()

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		try {
			const response = await request(
				'users/login',
				'POST',
				qs.stringify({
					username,
					password,
				}),
				{
					'Content-Type': 'application/x-www-form-urlencoded',
				}
			)

			if (response.data.message === 'Успешный вход') {
				localStorage.setItem('is_authenticated', 'true')
				localStorage.setItem('role', response.data.role)
				router.push('/')
			} else {
				setError('Ошибка: ' + response.data.message)
			}
		} catch (err: unknown) {
			setError((err as any)?.response?.data?.error || 'Ошибка при входе')
		}
	}

	return (
		<div className='min-h-screen flex justify-center px-4'>
			<div className={cn('flex flex-col gap-6', className)} {...props}>
				<Card className='overflow-hidden'>
					<div className='flex flex-col md:flex-row'>
						{/* Левая часть - форма */}
						<div className='flex-1 flex flex-col p-6 md:min-w-[400px]'>
							<CardHeader className='px-0 pt-0 pb-4'>
								<CardTitle className='md:text-4xl md:py-5 text-[1.2em] md:text-center'>
									Войдите в свою учетную запись
								</CardTitle>
								<CardDescription>
									Введите свой логин чтобы войти в аккаунт
								</CardDescription>
							</CardHeader>

							<form
								onSubmit={handleSubmit}
								className='flex-1 flex flex-col gap-4'
							>
								<div className='space-y-2'>
									<Label htmlFor='email'>Логин</Label>
									<Input
										id='text'
										type='text'
										onChange={e => setUserName(e.target.value)}
										placeholder='Введите логин'
										required
									/>
								</div>

								<div className='space-y-2'>
									<div className='flex items-center'>
										<Label htmlFor='password'>Пароль</Label>
										<a href='#' className='ml-auto text-sm underline'>
											Забыли пароль?
										</a>
									</div>
									<Input
										id='password'
										type='password'
										onChange={e => setPassword(e.target.value)}
										placeholder='Введите пароль'
										required
									/>
								</div>

								{error && <p className='text-red-500'>{error}</p>}

								<div className='mt-auto space-y-4'>
									<Button type='submit' className='w-full' size='lg'>
										Войти
									</Button>
									<p className='text-center text-sm'>
										Нет учетной записи?{' '}
										<Link href='/auth/register' className='font-bold underline'>
											Зарегистрируйтесь
										</Link>
									</p>
								</div>
							</form>
						</div>

						{/* Правая часть - изображение (только на десктопах) */}
						<div className='hidden lg:block flex-1 relative min-w-[400px] max-w-[500px]'>
							<Image
								src='/login.png'
								alt='Иллюстрация входа'
								width={500}
								height={667}
								className='object-cover rounded-2xl w-full h-auto'
								priority
							/>
						</div>
					</div>
				</Card>
			</div>
		</div>
	)
}
