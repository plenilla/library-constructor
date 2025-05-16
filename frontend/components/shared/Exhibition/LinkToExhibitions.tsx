import Link from "next/link"

export const Exhibitions = () => {
   
    return (
        <Link href={`/exhibitions/`} className="bg-black text-white w-[700px] hover:bg-darkblue-700 transition duration-300 p-4">
          Выставка
        </Link>
   )
}