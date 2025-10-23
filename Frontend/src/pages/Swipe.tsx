import { useContext, useEffect, useMemo, useState } from "react";
import { UserContext } from "../user";
import { getRecs, logInteraction, type ItemPayload } from "../api/swipe";
import SwipeDeck from "../components/SwipeDeck";

export default function SwipePage() {
  const { token } = useContext(UserContext);
  const [items, setItems] = useState<ItemPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!token) return;
      setLoading(true);
      setErr(null);
      try {
        const { items } = await getRecs(token, 30);
        if (!cancelled) setItems(items);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message ?? "failed to fetch");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [token]);

  const handleLike = async (item: ItemPayload) => {
    if (!token) return;
    try { await logInteraction(token, item, true, true); } catch {}
  };
  const handlePass = async (item: ItemPayload) => {
    if (!token) return;
    try { await logInteraction(token, item, true, false); } catch {}
  };

  if (loading) return <p className="text-center">Loading…</p>;
  if (err) return <p className="text-center text-red-600">{err}</p>;

  return (
    <div className="mx-auto my-6">
      <SwipeDeck items={items} onLike={handleLike} onPass={handlePass} />
    </div>
  );
}
