import { ulid } from 'ulid';

export function generateUserId() { 
  return `lid_${ulid()}`; 
}