import { Book } from "@/interfaces/books";
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import Image from "next/image";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { useState, Fragment, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';


interface BookProps {
  book: Book;
}

export const Books = ({ book }: BookProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (isModalOpen) {
      // Блокируем скролл основного контента
      document.body.style.overflow = 'hidden';
    } else {
      // Восстанавливаем скролл
      document.body.style.overflow = 'auto';
    }// Очистка эффекта
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isModalOpen]);
  const imageUrl = book.image_url?.startsWith("http")
    ? book.image_url
    : new URL(book.image_url!, process.env.NEXT_PUBLIC_URL).toString();

  return (
    <>
      <Card
  className="rounded-lg shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer group overflow-hidden flex flex-row items-center justify-between p-2"
  onClick={() => setIsModalOpen(true)}
>
  {/* Левая часть - изображение */}
  <div className="flex items-center gap-3">
    <div className="relative w-[70px] md:w-[150]">
      <Image 
        src={imageUrl}
        alt={book.title}
        width={150}
        height={200}
        className="object-contain w-full h-[70px] md:h-[150px] shadow-accent-foreground"
      />
    </div>

    {/* Центральная часть - текст */}
    <CardContent className="flex flex-col items-start">
      <h3 className="text-sm truncate">{book.title}</h3>
      <p className="text-xs text-muted-foreground truncate">
        {book.author}
      </p>
    </CardContent>
  </div>

  {/* Правая часть - иконки действий */}
  <div className="flex gap-2 pr-2">
    <button 
      onClick={(e) => {
        e.stopPropagation();
        handleEdit(book.id);
      }}
      className="text-muted-foreground hover:text-blue-500 transition-colors p-1"
      aria-label="Редактировать"
    >
      <PencilIcon className="h-4 w-4" />
    </button>
    <button 
      onClick={(e) => {
        e.stopPropagation();
        handleDelete(book.id);
      }}
      className="text-muted-foreground hover:text-red-500 transition-colors p-1"
      aria-label="Удалить"
    >
      <TrashIcon className="h-4 w-4" />
    </button>
  </div>
</Card>

      <Modal
        size="full"
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setIsFullscreen(false);
        }}
        className={isFullscreen ? "fixed z-50 bg-transparent border-none shadow-none" : "overflow-y-auto w-full h-full m-0 p-0"}
      >
        {isFullscreen ? (
          <div className="fixed inset-0 md:inset-20 flex items-center justify-center">
            <Image
              src={imageUrl}
              alt={book.title}
              fill
              unoptimized
              className="object-contain"
              onClick={(e) => {
                e.stopPropagation();
                setIsFullscreen(false);
              }}
            />
          </div>
        ) : (
          <div className="flex flex-col w-full md:flex-row gap-6">
            <div className="relative md:w-1/3 cursor-zoom-in min-h-[200px]">
              {/* Размытый задний фон */}
              <div className="absolute inset-0 overflow-hidden">
                <Image
                  src={imageUrl}
                  alt={book.title}
                  fill
                  className="object-cover blur-xs"
                  unoptimized
                />
                <div className="absolute inset-0 bg-black/50"></div> {/* Затемнение */}
              </div>

              {/* Основное изображение */}
              <div className="relative z-10 flex flex-col items-center justify-center h-full p-4">
              <Image
                  src={imageUrl}
                  alt={book.title}
                  width={150}
                  height={200}
                  className="object-contain h-auto w-full shadow-accent-foreground"
                  unoptimized
                />
                <div className="mt-4 text-center">
                  <h2 className="text-2xl font-bold text-white drop-shadow-md">{book.title}</h2>
                  <p className="text-lg text-white/80">{book.author}</p>
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsFullscreen(true);
                }}
                className="absolute inset-0 z-20 w-full h-full opacity-0 hover:opacity-100 transition-opacity duration-300 flex items-center justify-center"
                aria-label="Увеличить изображение"
              >
                <span className="bg-black/70 text-white p-3 rounded-full">
                  <MagnifyingGlassIcon className="h-6 w-6" />
                </span>
              </button>
            </div>
            <div className="w-full md:w-2/3 space-y-4">
              <div className="overflow-y-auto rounded-lg p-3">
                <h1 className="font-bold">О книге</h1>
                <p className="text-sm whitespace-pre-line">{book.annotations}</p>
                <p className="text-sm whitespace-pre-line break-words">
                  {book.library_description}
                </p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
};