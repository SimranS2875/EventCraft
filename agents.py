"""EventCraft agents: a Coordinator, seven specialists, a Budget Agent and a Schedule Agent.

Agents talk only through structured JSON messages on a Bus (Contract-Net style:
the Coordinator announces tasks, specialists bid with a proposal). The Budget
Agent runs a negotiation loop, asking agents for cheaper alternatives.
"""
import datetime as dt
import zlib

# ---------------------------------------------------------------- catalogues
VENUES = [  # name, type, capacity, cost (INR, flat), rating
    ("Backyard Party Plot", "outdoor", 80, 3000, 3.3),
    ("Neighbourhood Community Hall", "indoor", 60, 3500, 3.4),
    ("College Seminar Hall", "indoor", 150, 5000, 3.5),
    ("Sunset Terrace Cafe", "outdoor", 50, 6000, 4.0),
    ("Open Sky Garden Lawn", "outdoor", 150, 8000, 3.9),
    ("Green Leaf Banquet", "indoor", 100, 9000, 4.1),
    ("The Lotus Banquet", "indoor", 200, 16000, 4.4),
    ("Riverside Farmhouse", "outdoor", 300, 22000, 4.5),
    ("Grand Orchid Ballroom", "indoor", 400, 38000, 4.7),
]
FOOD = [  # name, diet tags, cost per plate, rating, dishes
    ("Tea, Snacks & Samosas", {"veg", "jain", "nonveg"}, 90, 3.0,
     ["Masala chai", "Samosa (2 pc)", "Veg pakora", "Mint chutney", "Biscuits"]),
    ("Basic Veg Thali", {"veg"}, 150, 3.4,
     ["Dal tadka", "Aloo gobi", "Jeera rice", "Roti (2 pc)", "Salad", "Pickle"]),
    ("South Indian Meals", {"veg"}, 200, 3.9,
     ["Sambar", "Rasam", "Beans poriyal", "Kootu", "Steamed rice", "Appalam", "Curd", "Payasam"]),
    ("Chicken Combo Meal", {"nonveg"}, 220, 3.6,
     ["Chicken curry", "Jeera rice", "Roti (2 pc)", "Onion salad", "Raita"]),
    ("Indo-Chinese Veg Combo", {"veg"}, 240, 3.8,
     ["Veg manchurian", "Hakka noodles", "Veg fried rice", "Spring rolls", "Sweet corn soup"]),
    ("Jain Thali", {"veg", "jain"}, 250, 3.9,
     ["Dal (no onion or garlic)", "Paneer sabzi", "Lauki sabzi", "Steamed rice", "Phulka (3 pc)", "Papad"]),
    ("South Indian Tiffin Buffet", {"veg"}, 260, 4.2,
     ["Idli", "Medu vada", "Masala dosa (live)", "Pongal", "Coconut and tomato chutney", "Sambar", "Filter coffee"]),
    ("Classic Veg Buffet", {"veg"}, 280, 4.0,
     ["Paneer butter masala", "Mixed vegetable", "Dal makhani", "Veg pulao", "Naan and roti", "Green salad", "Raita"]),
    ("Vegan Kitchen Combo", {"veg", "vegan"}, 300, 4.0,
     ["Chana masala", "Tofu stir-fry", "Steamed rice", "Millet roti", "Kachumber salad"]),
    ("Indo-Chinese Non-Veg Combo", {"nonveg"}, 320, 4.0,
     ["Chilli chicken", "Chicken hakka noodles", "Egg fried rice", "Spring rolls", "Hot and sour soup"]),
    ("Classic Non-Veg Buffet", {"nonveg"}, 380, 4.1,
     ["Butter chicken", "Egg curry", "Dal makhani", "Veg pulao", "Naan", "Green salad", "Raita"]),
    ("Jain Royal Buffet", {"veg", "jain"}, 450, 4.4,
     ["Jain paneer makhani", "Kaju curry", "Dal fry", "Veg biryani", "Puri and phulka", "Farsan", "Buttermilk"]),
    ("Premium Veg Feast", {"veg"}, 480, 4.5,
     ["Welcome drink", "Paneer tikka", "Hara bhara kebab", "Shahi paneer", "Malai kofta", "Dal makhani",
      "Veg biryani", "Assorted breads", "Salad bar"]),
    ("Vegan Gourmet Spread", {"veg", "vegan"}, 520, 4.5,
     ["Welcome cooler", "Tofu tikka", "Jackfruit biryani", "Coconut vegetable curry", "Quinoa salad",
      "Millet breads", "Hummus platter"]),
    ("Royal Non-Veg Feast", {"nonveg"}, 650, 4.6,
     ["Welcome drink", "Chicken tikka", "Fish fry", "Mutton rogan josh", "Butter chicken", "Chicken biryani",
      "Dal makhani", "Assorted breads", "Salad bar"]),
]
CUISINE = {"South Indian Meals": "south", "South Indian Tiffin Buffet": "south",
           "Indo-Chinese Veg Combo": "chinese", "Indo-Chinese Non-Veg Combo": "chinese"}  # everything else: north
