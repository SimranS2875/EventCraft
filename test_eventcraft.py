import json

import app as ev
import nlp

EXAMPLE = ("I want to organize a farewell party for 50 people next Saturday. "
           "My budget is ₹30,000. I want an indoor venue and vegetarian food.")


def state():
    return {"req": {}, "pending": [], "plan": None}


def test_extraction_matches_slide():
    e = nlp.parse(EXAMPLE)["entities"]
    assert (e["event_type"], e["guests"], e["budget"]) == ("Farewell", 50, 30000)
    assert (e["date"], e["venue_pref"], e["food_pref"]) == ("Next Saturday", "Indoor", "Vegetarian")


def test_budget_formats():
    assert nlp.parse("under 30k for 20 people")["entities"]["budget"] == 30000
    assert nlp.parse("budget is 1.5 lakh, 80 guests")["entities"]["guests"] == 80
    assert nlp.parse("non-veg food")["entities"]["food_pref"] == "Non-Vegetarian"


def test_full_plan_within_budget():
    r = ev.handle_message(state(), EXAMPLE)
    p = r["plan"]
    assert p["within_budget"] and p["total"] <= 30000
    print(json.dumps(r["requirement"], indent=1), r["reply"], sep="\n")


def test_negotiation_triggers_on_small_budget():
    r = ev.handle_message(state(), "birthday party for 60 people, budget 15000, indoor, vegetarian, dj")
    p = r["plan"]
    assert p["negotiation_rounds"] >= 1 and p["within_budget"]
    assert any(m["type"] == "propose_cheaper" for m in r["messages"])
    print(r["reply"])


def test_impossible_budget_reports_overrun():
    r = ev.handle_message(state(), "wedding for 300 guests, budget 5000")
    assert r["plan"] and not r["plan"]["within_budget"]


def test_multi_turn_and_modification():
    s = state()
    r = ev.handle_message(s, "plan a birthday party")
    assert r["plan"] is None and "guests" in r["reply"]
    r = ev.handle_message(s, "40")
    assert s["req"]["guests"] == 40 and r["plan"] is None
    r = ev.handle_message(s, "25000")
    assert r["plan"] and s["req"]["budget"] == 25000
    r = ev.handle_message(s, "make it outdoor")
    assert r["plan"]["items"][0]["name"] and s["req"]["venue_pref"] == "Outdoor"


def test_no_venue_match():
    r = ev.handle_message(state(), "party for 900 people, budget 100000")
    assert r["plan"] is None and "venue" in r["reply"]


def test_api():
    c = ev.app.test_client()
    j = c.post("/api/chat", json={"message": EXAMPLE}).get_json()
    assert j["plan"] and j["session_id"]
    assert c.post("/api/chat", json={"message": ""}).status_code == 400


def test_pages_and_apis():
    c = ev.app.test_client()
    for p in ev.PAGES:
        r = c.get("/" + p)
        assert r.status_code == 200 and b"nav.js" in r.data, p
        r.close()
    assert c.get("/nope").status_code == 404
    assert c.get("/static/style.css").status_code == 200
    cat = c.get("/api/catalog").get_json()
    assert set(cat) == {"venue", "food", "dessert", "decor", "entertainment", "photography", "gifts"}
    assert all(f["includes"] for k in ("food", "dessert", "decor", "photography", "gifts") for f in cat[k])
    assert c.get("/overview").status_code == 404
    import evaluation
    rows = evaluation.run()["rows"]
    assert len(rows) == 7 and all(r["met"] for r in rows if r["met"] is not None)


def test_decor_dessert_optional():
    s = state()
    r = ev.handle_message(s, EXAMPLE)
    cats = [i["category"] for i in r["plan"]["items"]]
    assert cats == ["Venue", "Food", "Dessert", "Decor", "Entertainment"]  # photography and gifts are opt-in
    assert r["plan"]["items"][1]["includes"]
    r = ev.handle_message(s, "no decor please")
    decor = r["plan"]["items"][3]
    assert decor["skipped"] and decor["cost"] == 0 and not any("dropped" in n for n in r["plan"]["notes"])
    r = ev.handle_message(s, "add floral decor and skip deserts")
    assert s["req"]["decor_pref"] == "Floral" and r["plan"]["items"][2]["skipped"]
    r = ev.handle_message(s, "add dessert")
    assert "dessert_pref" not in s["req"] and not r["plan"]["items"][2]["skipped"]


