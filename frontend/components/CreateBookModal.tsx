// components/CreateBookModal.tsx
'use client'

import React, { useState } from 'react'
import Autocomplete from '@/components/shared/Autocomplete'
import useMyAxios from '@/composables/useMyAxios'
import { Author, Genre, Book } from '@/interfaces/books'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Modal } from '@/components/ui/modal'

interface CreateBookModalProps {
  isOpen: boolean
  onClose: () => void
  onBookCreated?: (book: Book) => void
}

const CreateBookModal: React.FC<CreateBookModalProps> = ({ 
  isOpen, 
  onClose,
  onBookCreated
}) => {
  const { request, loading, error } = useMyAxios()

  const [title, setTitle] = useState('')
  const [selectedAuthors, setSelectedAuthors] = useState<Author[]>([])
  const [selectedGenres, setSelectedGenres] = useState<Genre[]>([])
  const [annotations, setAnnotations] = useState('')
  const [libraryDescription, setLibraryDescription] = useState('')
  const [year, setYear] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [authorInputVisible, setAuthorInputVisible] = useState(false)
  const [newAuthorName, setNewAuthorName] = useState('')
  const [genreInputVisible, setGenreInputVisible] = useState(false)
  const [newGenreName, setNewGenreName] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title || selectedAuthors.length === 0 || selectedGenres.length === 0) {
      alert('Заполните обязательные поля: название, авторы, жанры.')
      return
    }

    try {
      const formData = new FormData()
      formData.append('title', title)
      formData.append('annotations', annotations)
      formData.append('library_description', libraryDescription)
      formData.append('year_of_publication', year)
      formData.append('genre_ids', selectedGenres.map(g => g.id).join(','))
      formData.append('author_ids', selectedAuthors.map(a => a.id).join(','))
      if (file) formData.append('image_url', file)

      const res = await request('/v2/library/books/', 'POST', formData)

      const createdBook: Book = res.data
      
      // Закрываем модальное окно
      onClose()
      
      // Сбрасываем форму
      resetForm()
      
      // Вызываем callback если нужно
      if (onBookCreated) {
        onBookCreated(createdBook)
      }
    } catch (err) {
      console.error('Ошибка при создании книги', err)
      alert('Ошибка при создании книги')
    }
  }

  const resetForm = () => {
    setTitle('')
    setSelectedAuthors([])
    setSelectedGenres([])
    setAnnotations('')
    setLibraryDescription('')
    setYear('')
    setFile(null)
    setAuthorInputVisible(false)
    setNewAuthorName('')
    setGenreInputVisible(false)
    setNewGenreName('')
  }

  const handleCreateAuthor = async () => {
    const name = newAuthorName.trim()
    if (!name) return
    try {
      const res = await request('/v2/library/authors/', 'POST', { name })
      setSelectedAuthors(prev => [...prev, res.data])
      setNewAuthorName('')
      setAuthorInputVisible(false)
    } catch (err) {
      console.error('Ошибка при создании автора', err)
      alert('Не удалось создать автора')
    }
  }

  const handleCreateGenre = async () => {
    const name = newGenreName.trim()
    if (!name) return
    try {
      const res = await request('/v2/library/genres/', 'POST', { name })
      setSelectedGenres(prev => [...prev, res.data])
      setNewGenreName('')
      setGenreInputVisible(false)
    } catch (err) {
      console.error('Ошибка при создании жанра', err)
      alert('Не удалось создать жанр')
    }
  }

  const onAuthorsChange = (authors: Author[]) => {
    setSelectedAuthors(authors)
    setAuthorInputVisible(false)
  }

  const onGenresChange = (genres: Genre[]) => {
    setSelectedGenres(genres)
    setGenreInputVisible(false)
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Создание новой книги"
      size="xl"
      disableOutsideClick={loading}
    >
      <div className="p-4 max-h-[80vh] overflow-y-auto">
        {error && <div className="text-red-500 mb-4">Ошибка: {error.message}</div>}

        <form onSubmit={handleSubmit} className="space-y-4" encType="multipart/form-data">
          <div>
            <label className="block font-medium mb-1">Название *</label>
            <Input
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="font-medium">Авторы *</label>
              {!authorInputVisible && (
                <button
                  type="button"
                  className="text-blue-500 text-sm"
                  onClick={() => setAuthorInputVisible(true)}
                >
                  + Добавить автора
                </button>
              )}
            </div>

            {authorInputVisible && (
              <div className="flex gap-2 mb-2 flex-wrap">
                <Input
                  value={newAuthorName}
                  onChange={e => setNewAuthorName(e.target.value)}
                  placeholder="Имя нового автора"
                  autoFocus
                  className="flex-1 min-w-[200px]"
                />
                <Button type="button" onClick={handleCreateAuthor} disabled={loading}>
                  Сохранить
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setAuthorInputVisible(false)
                    setNewAuthorName('')
                  }}
                >
                  Отмена
                </Button>
              </div>
            )}

            <Autocomplete<Author>
              endpoint="v2/library/authors/search/"
              placeholder="Введите имя автора..."
              labelField="name"
              multiple
              onMultiSelect={onAuthorsChange}
              selectedItems={selectedAuthors}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="font-medium">Формы *</label>
              {!genreInputVisible && (
                <button
                  type="button"
                  className="text-blue-500 text-sm"
                  onClick={() => setGenreInputVisible(true)}
                >
                  + Добавить форму
                </button>
              )}
            </div>

            {genreInputVisible && (
              <div className="flex gap-2 mb-2 flex-wrap">
                <Input
                  value={newGenreName}
                  onChange={e => setNewGenreName(e.target.value)}
                  placeholder="Название нового форму"
                  autoFocus
                  className="flex-1 min-w-[200px]"
                />
                <Button type="button" onClick={handleCreateGenre} disabled={loading}>
                  Сохранить
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setGenreInputVisible(false)
                    setNewGenreName('')
                  }}
                >
                  Отмена
                </Button>
              </div>
            )}

            <Autocomplete<Genre>
              endpoint="v2/library/genres/search/"
              placeholder="Введите название форму..."
              labelField="name"
              multiple
              onMultiSelect={onGenresChange}
              selectedItems={selectedGenres}
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Аннотация</label>
            <textarea
              value={annotations}
              onChange={e => setAnnotations(e.target.value)}
              rows={4}
              className="w-full border rounded p-2"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Описание для библиотеки</label>
            <textarea
              value={libraryDescription}
              onChange={e => setLibraryDescription(e.target.value)}
              rows={4}
              className="w-full border rounded p-2"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Год публикации</label>
            <Input
              value={year}
              onChange={e => setYear(e.target.value)}
              placeholder="2025"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Обложка (файл)</label>
            <Input
              type="file"
              accept="image/*"
              onChange={e => setFile(e.target.files?.[0] || null)}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
              disabled={loading}
            >
              Отмена
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Создание...' : 'Создать книгу'}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  )
}

export default CreateBookModal