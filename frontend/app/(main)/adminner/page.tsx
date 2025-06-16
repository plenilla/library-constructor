'use client'

import BackButton from '@/components/Mybuttons/BackButton'
import useMyAxios from '@/composables/useMyAxios'
import Image from 'next/image'
import { useEffect, useState } from 'react'

type User = {
	id: number
	username: string
	fullname: string | null
	role: 'reader' | 'admin' | 'librarian'
}

export default function AdminPage() {
	const { request, loading } = useMyAxios<User[]>()
	const [users, setUsers] = useState<User[]>([])
	// Стейт для ошибок по каждому пользователю (по id)
	const [errors, setErrors] = useState<Record<number, string>>({})

	// Проверка ФИО локально (в формате "Фамилия И.О.")
	const validateFullname = (value: string) => {
		if (value.trim() === '') return '' // пустое значение считаем валидным
		const pattern = /^[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\.$/
		return pattern.test(value)
			? ''
			: 'ФИО должно быть в формате Фамилия И.О. (например, Федоров Н.С.)'
	}

	const fetchUsers = async () => {
		const res = await request('/admin/users', 'GET')
		setUsers(res.data)
		setErrors({})
	}

	const deleteUser = async (id: number) => {
		if (confirm('Удалить пользователя?')) {
			await request(`/admin/users/${id}`, 'DELETE')
			fetchUsers()
		}
	}

	const updateUser = async (id: number, updated: Partial<User>) => {
		if ('fullname' in updated) {
			const error = validateFullname(updated.fullname ?? '')
			setErrors(prev => ({ ...prev, [id]: error }))
			if (error) {
				// Не отправляем запрос, если есть ошибка
				return
			}
		}
		await request(`/admin/users/${id}`, 'PUT', updated)
		fetchUsers()
	}

	useEffect(() => {
		fetchUsers()
	}, [])
	return (
		<div className='p-6'>
			<BackButton className='top-25 left-0'></BackButton>
			<h1 className='text-2xl font-bold mb-4'>
				Администрирование пользователей
			</h1>
			{loading ? (
				<p>Загрузка...</p>
			) : (
				<table className='w-full border border-gray-300 rounded-lg overflow-hidden'>
					<thead className='bg-gray-200'>
						<tr>
							<th className='p-2 text-left'>Логин</th>
							<th className='p-2 text-left'>ФИО</th>
							<th className='p-2 text-left'>Роль</th>
							<th className='p-2 text-left'>Действия</th>
						</tr>
					</thead>
					<tbody>
						{users.map(user => (
							<tr key={user.id} className='border-t'>
								<td className='p-2'>{user.username}</td>
								<td className='p-2 flex flex-col'>
									<input
										className={`border p-1 w-full ${
											errors[user.id] ? 'border-red-500 bg-red-50' : ''
										}`}
										defaultValue={user.fullname ?? ''}
										onBlur={e =>
											updateUser(user.id, { fullname: e.target.value })
										}
										placeholder='Фамилия И.О.'
										title='Введите ФИО в формате: Фамилия И.О. (например, Илья И.И.)'
									/>
									{errors[user.id] && (
										<span className='text-red-600 text-sm mt-1'>
											{errors[user.id]}
										</span>
									)}
								</td>
								<td className='p-2'>
									<select
										defaultValue={user.role}
										onChange={e =>
											updateUser(user.id, { role: e.target.value })
										}
										className='border p-1'
									>
										<option value='reader'>Читатель</option>
										<option value='admin'>Админ</option>
										<option value='librarian'>Библиотекарь</option>
									</select>
								</td>
								<td className='p-2 flex gap-2'>
									<button
										onClick={() => deleteUser(user.id)}
										className='text-red-500 hover:text-red-700'
									>
										<Image
											src={'/icons/delete.svg'}
											width={25}
											height={25}
											className='hover:bg-black/25'
											alt={'Удалить'}
										/>
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			)}
		</div>
	)
}
