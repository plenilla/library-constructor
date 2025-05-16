'use client'

import { Exhibition } from '@/components/shared/Exhibition/exhibition'
import { Modal } from '@/components/ui/modal'
import useMyAxios from '@/composables/useMyAxios'
import { ApiResponse, ExhibitionType } from '@/interfaces/exhibition'
import Link from 'next/link'
import { useEffect, useState } from 'react'
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
	const [imageFile, setImageFile] = useState<File | null>(null)
	const [editingExhibition, setEditingExhibition] =
		useState<ExhibitionType | null>(null)

	useEffect(() => {
		const fetchList = async () => {
			try {
				const resp = await listRequest(
					`v2/exhibitionsPage/?page=${page}&size=${size}`,
					'GET'
				)
				if (resp.data) {
					setTotalPages(Math.max(1, resp.data.total_pages))
					if (page > resp.data.total_pages) setPage(resp.data.total_pages)
				}
			} catch (e) {
				console.error(e)
			}
		}
		fetchList()
	}, [page, listRequest])

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
			listRequest(`v2/exhibitionsPage/?page=${page}&size=${size}`, 'GET')
		}
	}, [createdExhibition, page, listRequest])

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
		if (imageFile) form.append('image', imageFile)
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
			console.error(e)
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
				await listRequest(
					`v2/exhibitionsPage/?page=${page}&size=${size}`,
					'GET'
				)
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
					className='flex items-center text-blue-600 hover:underline'
				>
					<MdArrowBack size={24} />
					<span className='ml-2'>Назад к списку</span>
				</Link>
				<button
					onClick={openModal}
					className='flex items-center bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700'
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
						<label htmlFor='published'>Опубликовать сразу</label>
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
							className='px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50'
						>
							{createLoading ? 'Сохранение...' : 'Сохранить'}
						</button>
					</div>

					{createError && (
						<p className='text-red-500'>Ошибка: {String(createError)}</p>
					)}
				</form>
			</Modal>

			{listLoading && <p>Загрузка...</p>}
			{listError && <p className='text-red-500'>Ошибка при загрузке списка</p>}

			{listData && (
				<ul className='space-y-4'>
					{listData.items.map(exh => (
						<li key={exh.id} className='border rounded p-4 relative'>
							<Link href={`/exhibitions/${exh.slug}`} className='block mb-2'>
								<Exhibition exhibition={exh} />
							</Link>
							<div className='flex space-x-2 absolute top-2 right-2'>
								<button
									onClick={() => handleEditClick(exh)}
									className='px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600'
								>
									Изменить
								</button>
								<Link
									href={`/exhibitions/${exh.slug}/edit`}
									className='px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600'
								>
									Редактор
								</Link>
								<button
									onClick={() => handleDelete(exh.id)}
									className='px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700'
								>
									Удалить
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
