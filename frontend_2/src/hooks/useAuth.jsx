// src/hooks/useAuth.js
import { useEffect, useState } from 'react'

export default function useAuth() {
	const [isAuthenticated, setIsAuthenticated] = useState(false)

	useEffect(() => {
		async function checkAuth() {
			try {
				const response = await fetch('/users/check_auth')
				const data = await response.json()
				setIsAuthenticated(data.is_authenticated)
			} catch (error) {
				console.error('Ошибка проверки авторизации: ', error)
				setIsAuthenticated(false)
			}
		}
		checkAuth()
	}, [])

	return isAuthenticated
}