DESSERTS = [  # name, diet tags, cost per plate, rating, items
    ("Gulab Jamun", {"veg", "jain"}, 40, 3.5, ["Gulab jamun (2 pc)", "Warm sugar syrup"]),
    ("Ice Cream Cup", {"veg", "jain"}, 50, 3.6, ["Vanilla, chocolate or strawberry scoop", "Wafer"]),
    ("Fresh Fruit Platter", {"veg", "vegan", "jain"}, 60, 3.7, ["Watermelon", "Papaya", "Pineapple", "Grapes", "Chaat masala"]),
    ("Jamun & Ice Cream Duo", {"veg", "jain"}, 80, 4.0, ["Gulab jamun (2 pc)", "Vanilla ice cream scoop"]),
    ("Coconut Ladoo & Sorbet", {"veg", "vegan"}, 100, 4.1, ["Coconut ladoo (2 pc)", "Mango sorbet", "Roasted nuts"]),
    ("Indian Sweets Trio", {"veg", "jain"}, 110, 4.3, ["Gulab jamun", "Rasmalai", "Kaju katli"]),
    ("Celebration Cake & Sweets", {"veg"}, 140, 4.4, ["Eggless cake slice", "Gulab jamun", "Chocolate brownie bite"]),
    ("Live Dessert Counter", {"veg"}, 180, 4.7, ["Hot jalebi with rabri", "Gulab jamun", "Ice cream sundae bar", "Pastries", "Paan"]),
]
DECOR = [  # name, theme tags, cost (flat), rating, what's included
    ("Balloons & Banner", {"balloons"}, 1500, 3.2, ["100 balloons", "Custom banner", "Table confetti"]),
    ("Fairy Lights & Drapes", {"lights"}, 3500, 3.8, ["Warm fairy lights", "Fabric backdrop", "Entrance drape"]),
    ("Minimalist Greens & Candles", {"minimalist"}, 4000, 4.0, ["Eucalyptus table runners", "Pillar candles", "Neutral linen", "Simple welcome sign"]),
    ("Photo Booth & Backdrop", {"photo"}, 4500, 3.9, ["Themed backdrop", "Photo props", "Ring light"]),
    ("Marigold Floral", {"floral", "traditional"}, 5000, 4.1,
     ["Marigold garlands", "Floral entrance arch", "Rangoli", "Table centrepieces"]),
    ("Boho Pampas & Macrame", {"boho"}, 7000, 4.2, ["Pampas grass arrangements", "Macrame backdrop", "Rattan lanterns", "Floor cushions"]),
    ("Themed Stage Setup", {"stage"}, 9000, 4.3, ["Stage with backdrop", "Spotlights", "Flower arrangements", "Welcome board"]),
    ("Premium Floral & Lighting", {"floral", "lights", "royal"}, 16000, 4.6,
     ["Fresh flower wall", "Uplighting", "Aisle decor", "Decorated stage", "Table centrepieces"]),
    ("Royal Mandap & Drapes", {"traditional", "stage", "royal"}, 28000, 4.8,
     ["Carved mandap", "Ceiling drapes", "Floral pillars", "Chandeliers", "Carpeted aisle"]),
]
ENTERTAINMENT = [  # name, tags, cost (flat), max guests, rating
    ("DIY Playlist + Rented Speaker", {"music"}, 1000, 300, 3.0),
    ("Games & Emcee Host", {"games"}, 3000, 150, 3.6),
    ("Karaoke Setup", {"karaoke", "music"}, 4000, 100, 3.7),
    ("Live Acoustic Duo", {"music"}, 8000, 150, 4.2),
    ("Magician / Stand-up Act", {"magician"}, 10000, 300, 4.0),
    ("Professional DJ + Lights", {"dj", "music"}, 12000, 500, 4.3),
    ("Live Band", {"band", "music"}, 25000, 500, 4.6),
]
PHOTOGRAPHY = [  # name, tags, cost (flat), rating, what's included
    ("Reels & Phone Content Creator", {"video"}, 2500, 3.5, ["1 content creator", "2 hours", "3 edited reels", "Same-day delivery"]),
    ("Candid Photographer (2 hrs)", {"photo"}, 4000, 3.8, ["1 photographer", "2 hours", "100 edited photos"]),
    ("Full Event Photographer", {"photo"}, 8000, 4.1, ["1 photographer", "4 hours", "250 edited photos", "Online gallery"]),
    ("Photo + Highlight Video", {"photo", "video"}, 15000, 4.4, ["Photographer", "Videographer", "3-minute highlight film", "300 edited photos"]),
    ("Cinematic Photo & Film", {"photo", "video"}, 30000, 4.7, ["2 photographers", "Cinematographer", "Teaser and full film", "Printed album"]),
]
GIFTS = [  # name, cost per guest, rating, what's inside
    ("Chocolate Favour Box", 40, 3.5, ["4 assorted chocolates", "Ribbon box", "Thank-you tag"]),
    ("Potted Succulent", 80, 4.0, ["Succulent in ceramic pot", "Name tag"]),
    ("Dry Fruit Pouch", 120, 4.1, ["Almonds", "Cashews", "Raisins", "Jute pouch"]),
    ("Personalised Mug", 150, 4.0, ["Printed mug", "Gift box"]),
    ("Scented Candle Set", 200, 4.3, ["2 soy candles", "Matchbox", "Gift box"]),
    ("Premium Gift Hamper", 450, 4.7, ["Dry fruits", "Chocolates", "Scented candle", "Diary", "Wicker basket"]),
]

