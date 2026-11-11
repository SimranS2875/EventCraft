"""EventCraft: Flask backend with dialogue management around NLP + agents."""
import re
import uuid

from flask import Flask, jsonify, request, send_from_directory

import nlp
from agents import CATS, LABEL, OPT_IN, Coordinator, catalog

app = Flask(__name__, static_folder="static")
SESSIONS = {}
SLOTS = ("event_type", "guests", "date", "date_iso", "budget", "venue_pref", "food_pref", "cuisine",
         "dessert_pref", "decor_pref", "entertainment_pref", "photography_pref", "gifts_pref")
REQUIRED = {"guests": "how many guests", "budget": "your total budget (e.g. ₹30,000)"}
VENDORS = {cat: {v["name"] for v in rows} for cat, rows in catalog().items()}

HELP = ("Describe your event in one message, e.g. “I want to organise a farewell party for 50 people next "
        "Saturday. My budget is ₹30,000. I want an indoor venue and vegetarian food.” I'll pick a venue, "
        "food, dessert, decor and entertainment, keep it within budget, and build a timeline. You can then "
        "tweak it (“make it outdoor”, “South Indian food”, “add a photographer”, “no decor”) or pick "
        "vendors yourself in the catalog.")


def rupees(n):
    s = str(int(n))
    head, tail = s[:-3], s[-3:]
    head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
    return "₹" + (head + "," if head else "") + tail


def requirement_object(req):
    out = {"intent": "PlanEvent"}
    out.update({k: req[k] for k in SLOTS if req.get(k) is not None})
    if req.get("picks"):
        out["picks"] = dict(req["picks"])
    return out


def clean_requirement(seed):
    """Validate a requirement object sent back by the browser (used to restore a lost session)."""
    if not isinstance(seed, dict):
        return {}
    req = {k: v for k, v in seed.items() if k in SLOTS and isinstance(v, (str, int)) and not isinstance(v, bool)}
    for k in ("guests", "budget"):
        if k in req and (not isinstance(req[k], int) or req[k] <= 0):
            del req[k]
    picks = seed.get("picks")
    if isinstance(picks, dict):
        picks = {c: n for c, n in picks.items() if c in VENDORS and n in VENDORS[c]}
        if picks:
            req["picks"] = picks
    return req


def replan(state, resp, lead=""):
    """Ask for missing slots, or run the agents and describe the plan."""
    req = state["req"]
    missing = [s for s in REQUIRED if not req.get(s)]
    state["pending"] = missing
    if missing:
        need = " and ".join(REQUIRED[m] for m in missing)
        resp["reply"] = (lead + f" To build the plan I still need {need}.") if lead else f"Thanks! To plan this I still need {need}."
        return
    result = Coordinator().plan(req)
    if not result["ok"]:
        resp["reply"] = result["error"]
        return
    for cat in result["rejected"]:  # picks that can't work are dropped so they don't nag on every turn
        req.get("picks", {}).pop(cat, None)
    plan = result["plan"]
    state["plan"] = plan
    resp.update(plan=plan, messages=result["messages"])
    resp["reply"] = (lead + "\n" if lead else "") + summarise(req, plan)


def handle_message(state, text):
    parsed = nlp.parse(text)
    ent, intent = parsed["entities"], parsed["intent"]
    resp = {"nlp": parsed, "plan": None, "messages": []}

    if intent == "Reset":
        state.update(req={}, pending=[], plan=None)
        resp["reply"] = "Okay, starting fresh. Tell me about your event."
    elif intent in ("Greeting", "Help"):
        resp["reply"] = ("Hi! I'm EventCraft. " if intent == "Greeting" else "") + HELP
    elif intent == "Thanks":
        resp["reply"] = "You're welcome! Tell me if you want to change anything."
    else:
        # Context handling: a bare number answers the slot we asked about.
        bare = re.fullmatch(r"\s*(?:₹|rs\.?)?\s*(\d[\d,]*)\s*(k)?\s*", text.lower())
        if bare and state["pending"]:
            val = nlp._num(bare.group(1), bare.group(2))
            slot = state["pending"][0] if len(state["pending"]) == 1 else ("budget" if val >= 1000 else "guests")
            ent = {slot: val}
        ent = {k: v for k, v in ent.items() if k in SLOTS}
        if not ent and not state["req"]:
            resp["reply"] = "I didn't catch any event details. " + HELP
            return resp
        if not ent:
            resp["reply"] = ("I didn't catch a change there. Tell me what to adjust, such as the budget, "
                             "guest count, venue type or food preference.")
            return resp

        req = state["req"]
        req.update(ent)
        if "date" in ent and "date_iso" not in ent:
            req.pop("date_iso", None)
        for k, v in list(req.items()):
            cat = k[:-5] if k.endswith("_pref") else None
            if v == "Any" and cat not in OPT_IN:  # "add decor" clears an earlier "no decor"
                del req[k]
            if v == "None" and k in ent and cat in req.get("picks", {}):  # "no decor" also removes a catalog pick
                del req["picks"][cat]
        replan(state, resp)

    resp["requirement"] = requirement_object(state["req"]) if state["req"] else None
    return resp


