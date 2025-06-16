'use client'

import { Exhibition } from '@/components/shared/Exhibition/exhibition'
import useMyAxios from '@/composables/useMyAxios'
import { ApiResponse, ExhibitionType } from '@/interfaces/exhibition'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { MdArrowBack, MdArrowForward, MdSearch } from 'react-icons/md'

const ExhibitionsPage: React.FC = () => {
  const { request, loading, error, data } =
    useMyAxios<ApiResponse<ExhibitionType>>()
  const [page, setPage] = useState(1)
  const [size] = useState(10)
  const [totalPages, setTotalPages] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [startDate, setStartDate] = useState<Date | null>(null)
  const [endDate, setEndDate] = useState<Date | null>(null)
  const [showEmpty, setShowEmpty] = useState(false)

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    setPage(1)
  }

  const getPageNumbers = () => {
    const maxPagesToShow = 5
    let startPage: number, endPage: number

    if (totalPages <= maxPagesToShow) {
      startPage = 1
      endPage = totalPages
    } else if (page <= 3) {
      startPage = 1
      endPage = maxPagesToShow
    } else if (page + 2 >= totalPages) {
      startPage = totalPages - (maxPagesToShow - 1)
      endPage = totalPages
    } else {
      startPage = page - 2
      endPage = page + 2
    }

    return Array.from(
      { length: endPage - startPage + 1 },
      (_, i) => startPage + i
    )
  }

  useEffect(() => {
    if (loading || (data && data.items.length > 0)) {
      setShowEmpty(false)
      return
    }
    const timer = setTimeout(() => {
      setShowEmpty(true)
    }, 5000)
    return () => clearTimeout(timer)
  }, [loading, data])

  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          size: size.toString(),
          published: 'true',
        })
        if (searchQuery) params.append('search', searchQuery)
        if (startDate) params.append('date_from', startDate.toISOString())
        if (endDate) params.append('date_to', endDate.toISOString())

        const response = await request(
          `v2/exhibitionsPage/?${params.toString()}`,
          'GET'
        )
        if (response?.data) {
          const pages = Math.max(1, response.data.total_pages || 1)
          setTotalPages(pages)
          if (page > pages) setPage(pages)
        }
      } catch (err) {
        console.error('Ошибка при загрузке выставок', err)
      }
    }

    fetchData()
  }, [page, size, searchQuery, startDate, endDate, request])

  return (
    <main className="relative min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
          <div className="space-y-2">
            <h1 className="text-4xl md:text-5xl font-bold">Выставки</h1>
            <div className="flex gap-4 items-center">
              <DatePicker
                selected={startDate}
                onChange={date => setStartDate(date)}
                placeholderText="Дата от"
                className="p-2 border rounded"
              />
              <DatePicker
                selected={endDate}
                onChange={date => setEndDate(date)}
                placeholderText="Дата до"
                className="p-2 border rounded"
              />
            </div>
          </div>
          <div className="w-full md:w-72 relative">
            <input
              type="search"
              placeholder="Поиск выставок..."
              value={searchQuery}
              onChange={handleSearch}
              className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl" />
          </div>
        </div>

        {error && (
          <div className="fixed inset-0 flex items-center justify-center bg-white">
            <div className="px-4 py-2 bg-red-100 text-red-700 rounded">
              Ошибка при загрузке выставок
            </div>
          </div>
        )}

        {/* Основной блок: спиннер / список / сообщение «Нет выставок» */}
        {(() => {
          // 1) Список есть — сразу рендерим
          if (data && data.items.length > 0) {
            return (
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <ul>
                  {data.items.map(exhibit => (
                    <Link
                      href={`/exhibitions/${encodeURIComponent(exhibit.slug)}`}
                      key={exhibit.id}
                    >
                      <Exhibition exhibition={exhibit} />
                    </Link>
                  ))}
                </ul>
              </div>
            )
          }
          // 2) Список пуст и таймер истёк — показываем сообщение
          if (showEmpty) {
            return (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="px-4 py-2 bg-blue-100 text-black rounded">
                  Нет выставок для отображения
                </div>
              </div>
            )
          }
          // 3) Иначе — показываем спиннер
          return (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )
        })()}

        {/* Пагинация */}
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="px-3 py-2 rounded text-black hover:text-blue-500 disabled:opacity-50"
          >
            <MdArrowBack size={24} />
          </button>

          {getPageNumbers().map(pageNumber => (
            <button
              key={pageNumber}
              onClick={() => setPage(pageNumber)}
              disabled={loading}
              className={`px-3 py-2 rounded ${
                page === pageNumber
                  ? 'bg-black text-white'
                  : 'bg-transparent text-black hover:text-blue-500'
              } disabled:opacity-50`}
            >
              {pageNumber}
            </button>
          ))}

          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || loading}
            className="px-3 py-2 rounded text-black hover:text-blue-500 disabled:opacity-50"
          >
            <MdArrowForward size={24} />
          </button>
        </div>
      </div>
    </main>
  )
}

export default ExhibitionsPage