CATS = ["venue", "food", "dessert", "decor", "entertainment", "photography", "gifts"]
OPT_IN = {"photography", "gifts"}  # only planned when the user asks for them
NONE_NAME = {"dessert": "No dessert", "decor": "No decor", "entertainment": "No entertainment",
             "photography": "No photography", "gifts": "No return gifts"}
LABEL = {"gifts": "Return gifts"}
SHARE = {"venue": 0.27, "food": 0.40, "dessert": 0.08, "decor": 0.12, "entertainment": 0.18, "photography": 0.12, "gifts": 0.08}
OPENING_HEADROOM = 1.05 * 1.3  # specialists open with premium bids; Budget Agent negotiates down

DIET_KEY = {"Vegetarian": "veg", "Vegan": "vegan", "Jain": "jain", "Non-Vegetarian": "nonveg"}
PREF_KEY = {"DJ": "dj", "Live band": "band", "Karaoke": "karaoke", "Magician": "magician", "Games": "games", "Music": "music",
            "Floral": "floral", "Balloons": "balloons", "Lights": "lights", "Photo booth": "photo", "Traditional": "traditional",
            "Royal": "royal", "Boho": "boho", "Minimalist": "minimalist", "Video": "video",
            "North Indian": "north", "South Indian": "south", "Chinese": "chinese"}


