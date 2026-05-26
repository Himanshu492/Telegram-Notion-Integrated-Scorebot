RAW_TEXT_EXTRACTION_PROMPT = """
You are a receipt/ticket parser. Given the image, extract ALL readable text and numbers in a structured way.
Include: any dates, prices, item names, venue names, locations, movie/event names, totals.
Do not interpret yet — just faithfully extract the text.

Output ONLY valid JSON with these exact keys:
{
  "dates_found": ["list of any date strings found"],
  "venue": "venue or establishment name or null",
  "items": ["list of item or dish names"],
  "prices": ["list of price strings found"],
  "location_hints": ["address lines, city, mall name, etc."],
  "other_text": "any other notable text"
}

If the image is unreadable, return: {"error": "unreadable"}
"""

DATE_EXTRACTION_PROMPT = """
Given this extracted receipt/ticket text:
{raw_text}

Identify the TRANSACTION DATE, ACTIVITY DATE, BOOKING DATE, or TICKET DATE.

Rules:
- Use the date of the actual activity, booking, or purchase
- Do NOT use: terms & conditions dates, validity/expiry periods, promotional dates, random dates in fine print
- If multiple dates are present, choose the most likely "event date"
- Return ONLY valid JSON: {{"date": "YYYY-MM-DD"}} or {{"date": null}}
"""

TYPE_CLASSIFICATION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Classify the activity type. Choose one or more from ONLY these exact options:
Fancy, Activity, Drive, Game, Food, Shopping, Chilling, Movie, Nightlife, Attraction, Nature

Classification rules:
- Movie ticket or cinema → ["Movie"]
- Restaurant / cafe / food delivery → ["Food"]
- Grocery / supermarket → ["Shopping"]
- Theme park / zoo / museum / gallery → ["Attraction"]
- Bar / club / pub → ["Nightlife"]
- Dinner at fancy restaurant → ["Fancy", "Food"]
- Multiple clearly apply: include all

Return ONLY a valid JSON array, e.g. ["Food"] or ["Movie", "Food"]
"""

LOCATION_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the venue name and/or physical address where the activity took place.
This could be a restaurant name, cinema name, mall, street address, or city.

Return ONLY valid JSON: {{"location": "venue or address string"}} or {{"location": null}}
"""

MOVIE_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the full movie title being watched (cinema ticket, streaming receipt, etc.).
Return ONLY valid JSON: {{"movie_name": "Full Movie Title"}} or {{"movie_name": null}}
"""

RESTAURANT_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the restaurant, cafe, or food establishment name.
Return ONLY valid JSON: {{"restaurant_name": "establishment name"}} or {{"restaurant_name": null}}
"""

FOOD_ITEMS_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract each individual food item or dish ordered.
Exclude: drinks, service charges, taxes, delivery fees, discounts, misc charges.

Return ONLY a valid JSON array:
[{{"dish": "item name", "price": 12.50, "quantity": 1}}]

Use null for price or quantity if not shown. Return [] if no food items found.
"""

PRICE_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the final total bill amount (after tax/service if shown).
Return ONLY valid JSON: {{"total_price": 45.80}} or {{"total_price": null}}
The value must be a number, not a string.
"""

CUISINE_EXTRACTION_PROMPT = """
Given restaurant name "{restaurant_name}" and food items {food_items},
identify the cuisine type(s).

Return ONLY a valid JSON array of cuisine strings.
Examples: ["Japanese"] or ["Italian", "Mediterranean"] or ["Chinese", "Cantonese"]
Return [] if cuisine cannot be confidently determined.
"""

NORMALIZATION_PROMPT = """
Review these extracted activity values:
{state_json}

Check for obvious errors:
- date: must be a valid calendar date in YYYY-MM-DD format
- types: each item must be one of: Fancy, Activity, Drive, Game, Food, Shopping, Chilling, Movie, Nightlife, Attraction, Nature
- total_price: must be a positive number if present
- food_items: each must have a non-empty "dish" field

Return ONLY valid JSON with the same structure plus an "errors" key listing any problems found.
If all looks good, set "errors" to [].
"""