def handle_pick(state, cat, name):
    """The user chose (name) or released (name=None) a specific vendor in the catalog."""
    resp = {"nlp": None, "plan": None, "messages": []}
    req = state["req"]
    picks = req.setdefault("picks", {})
    what = LABEL.get(cat, cat).lower()
    if name is None:
        was = picks.pop(cat, None)
        lead = f"Released {was}; the agents choose the {what} again." if was else f"There was no pick for {what}."
        if cat in OPT_IN and not req.get(cat + "_pref"):
            lead = f"Removed {was} from the plan." if was else lead
    else:
        picks[cat] = name
        if req.get(cat + "_pref") == "None":
            del req[cat + "_pref"]
        lead = f"Added {name} to your plan."
    if not picks:
        del req["picks"]
    replan(state, resp, lead)
    if name and cat not in req.get("picks", {}):
        resp["rejected"] = True
    resp["requirement"] = requirement_object(req) if req else None
    return resp


def summarise(req, plan):
    kind = req.get("event_type") or "event"
    when = f" on {req['date']}" if req.get("date") else ""
    lines = [f"Here's your {kind.lower()} plan for {req['guests']} guests{when}:"]
    lines += [f"• {i['category']}: {i['name']} ({rupees(i['cost'])})" + (" (your pick)" if i["pinned"] else "")
              for i in plan["items"] if not i["skipped"]]
    if plan["within_budget"]:
        lines.append(f"Total {rupees(plan['total'])} of {rupees(plan['budget'])}, "
                     f"leaving {rupees(plan['remaining'])}.")
    else:
        lines.append(f"Total {rupees(plan['total'])} is over your {rupees(plan['budget'])} budget.")
    if plan["negotiation_rounds"]:
        lines.append(f"The Budget Agent negotiated {plan['negotiation_rounds']} round(s) to bring costs down.")
    lines += plan["notes"]
    return "\n".join(lines)


PAGES = {"": "index.html", "catalog": "catalog.html"}


@app.get("/", defaults={"page": ""})
@app.get("/<page>")
def pages(page):
    if page not in PAGES:
        return send_from_directory(app.static_folder, "404.html"), 404
    return send_from_directory(app.static_folder, PAGES[page])


@app.get("/api/catalog")
def api_catalog():
    return jsonify(catalog())


@app.post("/api/chat")
def chat():
    """Body: {message} for chat, or {pick: {category, name|null}} to pin/release a catalog vendor."""
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip() if isinstance(data.get("message"), str) else ""
    pick = data.get("pick") if isinstance(data.get("pick"), dict) else None
    if pick:
        cat, name = pick.get("category"), pick.get("name")
        if cat not in CATS or (name is not None and name not in VENDORS[cat]):
            return jsonify(error="Unknown vendor"), 400
    elif not text:
        return jsonify(error="Empty message"), 400
    sid = data.get("session_id") if isinstance(data.get("session_id"), str) else None
    sid = sid or str(uuid.uuid4())
    if sid not in SESSIONS:
        # After a server restart the browser still has the conversation: restore what it knew.
        SESSIONS[sid] = {"req": clean_requirement(data.get("requirement")), "pending": [], "plan": None}
    state = SESSIONS[sid]
    out = handle_pick(state, cat, name) if pick else handle_message(state, text[:1000])
    out["session_id"] = sid
    return jsonify(out)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
