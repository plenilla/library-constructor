'use client'
import Autocomplete from '@/components/shared/Autocomplete'
import { Books } from '@/components/shared/Books/books'
import useMyAxios from '@/composables/useMyAxios'
import { Author, Book, Genre } from '@/interfaces/books'
import React, { useEffect, useState } from 'react'
import ImageWithRefresh from '@/components/ImageWithRefresh'


const BookPage: React.FC = () => {
  const { request, loading, error } = useMyAxios()

  const [selectedAuthor, setSelectedAuthor] = useState<Author | null>(null)
  const [selectedGenre, setSelectedGenre] = useState<Genre | null>(null)
  const [selectedSort, setSelectedSort] = useState<string>('')

  const [books, setBooks] = useState<Book[]>([])
  const [authors, setAuthors] = useState<Author[]>([])
  const [genres, setGenres] = useState<Genre[]>([])

  // Добавляем базовый URL для API
  const API_BASE = '/v2/'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [booksRes, authorsRes, genresRes] = await Promise.all([
          request(`${API_BASE}library/books/`, 'GET'), // 
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
        
        if (selectedAuthor) params.append('author_id', String(selectedAuthor.id))
        if (selectedGenre) params.append('genre_id', String(selectedGenre.id))
        if (selectedSort) params.append('sort_order', selectedSort)

        // Используем URLSearchParams для правильного формирования URL
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

			<div className='filters'>
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

				<div className='filter-item'>
					<label>Сортировка:</label>
					<select
						value={selectedSort}
						onChange={e => setSelectedSort(e.target.value)}
					>
						<option value=''>Без сортировки</option>
						<option value='asc'>По возрастанию (А-Я)</option>
						<option value='desc'>По убыванию (Я-А)</option>
					</select>
				</div>
			</div>

			<div className='book-list'>
				{books.map(book => (
					<Books key={book.id} book={book} />
				))}
			</div>
		</>
	)
}

export default BookPage