def test_session_restored_from_client():
    c = ev.app.test_client()
    j = c.post("/api/chat", json={"message": "make it outdoor", "session_id": "gone-after-restart",
                                  "requirement": {"guests": 40, "budget": 30000, "event_type": "Birthday", "junk": 1}}).get_json()
    assert j["plan"] and j["requirement"]["venue_pref"] == "Outdoor" and "junk" not in j["requirement"]


BASE = "Birthday party for 40 people, budget 60000, indoor"


def items(r):
    return {i["key"]: i for i in r["plan"]["items"]}


def test_opt_in_photography_gifts_and_cuisine():
    s = state()
    r = ev.handle_message(s, BASE + ", South Indian vegetarian food, boho decor")
    it = items(r)
    assert "photography" not in it and "gifts" not in it
    assert it["food"]["name"].startswith("South Indian") and it["decor"]["name"].startswith("Boho")
    r = ev.handle_message(s, "add a photographer and return gifts")
    it = items(r)
    assert not it["photography"]["skipped"] and not it["gifts"]["skipped"] and r["plan"]["within_budget"]
    r = ev.handle_message(s, "no photography")
    assert "photography" not in items(r)


def test_catalog_pick_is_pinned_and_released():
    s = state()
    ev.handle_message(s, BASE)
    r = ev.handle_pick(s, "entertainment", "Live Band")
    it = items(r)
    assert it["entertainment"]["name"] == "Live Band" and it["entertainment"]["pinned"]
    assert r["requirement"]["picks"] == {"entertainment": "Live Band"} and "Added Live Band" in r["reply"]
    r = ev.handle_message(s, "budget 30000")  # tight budget: the pick survives, others get cheaper
    assert items(r)["entertainment"]["name"] == "Live Band"
    r = ev.handle_pick(s, "entertainment", None)
    assert not items(r)["entertainment"]["pinned"] and "picks" not in r["requirement"]


def test_pick_before_details_and_bad_pick():
    s = state()
    r = ev.handle_pick(s, "gifts", "Potted Succulent")
    assert r["plan"] is None and "Added Potted Succulent" in r["reply"] and "guests" in r["reply"]
    r = ev.handle_message(s, "wedding for 300 people, budget 500000")
    assert items(r)["gifts"]["name"] == "Potted Succulent"
    r = ev.handle_pick(s, "venue", "Sunset Terrace Cafe")  # holds 50, event has 300
    assert r["rejected"] and items(r)["venue"]["name"] != "Sunset Terrace Cafe" and "picks" in r["requirement"]
    assert "venue" not in r["requirement"]["picks"]
    c = ev.app.test_client()
    assert c.post("/api/chat", json={"pick": {"category": "venue", "name": "Nope"}}).status_code == 400
    j = c.post("/api/chat", json={"pick": {"category": "decor", "name": "Marigold Floral"},
                                  "requirement": {"guests": 40, "budget": 50000}}).get_json()
    assert j["plan"] and any(i["pinned"] for i in j["plan"]["items"])


def test_venue_availability():
    import agents
    iso = next(d for d in (f"2027-01-{n:02d}" for n in range(1, 29)) if not agents.available("Green Leaf Banquet", d))
    s = state()
    s["req"].update(guests=50, budget=30000, venue_pref="Indoor", date="that day", date_iso=iso)
    r = ev.handle_message(s, "vegetarian food")
    assert items(r)["venue"]["name"] != "Green Leaf Banquet"
    assert any("Green Leaf Banquet" in n and "booked" in n for n in r["plan"]["notes"])
