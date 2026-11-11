"""EventCraft NLP module: tokenisation, entity extraction, intent detection.

Lightweight rule-based pipeline (no model downloads). Produces the structured
requirement object that the Coordinator Agent consumes.
"""
import datetime as dt
import re

EVENT_TYPES = [  # specific before generic
    ("farewell", "Farewell"), ("birthday", "Birthday"), ("wedding", "Wedding"),
    ("anniversary", "Anniversary"), ("off-?site", "Corporate Offsite"),
    ("team (?:dinner|lunch|outing)", "Team Dinner"), ("fest(?:ival)?", "College Fest"),
    ("fundrais\\w+", "Fundraiser"), ("get[- ]?together", "Get-together"),
    ("reunion", "Reunion"), ("baby shower", "Baby Shower"), ("engagement", "Engagement"),
    ("house ?warming", "Housewarming"), ("graduation", "Graduation"),
    ("conference", "Conference"), ("seminar", "Seminar"), ("meet-?up", "Meetup"),
    ("party", "Party"), ("dinner", "Dinner"),
]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MULT = {"k": 1_000, "thousand": 1_000, "lakh": 100_000, "lakhs": 100_000, "lac": 100_000, "lacs": 100_000}
GUEST_WORDS = r"(?:people|persons?|guests?|pax|attendees|members|friends|folks|students|colleagues|employees|adults)"
DECOR_PREFS = [(r"flor\w+|flowers?", "Floral"), (r"balloons?", "Balloons"), (r"fairy lights|string lights|lighting", "Lights"),
               (r"photo ?booth", "Photo booth"), (r"mandap|traditional|marigold", "Traditional"),
               (r"royal|regal|grand decor", "Royal"), (r"boho|bohemian", "Boho"), (r"minimal\w*", "Minimalist")]
CUISINES = [(r"south[- ]indian|dosa|idli", "South Indian"), (r"north[- ]indian|punjabi", "North Indian"),
            (r"(?:indo[- ])?chinese|noodles|manchurian", "Chinese")]
PHOTO = r"photograph\w*|videograph\w*|cinematograph\w*|camera ?(?:man|person)|photos?(?! ?booth)|video\w*"
GIFTS = r"(?:return )?gifts?|favou?rs|hampers?"
OPTIONAL = [(r"decor\w*", "decor_pref"), (r"des{1,2}erts?|sweets", "dessert_pref"), (r"entertainment", "entertainment_pref"),
            (PHOTO, "photography_pref"), (GIFTS, "gifts_pref")]
ENT_PREFS = [("dj", "DJ"), ("live band|band", "Live band"), ("karaoke", "Karaoke"),
             ("magician|magic", "Magician"), ("games?", "Games"), ("music", "Music")]


def tokenize(text):
    return re.findall(r"₹|\d+(?:,\d+)*(?:\.\d+)?|[A-Za-z]+(?:[-'][A-Za-z]+)*|[^\sA-Za-z\d]", text)


def _num(s, suffix=None):
    v = float(s.replace(",", ""))
    return int(round(v * MULT.get((suffix or "").lower(), 1)))


def extract_budget(text):
    """Returns (amount, (start, end)) or (None, None)."""
    t = text.lower()
    amt = r"(?:₹|rs\.?|inr)?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|thousand|lakhs?|lacs?)?"
    neg = rf"(?!\s*{GUEST_WORDS}\b)"
    patterns = [
        rf"(?:budget|under|within|upto|up to|maximum|max|around|about|spend|afford)\b[^\d₹]{{0,20}}?{amt}\b{neg}",
        r"(?:₹|rs\.?|inr)\s*(\d[\d,]*(?:\.\d+)?)\s*(k|thousand|lakhs?|lacs?)?",
        r"(\d[\d,]*(?:\.\d+)?)\s*(k|thousand|lakhs?|lacs?)?\s*(?:rupees|rs|inr)\b",
        r"\b(\d+(?:\.\d+)?)\s*(k|lakhs?|lacs?)\b",
    ]
    for p in patterns:
        m = re.search(p, t)
        if m:
            return _num(m.group(1), m.group(2)), m.span()
    return None, None


