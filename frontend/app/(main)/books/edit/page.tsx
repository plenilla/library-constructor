'use client'
import Autocomplete from '@/components/shared/Autocomplete'
import { Books } from '@/components/shared/Books/books'
import { Modal } from '@/components/ui/modal'
import useMyAxios from '@/composables/useMyAxios'
import { Author, Book, Genre } from '@/interfaces/books'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import React, { useEffect, useState } from 'react'

const BookPage: React.FC = () => {
	const { request, loading, error } = useMyAxios()
	const [books, setBooks] = useState<Book[]>([])
	const [authors, setAuthors] = useState<Author[]>([])
	const [genres, setGenres] = useState<Genre[]>([])
	const [selectedAuthor, setSelectedAuthor] = useState<Author | null>(null)
	const [selectedGenre, setSelectedGenre] = useState<Genre | null>(null)
	const [selectedSort, setSelectedSort] = useState<string>('')

	const [editingBook, setEditingBook] = useState<Book | null>(null)
	const [editTitle, setEditTitle] = useState('')
	const [editAnnotations, setEditAnnotations] = useState('')
	const [editLibraryDescription, setEditLibraryDescription] = useState('')
	const [editImageFile, setEditImageFile] = useState<File | null>(null)
	const [editYear, setEditYear] = useState('')
	const [editGenres, setEditGenres] = useState<Genre[]>([])
	const [editAuthors, setEditAuthors] = useState<Author[]>([])

	const [newGenreName, setNewGenreName] = useState('')
	const [isAddingGenre, setIsAddingGenre] = useState(false)
	const [creatingGenreLoading, setCreatingGenreLoading] = useState(false)
	const [creatingGenreError, setCreatingGenreError] = useState('')

	const [newAuthorName, setNewAuthorName] = useState('')
	const [isAddingAuthor, setIsAddingAuthor] = useState(false)
	const [creatingAuthorLoading, setCreatingAuthorLoading] = useState(false)
	const [creatingAuthorError, setCreatingAuthorError] = useState('')

	const API_BASE = '/v2/'

	const router = useRouter()

	const handleCreateGenre = async () => {
		if (!newGenreName.trim()) return
		setCreatingGenreLoading(true)
		setCreatingGenreError('')
		try {
			const response = await request('/v2/library/genres/', 'POST', {
				name: newGenreName.trim(),
			})
			setEditGenres(prev => [...prev, response.data]) // добавляем созданный жанр в выбранные
			setNewGenreName('')
			setIsAddingGenre(false)
		} catch (err) {
			setCreatingGenreError('Ошибка создания жанра')
		} finally {
			setCreatingGenreLoading(false)
		}
	}

	const handleCreateAuthor = async () => {
		if (!newAuthorName.trim()) return
		setCreatingAuthorLoading(true)
		setCreatingAuthorError('')
		try {
			const response = await request('/v2/library/authors/', 'POST', {
				name: newAuthorName.trim(),
			})
			setEditAuthors(prev => [...prev, response.data]) // добавляем созданного автора в выбранных
			setNewAuthorName('')
			setIsAddingAuthor(false)
		} catch (err) {
			setCreatingAuthorError('Ошибка создания автора')
		} finally {
			setCreatingAuthorLoading(false)
		}
	}

	const handleDelete = async (bookId: number) => {
		try {
			await request(`${API_BASE}library/books/${bookId}`, 'DELETE')
			setBooks(prevBooks => prevBooks.filter(book => book.id !== bookId))
		} catch (err) {
			console.error('Ошибка удаления книги', err)
		}
	}

	const handleEdit = (book: Book) => {
		setEditingBook(book)
		setEditTitle(book.title)
		setEditAnnotations(book.annotations)
		setEditLibraryDescription(book.library_description)
		setEditYear(book.year_of_publication || '')
		setEditGenres(book.genres)
		setEditAuthors(book.authors)
		setEditImageFile(null) // сброс при открытии
	}

	const handleUpdate = async () => {
		if (!editingBook) return
		try {
			const formData = new FormData()
			formData.append('title', editTitle)
			formData.append('annotations', editAnnotations)
			formData.append('library_description', editLibraryDescription)
			formData.append('year_of_publication', editYear)
			if (editImageFile) {
				formData.append('image_url', editImageFile)
			}
			formData.append('genre_ids', editGenres.map(g => g.id).join(','))
			formData.append('author_ids', editAuthors.map(a => a.id).join(','))

			await request(
				`${API_BASE}library/books/${editingBook.id}`,
				'PUT',
				formData,
				{
					headers: { 'Content-Type': 'multipart/form-data' },
				}
			)

			setEditingBook(null)
			const refreshed = await request(`${API_BASE}library/books/`, 'GET')
			setBooks(refreshed.data)
		} catch (err) {
			console.error('Ошибка при обновлении книги', err)
		}
	}

	useEffect(() => {
		const fetchData = async () => {
			try {
				const [booksRes, authorsRes, genresRes] = await Promise.all([
					request(`${API_BASE}library/books/`, 'GET'),
					request(`${API_BASE}library/authors/`, 'GET'),
					request(`${API_BASE}library/genres/`, 'GET'),
				])
				setBooks(booksRes.data)
				setAuthors(authorsRes.data)
				setGenres(genresRes.data)
			} catch (err) {
				console.error('Ошибка загрузки данных', err)
			}
		}
		fetchData()
	}, [request])

	useEffect(() => {
		const fetchFilteredBooks = async () => {
			try {
				const params = new URLSearchParams()
				if (selectedAuthor)
					params.append('author_id', String(selectedAuthor.id))
				if (selectedGenre) params.append('genre_id', String(selectedGenre.id))
				if (selectedSort) params.append('sort_order', selectedSort)

				const response = await request(
					`${API_BASE}library/books/?${params.toString()}`,
					'GET'
				)
				setBooks(response.data)
			} catch (err) {
				console.error('Ошибка фильтрации', err)
			}
		}
		fetchFilteredBooks()
	}, [selectedAuthor, selectedGenre, selectedSort, request])

	return (
		<>
			{loading && <div>Загрузка...</div>}
			{error && <div>Ошибка при загрузке данных</div>}
			<div className='p-5'>
				<button
					onClick={() => router.push('/books/create')}
					className='bg-black text-white px-4 py-2 rounded hover:bg-black/90 *:transition'
				>
					Создать книгу
				</button>
			</div>
			<div className='flex space-x-8 p-5'>
				<div className='filter-item'>
					<label>Автор:</label>
					<Autocomplete<Author>
						endpoint='v2/library/authors/search/'
						placeholder='Введите имя автора...'
						labelField='name'
						onSelect={author => setSelectedAuthor(author)}
					/>
				</div>

				<div className='filter-item'>
					<label>Жанр:</label>
					<Autocomplete<Genre>
						endpoint='v2/library/genres/search/'
						placeholder='Введите название жанра...'
						labelField='name'
						onSelect={genre => setSelectedGenre(genre)}
					/>
				</div>

				<div className='flex flex-col justify-center'>
					<label className='text-sm mb-1'>Сортировка:</label>
					<select
						value={selectedSort}
						onChange={e => setSelectedSort(e.target.value)}
						className='border rounded px-2 py-1'
					>
						<option value=''>Без сортировки</option>
						<option value='asc'>По возрастанию (А–Я)</option>
						<option value='desc'>По убыванию (Я–А)</option>
					</select>
				</div>
			</div>

			<div className='book-list'>
				{books.map(book => (
					<div key={book.id} className='relative'>
						<Books book={book} />
						<div className='flex absolute right-5 top-5 md:top-15'>
							<button className='edit-button' onClick={() => handleEdit(book)}>
								<Image
									src={'/icons/rewrite.svg'}
									width={35}
									height={35}
									className='hover:bg-black/25'
									alt={'Изменить'}
								/>
							</button>
							<button
								className='delete-button'
								onClick={() => handleDelete(book.id)}
							>
								<Image
									src={'/icons/delete.svg'}
									width={35}
									height={35}
									className='hover:bg-black/25'
									alt={'Удалить'}
								/>
							</button>
						</div>
					</div>
				))}
			</div>

			{/* Модальное окно редактирования */}
			<Modal
				isOpen={!!editingBook}
				onClose={() => setEditingBook(null)}
				title='Редактировать книгу'
				size='lg'
				actions={
					<div className='flex justify-end gap-2'>
						<button
							onClick={() => setEditingBook(null)}
							className='px-4 py-2 rounded border'
						>
							Отмена
						</button>
						<button
							onClick={handleUpdate}
							className='px-4 py-2 rounded bg-black hover:bg-black/90 text-white'
						>
							Сохранить
						</button>
					</div>
				}
			>
				<div className='space-y-4 p-4'>
					<div>
						<label className='block text-sm'>Название</label>
						<input
							value={editTitle}
							onChange={e => setEditTitle(e.target.value)}
							className='w-full border rounded p-2'
						/>
					</div>

					<div>
						<label className='block text-sm'>Аннотация</label>
						<textarea
							value={editAnnotations}
							onChange={e => setEditAnnotations(e.target.value)}
							className='w-full border rounded p-2'
						/>
					</div>

					<div>
						<label className='block text-sm'>Библиографическое описание</label>
						<textarea
							value={editLibraryDescription}
							onChange={e => setEditLibraryDescription(e.target.value)}
							className='w-full border rounded p-2'
						/>
					</div>

					<div>
						<label className='block text-sm'>Год публикации</label>
						<input
							value={editYear}
							onChange={e => setEditYear(e.target.value)}
							className='w-full border rounded p-2'
						/>
					</div>

					<div>
						<label className='block text-sm'>Изображение</label>
						<input
							type='file'
							accept='image/*'
							onChange={e => {
								if (e.target.files && e.target.files.length > 0) {
									setEditImageFile(e.target.files[0])
								}
							}}
							className='w-full border rounded p-2'
						/>
					</div>

					<div>
						<label className='block text-sm'>Авторы</label>
						<Autocomplete<Author>
							endpoint='v2/library/authors/search/'
							placeholder='Добавьте автора'
							labelField='name'
							onSelect={author => {
								if (!editAuthors.find(a => a.id === author.id)) {
									setEditAuthors(prev => [...prev, author])
								}
							}}
						/>

						{!isAddingAuthor && (
							<button
								type='button'
								className='mt-1 text-blue-600 underline text-sm'
								onClick={() => setIsAddingAuthor(true)}
							>
								Добавить нового автора
							</button>
						)}

						{isAddingAuthor && (
							<div className='mt-2 flex flex-col space-y-2'>
								<input
									type='text'
									value={newAuthorName}
									onChange={e => setNewAuthorName(e.target.value)}
									placeholder='Имя автора'
									className='border rounded px-2 py-1'
									disabled={creatingAuthorLoading}
								/>
								<div className='flex space-x-2'>
									<button
										onClick={handleCreateAuthor}
										disabled={creatingAuthorLoading}
										className='bg-black hover: text-white px-3 py-1 rounded disabled:opacity-50'
									>
										{creatingAuthorLoading ? 'Сохраняем...' : 'Сохранить'}
									</button>
									<button
										onClick={() => {
											setIsAddingAuthor(false)
											setNewAuthorName('')
											setCreatingAuthorError('')
										}}
										className='px-3 py-1 rounded border'
										disabled={creatingAuthorLoading}
									>
										Отмена
									</button>
								</div>
								{creatingAuthorError && (
									<p className='text-red-600 text-sm'>{creatingAuthorError}</p>
								)}
							</div>
						)}
						<div className='mt-2 flex flex-wrap gap-2'>
							{editAuthors.map(author => (
								<div
									key={author.id}
									className='px-2 py-1 bg-gray-100 rounded-full text-sm flex items-center gap-1'
								>
									{author.name}
									<button
										onClick={() =>
											setEditAuthors(prev =>
												prev.filter(a => a.id !== author.id)
											)
										}
										className='text-red-500 ml-1'
									>
										×
									</button>
								</div>
							))}
						</div>
					</div>

					<div>
						<label className='block text-sm'>Жанры</label>
						<Autocomplete<Genre>
							endpoint='v2/library/genres/search/'
							placeholder='Добавьте жанр'
							labelField='name'
							onSelect={genre => {
								if (!editGenres.find(g => g.id === genre.id)) {
									setEditGenres(prev => [...prev, genre])
								}
							}}
						/>

						{!isAddingGenre && (
							<button
								type='button'
								className='mt-1 text-blue-600 underline text-sm'
								onClick={() => setIsAddingGenre(true)}
							>
								Добавить новый жанр
							</button>
						)}

						{isAddingGenre && (
							<div className='mt-2 flex flex-col space-y-2'>
								<input
									type='text'
									value={newGenreName}
									onChange={e => setNewGenreName(e.target.value)}
									placeholder='Название жанра'
									className='border rounded px-2 py-1'
									disabled={creatingGenreLoading}
								/>
								<div className='flex space-x-2'>
									<button
										onClick={handleCreateGenre}
										disabled={creatingGenreLoading}
										className='bg-black hover:bg-black/90 text-white px-3 py-1 rounded disabled:opacity-50'
									>
										{creatingGenreLoading ? 'Сохраняем...' : 'Сохранить'}
									</button>
									<button
										onClick={() => {
											setIsAddingGenre(false)
											setNewGenreName('')
											setCreatingGenreError('')
										}}
										className='px-3 py-1 rounded border'
										disabled={creatingGenreLoading}
									>
										Отмена
									</button>
								</div>
								{creatingGenreError && (
									<p className='text-red-600 text-sm'>{creatingGenreError}</p>
								)}
							</div>
						)}
						<div className='mt-2 flex flex-wrap gap-2'>
							{editGenres.map(genre => (
								<div
									key={genre.id}
									className='px-2 py-1 bg-gray-100 rounded-full text-sm flex items-center gap-1'
								>
									{genre.name}
									<button
										onClick={() =>
											setEditGenres(prev => prev.filter(g => g.id !== genre.id))
										}
										className='text-red-500 ml-1'
									>
										×
									</button>
								</div>
							))}
						</div>
					</div>
				</div>
			</Modal>
		</>
	)
}

export default BookPage
