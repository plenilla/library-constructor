'use client'
import useMyAxios from '@/composables/useMyAxios'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import BackButton from '../Mybuttons/BackButton'
import { Button } from '../ui/button'

export const Header = () => {
	const [error, setError] = useState('')
	const [isAuthenticated, setIsAuthenticated] = useState(false)
	const [role, setRole] = useState('')

	const { request } = useMyAxios()
	const router = useRouter()
	const pathname = usePathname()

	const isExhibitionPage = /^\/exhibitions\/[^/]+$/.test(pathname)

	useEffect(() => {
		if (typeof window !== 'undefined') {
			const authStatus = localStorage.getItem('is_authenticated')
			const userRole = localStorage.getItem('role')
			setIsAuthenticated(authStatus === 'true')
			setRole(userRole)

			const handleStorageChange = () => {
				const updatedAuthStatus = localStorage.getItem('is_authenticated')
				const updatedRole = localStorage.getItem('role')
				setIsAuthenticated(updatedAuthStatus === 'true')
				setRole(updatedRole)
			}

			window.addEventListener('storage', handleStorageChange)

			return () => {
				window.removeEventListener('storage', handleStorageChange)
			}
		}
	}, [])

	const logout = async e => {
		e.preventDefault()

		try {
			const response = await request('users/logout', 'POST')
			if (response.status === 200) {
				localStorage.setItem('is_authenticated', 'false')
				localStorage.removeItem('role')
				router.push('/auth/login')
			} else {
				setError('Ошибка: ' + response.data.message)
			}
		} catch (error) {
			const err = error as { response?: { data?: { message?: string } } }
			const errorMessage = err.response?.data?.message || 'Ошибка регистрации'
			setError(errorMessage)
		}
	}

	return (
		<>
			<div className='py-5 px-5 flex flex-col md:flex-row justify-between items-center gap-4'>
				{/* Левая часть – заголовок */}
				<Link href='/'>
					<Image
						src='/icons/main_icon.svg'
						alt='Color Picker'
						width={250}
						height={200}
						className='cursor-pointer'
					/>
				</Link>
				{/* Правая часть – меню навигации */}
				<div className='flex flex-row items-center gap-2 md:gap-4 overflow-x-auto whitespace-nowrap'>
					<Link href='/' className='text-sm px-2 py-1 md:px-0 md:py-0'>
						Главная
					</Link>
					<BackButton
						className={
							isExhibitionPage && pathname !== '/exhibitions/create'
								? 'relative w-max text-sm  bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 rounded-md'
								: 'hidden'
						}
						name={'Вернуться к выставкам'}
						customAction={() => router.push('/exhibitions')}
					/>
					<Link
						href='/auth/register'
						className={
							isAuthenticated || isExhibitionPage
								? 'hidden'
								: 'w-max text-sm px-3 py-1 md:px-4 md:py-2 bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 rounded-md'
						}
					>
						Регистрация
					</Link>
					<Link
						href='/exhibitions/dashboard'
						className={
							isAuthenticated && role === 'admin' && !isExhibitionPage
								? 'w-max text-sm px-3 py-1 md:px-4 md:py-2 bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 rounded-md'
								: 'hidden'
						}
					>
						Админ панель
					</Link>
					<Link
						href='/exhibitions/create'
						className={
							isAuthenticated && role === 'librarian' && !isExhibitionPage
								? 'w-max text-sm px-3 py-1 md:px-4 md:py-2 bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 rounded-md'
								: 'hidden'
						}
					>
						Создать выставку
					</Link>
					<Link
						href='/auth/login'
						className={
							isAuthenticated || isExhibitionPage
								? 'hidden'
								: 'w-max text-sm px-3 py-1 md:px-4 md:py-2 bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 rounded-md'
						}
					>
						Войти
					</Link>
					<Button
						type='submit'
						className={
							isAuthenticated
								? 'w-max text-sm px-3 py-1 md:px-4 md:py-2'
								: 'hidden'
						}
						onClick={logout}
					>
						Выйти
					</Button>
				</div>
			</div>
		</>
	)
}
