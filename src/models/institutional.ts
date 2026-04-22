export interface WikiArticle {
  title: string;
  summary: string;
  imageUrl?: string;
  pageUrl: string;
  lastModified: string;
}

export interface CategoryItem {
  id: string;
  name: string;
  searchTerm: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
  items: CategoryItem[];
}
