// frontend/src/types/sharedItem.ts

import { User } from './user';

export interface SharedItem {
  id: string;
  content: string;
  created_at: string;
  original_author: User;
  shared_by: User;
  original_content: string;
  // Add any additional fields as required by your backend
}
