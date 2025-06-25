'use client'

import { Exhibition } from '@/components/shared/Exhibition/exhibition'
import { Modal } from '@/components/ui/modal'
import useMyAxios from '@/composables/useMyAxios'
import { ApiResponse, ExhibitionType } from '@/interfaces/exhibition'
import Image from 'next/image'
import Link from 'next/link'
import { useCallback, useEffect, useState } from 'react'
import { MdAdd, MdArrowBack } from 'react-icons/md'

export default function CreateExhibitionsPage() {
	const {
		request: listRequest,
		loading: listLoading,
		error: listError,
		data: listData,
	} = useMyAxios<ApiResponse<ExhibitionType>>()

	const {
		request: createRequest,
		loading: createLoading,
		error: createError,
		data: createdExhibition,
	} = useMyAxios<ExhibitionType>()

	const {
		request: deleteRequest,
		loading: deleteLoading,
		error: deleteError,
	} = useMyAxios()

	const [page, setPage] = useState(1)
	const size = 10
	const [totalPages, setTotalPages] = useState(1)
	const [roleState, setRoleState] = useState(false)
	const [isModalOpen, setModalOpen] = useState(false)
	const [title, setTitle] = useState('')
	const [description, setDescription] = useState('')
	const [isPublished, setIsPublished] = useState(false)
	const [showEmpty, setShowEmpty] = useState(false)
	const [imageFile, setImageFile] = useState<File | null>(null)
	const [editingExhibition, setEditingExhibition] =
		useState<ExhibitionType | null>(null)

	// Функция для безопасного запроса списка с гарантией page >= 1
	const fetchList = useCallback(async () => {
		try {
			const safePage = Math.max(1, page)
			if (safePage !== page) {
				setPage(1)
			}

			const resp = await listRequest(
				`v2/exhibitionsPage/?page=${safePage}&size=${size}`,
				'GET'
			)
			if (resp.data) {
				setTotalPages(Math.max(1, resp.data.total_pages))
				if (safePage > resp.data.total_pages) {
					setPage(resp.data.total_pages)
				}
			}
		} catch (e) {
			console.error('Ошибка при загрузке списка:', e)
		}
	}, [page, size, listRequest])

	// При изменении page — загружаем список
	useEffect(() => {
		fetchList()
	}, [fetchList])

	// При создании новой выставки сбрасываем форму и перезагружаем список
	useEffect(() => {
		const roleAdmin = localStorage.getItem('role')
		if (roleAdmin === 'admin') {
			setRoleState(true)
		}

		if (createdExhibition) {
			setModalOpen(false)
			setTitle('')
			setDescription('')
			setIsPublished(false)
			setImageFile(null)
			setEditingExhibition(null)
			fetchList()
		}
	}, [createdExhibition, fetchList])

	useEffect(() => {
		if (createLoading || (listData && listData.items.length > 0)) {
			setShowEmpty(false)
			return
		}
		const timer = setTimeout(() => {
			setShowEmpty(true)
		}, 5000)
		return () => clearTimeout(timer)
	}, [createLoading, listData])

	const openModal = () => {
		setModalOpen(true)
		setEditingExhibition(null)
	}
	const closeModal = () => setModalOpen(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		const form = new FormData()
		form.append('title', title)
		form.append('description', description)
		form.append('is_published', String(isPublished))
		if (imageFile) {
			form.append('image', imageFile)
		}
		try {
			if (editingExhibition) {
				await createRequest(
					`v2/exhibitions/${editingExhibition.id}`,
					'PUT',
					form
				)
			} else {
				await createRequest('v2/exhibitions/', 'POST', form)
			}
		} catch (e) {
			console.error('Ошибка при сохранении:', e)
		}
	}

	const handleEditClick = (exh: ExhibitionType) => {
		setEditingExhibition(exh)
		setTitle(exh.title)
		setDescription(exh.description)
		setIsPublished(exh.is_published)
		setModalOpen(true)
	}

	const handleDelete = async (id: number) => {
		if (confirm('Вы уверены, что хотите удалить эту выставку?')) {
			try {
				await deleteRequest(`v2/exhibitions/${id}`, 'DELETE')
				fetchList()
			} catch (e) {
				console.error('Ошибка при удалении:', e)
			}
		}
	}

	const getPageNumbers = () => {
		const max = 5
		let start = 1,
			end = totalPages
		if (totalPages > max) {
			if (page <= 3) {
				start = 1
				end = max
			} else if (page + 2 >= totalPages) {
				start = totalPages - (max - 1)
				end = totalPages
			} else {
				start = page - 2
				end = page + 2
			}
		}
		const nums: number[] = []
		for (let i = start; i <= end; i++) nums.push(i)
		return nums
	}

	return (
		<main className='max-w-7xl mx-auto p-4'>
			<div className='flex justify-between items-center mb-6'>
				<Link
					href='/exhibitions'
					className='flex items-center text-black hover:underline'
				>
					<MdArrowBack size={24} />
					<span className='ml-2'>Назад к списку</span>
				</Link>
				<button
					onClick={openModal}
					className='flex items-center z-40 bg-black text-white px-4 py-2 rounded hover:bg-black/90'
				>
					<MdAdd size={20} className='mr-2' /> Создать выставку
				</button>
			</div>

			<Modal
				isOpen={isModalOpen}
				onClose={closeModal}
				title={
					editingExhibition ? 'Редактировать выставку' : 'Создать выставку'
				}
				size='md'
			>
				<form onSubmit={handleSubmit} className='space-y-4 p-4'>
					<div>
						<label className='block mb-1'>Заголовок</label>
						<input
							type='text'
							value={title}
							onChange={e => setTitle(e.target.value)}
							required
							className='w-full border rounded px-3 py-2'
						/>
					</div>

					<div>
						<label className='block mb-1'>Описание</label>
						<textarea
							value={description}
							onChange={e => setDescription(e.target.value)}
							className='w-full border rounded px-3 py-2'
						/>
					</div>

					<div className='flex items-center'>
						<input
							id='published'
							type='checkbox'
							checked={isPublished}
							onChange={e => setIsPublished(e.target.checked)}
							className='mr-2'
						/>
						<label htmlFor='published'>Опубликовать</label>
					</div>

					<div>
						<label className='block mb-1'>Изображение</label>
						<input
							type='file'
							accept='image/*'
							onChange={e => e.target.files && setImageFile(e.target.files[0])}
						/>
					</div>

					<div className='flex justify-end space-x-2'>
						<button
							type='button'
							onClick={closeModal}
							className='px-4 py-2 rounded border'
						>
							Отмена
						</button>
						<button
							type='submit'
							disabled={createLoading}
							className='px-4 py-2 rounded bg-black hover:bg-black/90 text-white disabled:opacity-50'
						>
							{createLoading ? 'Сохранение...' : 'Сохранить'}
						</button>
					</div>

					{createError && (
						<p className='text-red-500'>Ошибка: {String(createError)}</p>
					)}
				</form>
			</Modal>

			{listError && (
				<div className='fixed inset-0 flex items-center justify-center bg-white'>
					<div className='px-4 py-2 bg-red-100 text-red-700 rounded'>
						Ошибка при загрузке выставок
					</div>
				</div>
			)}

			{(() => {
				if (listData && listData.items.length > 0) {
					return <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'></div>
				}
				if (showEmpty) {
					return (
						<div className='absolute inset-0 flex items-center justify-center'>
							<div className='px-4 py-2 bg-blue-100 text-black rounded'>
								Нет выставок для отображения
							</div>
						</div>
					)
				}
				return (
					<div className='absolute inset-0 flex items-center justify-center'>
						<div className='w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin' />
					</div>
				)
			})()}

			{listData && (
				<ul className='space-y-4'>
					{listData.items.map(exh => (
						<li
							key={exh.id}
							className='relative border rounded p-4 pl-12' 
						>
							<Image
								src={
									exh.is_published
										? '/icons/publish.svg'
										: '/icons/unpublished.svg'
								}
								alt={exh.is_published ? 'Published' : 'Unpublished'}
								className='absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6'
								width={50}
								height={50}
							/>

							<Link href={`/exhibitions/${exh.slug}`} className='block mb-2'>
								<Exhibition exhibition={exh} />
							</Link>
							<div
								className='flex space-x-1 absolute bottom-10 right-5 md:bottom-26 md:right-10'
							>
								<button onClick={() => handleEditClick(exh)} className='' title='Изменить данные выставки'>
									<Image
										src={'/icons/rewrite.svg'}
										width={35}
										height={35}
										className='hover:bg-black/25'
										alt={'Изменить выставку'}
									></Image>
								</button>
								<Link href={`/exhibitions/${exh.slug}/edit`} className='' title='Конструктор ЭКВ'>
									<Image
										src={'/icons/redactor.svg'}
										width={35}
										height={35}
										className='hover:bg-black/25'
										alt={'Радектор'}
									></Image>
								</Link>
								<button onClick={() => handleDelete(exh.id)} className='' title='Удалить'>
									<Image
										src={'/icons/delete.svg'}
										width={35}
										height={35}
										className='hover:bg-black/25'
										alt={'Удалить'}
									></Image>
								</button>
							</div>
						</li>
					))}
				</ul>
			)}

			<div className='flex justify-center mt-6 space-x-1'>
				<button
					onClick={() => setPage(p => Math.max(1, p - 1))}
					disabled={page === 1 || listLoading}
					className='px-2 py-1 border rounded disabled:opacity-50'
				>
					‹
				</button>
				{getPageNumbers().map(num => (
					<button
						key={num}
						onClick={() => setPage(num)}
						disabled={listLoading}
						className={`px-2 py-1 rounded ${
							num === page ? 'bg-black text-white' : 'border'
						}`}
					>
						{num}
					</button>
				))}
				<button
					onClick={() => setPage(p => Math.min(totalPages, p + 1))}
					disabled={page === totalPages || listLoading}
					className='px-2 py-1 border rounded disabled:opacity-50'
				>
					›
				</button>
			</div>
		</main>
	)
}
