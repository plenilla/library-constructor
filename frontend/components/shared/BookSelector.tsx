'use client'
import useMyAxios from '@/composables/useMyAxios'
import { useEffect, useState } from 'react'
import { BookInfo } from '@/interfaces/books'

interface BookSelectorProps {
  selectedBookId: number | null
  onSelect: (bookId: number) => void
}

export default function BookSelector({ selectedBookId, onSelect }: BookSelectorProps) {
  const { request, loading, error, data } = useMyAxios<BookInfo[]>()

  const [searchTerm, setSearchTerm] = useState('')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [selectedAuthor, setSelectedAuthor] = useState<number | ''>('')
  const [selectedGenre, setSelectedGenre] = useState<number | ''>('')
  const [books, setBooks] = useState<BookInfo[]>([])
  const [authors, setAuthors] = useState<{ id: number; name: string }[]>([])
  const [genres, setGenres] = useState<{ id: number; name: string }[]>([])

  // Fetch authors and genres once
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const authRes = await request('/v2/library/authors/options', 'GET')
        setAuthors(authRes.data)
        const genRes = await request('/v2/library/genres/options', 'GET')
        setGenres(genRes.data)
      } catch (e) {
        console.error('Error fetching options:', e)
      }
    }
    fetchOptions()
  }, [request])

  // Fetch books when filters change
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const params = new URLSearchParams()
        if (searchTerm) params.append('search', searchTerm)
        params.append('sort_order', sortOrder)
        if (selectedAuthor) params.append('author_id', String(selectedAuthor))
        if (selectedGenre) params.append('genre_id', String(selectedGenre))

        const res = await request(`/v2/library/books?${params.toString()}`, 'GET')
        setBooks(res.data)
      } catch (e) {
        console.error('Error fetching books:', e)
      }
    }

    const timer = setTimeout(fetchBooks, 500)
    return () => clearTimeout(timer)
  }, [searchTerm, sortOrder, selectedAuthor, selectedGenre, request])

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
          {books.map((book) => {
            const img = book.image_url ?? ''
            const imageUrl = img.startsWith('http')
              ? img
              : new URL(img, process.env.NEXT_PUBLIC_BASE_URL).toString()

            return (
              <div
                key={book.id}
                onClick={() => onSelect(book.id)}
                className={`p-4 border rounded cursor-pointer ${
                  selectedBookId === book.id ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-4">
                  {img && (
                    <img
                      src={imageUrl}
                      alt={book.title}
                      className="w-16 h-24 object-cover rounded"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none'
                      }}
                    />
                  )}
                  <div>
                    <h3 className="font-medium">{book.title}</h3>
                    <p className="text-sm text-gray-500">
                      {book.authors?.map((a) => a.name).join(', ')}
                    </p>
                    <p className="text-sm text-gray-500">Год: {book.year_of_publication}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {error && <div className="text-red-600">Ошибка: {String(error)}</div>}
    </div>
  )
}
