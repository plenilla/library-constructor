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
  const [errors, setErrors] = useState<Record<number, string>>({})
  const [tempFullnames, setTempFullnames] = useState<Record<number, string>>({})
  const [originalFullnames, setOriginalFullnames] = useState<Record<number, string>>({})

  const validateFullname = (value: string) => {
    if (value.trim() === '') return ''
    const pattern = /^[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\.$/
    return pattern.test(value)
      ? ''
      : 'ФИО должно быть в формате Фамилия И.О. (например, Федоров Н.С.)'
  }

  const fetchUsers = async () => {
    const res = await request('/admin/users', 'GET')
    setUsers(res.data)
    setErrors({})
    
    // Сохраняем оригинальные значения
    const originals: Record<number, string> = {}
    res.data.forEach(user => {
      originals[user.id] = user.fullname ?? ''
    })
    setOriginalFullnames(originals)
    setTempFullnames(originals)
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
      if (error) return
    }
    await request(`/admin/users/${id}`, 'PUT', updated)
    fetchUsers()
  }

  const handleFullnameChange = (id: number, value: string) => {
    setTempFullnames(prev => ({ ...prev, [id]: value }))
  }

  const saveFullname = (id: number) => {
    const newFullname = tempFullnames[id]?.trim() || null
    const originalFullname = originalFullnames[id] || null
    
    // Проверяем, изменилось ли значение
    if (newFullname === originalFullname) {
      // Если не изменилось, просто очищаем ошибку
      setErrors(prev => ({ ...prev, [id]: '' }))
      return
    }

    // Проверяем валидность
    const error = validateFullname(newFullname || '')
    if (error) {
      setErrors(prev => ({ ...prev, [id]: error }))
      return
    }

    // Обновляем на сервере
    updateUser(id, { fullname: newFullname })
  }

  // Проверяем, изменилось ли ФИО для конкретного пользователя
  const isFullnameChanged = (id: number) => {
    const current = tempFullnames[id]?.trim() || null
    const original = originalFullnames[id] || null
    return current !== original
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
        <table className='w-full border bg-white rounded-lg overflow-hidden'>
          <thead className='bg-black text-white'>
            <tr>
              <th className='p-2 text-left'>Логин</th>
              <th className='p-2 text-left'>ФИО</th>
              <th className='p-2 text-left'>Роль</th>
              <th className='p-2 text-left'>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className='border-t hover:bg-gray-50'>
                <td className='p-2'>{user.username}</td>
                <td className='p-2'>
                  <div className='flex items-center gap-1 w-full'>
                    <input
                      className={`border p-1 ${
                        errors[user.id] ? 'border-red-500 bg-red-50' : ''
                      }`}
                      value={tempFullnames[user.id] ?? ''}
                      onChange={e => handleFullnameChange(user.id, e.target.value)}
                      placeholder='Фамилия И.О.'
                      title='Введите ФИО в формате: Фамилия И.О. (например, Илья И.И.)'
                    />
                    <button
                      onClick={() => saveFullname(user.id)}
                      className={`p-1 rounded transition-colors group relative ${
                        isFullnameChanged(user.id) 
                          ? 'text-blue-500 hover:bg-blue-50' 
                          : 'text-gray-300 cursor-default'
                      }`}
                      title={isFullnameChanged(user.id) ? 'Сохранить изменения' : 'Нет изменений'}
                      disabled={!isFullnameChanged(user.id)}
                    >
                      <Image
                        src='/icons/save.svg'
                        alt='Сохранить'
                        width={18}
                        height={18}
                        className={`transition-opacity ${
                          isFullnameChanged(user.id) ? 'opacity-80 hover:opacity-100' : 'opacity-40'
                        }`}
                      />
                      <span className='absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap'>
                        {isFullnameChanged(user.id) ? 'Сохранить' : 'Нет изменений'}
                      </span>
                    </button>
                  </div>
                  {errors[user.id] && (
                    <span className='text-red-600 text-sm mt-1 block'>
                      {errors[user.id]}
                    </span>
                  )}
                </td>
                <td className='p-2'>
                  <select
                    defaultValue={user.role}
                    onChange={e =>
                      updateUser(user.id, { role: e.target.value as User['role'] })
                    }
                    className='border p-1 w-full max-w-[150px]'
                  >
                    <option value='reader'>Читатель</option>
                    <option value='admin'>Админ</option>
                    <option value='librarian'>Библиотекарь</option>
                  </select>
                </td>
                <td className='p-2'>
                  <button
                    onClick={() => deleteUser(user.id)}
                    className='p-1 rounded hover:bg-red-50 transition-colors group relative'
                    title='Удалить'
                  >
                    <Image
                      src={'/icons/delete.svg'}
                      width={20}
                      height={20}
                      className='opacity-70 hover:opacity-100 transition-opacity'
                      alt={'Удалить'}
                    />
                    <span className='absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 px-2 py-1 text-xs text-white bg-black rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none'>
                      Удалить
                    </span>
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