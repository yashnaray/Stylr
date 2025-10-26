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

export function api(url: string, init: RequestInit): Promise<Response> {
  return fetch((import.meta.env.VITE_API_URL ?? "/api") + url, init);
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

}
