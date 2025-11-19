import { useEffect, useState } from "react";
import { useUser } from "../user.tsx";

const SWIPE_THRESHOLD = 120;
const HINT_THRESHOLD = 40;
const ROTATION_AMT = 15;
const FLY_OUT_MULT = 6;

interface Item {
  id: number;
  tags: string[];
  name: string;
  url: string;
}

interface CardProps {
  top?: boolean;
  item: Item;
  onSwipe(like: boolean): void;
}

function Card({ top = false, item, onSwipe }: CardProps) {
  const [origin, setOrigin] = useState<{ x: number, y: number } | null>(null);
  const [delta, setDelta] = useState({ x: 0, y: 0 });

  function swipe(like: boolean) {
    const sign = like ? 1 : -1;
    setDelta(({ y }) => ({ x: sign * SWIPE_THRESHOLD * FLY_OUT_MULT, y }));
    setTimeout(() => onSwipe(like), 200);
  }

  useEffect(() => {
    if (!top) {
      return;
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") {
        swipe(false);
      } else if (e.key === "ArrowRight") {
        swipe(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [top]);

  const onPointerDown = top ? (e: React.PointerEvent) => {
    setOrigin({
      x: e.clientX,
      y: e.clientY
    });
  } : undefined;

  const onPointerMove = top ? (e: React.PointerEvent) => {
    if (origin) {
      setDelta({
        x: e.clientX - origin.x,
        y: e.clientY - origin.y
      });
    }
  } : undefined;

  const onPointerUp = top ? () => {
    if (origin) {
      setOrigin(null);
      if (Math.abs(delta.x) > SWIPE_THRESHOLD) {
        swipe(delta.x > 0);
      } else {
        setDelta({ x: 0, y: 0 });
      }
    }
  } : undefined;

  const rot = (delta.x / SWIPE_THRESHOLD) * ROTATION_AMT;
  const transform = `translate(${delta.x}px, ${delta.y}px) rotate(${rot}deg)`;

  return (
    <div
      className={
        "absolute grid size-full touch-none select-none rounded-2xl"
        + (origin ? " shadow-2xl" : " shadow-lg transition duration-200 ease-out")
        + (top ? "" : " scale-90 opacity-80")
      }
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
      style={{
        transform,
        //cursor: released ? "default" : "grab",
        gridTemplateRows: "1fr auto",
      }}
    >
      <img
        className="size-full min-h-0 object-cover bg-white rounded-t-2xl"
        src={item.url}
        draggable="false"
      />

      <div className="px-4 py-2 border-t-1 border-gray-300 bg-white rounded-b-2xl">
        <strong>{item.name}</strong>
        <div className="text-xs text-gray-600">
          {item.tags.join(" \xb7 ")}
        </div>
      </div>

      {/* swipe hints */ (
        <>
          <div style={hintLeftStyle(delta.x)}>PASS</div>
          <div style={hintRightStyle(delta.x)}>LIKE</div>
        </>
      )}

      <div
        className="absolute inset-0 pointer-events-none rounded-2xl"
        style={{
          opacity: Math.abs(delta.x) / 1000,
          backgroundColor: delta.x > 0 ? "#00ff00" : "#ff0000"
        }}
      />
    </div>
  );
}

const hintLeftStyle = (dx: number): React.CSSProperties => ({
  position: "absolute",
  left: 16,
  top: 16,
  padding: "6px 10px",
  borderRadius: 8,
  background: "rgba(255, 59, 48, 0.1)",
  border: "2px solid rgba(255, 59, 48, 0.6)",
  color: "rgb(255, 59, 48)",
  fontWeight: 800,
  opacity: dx < -HINT_THRESHOLD ? 1 : 0,
  transform: "rotate(-12deg)",
});

const hintRightStyle = (dx: number): React.CSSProperties => ({
  position: "absolute",
  right: 16,
  top: 16,
  padding: "6px 10px",
  borderRadius: 8,
  background: "rgba(52,199,89,0.1)",
  border: "2px solid rgba(52,199,89,0.6)",
  color: "rgb(52,199,89)",
  fontWeight: 800,
  opacity: dx > HINT_THRESHOLD ? 1 : 0,
  transform: "rotate(12deg)",
});

interface CircleButtonProps {
  alt: string;
  content: string;
  className: string;
  onClick(): void;
}

function CircleButton({ alt, content, className, onClick }: CircleButtonProps) {
  return (
    <button
      className={
        "size-14 rounded-full bg-white shadow-lg border-2 text-center cursor-pointer " +
        "transition-colors duration-200 ease-out hover:text-white " +
        className
      }
      aria-label={alt}
      onClick={onClick}
    >
      {content}
    </button>
  );
}

interface DeckProps {
  items: Item[];
}

function Deck({ items }: DeckProps) {
  const [index, setIndex] = useState(0);

  const top = items[index];
  const next = items[index + 1];

  function swipe(_like: boolean) {
    setIndex(index + 1);
  }

  return (
    <div className="grow flex flex-col items-center justify-center gap-4 overflow-hidden">
      <div style={{ position: "relative", width: "min(92vw, 420px)", maxWidth: 420, aspectRatio: "3/4" }}>
        <div className="absolute inset-0 rounded-2xl border-1 border-dashed border-gray-400 grid place-items-center text-gray-500">
          No more items
        </div>
        {next && <Card key={next.id} item={next} onSwipe={swipe} />}
        {top && <Card top key={top.id} item={top} onSwipe={swipe} />}
      </div>

      <div className="flex gap-4">
        <CircleButton alt="Pass" content="&times;" onClick={() => swipe(false)}
          className="text-3xl text-red-400 border-red-400 hover:bg-red-400" />
        <CircleButton alt="Like" content="&hearts;" onClick={() => swipe(true)}
          className="text-2xl text-green-500 border-green-500 hover:bg-green-500" />
      </div>
    </div>
  );
}

export default function Swipe() {
  const { token, setToken } = useUser();
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setErr(null);
      try {
        const response = await fetch(`${__api}/match?access_token=${token}&limit=30`);
        if (response.status === 401) {
          return void setToken(null);
        }
        const payload = await response.json();
        if (response.status !== 200) {
          throw new Error(payload);
        }
        if (!cancelled) {
          setItems(payload);
        }
      } catch (e: any) {
        if (!cancelled) {
          setErr(e?.message ?? "failed to fetch");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => { cancelled = true; };
  }, []);

  //  const handleLike = async (item: Item) => {
  //    if (!token) return;
  //    try { await logInteraction(token, item, true, true); } catch {}
  //  };
  //  const handlePass = async (item: Item) => {
  //    if (!token) return;
  //    try { await logInteraction(token, item, true, false); } catch {}
  //  };

  if (loading) {
    return <p className="text-center">Loading...</p>;
  }

  if (err) {
    return <p className="text-center text-red-600">{err}</p>;
  }

  return <Deck items={items} />;
}
