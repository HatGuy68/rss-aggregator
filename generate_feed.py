import feedparser
import yaml
from feedgen.feed import FeedGenerator
from datetime import datetime
from dateutil import parser as date_parser
import os

def load_feeds():
    with open("feeds.yaml", "r") as f:
        return yaml.safe_load(f).get("feeds", [])

def deduplicate_entries(entries):
    seen = set()
    deduped = []
    for entry in entries:
        key = entry.get("link") or entry.get("title")
        if key and key not in seen:
            seen.add(key)
            deduped.append(entry)
    return deduped

def main():
    feed_configs = load_feeds()
    entries = []
    max_items_per_feed = 10
    max_total_items = len(feed_configs) * max_items_per_feed

    for feed_cfg in feed_configs:
        url = feed_cfg.get("url") if isinstance(feed_cfg, dict) else feed_cfg
        print(f"Fetching: {url}")
        feed = feedparser.parse(url)

        count = 0
        for entry in feed.entries:
            if count >= max_items_per_feed:
                break

            pub_date = entry.get("published") or entry.get("updated")
            if isinstance(pub_date, list):
                pub_date = pub_date[0] if pub_date else None
            if not isinstance(pub_date, str):
                pub_date = str(pub_date) if pub_date is not None else None
            entry["parsed_date"] = date_parser.parse(pub_date) if pub_date else datetime.utcnow()
            entries.append(entry)
            count += 1

    entries = deduplicate_entries(entries)
    entries.sort(key=lambda e: e["parsed_date"], reverse=True)
    entries = entries[:max_total_items]

    fg = FeedGenerator()
    fg.title("Aggregated Daily Feed")
    fg.link(href="https://hatguy68.github.io/rss-aggregator/rss.xml", rel="self")
    fg.description("A daily combined RSS feed from multiple sources.")
    fg.language("en")

    for entry in entries:
        fe = fg.add_entry()
        fe.title(entry.get("title", "No title"))
        fe.link(href=entry.get("link", "#"))
        fe.description(entry.get("summary", ""))
        fe.pubDate(entry["parsed_date"])

    os.makedirs("docs", exist_ok=True)
    fg.rss_file("docs/rss.xml")
    print(f"✅ Generated {len(entries)} items in docs/rss.xml")

if __name__ == "__main__":
    main()
