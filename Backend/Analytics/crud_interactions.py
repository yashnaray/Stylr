from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.db import User
from model_interactions import Item, Interaction

def parse_price_to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def get_user_id(db: Session, username: str) -> Optional[int]:
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    return user.id if user else None


def identify_item(db: Session, item_payload: Dict[str, Any]) -> Item:
    item_id = item_payload.get("id")
    if item_id is None:
        raise ValueError("Item id is required in payload")

    # if the id comes as a numeric string, coerce to int to match PK type
    if isinstance(item_id, str) and item_id.isdigit():
        item_id = int(item_id)

    existing = db.get(Item, item_id)
    if existing:
        return existing

    new_item = Item(
        id=item_id,
        name=item_payload.get("name") or item_payload.get("productDisplayName") or "",
        category=item_payload.get("masterCategory") or "",
        subcategory=item_payload.get("subCategory") or "",
        article_type=item_payload.get("articleType") or "",
        base_colour=item_payload.get("baseColour") or "",
        season=item_payload.get("season") or "",
        usage=item_payload.get("usage") or "",
        image_url=item_payload.get("imageURL") or item_payload.get("image") or "",
        price=parse_price_to_float(item_payload.get("price")),
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# CRUD-style functions

def record_interaction(
    db: Session,
    *,
    username: str,
    item_payload: Dict[str, Any],
    viewed: bool,
    liked: bool,
) -> Dict[str, Any]:

    user_id = get_user_id(db, username)
    if user_id is None:
        return {"error": "unknown_user", "message": f"username '{username}' not found; create the user first"}

    item = identify_item(db, item_payload)

    interaction = Interaction(
        user_id=user_id,
        item_id=item.id,
        viewed=bool(viewed),
        liked=bool(liked),
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "interaction_id": interaction.id,
        "user_id": interaction.user_id,
        "item_id": interaction.item_id,
        "viewed": interaction.viewed,
        "liked": interaction.liked,
        "ts": interaction.ts.isoformat(),
    }


def preference_summary(db: Session, username: str, top_n: int = 10) -> Dict[str, Any]:
    user_id = get_user_id(db, username)
    if user_id is None:
        return {"username": username, "counts": {}}

    query = (
        db.query(
            Item.category,
            Item.base_colour,
            Item.season,
            Item.usage,
            Interaction.liked,
        )
        .join(Interaction, Item.id == Interaction.item_id)
        .filter(Interaction.user_id == user_id)
    )

    category_counts: Counter[str] = Counter()
    colour_counts:   Counter[str] = Counter()
    season_counts:   Counter[str] = Counter()
    usage_counts:    Counter[str] = Counter()

    for category, base_colour, season, usage, liked in query:
        weight = 3 if liked else 1
        if category:
            category_counts[category] += weight
        if base_colour:
            colour_counts[base_colour] += weight
        if season:
            season_counts[season] += weight
        if usage:
            usage_counts[usage] += weight

    def top(counter: Counter[str], n: int) -> List[Tuple[str, int]]:
        return counter.most_common(n)

    return {
        "username": username,
        "counts": {
            "category":  top(category_counts, top_n),
            "baseColour": top(colour_counts, top_n),
            "season":    top(season_counts, top_n),
            "usage":     top(usage_counts, top_n),
        },
    }


def get_recs(db: Session, username: str, limit: int = 10) -> List[Dict[str, Any]]:
    summary = preference_summary(db, username)
    counts = summary.get("counts") or {}

    top_categories = [name for name, _ in (counts.get("category") or [])[:3]]
    top_colours    = [name for name, _ in (counts.get("baseColour") or [])[:3]]

    q = db.query(Item)
    if top_categories:
        q = q.filter(Item.category.in_(top_categories))
    if top_colours:
        q = q.filter(Item.base_colour.in_(top_colours))
    q = q.limit(limit)

    items: List[Item] = q.all()
    return [
        {
            "id": it.id,
            "name": it.name,
            "category": it.category,
            "subCategory": it.subcategory,
            "articleType": it.article_type,
            "baseColour": it.base_colour,
            "season": it.season,
            "usage": it.usage,
            "image_url": it.image_url,
            "price": it.price,
        }
        for it in items
    ]
