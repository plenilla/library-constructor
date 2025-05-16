/* interfaces/exhibition.ts */
export interface ContentBlock {
  id: number;
  type: 'text' | 'book';
  text_content?: string;
  book_id?: number | null;
  book?: Book;
}

export interface ExhibitionSection {
  id: number
  title: string
  content_blocks?: ContentBlock[]
}

export interface ExhibitionType {
  id: number;
  title: string;
  slug: string;
  image?: string;
  description?: string;
  isPublished: boolean;
  createdAt: string;
  is_published?: string;
  author: string; 
  sections: ExhibitionSection[];
}


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

export interface ApiResponse<T = any> {
  items: T[]
  page: number
  size: number
  total: number
  total_pages: number
}