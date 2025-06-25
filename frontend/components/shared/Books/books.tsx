'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Modal } from '@/components/ui/modal'
import useMyAxios from '@/composables/useMyAxios'
import { Book } from '@/interfaces/books'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface BookProps {
	book: Book
}

export const Books = ({ book }: BookProps) => {
	const [isModalOpen, setIsModalOpen] = useState(false)
	const [isFullscreen, setIsFullscreen] = useState(false)
	const { request: deleteRequest } = useMyAxios()
	const [isDeleting, setIsDeleting] = useState(false)
	const router = useRouter()

	useEffect(() => {
		document.body.style.overflow = isModalOpen ? 'hidden' : 'auto'
		return () => {
			document.body.style.overflow = 'auto'
		}
	}, [isModalOpen])

	function truncateWords(text: string, maxWords: number): string {
		const words = text.trim().split(/\s+/)
		return words.length > maxWords
			? words.slice(0, maxWords).join(' ') + '...'
			: text
	}

	const imageUrl = book.image_url?.startsWith('http')
		? book.image_url
		: new URL(book.image_url!, process.env.NEXT_PUBLIC_BASE_URL).toString()

	return (
		<>
			<Card
				className='rounded-lg shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer group overflow-hidden flex flex-row p-3 h-40 md:h-60'
				onClick={() => setIsModalOpen(true)}
			>
				{/* Блок с изображением */}
				<div className="relative flex-shrink-0 w-[80px] h-[120px] md:w-[130px] md:h-[220px]">
					<Image
					src={imageUrl}
					fill
					alt={book.title}
					sizes="(max-width: 768px) 100vw, 50vw"
					className="transition-transform duration-300"
					/>
				</div>

				{/* Контент - занимает оставшееся пространство */}
				<CardContent className='flex-1 flex flex-col min-h-0 pl-3 md:pl-4 py-0'>
					{/* Заголовок с фиксированной высотой */}
					<h1 className='text-lg md:text-xl font-bold truncate mb-1'>{book.title}</h1>
					
					{/* Описание с адаптивным размером и скроллом */}
					<div className="flex-1 min-h-0 w-50 md:w-auto">
						<div className="md:hidden">
							<p className='text-xs whitespace-pre-line'>
							{truncateWords(book.annotations, 10)}
							</p>
						</div>
						<div className="hidden md:block">
							<p className='text-sm whitespace-pre-line'>
							{truncateWords(book.annotations, 50)}
							</p>
						</div>
					</div>
					
					{/* Мета-информация - прижимается к низу */}
					<div className='mt-2 space-y-1 w-50 md:w-aut'>
						<p className='text-xs text-muted-foreground truncate'>
							Форма произведения: {book.genres.map(genre => genre.name).join(', ')}
						</p>
						<p className='text-xs text-muted-foreground truncate'>
							Авторы: {book.authors.map(author => author.name).join(', ')}
						</p>
					</div>
				</CardContent>
			</Card>

			<Modal
				size='full'
				isOpen={isModalOpen}
				onClose={() => {
					setIsModalOpen(false)
					setIsFullscreen(false)
				}}
				showCloseButton={true}
				className={
					isFullscreen
						? 'fixed z-50 bg-transparent border-none shadow-none'
						: 'overflow-y-auto w-full h-full m-0 p-0 md:justify-center'
				}
			>
				{isFullscreen ? (
					<div className='fixed inset-0 md:inset-20 flex items-center justify-center'>
						<Image
							src={imageUrl}
							alt={book.title}
							fill
							unoptimized
							className='object-contain'
							onClick={e => {
								e.stopPropagation()
								setIsFullscreen(false)
							}}
						/>
					</div>
				) : (
					<div className='flex flex-col w-full md:flex-row gap-6'>
						<div className='relative md:w-1/4 cursor-zoom-in min-h-[150px]'>
							<div className='absolute inset-0 overflow-hidden'>
								<Image
									src={imageUrl}
									alt={book.title}
									fill
									className='object-cover blur-xs'
									unoptimized
								/>
								<div className='absolute inset-0 bg-black/50'></div>
							</div>
							<div className='relative z-10 flex flex-col items-center justify-center h-full p-4'>
								<Image
									src={imageUrl}
									alt={book.title}
									width={150}
									height={200}
									className='object-contain h-auto w-full shadow-accent-foreground'
									unoptimized
								/>
								<div className='mt-4 text-center'>
									<h2 className='text-2xl font-bold text-white drop-shadow-md'>
										{book.title}
									</h2>
									<p className='text-lg text-white/80'>{book.author}</p>
								</div>
							</div>
							<button
								onClick={e => {
									e.stopPropagation()
									setIsFullscreen(true)
								}}
								className='absolute inset-0 z-20 w-full h-full opacity-0 hover:opacity-100 transition-opacity duration-300 flex items-center justify-center'
								aria-label='Увеличить изображение'
							>
								<span className='bg-black/70 text-white p-3 rounded-full'>
									<MagnifyingGlassIcon className='h-6 w-6' />
								</span>
							</button>
							<p className='text-center mt-4'>Год публикации книги: {book.year_of_publication}г.</p>
						</div>
						<div className="flex flex-col md:flex-row md:justify-center w-full">
							<div className='w-full md:w-1/2 bg-gray-100 p-4 rounded-lg'>
								<div className='overflow-y-auto rounded-lg p-3 flex flex-col h-[500px]'>
									<div>
										<h2 className='font-bold text-center text-2xl mt-6'>
										{book.title}
										</h2>
										<h3 className='font-bold text-center'>Аннотация</h3>
										<p className="text-md whitespace-pre-line mt-2">
											{book.annotations}
										</p>
										<p className='font-bold text-md text-center'>
										Библиографическое описание книги
										</p>
										<p className='text-sm whitespace-pre-line break-words'>
										{book.library_description}
										</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				)}
				</Modal>
		</>
	)
}