def available(name, iso):
    """Sample availability calendar: each venue is booked on roughly one date in five."""
    return not iso or zlib.crc32(f"{name}|{iso}".encode()) % 5 != 0


def best(cands, max_cost):
    """Highest rating within max_cost; else the cheapest candidate (flagged over)."""
    ok = [c for c in cands if c["cost"] <= max_cost]
    if ok:
        return max(ok, key=lambda c: (c["rating"], -c["cost"])), "ok"
    return (min(cands, key=lambda c: c["cost"]), "over") if cands else (None, "none")


# ------------------------------------------------------------------- agents
class Agent:
    name = "Agent"

    def handle(self, msg):
        raise NotImplementedError


class OptionAgent(Agent):
    """A specialist that bids one option from its catalogue."""
    category = ""

    def options(self, b):
        """All options meeting the hard constraints in body b. Each has a 'tags' set."""
        raise NotImplementedError

    def handle(self, msg):
        b, cheaper = msg["body"], msg["type"] == "propose_cheaper"
        none_name = NONE_NAME.get(self.category)
        none = dict(name=none_name, cost=0, rating=0, detail="Skipped", tags=set(), skipped=True) if none_name else None
        if b.get("skip") and none:
            return {"status": "ok", "option": _public(none)}
        allc, extra = self.options(b), {}
        if b.get("pick") and not cheaper:  # the user chose this vendor themselves in the catalog
            mine = [c for c in allc if c["name"] == b["pick"]]
            if mine:
                return {"status": "ok", "option": _public(mine[0]), "pinned": True}
            extra["pick_rejected"] = b["pick"]
        if none and b.get("allow_last_resort"):
            allc = allc + [none]
        pref, relaxed = b.get("pref"), False
        matched = [c for c in allc if pref in c["tags"]] if pref else []
        cands = matched or allc
        if pref and cheaper:
            # honour the preference if a cheaper match exists, otherwise relax it
            if not [c for c in matched if c["cost"] < b["current_cost"]]:
                cands, relaxed = allc, True
        elif pref and not matched:
            relaxed = True
        if cheaper:
            cands = [c for c in cands if c["cost"] < b["current_cost"]]
        opt, status = best(cands, b["max_cost"])
        if cheaper:
            status = "declined" if status == "none" else ("partial" if status == "over" else "ok")
        return dict({"status": status, "option": _public(opt), "preference_relaxed": relaxed and opt is not None}, **extra)


def _public(opt):
    return None if opt is None else {k: v for k, v in opt.items() if k != "tags"}


class VenueAgent(OptionAgent):
    name, category = "Venue", "venue"

    @staticmethod
    def _fits(b):
        return [v for v in VENUES if v[2] >= b["capacity"] and (not b.get("type") or v[1] == b["type"])]

    def options(self, b):
        return [dict(name=n, type=t, capacity=c, cost=p, rating=r, tags=set(), detail=f"{t.title()}, up to {c} guests")
                for n, t, c, p, r in self._fits(b) if available(n, b.get("date"))]

    def handle(self, msg):
        reply = super().handle(msg)
        b = msg["body"]
        booked = [v[0] for v in self._fits(b) if not available(v[0], b.get("date"))]
        if booked and msg["type"] != "propose_cheaper":
            reply["booked"] = booked
        return reply


class FoodAgent(OptionAgent):
    name, category, table = "Food", "food", FOOD

    def options(self, b):
        g, key = b["guests"], b.get("diet")
        return [dict(name=n, per_plate=p, cost=p * g, rating=r, tags={CUISINE.get(n, "north")}, includes=items,
                     detail=f"₹{p}/plate × {g} guests")
                for n, tags, p, r, items in self.table if not key or key in tags]


class DessertAgent(FoodAgent):
    name, category, table = "Dessert", "dessert", DESSERTS


