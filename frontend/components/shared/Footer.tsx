import Image from 'next/image'
import Link from 'next/link'

export const Footer = () => {
	return (
		<>
			<div className='bg-white text-black py-8'>
				<div className='container mx-auto flex flex-col md:flex-row items-center justify-between px-4'>
					{/* Логотип */}
					<div className='mb-6 md:mb-0 bg-white rounded-2xl'>
							<Image
								src='/icons/main_icon.svg'
								alt='Color Picker'
								width={250}
								height={200}
								className='cursor-pointer'
							/>
					</div>

					{/* Навигация */}
					<nav className='flex space-x-6 mb-6 md:mb-0'>
						{/* <Link href='/about' className='hover:text-white transition-colors'>
							О проекте
						</Link>
						<Link
							href='/contact'
							className='hover:text-white transition-colors'
						>
							Контакты
						</Link> */}
					</nav>
				</div>
			</div>
		</>
	)
}
