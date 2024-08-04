export interface Tag {
  id: number;
  name: string;
}

export interface Ingredient {
  id: number;
  name: string;
}

export interface Recipe {
  id: number;
  title: string;
  description: string;
  instructions: string;
  tags: Tag[];
  ingredients: Ingredient[];
  average_rating: string;
  image: string | null;
}
