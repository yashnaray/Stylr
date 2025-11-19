def match(*, gender, tags, limit=10):
    import random
    items = []
    id = 0
    with open("data/items", "rb") as file:
        while data := file.read(8):
            id += 1
            gen, ta1, ta2, ta3, ta4, ta5, nsz, usz = data
            name = file.read(nsz).decode()
            url = file.read(usz).decode()
            if ((not gender or gender == gen) and (
                tags[ta1] or
                tags[ta2] or
                tags[ta3] or
                tags[ta4] or
                tags[ta5])):
                items.append((id, gen, (ta1, ta2, ta3, ta4, ta5), name, url))

    if not items:
        return []

    if len(items) > limit:
        items = random.sample(items, limit)

    import enums
    return [{
        "id": id,
        "gender": enums.gender_names[gender],
        "tags": [enums.tag_names[tag] for tag in tags if tag],
        "name": name,
        "url": "https://assets.myntassets.com/h_720,q_90,w_540/v1/" + url
    } for id, gender, tags, name, url in items]