class DecorAgent(OptionAgent):
    name, category = "Decor", "decor"

    def options(self, b):
        return [dict(name=n, cost=p, rating=r, tags=tg, includes=items, detail="Flat fee") for n, tg, p, r, items in DECOR]


class EntertainmentAgent(OptionAgent):
    name, category = "Entertainment", "entertainment"

    def options(self, b):
        return [dict(name=n, cost=p, rating=r, tags=tg, detail="Flat fee") for n, tg, p, mx, r in ENTERTAINMENT if mx >= b["guests"]]


class PhotographyAgent(OptionAgent):
    name, category = "Photography", "photography"

    def options(self, b):
        return [dict(name=n, cost=p, rating=r, tags=tg, includes=items, detail="Flat fee") for n, tg, p, r, items in PHOTOGRAPHY]


class GiftsAgent(OptionAgent):
    name, category = "Gifts", "gifts"

    def options(self, b):
        g = b["guests"]
        return [dict(name=n, cost=p * g, rating=r, tags=set(), includes=items, detail=f"₹{p} each × {g} guests") for n, p, r, items in GIFTS]


class BudgetAgent(Agent):
    name = "Budget"
    PRIORITY = ["gifts", "photography", "entertainment", "decor", "dessert", "venue", "food"]  # least essential asked first
    LAST_RESORT = ["gifts", "photography", "decor", "entertainment", "dessert"]  # dropped entirely, in this order

    def handle(self, msg):
        b = msg["body"]
        total = sum(b["items"].values())
        over = max(0, total - b["budget"])
        return {"status": "over" if over else "ok", "total": total, "over_by": over}

    def negotiate(self, bus, req, items, constraints, pinned=(), max_rounds=20):
        """items: category -> option. The user's own picks (pinned) are never bargained with.
        Returns (items, rounds, reached_budget, relaxed categories)."""
        rounds, relaxed = 0, set()
        declined = {c for c in items if items[c]["cost"] == 0} | set(pinned)
        while rounds < max_rounds:
            ev = self.handle({"body": {"items": {k: v["cost"] for k, v in items.items()}, "budget": req["budget"]}})
            if ev["status"] == "ok":
                return items, rounds, True, relaxed
            avail = [c for c in self.PRIORITY if c not in declined]
            last = not avail
            if last:
                avail = [c for c in self.LAST_RESORT if items[c]["cost"] > 0 and c not in pinned]
                if not avail:
                    return items, rounds, False, relaxed
            target = avail[0]
            cur = items[target]["cost"]
            body = dict(constraints[target], current_cost=cur, max_cost=max(0, cur - ev["over_by"]),
                        allow_last_resort=last, reason=f"plan exceeds budget by ₹{ev['over_by']:,}")
            rounds += 1
            reply = bus.send("Budget", target.title(), "propose_cheaper", body)
            if reply["status"] in ("ok", "partial"):
                items[target] = reply["option"]
                if reply.get("preference_relaxed"):
                    relaxed.add(target)
            if reply["status"] != "ok":
                declined.add(target)  # nothing (more) to save here; move on
        return items, rounds, False, relaxed


class ScheduleAgent(Agent):
    name = "Schedule"
    CEREMONY = {"Farewell": "Farewell speeches & gift presentation", "Birthday": "Cake cutting & wishes",
                "Wedding": "Ceremony & toasts", "Anniversary": "Toast & cake cutting",
                "Fundraiser": "Fundraising appeal & announcements", "Corporate Offsite": "Team activity & announcements",
                "Graduation": "Felicitation & photos", "Engagement": "Ring ceremony & toasts"}

    def handle(self, msg):
        b = msg["body"]
        ceremony = self.CEREMONY.get(b["event_type"], "Highlights & announcements")
        start = dt.datetime.combine(dt.date.today(), dt.time(18, 0))
        setup = "Vendor setup: " + ", ".join(filter(None, [b.get("decor") and f"decor ({b['decor']})", "sound check", "kitchen prep"]))
        steps = [(-90, setup), (-15, b.get("photography") and f"Photo team arrives: {b['photography']}"),
                 (0, "Guests arrive & welcome drinks"),
                 (30, b.get("entertainment") and f"Entertainment begins: {b['entertainment']}"), (75, ceremony),
                 (120, f"Dinner served: {b['food']}"), (165, b.get("dessert") and f"Dessert: {b['dessert']}"),
                 (190, "Open floor, photos & networking"), (225, b.get("gifts") and f"Return gifts handed out: {b['gifts']}"),
                 (240, "Wrap-up, thank-you & vendor handover")]
        timeline = [{"time": (start + dt.timedelta(minutes=m)).strftime("%I:%M %p").lstrip("0"), "activity": a}
                    for m, a in steps if a]
        notes = []
        if b.get("venue_type") == "outdoor":
            notes.append("Outdoor venue: keep a weather backup (tent or covered area) on standby.")
        return {"timeline": timeline, "notes": notes}


