import React, { useEffect, useRef, useState } from "react";

type Props = {
  item: any;
  onDecision: (dir: "left" | "right", item: any) => void;
  zIndex?: number;
};

const SWIPE_THRESHOLD = 120;
const ROTATION_AMT = 15;
const FLY_OUT_MULT = 6;

export default function SwipeCard({ item, onDecision, zIndex = 1 }: Props) {
  const start = useRef({ x: 0, y: 0 });
  const [delta, setDelta] = useState({ x: 0, y: 0 });
  const [released, setReleased] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (released) return;
      if (e.key === "ArrowLeft") flyOut("left");
      if (e.key === "ArrowRight") flyOut("right");
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [released]);

  const onPointerDown = (e: React.PointerEvent) => {
    if (released) return;
    (e.target as Element).setPointerCapture(e.pointerId);
    start.current = { x: e.clientX - delta.x, y: e.clientY - delta.y };
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (released) return;
    if (e.pressure === 0) return;
    setDelta({ x: e.clientX - start.current.x, y: e.clientY - start.current.y });
  };

  const onPointerUp = () => {
    if (released) return;
    if (Math.abs(delta.x) > SWIPE_THRESHOLD) {
      flyOut(delta.x > 0 ? "right" : "left");
    } else {
      setDelta({ x: 0, y: 0 });
    }
  };

  function flyOut(direction: "left" | "right") {
    setReleased(true);
    const sign = direction === "right" ? 1 : -1;
    setDelta(({ y }) => ({ x: sign * SWIPE_THRESHOLD * FLY_OUT_MULT, y }));
    setTimeout(() => onDecision(direction, item), 220);
  }

  const rot = (delta.x / SWIPE_THRESHOLD) * ROTATION_AMT;
  const transform = `translate(${delta.x}px, ${delta.y}px) rotate(${rot}deg)`;

  const name = item.productDisplayName || item.name || "Unnamed item";
  const imageURL = item.image_url || item.imageURL || item.link || "";

  return (
    <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", padding: 12 }}>
      <div
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        style={{
          transform,
          transition: released ? "transform 220ms ease-out" : "transform 0s",
          zIndex,
          touchAction: "none",
          cursor: released ? "default" : "grab",
          width: "min(92vw, 420px)",
          maxWidth: 420,
          aspectRatio: "3/4",
          borderRadius: 16,
          background: "#fff",
          boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
          overflow: "hidden",
          display: "grid",
          gridTemplateRows: "1fr auto",
          userSelect: "none",
          position: "relative",
        }}
      >
        {imageURL ? (
          <img
            src={imageURL}
            alt={name}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
          />
        ) : (
          <div style={{ display: "grid", placeItems: "center", color: "#888" }}>No image</div>
        )}

        <div style={{ padding: "10px 12px", borderTop: "1px solid #eee" }}>
          <div style={{ fontWeight: 700 }}>{name}</div>
          <div style={{ fontSize: 12, color: "#666" }}>
            {(item.masterCategory || item.category || "")}
            {item.subCategory ? ` • ${item.subCategory}` : ""}
            {item.baseColour ? ` • ${item.baseColour}` : ""}
          </div>
        </div>

        {/* swipe hints */}
        {!released && (
          <>
            <div style={hintLeftStyle(delta.x)}>PASS</div>
            <div style={hintRightStyle(delta.x)}>LIKE</div>
          </>
        )}
      </div>
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
  opacity: dx < -40 ? 1 : 0,
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
  opacity: dx > 40 ? 1 : 0,
  transform: "rotate(12deg)",
});
