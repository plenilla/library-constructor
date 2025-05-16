// components/shared/Autocomplete.tsx
"use client";
import React, { useState, useRef, ChangeEvent, useCallback } from "react";
import useMyAxios from "@/composables/useMyAxios";

interface AutocompleteProps<T> {
  endpoint: string;
  placeholder?: string;
  labelField: keyof T;
  onSelect: (item: T) => void;
  queryParam?: string;
}

const Autocomplete = <T extends { id: number | string }>({
  endpoint,
  placeholder = "Начните ввод...",
  labelField,
  onSelect,
  queryParam = "q"
}: AutocompleteProps<T>) => {
  const { request } = useMyAxios();
  const [query, setQuery] = useState<string>("");
  const [suggestions, setSuggestions] = useState<T[]>([]);
  const [visible, setVisible] = useState<boolean>(false);

  // Timer для debounce
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Функция для дебаунсинга без внешней библиотеки
  const debounce = useCallback((fn: Function, delay: number) => {
    return (...args: any[]) => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
      debounceTimer.current = setTimeout(() => {
        fn(...args);
      }, delay);
    };
  }, []);

  const fetchItems = async (searchText: string) => {
    try {
      const response = await request(
        `${endpoint}?${queryParam}=${encodeURIComponent(searchText)}`,
        "GET"
      );
      setSuggestions(response.data);
      setVisible(true);
    } catch (err) {
      console.error(`Ошибка поиска по ${endpoint}`, err);
      setSuggestions([]);
    }
  };

  // Создаем дебаунсированную версию функции fetchItems с задержкой 300 мс
  const debouncedFetchItems = useCallback(debounce(fetchItems, 300), [debounce, fetchItems]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    if (value.length > 0) {
      debouncedFetchItems(value);
    } else {
      setSuggestions([]);
      setVisible(false);
    }
  };

  const handleSelect = (item: T) => {
    setQuery(String(item[labelField]));
    setVisible(false);
    onSelect(item);
  };

  return (
    <div className="autocomplete" style={{ position: "relative" }}>
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
      />
      {visible && suggestions.length > 0 && (
        <ul
          className="autocomplete-list"
          style={{
            position: "absolute",
            background: "#fff",
            opacity: 0.9,
            width: "100%",
            listStyle: "none",
            margin: 0,
            padding: "0.5em",
            border: "1px solid #ccc",
            zIndex: 100
          }}
        >
          {suggestions.map((item) => (
            <li
              key={item.id}
              onClick={() => handleSelect(item)}
              style={{ padding: "0.25em 0", cursor: "pointer" }}
            >
              {item[labelField]}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Autocomplete;
