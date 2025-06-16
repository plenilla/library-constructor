'use client'
import React, {
  useState,
  useRef,
  ChangeEvent,
  useCallback,
  useEffect,
} from 'react'
import useMyAxios from '@/composables/useMyAxios'

interface AutocompleteProps<T> {
  endpoint: string
  placeholder?: string
  labelField: keyof T
  onSelect?: (item: T) => void
  onMultiSelect?: (items: T[]) => void
  queryParam?: string
  multiple?: boolean
}

const Autocomplete = <T extends { id: number | string }>({
  endpoint,
  placeholder = 'Начните ввод...',
  labelField,
  onSelect,
  onMultiSelect,
  queryParam = 'q',
  multiple = false,
}: AutocompleteProps<T>) => {
  const { request } = useMyAxios()
  const [query, setQuery] = useState<string>('')
  const [suggestions, setSuggestions] = useState<T[]>([])
  const [visible, setVisible] = useState<boolean>(false)
  const [selectedItems, setSelectedItems] = useState<T[]>([])

  const containerRef = useRef<HTMLDivElement>(null)
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const debounce = useCallback((fn: Function, delay: number) => {
    return (...args: any[]) => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
      debounceTimer.current = setTimeout(() => {
        fn(...args)
      }, delay)
    }
  }, [])

  const fetchItems = async (searchText: string) => {
    try {
      const response = await request(
        `${endpoint}?${queryParam}=${encodeURIComponent(searchText)}`,
        'GET'
      )
      setSuggestions(response.data)
      setVisible(true)
    } catch (err) {
      console.error(`Ошибка поиска по ${endpoint}`, err)
      setSuggestions([])
    }
  }

  const debouncedFetchItems = useCallback(
    debounce(fetchItems, 300),
    [debounce]
  )

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    if (value.length > 0) {
      debouncedFetchItems(value)
    } else {
      setSuggestions([])
      setVisible(false)
    }
  }

  // Закрываем список при клике вне компонента
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setVisible(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleSelect = (item: T) => {
    if (multiple) {
      if (!selectedItems.some((i) => i.id === item.id)) {
        const updatedItems = [...selectedItems, item]
        setSelectedItems(updatedItems)
        onMultiSelect?.(updatedItems)
      }
      setQuery('')
      // Для мультивыбора оставляем список открытым (если нужно, можно поменять)
      setVisible(true)
    } else {
      setQuery(String(item[labelField]))
      setVisible(false)
      onSelect?.(item)
    }
  }

  const handleRemove = (id: number | string) => {
    const updatedItems = selectedItems.filter((item) => item.id !== id)
    setSelectedItems(updatedItems)
    onMultiSelect?.(updatedItems)
  }

  // При фокусе открываем список, если есть данные
  const handleFocus = () => {
    if (suggestions.length > 0) {
      setVisible(true)
    }
  }

  return (
    <div className="autocomplete relative" ref={containerRef}>
      <input
        type="text"
        value={query}
        onChange={handleChange}
        onFocus={handleFocus}
        placeholder={placeholder}
        className="w-full border rounded px-3 py-2"
      />

      {multiple && selectedItems.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {selectedItems.map((item) => (
            <span
              key={item.id}
              className="bg-gray-200 px-2 py-1 rounded-full text-sm flex items-center"
            >
              {item[labelField]}
              <button
                type="button"
                onClick={() => handleRemove(item.id)}
                className="ml-2 text-red-500 font-bold"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {visible && suggestions.length > 0 && (
        <ul className="absolute bg-white border border-gray-300 mt-1 w-full z-10 rounded shadow max-h-48 overflow-auto">
          {suggestions.map((item) => (
            <li
              key={item.id}
              onClick={() => handleSelect(item)}
              className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
            >
              {item[labelField]}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Autocomplete
