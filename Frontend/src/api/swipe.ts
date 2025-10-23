export type ItemPayload = {
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
};

export async function getRecs(accessToken: string, limit = 30) {
  const url = `/api/recommendations?limit=${limit}&access_token=${encodeURIComponent(accessToken)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { items: any[] };
}

export async function logInteraction(
  accessToken: string,
  item: ItemPayload,
  viewed = true,
  liked = false
) {
  const res = await fetch(`/api/interactions/log?access_token=${encodeURIComponent(accessToken)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item, viewed, liked }),
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}
