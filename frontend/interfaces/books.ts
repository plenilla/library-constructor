export interface Book {
    id: number;
    title: string;
    genres: string;
    image_url: string;
    authors: string;
    library_description: string;
    annotations: string;
    year_of_publication: string

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

