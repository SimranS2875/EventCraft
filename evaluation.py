"""Measures the real system against the slide-10 targets on a generated test set."""
import random
import time

import app as ev
from agents import FOOD, VENUES, available

TARGETS = [
    ("Intent classification accuracy", "intent_accuracy", "≥ 90%", lambda v: v >= 0.90, "pct"),
    ("Entity extraction F1-score", "entity_f1", "≥ 0.85", lambda v: v >= 0.85, "f"),
    ("Budget-fit success rate (feasible budgets)", "budget_fit", "≥ 95%", lambda v: v >= 0.95, "pct"),
    ("Negotiation resolution time", "avg_rounds", "≤ 3 rounds", lambda v: v <= 3, "rounds"),
    ("Plan completion rate", "completion", "≥ 90%", lambda v: v >= 0.90, "pct"),
    ("Average response latency", "latency_s", "≤ 2 sec", lambda v: v <= 2, "sec"),
]
EVENTS = [("farewell party", "Farewell"), ("birthday party", "Birthday"), ("team dinner", "Team Dinner"),
          ("wedding reception", "Wedding"), ("college fest", "College Fest"), ("fundraiser", "Fundraiser")]
BUDGET_FMT = [lambda b: f"My budget is ₹{b:,}.", lambda b: f"Budget: {b} rupees.",
              lambda b: f"Keep it under {b // 1000}k.", lambda b: f"I can spend Rs. {b:,}."]
GUEST_FMT = [lambda g: f"for {g} people", lambda g: f"for {g} guests", lambda g: f"with {g} attendees"]
DATES = ["next Saturday", "tomorrow", "this Friday", "on 12 December"]
NON_PLAN = [("hello there", "Greeting"), ("hi", "Greeting"), ("what can you do?", "Help"),
            ("thanks a lot", "Thanks"), ("start over please", "Reset"), ("new event", "Reset")]


def generate(n=60, seed=7):
    rnd, cases = random.Random(seed), []
    for _ in range(n):
        phrase, label = rnd.choice(EVENTS)
        g, b = rnd.choice([20, 30, 40, 50, 60, 80, 100]), rnd.choice([15000, 20000, 30000, 40000, 60000, 90000])
        venue, food = rnd.choice(["Indoor", "Outdoor"]), rnd.choice(["Vegetarian", "Non-Vegetarian", "Vegan", "Jain"])
        date = rnd.choice(DATES)
        text = (f"I want to organize a {phrase} {rnd.choice(GUEST_FMT)(g)} {date}. {rnd.choice(BUDGET_FMT)(b)} "
                f"I want an {venue.lower()} venue and {food.lower()} food.")
        cases.append({"text": text, "gold": {"event_type": label, "guests": g, "budget": b,
                                                "venue_pref": venue, "food_pref": food}})
    return cases


def min_cost(g, venue, food, iso=None):
    """Cheapest possible plan from the catalogue (no entertainment)."""
    key = {"Vegetarian": "veg", "Vegan": "vegan", "Jain": "jain", "Non-Vegetarian": "nonveg"}[food]
    v = min((p for n, t, c, p, _ in VENUES if c >= g and t == venue.lower() and available(n, iso)), default=10**9)
    f = min(p for _, tg, p, *_ in FOOD if key in tg) * g
    return v + f


def run(n=60):
    cases = generate(n)
    tp = fp = fn = 0
    intent_ok = intent_n = 0
    fits = done = feas = feas_fit = 0
    rounds, lat = [], []
    for c in cases:
        state = {"req": {}, "pending": [], "plan": None}
        t0 = time.perf_counter()
        r = ev.handle_message(state, c["text"])
        lat.append(time.perf_counter() - t0)
        ent = r["nlp"]["entities"]
        intent_n += 1
        intent_ok += r["nlp"]["intent"] == "PlanEvent"
        for k, v in c["gold"].items():
            if k in ent and ent[k] == v:
                tp += 1
            elif k in ent:
                fp += 1
                fn += 1
            else:
                fn += 1
        if r["plan"]:
            done += 1
            fits += r["plan"]["within_budget"]
            gd = c["gold"]
            if min_cost(gd["guests"], gd["venue_pref"], gd["food_pref"], ent.get("date_iso")) <= gd["budget"]:
                feas += 1
                feas_fit += r["plan"]["within_budget"]
            rounds.append(r["plan"]["negotiation_rounds"])
    for text, gold in NON_PLAN:
        intent_n += 1
        intent_ok += ev.nlp.parse(text)["intent"] == gold
    prec, rec = tp / max(1, tp + fp), tp / max(1, tp + fn)
    m = {"intent_accuracy": intent_ok / intent_n, "entity_f1": 2 * prec * rec / max(1e-9, prec + rec),
         "budget_fit": feas_fit / max(1, feas), "budget_fit_raw": fits / max(1, done),
         "infeasible": done - feas, "avg_rounds": sum(rounds) / max(1, len(rounds)),
         "max_rounds": max(rounds or [0]), "completion": done / len(cases), "latency_s": sum(lat) / len(lat)}
    rows = []
    for name, key, target, ok, kind in TARGETS:
        v = m[key]
        shown = {"pct": f"{v:.1%}", "f": f"{v:.2f}", "rounds": f"{v:.2f} avg (max {m['max_rounds']})",
                 "sec": f"{v * 1000:.1f} ms"}[kind]
        rows.append({"metric": name, "target": target, "measured": shown, "met": bool(ok(v))})
    rows.append({"metric": "User satisfaction (survey)", "target": "≥ 4 / 5", "measured": "Not measured (needs test users)", "met": None})
    return {"cases": len(cases) + len(NON_PLAN), "rows": rows, "examples": [c["text"] for c in cases[:3]],
            "raw_budget_fit": f"{m['budget_fit_raw']:.1%}", "infeasible": m["infeasible"],
            "note": "Synthetic, template-generated utterances; real user phrasing will score lower."}

