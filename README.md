# EventCraft

Conversational multi-agent event planner (from the project review slides).

```
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
pytest                 # tests
```

- `nlp.py`: tokenisation, entity extraction (type, guests, date, budget, venue/food/entertainment prefs), intent detection. Rule-based, no model downloads.
- `agents.py`: Coordinator plus Venue, Food, Dessert, Decor, Entertainment, Photography, Gifts, Budget and Schedule agents exchanging structured JSON messages over a `Bus`. Specialists open with premium bids; the Budget Agent negotiates cheaper alternatives until the plan fits.
- `app.py`: Flask API (`POST /api/chat`) with dialogue management (multi-turn slot filling, follow-up edits like "make it outdoor").
- `static/index.html`: chat UI showing the plan, requirement object, agent messages and NLP trace.

Catalogues in `agents.py` are sample data; swap in SQLite/MongoDB for real vendors.

## Pages

`/` plan an event (chat, plan ticket, agent messages) and `/catalog` vendor catalog (filters, search, per-guest pricing). Vendor pictures are SVG illustrations drawn in `static/art.js`.

`python -c "import evaluation, json; print(json.dumps(evaluation.run(), indent=1))"` runs the metrics check.

Dessert, decor and entertainment are optional: say "no decor" or "skip dessert" to drop one, "add dessert" to bring it back. The chat is saved in the browser (localStorage), so it survives page changes and reloads; "New event" clears it.

Photography and return gifts are opt-in ("add a photographer", "return gifts"). Food understands cuisines (North Indian, South Indian, Chinese) and decor understands themes (royal, boho, minimalist, floral...). Venues have a sample availability calendar, so some are booked on a given date. In the catalog, "Add to plan" pins a vendor: the agents plan around it and the Budget Agent never bargains it away.
