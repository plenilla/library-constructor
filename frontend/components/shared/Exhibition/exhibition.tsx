import { ExhibitionType } from '@/interfaces/exhibition'
import Image from "next/image"
interface ExhibitionProps {
  exhibition: ExhibitionType
}

export const Exhibition = ({ exhibition }: ExhibitionProps) => {
  const publishedDate = new Date(exhibition.published_at)
  const createdDate = new Date(exhibition.created_at)
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'long', year: 'numeric' }
  const formattedPublished = publishedDate.toLocaleDateString('ru-RU', options)
  const formattedCreated = createdDate.toLocaleDateString('ru-RU', options)

  const imageUrl = exhibition.image?.startsWith('http')
    ? exhibition.image
    : `${process.env.NEXT_PUBLIC_URL}${exhibition.image}`

  return (
    <div className="bg-white flex flex-col md:flex-row items-center p-4 cursor-pointer hover:shadow-lg transition-shadow mb-1">
      <div className="relative w-full md:w-1/4 aspect-video">
        <Image
          src={imageUrl}
          alt={exhibition.title}
          fill
          style={{ objectFit: 'cover' }}
          unoptimized
        />
      </div>
      <div className="flex flex-col justify-center p-4 w-full md:w-1/2">
        <h2 className="text-xl md:text-2xl font-bold mb-2">{exhibition.title}</h2>
        <p className="text-gray-700 mb-2 text-sm md:text-base">{exhibition.description}</p>
        <p className="text-gray-700 mb-2 text-sm md:text-base">Автор: {exhibition.author}</p>
        <span className="text-xs md:text-sm text-gray-500">
          {exhibition.is_published
            ? `Дата публикации: ${formattedPublished}`
            : `Дата создания: ${formattedCreated}`}
        </span>
      </div>
    </div>
  )
}