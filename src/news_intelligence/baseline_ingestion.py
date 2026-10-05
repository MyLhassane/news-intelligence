from pathlib import Path

from news_intelligence.article_ingestion import insert_article
from news_intelligence.article_normalization import normalize_article
from news_intelligence.article_validation import validate_article
from news_intelligence.rss_parser import parse_feed


def ingest_feed(
    conn,
    feed_path: Path,
    source_id: int,
    feed_id: int,
) -> dict:
    raw_articles = parse_feed(feed_path)

    inserted = 0
    skipped = 0
    rejected = []

    for raw_article in raw_articles:
        article = normalize_article(raw_article)
        errors = validate_article(article)

        if errors:
            rejected.append(
                {
                    "article": article,
                    "errors": errors,
                }
            )
            continue

        was_inserted = insert_article(
            conn,
            source_id=source_id,
            feed_id=feed_id,
            article=article,
        )

        if was_inserted:
            inserted += 1
        else:
            skipped += 1

    return {
        "parsed": len(raw_articles),
        "inserted": inserted,
        "skipped": skipped,
        "rejected": rejected,
    }
