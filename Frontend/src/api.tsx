export interface Item {
  id: number | string;
  productDisplayName?: string;
  masterCategory?: string;
  subCategory?: string;
  articleType?: string;
  baseColour?: string;
  season?: string;
  usage?: string;
  imageURL?: string;
  price?: number;
  name?: string;
}

export interface ItemPayload {
  id: number | string;
  name?: string;
  url?: string;
  tags?: string[];
  productDisplayName?: string;
  masterCategory?: string;
  subCategory?: string;
  articleType?: string;
  baseColour?: string;
  season?: string;
  usage?: string;
  imageURL?: string;
  price?: number;
}

const baseURL = import.meta.env.VITE_API_URL ?? "/api";

export function api(url: string, init: RequestInit): Promise<Response> {
  return fetch(baseURL + url, init);
}

export async function getMatches(token: string, limit = 30): Promise<Item[]> {
  const url = `${baseURL}/match?access_token=${token}&limit=${limit}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function logInteraction(
  accessToken: string,
  item: ItemPayload,
  viewed = true,
  liked = false
) {
  const url = `${baseURL}/interactions?access_token=${accessToken}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item, viewed, liked })
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}
