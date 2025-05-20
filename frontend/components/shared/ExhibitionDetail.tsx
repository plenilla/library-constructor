'use client'
import { Modal } from '@/components/ui/modal'
import useMyAxios from '@/composables/useMyAxios'
import {
  ContentBlock,
  ExhibitionSection,
  ExhibitionType,
} from "@/interfaces/exhibition";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";

interface Props {
  slug: string;
}

export default function ExhibitionDetail({ slug }: Props) {
  const { request, loading, error, data } = useMyAxios<ExhibitionType>();
  const [isFixed, setIsFixed] = useState(false);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [selectedBook, setSelectedBook] = useState<any>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    request(`/v2/exhibitions/${slug}`, "GET");
  }, [slug, request]);

  const handleScroll = () => {
    if (!contentRef.current) return;
    const rect = contentRef.current.getBoundingClientRect();
    const scrollY = window.scrollY;
    if (rect.top <= 0 && !isFixed) {
      setLastScrollY(scrollY);
      setIsFixed(true);
    } else if (scrollY < lastScrollY) {
      setIsFixed(false);
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [isFixed, lastScrollY]);

  useEffect(() => {
    document.body.style.overflow = selectedBook ? "hidden" : "auto";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [selectedBook]);

  if (loading) return <p className="text-center py-20">Загрузка...</p>;
  if (error)
    return (
      <p className="text-center py-20 text-red-500">
        Ошибка: {error.message || error}
      </p>
    );
  if (!data) return <p className="text-center py-20">Данных нет</p>;

  // Функция для расчета классов сетки: максимум 3 колонки на мобильных,
  // новые строки автоматически при >3 элементов
  const getBookGridClasses = (section: ExhibitionSection) => {
    const bookCount = section.content_blocks.filter(
      (b) => b.type === 'book' && b.book
    ).length;
    const mobileCols =
      bookCount === 1 ? 'grid-cols-1' : bookCount === 2 ? 'grid-cols-2' : 'grid-cols-3';
    return `grid ${mobileCols} md:grid-cols-3 gap-4`;
  };

  const imageUrl = data.image?.startsWith("http")
    ? data.image
    : new URL(data.image!, process.env.NEXT_PUBLIC_URL).toString();

  return (
    <div>
      <div className="relative min-h-[50vh] bg-gray-200">
        {data.image && (
          <Image
            src={imageUrl}
            alt={data.title}
            fill
            style={{ objectFit: "cover" }}
            unoptimized
          />
        )}
        <h1 className="relative text-3xl sm:text-5xl p-4 sm:p-5 text-white leading-tight">
          {data.title}
        </h1>
      </div>

      <div className="flex flex-col md:flex-row p-4 md:p-15">
        <div className="w-full md:w-[80%] p-2 md:p-5 space-y-10">
          {data.sections.map((section: ExhibitionSection) => (
            <div key={section.id} id={`section-${section.id}`}>   
              <h2 className="text-2xl sm:text-4xl mb-4">{section.title}</h2>
              <div className={getBookGridClasses(section)}>
                {section.content_blocks.map((block: ContentBlock) => {
                  if (block.type === 'text') {
                    return (
                      <div
                        key={block.id}
                        className='text-base sm:text-2xl mb-2 col-span-full prose max-w-none'
                        dangerouslySetInnerHTML={{ __html: block.text_content }}
                      />
                    )
                  }
                  if (block.type === "book" && block.book) {
                    return (
                      <div
                        key={block.id}
                        className="group cursor-pointer relative"
                        onClick={() => setSelectedBook(block.book)}
                      >
                        <div className="relative aspect-[3/4] bg-gray-50 rounded-lg overflow-hidden shadow-md">
                          {block.book.image_url && (
                            <Image
                              src={`${process.env.NEXT_PUBLIC_BASE_URL}${block.book.image_url}`}
                              alt={block.book.title}
                              fill
                              className="object-cover transition-transform duration-300 group-hover:scale-105"
                              sizes="(max-width: 768px) 100vw, 33vw"
                            />
                          )}
                        </div>
                        <div className="mt-2 text-center space-y-1">
                          <h3 className="text-base sm:text-lg font-semibold text-gray-900">
                            {block.book.title}
                          </h3>
                          <p className="text-xs sm:text-sm text-gray-600">
                            {block.book.author}
                          </p>
                        </div>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          ))}
        </div>

        <div
          ref={contentRef}
          className={`hidden sm:block pl-5 md:pl-15 w-full md:w-[20%] ${isFixed ? "fixed top-5 right-5" : "relative"}`}
        >
          <h3 className="text-xl sm:text-2xl mb-4">Содержание</h3>
          <nav>
            <ul className="space-y-2">
              {data.sections.map((section) => (
                <li key={section.id}>
                  <span
                    onClick={() => {
                      const sectionElement = document.getElementById(
                        `${section.id}`
                      );
                      if (sectionElement) {
                        sectionElement.scrollIntoView({ behavior: "smooth" });
                      }
                    }}
                    className="text-blue-600 hover:text-blue-800 transition-colors text-sm"
                  >
                    {section.title}
                  </span>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>

      <Modal
        size="full"
        isOpen={!!selectedBook}
        onClose={() => {
          setSelectedBook(null);
          setIsFullscreen(false);
        }}
        className={
          isFullscreen
            ? "fixed z-50 bg-transparent border-none shadow-none"
            : "overflow-y-auto w-full h-full m-0 p-0"
        }
      >
        {selectedBook && (
          <>            
            {isFullscreen ? (
              <div className="fixed inset-0 flex items-center justify-center p-4">
                <Image
                  src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                  alt={selectedBook.title}
                  fill
                  className="object-contain"
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsFullscreen(false);
                  }}
                />
              </div>
            ) : (
              <div className="flex flex-col space-y-6 p-4">
                <div className="relative w-full cursor-zoom-in min-h-[180px]">
                  <div className="absolute inset-0 overflow-hidden rounded-lg">
                    <Image
                      src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                      alt={selectedBook.title}
                      fill
                      className="object-cover blur-xs"
                    />
                    <div className="absolute inset-0 bg-black/50"></div>
                  </div>

                  <div className="relative z-10 flex flex-col items-center justify-center h-full p-4">
                    <Image
                      src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                      alt={selectedBook.title}
                      width={120}
                      height={160}
                      className="object-contain w-2/3 shadow-accent-foreground"
                    />
                    <div className="mt-3 text-center">
                      <h2 className="text-lg sm:text-2xl font-bold text-white drop-shadow-md">
                        {selectedBook.title}
                      </h2>
                      <p className="text-sm sm:text-lg text-white/80">
                        {selectedBook.author}
                      </p>
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
                      <MagnifyingGlassIcon className="h-5 w-5" />
                    </span>
                  </button>
                </div>
                <div className="w-full space-y-4">
                  <div className="overflow-y-auto rounded-lg p-3 bg-white">
                    <h1 className="font-bold text-xl mb-3">О книге</h1>
                    <p className="text-sm sm:text-base whitespace-pre-line">
                      {selectedBook.annotations}
                    </p>
                    <p className="text-sm sm:text-base whitespace-pre-line break-words mt-3">
                      {selectedBook.library_description}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  );
}