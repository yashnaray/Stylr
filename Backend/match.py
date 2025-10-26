def match(*, gender, categories, colors, contexts, limit=10):
    import random
    items = []
    id = 0
    with open("data/items", "rb") as file:
        while data := file.read(8):
            id += 1
            gen, cat1, cat2, cat3, clr, ctx, nsz, usz = data
            name = file.read(nsz).decode()
            url = file.read(usz).decode()
            if (gender == gen and
                colors >> clr & 1 and
                contexts >> ctx & 1 and
                (categories >> cat1 & 1 or
                 categories >> cat2 & 1 or
                 categories >> cat3 & 1)):
                items.append((id, gen, cat1, cat2, cat3, clr, ctx, name, url))

    if not items:
        return []

    if len(items) > limit:
        items = random.sample(items, limit)

    import enums
    return [{
        "id": id,
        "gender": enums.gender_names[gen],
        "categories": [enums.category_names[cat] for cat in (cat1, cat2, cat3)],
        "color": enums.color_names[clr],
        "context": enums.context_names[ctx],
        "name": name,
        "url": "https://assets.myntassets.com/v1/" + url
    } for id, gen, cat1, cat2, cat3, clr, ctx, name, url in items]
