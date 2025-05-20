'use client'
import { useEffect, useState } from 'react'
import { BookInfo } from '@/interfaces/books'
import axios from 'axios'

const backendApi = axios.create({
  baseURL: 'http://82.202.137.19/v2', // Базовый URL бэкенда
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

interface BookSelectorProps {
  selectedBookId: number | null
  onSelect: (bookId: number) => void
}

export default function BookSelector({ selectedBookId, onSelect }: BookSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [selectedAuthor, setSelectedAuthor] = useState<number | ''>('')
  const [selectedGenre, setSelectedGenre] = useState<number | ''>('')
  const [books, setBooks] = useState<BookInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [authors, setAuthors] = useState<{ id: number; name: string }[]>([])
  const [genres, setGenres] = useState<{ id: number; name: string }[]>([])

  // Загружаем авторов и жанры при монтировании
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [authorsRes, genresRes] = await Promise.all([
          backendApi.get('/library/authors/options'),
          backendApi.get('/library/genres/options'),
        ])
        setAuthors(authorsRes.data)
        setGenres(genresRes.data)
      } catch (error) {
        console.error('Error fetching options:', error)
      }
    }
    fetchOptions()
  }, [])

  useEffect(() => {
    const fetchBooks = async () => {
      setLoading(true)
      try {
        const params = {
          search: searchTerm,
          sort_order: sortOrder,
          author_id: selectedAuthor || undefined,
          genre_id: selectedGenre || undefined
        }
        
        const response = await backendApi.get<BookInfo[]>('/library/books', { params })
        setBooks(response.data)
      } catch (error) {
        console.error('Error fetching books:', error)
      } finally {
        setLoading(false)
      }
    }

    const debounceTimer = setTimeout(fetchBooks, 500)
    return () => clearTimeout(debounceTimer)
  }, [searchTerm, sortOrder, selectedAuthor, selectedGenre])

    const imageUrl = data.image?.startsWith("http")
      ? data.image
      : new URL(data.image!, process.env.NEXT_PUBLIC_URL).toString();
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Поиск по названию..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="p-2 border rounded"
        />
        
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
          className="p-2 border rounded"
        >
          <option value="asc">По возрастанию</option>
          <option value="desc">По убыванию</option>
        </select>

        <select
          value={selectedAuthor}
          onChange={(e) => setSelectedAuthor(Number(e.target.value) || '')}
          className="p-2 border rounded"
        >
          <option value="">Все авторы</option>
          {authors.map((author) => (
            <option key={author.id} value={author.id}>
              {author.name}
            </option>
          ))}
        </select>

        <select
          value={selectedGenre}
          onChange={(e) => setSelectedGenre(Number(e.target.value) || '')}
          className="p-2 border rounded"
        >
          <option value="">Все жанры</option>
          {genres.map((genre) => (
            <option key={genre.id} value={genre.id}>
              {genre.name}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-4">Загрузка...</div>
      ) : (
        <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto">
          {books.map((book) => (
            <div
              key={book.id}
              onClick={() => onSelect(book.id)}
              className={`p-4 border rounded cursor-pointer ${
                selectedBookId === book.id ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-4">
                {book.image_url && (
                  <img
                    src={imageUrl}
                    alt={book.title}
                    className="w-16 h-24 object-cover rounded"
                    onError={(e) => { // Обработка ошибок загрузки изображений
                      (e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                )}
                <div>
                  <h3 className="font-medium">{book.title}</h3>
                  <p className="text-sm text-gray-500">
                    {book.authors?.map(a => a.name).join(', ')}
                  </p>
                  <p className="text-sm text-gray-500">Год: {book.year_of_publication}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}