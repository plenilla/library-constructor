import Link from "next/link"
import { useRouter } from "next/navigation"


export const Sections = () => {
    
    
    return (
        <div className="flex flex-col items-center gap-5">
            <Link href={`/exhibitions/`} className="bg-black text-white w-[700px] hover:bg-darkblue-700 transition duration-300 p-4">
                Выставки
            </Link>
            <Link href={`/books/`} className="bg-black text-white w-[700px] hover:bg-darkblue-700 transition duration-300 p-4">       
                Книги
            </Link>
            Мероприятия
        </div>  
    )
}