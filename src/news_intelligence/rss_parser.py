from pathlib import Path
import xml.etree.ElementTree as ET


def parse_feed(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()

    items = []

    for item in root.findall("./channel/item"):
        def text_or_none(tag: str) -> str | None:
            element = item.find(tag)
            if element is None or element.text is None:
                return None
            return element.text.strip()

        items.append(
            {
                "title": text_or_none("title"),
                "url": text_or_none("link"),
                "published_at": text_or_none("pubDate"),
                "author": text_or_none("author"),
                "description": text_or_none("description"),
            }
        )

    return items