# -------------------------------------------------------------- bus + coord
class Bus:
    def __init__(self):
        self.agents, self.log = {}, []

    def register(self, agent):
        self.agents[agent.name] = agent

    def send(self, frm, to, mtype, body):
        reply = self.agents[to].handle({"from": frm, "to": to, "type": mtype, "body": body})
        self.log.append({"from": frm, "to": to, "type": mtype, "body": _clean(body)})
        self.log.append({"from": to, "to": frm, "type": mtype + "_reply", "body": _clean(reply)})
        return reply


def _clean(d):
    """JSON-safe, compact copy of a message body for the UI log."""
    if isinstance(d, dict):
        return {k: _clean(v) for k, v in d.items() if k not in ("tags", "includes")}
    if isinstance(d, (set, frozenset)):
        return sorted(d)
    return d


class Coordinator:
    name = "Coordinator"

    def __init__(self):
        self.bus = Bus()
        for a in (VenueAgent(), FoodAgent(), DessertAgent(), DecorAgent(), EntertainmentAgent(), PhotographyAgent(),
                  GiftsAgent(), BudgetAgent(), ScheduleAgent()):
            self.bus.register(a)

    def plan(self, req):
        bus, budget, guests = self.bus, req["budget"], req["guests"]
        diet = DIET_KEY.get(req.get("food_pref"))
        picks = dict(req.get("picks") or {})
        prefs = {c: req.get(c + "_pref") for c in CATS}
        prefs["food"] = req.get("cuisine")
        cons = {
            "venue": {"capacity": guests, "type": (req.get("venue_pref") or "").lower() or None, "date": req.get("date_iso")},
            "food": {"guests": guests, "diet": diet},
            "dessert": {"guests": guests, "diet": None if diet == "nonveg" else diet},
        }
        for c in CATS:
            cons.setdefault(c, {"guests": guests})
            if c != "venue" and PREF_KEY.get(prefs[c]):
                cons[c]["pref"] = PREF_KEY[prefs[c]]
            if c in picks:
                cons[c]["pick"] = picks[c]
            elif prefs[c] == "None" or (c in OPT_IN and not prefs[c]):
                cons[c]["skip"] = True
        scale = OPENING_HEADROOM / sum(SHARE[c] for c in CATS if not cons[c].get("skip"))
        for c in CATS:
            cons[c].update(task="find_" + c, max_cost=int(budget * SHARE[c] * scale))

        items, relaxed, pinned, rejected, notes = {}, set(), set(), [], []
        for cat in CATS:  # task announcement + bids
            reply = bus.send("Coordinator", cat.title(), cons[cat]["task"], dict(cons[cat]))
            if reply["option"] is None:
                return {"ok": False, "error": self._no_match(cat, req, reply)}
            items[cat] = reply["option"]
            if reply.get("preference_relaxed"):
                relaxed.add(cat)
            if reply.get("pinned"):
                pinned.add(cat)
            if reply.get("pick_rejected"):
                rejected.append(cat)
                notes.append(f"{reply['pick_rejected']} doesn't fit this event (guest count, venue type, date or diet), so the agents chose instead.")
            if reply.get("booked"):
                notes.append(f"Already booked on {req.get('date', 'that date')}: {', '.join(reply['booked'])}.")

        # Budget Agent verifies the combined plan and negotiates if over budget.
        bus.send("Coordinator", "Budget", "evaluate", {"budget": budget, "items": {k: v["cost"] for k, v in items.items()}})
        items, rounds, fits, relaxed2 = bus.agents["Budget"].negotiate(bus, req, items, cons, pinned)

        label = lambda c: LABEL.get(c, c.title())  # noqa: E731
        for cat in CATS:
            if items[cat].get("skipped"):
                if not cons[cat].get("skip"):
                    notes.append(f"{label(cat)} was dropped to meet the budget.")
            elif cat in relaxed2:
                notes.append(f"Your {prefs[cat].lower()} {cat} preference was relaxed to meet the budget.")
            elif cat in relaxed:
                notes.append(f"No {prefs[cat].lower()} {cat} option fits this event, so the closest alternative was chosen.")

        def name(cat):
            return None if items[cat].get("skipped") else items[cat]["name"]
        sched = bus.send("Coordinator", "Schedule", "build_timeline", dict(
            {c: name(c) for c in CATS if c != "venue"}, event_type=req.get("event_type") or "Event",
            venue_type=items["venue"].get("type")))
        notes += sched["notes"]

        total = sum(v["cost"] for v in items.values())
        if not fits:
            notes.append(f"Even the cheapest options exceed the budget by ₹{total - budget:,}. " + (
                "Your own picks are kept as chosen, so remove one or raise the budget." if pinned
                else "Consider raising the budget or reducing guests."))
        shown = [c for c in CATS if not (c in OPT_IN and cons[c].get("skip"))]
        return {"ok": True, "rejected": rejected, "plan": {
            "items": [{"key": c, "category": label(c), "name": items[c]["name"], "detail": items[c].get("detail", ""),
                       "cost": items[c]["cost"], "includes": items[c].get("includes", []),
                       "skipped": bool(items[c].get("skipped")), "pinned": c in pinned} for c in shown],
            "total": total, "budget": budget, "remaining": budget - total, "within_budget": fits,
            "negotiation_rounds": rounds, "timeline": sched["timeline"], "notes": notes},
            "messages": bus.log}

    @staticmethod
    def _no_match(cat, req, reply):
        if cat == "venue":
            kind = (req.get("venue_pref") or "").lower()
            msg = f"I couldn't find {'an ' + kind if kind else 'a'} venue for {req['guests']} guests"
            if reply.get("booked"):
                return f"{msg} on {req.get('date', 'that date')}: {', '.join(reply['booked'])} already booked. Try another date."
            return msg + ". Try a different venue type or fewer guests."
        return f"I couldn't find a {cat} option for those requirements."


def catalog():
    return {
        "venue": [dict(name=n, type=t, capacity=c, cost=p, rating=r) for n, t, c, p, r in VENUES],
        "food": [dict(name=n, diets=sorted(tg), cuisine=CUISINE.get(n, "north"), per_plate=p, rating=r, includes=it) for n, tg, p, r, it in FOOD],
        "dessert": [dict(name=n, diets=sorted(tg), per_plate=p, rating=r, includes=it) for n, tg, p, r, it in DESSERTS],
        "decor": [dict(name=n, tags=sorted(tg), cost=p, rating=r, includes=it) for n, tg, p, r, it in DECOR],
        "entertainment": [dict(name=n, tags=sorted(tg), cost=p, max_guests=mx, rating=r) for n, tg, p, mx, r in ENTERTAINMENT],
        "photography": [dict(name=n, tags=sorted(tg), cost=p, rating=r, includes=it) for n, tg, p, r, it in PHOTOGRAPHY],
        "gifts": [dict(name=n, per_plate=p, rating=r, includes=it) for n, p, r, it in GIFTS],
    }
