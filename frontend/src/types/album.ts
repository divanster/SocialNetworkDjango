// types/album.ts
export interface Album {
  id: string;
  user_id: string;
  author: {
    id: string;
    email: string;
    username: string;
    full_name: string;
    profile_picture?: string;
    // ...
  };
  title: string;
  description: string;
  visibility: string;
  created_at: string;
  updated_at: string;
  photos: Photo[];
  tags: Tag[];
}

export interface Photo {
  id: string;
  album: string; // also a UUID
  image: string;
  description: string;
  created_at: string;
  tags: Tag[];
}

export interface Tag {
  id: string;
  tagged_user: any; // or the correct interface
  tagged_by: any;   // or the correct interface
  content_type: number;
  object_id: string;
  content_object: string;
}
