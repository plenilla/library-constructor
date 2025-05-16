export interface Book {
    id: number;
    title: string;
    genre: string;
    image_url: string;
    author: string;
    library_description: string;
    annotations: string;
}
export interface Author {
  id: number;
  name: string;
}
export interface Genre {
  id: number;
  name: string;
}

export interface BookInfo {
  id: number
  title: string
  cover_url?: string
  authors?: string[]
  genres?: string[]
  year_of_publication?: string
}

