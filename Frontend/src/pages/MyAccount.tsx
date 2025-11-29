import { useEffect, useState } from "react";
import { useUser } from "../user";

interface LikedItem {
  id: number;
  name: string;
  category: string;
  subcategory: string;
  article_type: string;
  base_colour: string;
  season: string;
  usage: string;
  url: string;
  price?: number;
  liked_at?: string;
  tags?: string[];
}

export default function MyAccount() {
  const { token, setToken } = useUser();
  const [items, setItems] = useState<LikedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const deleteItem = async (itemId: number) => {
    try {
      const response = await fetch(`${__api}/interactions?access_token=${token}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId })
      });

      if (response.ok) {
        setItems(items.filter(item => item.id !== itemId));
      }
    } catch (e) {
    }
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${__api}/interactions?access_token=${token}`);
        
        if (response.status === 401) {
          return void setToken(null);
        }
        if (response.status === 404 || response.status === 500) {
          if (!cancelled) {
            setItems([]);
            setLoading(false);
          }
          return;
        }
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        
        if (!cancelled) {
          setItems(data);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Failed to load liked items");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [token, setToken]);

  if (loading) {
    return (
      <div className="grow flex items-center justify-center">
        <p className="text-gray-500">Loading your liked items...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="grow flex items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="grow flex flex-col items-center justify-center gap-4">
        <p className="text-gray-500 text-lg">You haven't liked any items yet</p>
        <p className="text-gray-400 text-sm">Start swiping to build your collection!</p>
      </div>
    );
  }

  return (
    <div className="grow overflow-auto bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">My Liked Items</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow relative group"
            >
              {/* Delete button - shows on hover */}
              <button
                onClick={() => deleteItem(item.id)}
                className="absolute top-2 right-2 z-10 bg-red-500 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 shadow-lg"
                aria-label="Delete item"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </button>

              <div className="aspect-[3/4] overflow-hidden bg-gray-100">
                <img
                  src={item.url}
                  alt={item.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-3">
                <h3 className="font-semibold text-sm mb-1 line-clamp-2">{item.name}</h3>
                <p className="text-xs text-gray-600 mb-2">
                  {[item.category, item.base_colour].filter(Boolean).join(" · ")}
                </p>
                {item.price && (
                  <p className="text-sm font-bold text-green-600">${item.price}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

