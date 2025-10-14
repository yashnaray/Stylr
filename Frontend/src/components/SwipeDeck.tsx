import React, { useMemo, useState } from "react";
import SwipeCard from "./SwipeCard";

type Props = {
  items: any[];
  onLike: (item: any) => void;
  onPass: (item: any) => void;
};

export default function SwipeDeck({ items, onLike, onPass }: Props) {
  const [index, setIndex] = useState(0);
  const queue = useMemo(() => items.slice(index), [items, index]);

  const decide = (dir: "left" | "right", item: any) => {
    if (dir === "right") onLike(item);
    else onPass(item);
    setIndex((i) => i + 1);
  };

  const top = queue.at(0);
  const next = queue.at(1);

  return (
    <div style={{ display: "grid", placeItems: "center", gap: 12 }}>
      <div style={{ position: "relative", width: "min(92vw, 420px)", maxWidth: 420, aspectRatio: "3/4" }}>
        {next && (
          <div style={{ position: "absolute", inset: 0, transform: "scale(0.96)", filter: "blur(0.5px)", opacity: 0.8 }}>
            <SwipeCard item={next} onDecision={() => {}} zIndex={1} />
          </div>
        )}
        {top ? (
          <SwipeCard item={top} onDecision={decide} zIndex={2} />
        ) : (
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: 16,
              border: "1px dashed #bbb",
              display: "grid",
              placeItems: "center",
              color: "#777",
            }}
          >
            No more items
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <button aria-label="Pass" onClick={() => top && decide("left", top)} style={circleBtn("#ff3b30")}>
          ⛔
        </button>
        <button aria-label="Like" onClick={() => top && decide("right", top)} style={circleBtn("#34c759")}>
          ❤️
        </button>
      </div>
    </div>
  );
}

const circleBtn = (color: string): React.CSSProperties => ({
  width: 56,
  height: 56,
  borderRadius: "50%",
  border: `2px solid ${color}`,
  fontSize: 20,
  background: "#fff",
  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
});
