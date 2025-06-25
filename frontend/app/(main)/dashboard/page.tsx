'use client'

import Link from 'next/link'

export default function Home() {

  return (
    <div className='flex flex-col items-center gap-5'>
      <Link
        href={`/dash_admin/`}
        className='bg-black text-white text-center w-[700px] hover:bg-darkblue-700 transition duration-300 p-4'
      >
        Админ панель
      </Link>
      <Link
        href={`/admin/`}
        className='bg-black text-white text-center	 w-[700px] hover:bg-darkblue-700 transition duration-300 p-4'
      >
        База данных
      </Link>
    </div>
  )
}