def extract_guests(text):
    t = text.lower()
    for p in (rf"(\d[\d,]*)\s*\+?\s*{GUEST_WORDS}\b",
              rf"{GUEST_WORDS}\s*(?:count|:|of|are|is)?\s*(\d[\d,]*)\b",
              r"\bfor\s+(?:about\s+|around\s+|approx\w*\s+)?(\d{1,4})\b(?!\s*[,\d]|\s*(?:k|rs|inr|rupees))"):
        m = re.search(p, t)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def resolve_date(text, today=None):
    """Returns (label, iso_date_or_None)."""
    today = today or dt.date.today()
    t = text.lower()
    m = re.search(r"\b(next|this|coming|upcoming)\s+(" + "|".join(WEEKDAYS) + r")\b", t)
    if m:
        ahead = (WEEKDAYS.index(m.group(2)) - today.weekday()) % 7 or 7
        d = today + dt.timedelta(days=ahead)
        return f"{m.group(1).title()} {m.group(2).title()}", d.isoformat()
    m = re.search(r"\b(?:on\s+)?(" + "|".join(WEEKDAYS) + r")\b", t)
    if m:
        ahead = (WEEKDAYS.index(m.group(1)) - today.weekday()) % 7 or 7
        return m.group(1).title(), (today + dt.timedelta(days=ahead)).isoformat()
    m = re.search(r"\b(today|tonight|tomorrow|day after tomorrow)\b", t)
    if m:
        off = {"today": 0, "tonight": 0, "tomorrow": 1, "day after tomorrow": 2}[m.group(1)]
        return m.group(1).title(), (today + dt.timedelta(days=off)).isoformat()
    m = re.search(r"\b(this|next)\s+weekend\b", t)
    if m:
        ahead = (5 - today.weekday()) % 7 or 7
        if m.group(1) == "next":
            ahead += 7
        return f"{m.group(1).title()} Weekend", (today + dt.timedelta(days=ahead)).isoformat()
    mon = "|".join(MONTHS)
    m = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({mon})[a-z]*\b(?:,?\s+(\d{{4}}))?", t) or None
    m2 = None if m else re.search(rf"\b({mon})[a-z]*\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,?\s+(\d{{4}}))?", t)
    if m or m2:
        day, mo, yr = (int(m.group(1)), m.group(2), m.group(3)) if m else (int(m2.group(2)), m2.group(1), m2.group(3))
        mi = MONTHS.index(mo) + 1
        year = int(yr) if yr else today.year
        try:
            d = dt.date(year, mi, day)
            if not yr and d < today:
                d = dt.date(year + 1, mi, day)
            return d.strftime("%d %b %Y"), d.isoformat()
        except ValueError:
            pass
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", t)
    if m:
        day, mi = int(m.group(1)), int(m.group(2))
        yr = int(m.group(3)) if m.group(3) else today.year
        yr += 2000 if yr < 100 else 0
        try:
            d = dt.date(yr, mi, day)
            return d.strftime("%d %b %Y"), d.isoformat()
        except ValueError:
            pass
    return None, None


def parse(text, today=None):
    """Full pipeline -> dict with intent, entities and a per-stage trace."""
    t = text.lower()
    tokens = tokenize(text)
    ent = {}

    for pat, label in EVENT_TYPES:
        if re.search(rf"\b{pat}\b", t):
            ent["event_type"] = label
            break

    budget, span = extract_budget(text)
    if budget:
        ent["budget"] = budget
    rest = t if not span else t[:span[0]] + " " + t[span[1]:]
    guests = extract_guests(rest)
    if guests:
        ent["guests"] = guests

    label, iso = resolve_date(text, today)
    if label:
        ent["date"], ent["date_iso"] = label, iso

    if re.search(r"\b(indoors?|inside|air[- ]?condition\w*|banquet|\bhall)\b", t):
        ent["venue_pref"] = "Indoor"
    elif re.search(r"\b(outdoors?|open[- ]air|garden|lawn|terrace|rooftop|farmhouse|poolside)\b", t):
        ent["venue_pref"] = "Outdoor"

    if re.search(r"\bnon[- ]?veg\w*|\bchicken\b|\bmutton\b|\bmeat\b", t):
        ent["food_pref"] = "Non-Vegetarian"
    elif re.search(r"\bvegan\b", t):
        ent["food_pref"] = "Vegan"
    elif re.search(r"\bjain\b", t):
        ent["food_pref"] = "Jain"
    elif re.search(r"\bveg(?:etarian)?\b", t):
        ent["food_pref"] = "Vegetarian"

    for pat, label in ENT_PREFS:
        if re.search(rf"\b(?:{pat})\b", t):
            ent["entertainment_pref"] = label
            break

    for pat, label in DECOR_PREFS:
        if re.search(rf"\b(?:{pat})\b", t):
            ent["decor_pref"] = label
            break

    for pat, label in CUISINES:
        if re.search(rf"\b(?:{pat})\b", t):
            ent["cuisine"] = label
            break

    # Photography and return gifts are opt-in: any mention switches them on.
    if re.search(rf"\b(?:{PHOTO})\b", t):
        ent["photography_pref"] = "Video" if re.search(r"\b(?:video\w*|cinematograph\w*|film)\b", t) else "Any"
    if re.search(rf"\b(?:{GIFTS})\b", t) and "gift presentation" not in t:
        ent["gifts_pref"] = "Any"

    # Optional extras: "no decor" skips one, "add dessert" brings it back.
    words = r"(?:\w+\s+){0,2}?"
    for pat, slot in OPTIONAL:
        if re.search(rf"\b(?:no|without|skip|remove|drop|cancel)\s+{words}(?:{pat})\b", t):
            ent[slot] = "None"
        elif slot not in ent and re.search(rf"\b(?:add|include|with|want|need)\s+{words}(?:{pat})\b", t):
            ent[slot] = "Any"

    if re.search(r"\b(start over|reset|new event|clear everything|from scratch)\b", t):
        intent = "Reset"
    elif re.match(r"\s*(hi|hello|hey|good (morning|evening|afternoon))\b", t) and not ent:
        intent = "Greeting"
    elif re.search(r"\b(help|what can you do|how does this work)\b", t) and not ent:
        intent = "Help"
    elif re.search(r"\b(thanks|thank you|thx)\b", t) and not ent:
        intent = "Thanks"
    elif ent or re.search(r"\b(plan|organi[sz]e|arrange|host|throw|book|event|party)\b", t):
        intent = "PlanEvent"
    else:
        intent = "Unknown"

    trace = [
        {"stage": "Tokenization", "output": tokens},
        {"stage": "Named entity recognition", "output": {k: v for k, v in ent.items() if k in ("date", "budget", "guests")}},
        {"stage": "Intent detection", "output": intent},
        {"stage": "Entity extraction", "output": {k: v for k, v in ent.items() if k != "date_iso"}},
    ]
    return {"intent": intent, "entities": ent, "trace": trace}
