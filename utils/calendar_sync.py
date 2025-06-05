import requests
from ics import Calendar
import json
from datetime import datetime

# Each property with both Airbnb and VRBO feeds
ICAL_FEEDS = {
    "hooked-on-islamorada": [
        "https://www.airbnb.com/calendar/ical/1328570188737989157.ics?s=0b6120cfca09c36bbb438dc86f7ef081",
        "http://www.vrbo.com/icalendar/d78d783698314b75a9bb5f133520ceb4.ics?nonTentative"
    ],
    "standish-lakehouse": [
        "https://www.airbnb.com/calendar/ical/1398569327700328777.ics?s=551da8374abbb57f09df6360146ac450",
        "http://www.vrbo.com/icalendar/8354a108516c40f68b238f78f9d827cb.ics?nonTentative"
    ]
}

def fetch_and_parse_ical():
    all_bookings = {}

    for slug, urls in ICAL_FEEDS.items():
        bookings = []
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                calendar = Calendar(response.text)

                for event in calendar.events:
                    bookings.append({
                        "start": event.begin.date().isoformat(),
                        "end": event.end.date().isoformat(),
                        "summary": event.name or "Booked"
                    })

            except Exception as e:
                print(f"[Error loading iCal for {slug}]: {e}")

        bookings.sort(key=lambda x: x["start"])
        all_bookings[slug] = bookings

    with open("content/calendar_data.json", "w") as f:
        json.dump(all_bookings, f, indent=2)

    return all_bookings

# Run manually or via cron later
if __name__ == "__main__":
    fetch_and_parse_ical()
    print("✅ Airbnb + VRBO calendar data saved to content/calendar_data.json")
