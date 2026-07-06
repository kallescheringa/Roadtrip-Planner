import { writable } from 'svelte/store';

const API_BASE = 'http://localhost:8000/api';

export const accessToken = writable<string | null>(null);
export const currentUser = writable<{ id: number; email: string; first_name: string; last_name: string } | null>(null);

export async function register(email: string, password: string, firstName: string, lastName: string) {
  const res = await fetch(`${API_BASE}/users/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  accessToken.set(data.access);
  await fetchMe(data.access);
  return data;
}

export async function fetchMe(token: string) {
  const res = await fetch(`${API_BASE}/users/me/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch user');
  const user = await res.json();
  currentUser.set(user);
  return user;
}

export function logout() {
  accessToken.set(null);
  currentUser.set(null);
}