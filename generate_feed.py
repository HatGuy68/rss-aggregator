import feedparser
import yaml
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from dateutil import parser as date_parser
import os

# Load feed URLs from feeds.yaml
with open("feeds.yaml", "r") as f:
    config = yaml.safe_load(f)
feed_urls = config.get("feeds", [])

# Collect entries from all feeds
entries = []
for url in feed_urls:
    print(f"Fetching: {url}")
    feed = feedparser.parse(url)
    for entry in feed.entries:
        # Parse date for sorting
        pub_date = entry.get("published") or entry.get("updated")
        if pub_date:
            entry["parsed_date"] = date_parser.parse(pub_date)
        else:
            entry["parsed_date"] = datetime.now(timezone.utc)
        entries.append(entry)

# Sort all entries by date descending
entries.sort(key=lambda e: e["parsed_date"], reverse=True)

# Generate new RSS feed
fg = FeedGenerator()
fg.title("Aggregated Daily Feed")
fg.link(href="https://yourdomain.com/rss.xml", rel="self")
fg.description("A daily combined RSS feed from multiple sources.")
fg.language("en")

for entry in entries[:50]:  # Limit to 50 latest items
    fe = fg.add_entry()
    fe.title(entry.get("title", "No title"))
    fe.link(href=entry.get("link", "#"))
    fe.description(entry.get("summary", ""))
    fe.pubDate(entry["parsed_date"])

# Ensure output folder exists
os.makedirs("public", exist_ok=True)
fg.rss_file("public/rss.xml")
print("✅ rss.xml generated in /public/")
