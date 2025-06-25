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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // Запрос данных
  useEffect(() => {
    request(`/v2/exhibitions/${slug}`, "GET");
  }, [slug, request]);

  // Фиксация оглавления при скролле
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

  // Блокировка скролла боди при открытой модалке
  useEffect(() => {
    document.body.style.overflow = isModalOpen ? "hidden" : "auto";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isModalOpen]);

  if (loading) return <p className="text-center py-20">Загрузка...</p>;
  if (error)
    return (
      <p className="text-center py-20 text-red-500">
        Ошибка: {error.message || error}
      </p>
    );
  if (!data) return <p className="text-center py-20">Данных нет</p>;

  // Обработка сетки книг
  const getBookGridClasses = (section: ExhibitionSection) => {
    const cnt = section.content_blocks.filter(
      (b) => b.type === 'book' && b.book
    ).length;
    const mobileCols =
      cnt === 1 ? 'grid-cols-1' : cnt === 2 ? 'grid-cols-2' : 'grid-cols-3';
    return `grid ${mobileCols} md:grid-cols-3 gap-4`;
  };

  // URL обложки выставки
  const expoImageUrl = data.image?.startsWith("http")
    ? data.image
    : new URL(data.image!, process.env.NEXT_PUBLIC_URL).toString();


    
  return (
    <div>
      {/* Заставка */}
      <div className="relative min-h-[50vh] bg-gray-200">
        {data.image && (
          <Image
            src={expoImageUrl}
            alt={data.title}
            fill
            style={{ objectFit: "cover" }}
            unoptimized
          />
        )}
        <h1 className="relative text-3xl sm:text-5xl p-4 sm:p-5 text-white leading-tight"
            style={{
              textShadow: '0 0 10px rgba(0, 0, 0, 0.5)',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
            }}>
          {data.title}
        </h1>
      </div>

      <div className="flex flex-col md:flex-row p-4 md:p-15">
        {/* Основное содержимое */}
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
                        className='text-base sm:text-2xl mb-2 col-span-full prose max-w-none indent-8'
                        dangerouslySetInnerHTML={{ __html: block.text_content }}
                      />
                    );
                  }
                  if (block.type === "book" && block.book) {
                    const imgUrl = block.book.image_url?.startsWith("http")
                      ? block.book.image_url
                      : `${process.env.NEXT_PUBLIC_BASE_URL}${block.book.image_url}`;
                    return (
                      <div
                        key={block.id}
                        className="group cursor-pointer relative"
                        onClick={() => {
                          setSelectedBook(block.book);
                          setIsModalOpen(true);
                        }}
                      >
                        <div className="relative aspect-[3/4] bg-gray-50 rounded-lg overflow-hidden shadow-md">
                          {block.book.image_url && (
                            <Image
                              src={imgUrl}
                              alt={block.book.title}
                              fill
                              className="object-cover transition-transform duration-300 group-hover:scale-105"
                              sizes="(max-width: 768px) 100vw, 33vw"
                              unoptimized
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

        {/* Оглавление */}
        <div
          ref={contentRef}
          className={`hidden sm:block pl-5 md:pl-15 w-full md:w-[20%] ${
            isFixed ? "fixed top-5 right-5" : "relative"
          }`}
        >
          <h3 className="text-xl sm:text-2xl mb-4">Содержание</h3>
          <nav>
            <ul className="space-y-2">
              {data.sections.map((section) => (
                <li key={section.id}>
                  <span
                    onClick={() => {
                      const el = document.getElementById(`section-${section.id}`);
                      if (el) el.scrollIntoView({ behavior: "smooth" });
                    }}
                    className="text-blue-600 hover:text-blue-800 transition-colors text-sm cursor-pointer"
                  >
                    {section.title}
                  </span>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>

      {/* Модалка книги */}
      <Modal
        size="full"
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setIsFullscreen(false);
        }}
        showCloseButton={true}
        className={
          isFullscreen
            ? 'fixed z-50 bg-transparent border-none shadow-none'
            : 'overflow-y-auto w-full h-full m-0 p-0 md:justify-center'
        }
      >
        {selectedBook && (
          isFullscreen ? (
            <div className="fixed inset-0 md:inset-20 flex items-center justify-center">
              <Image
                src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                alt={selectedBook.title}
                fill
                unoptimized
                className="object-contain"
                onClick={e => {
                  e.stopPropagation();
                  setIsFullscreen(false);
                }}
              />
            </div>
          ) : (
            <div className="flex flex-col w-full md:flex-row gap-6">
              {/* Левая половина */}
              <div className="relative md:w-1/4 cursor-zoom-in min-h-[150px]">
                <div className="absolute inset-0 overflow-hidden">
                  <Image
                    src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                    alt={selectedBook.title}
                    fill
                    className="object-cover blur-xs"
                    unoptimized
                  />
                  <div className="absolute inset-0 bg-black/50"></div>
                </div>
                <div className="relative z-10 flex flex-col items-center justify-center h-full p-4">
                  <Image
                    src={`${process.env.NEXT_PUBLIC_BASE_URL}${selectedBook.image_url}`}
                    alt={selectedBook.title}
                    width={150}
                    height={200}
                    className="object-contain h-auto w-full shadow-accent-foreground"
                    unoptimized
                  />
                  <div className="mt-4 text-center">
                    <h2 className="text-2xl font-bold text-white drop-shadow-md">
                      {selectedBook.title}
                    </h2>
                    <p className="text-lg text-white/80">
                      {selectedBook.author}
                    </p>
                  </div>
                </div>
                <button
                  onClick={e => {
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
                <p className="text-center mt-4">
                  Год публикации: {selectedBook.year_of_publication} г.
                </p>
              </div>

              <div className="flex flex-col md:flex-row md:justify-center w-full">
							<div className='w-full md:w-1/2 bg-gray-100 p-4 rounded-lg'>
								<div className='overflow-y-auto rounded-lg p-3 flex flex-col h-[500px]'>
									<div>
										<h2 className='font-bold text-center text-2xl mt-6'>
										{selectedBook.title}
										</h2>
										<h3 className='font-bold text-center'>Аннотация</h3>
										<p className="text-md whitespace-pre-line mt-2">
											{selectedBook.annotations}
										</p>
										<p className='font-bold text-md text-center'>
										Библиографическое описание книги
										</p>
										<p className='text-sm whitespace-pre-line break-words'>
										{selectedBook.library_description}
										</p>
									</div>
								</div>
							</div>
						</div>
            </div>
          )
        )}
      </Modal>
    </div>
  );
}
