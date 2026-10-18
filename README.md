# News Intelligence

News Intelligence is a project to build an evidence-oriented system that
collects and connects information across multiple sources while preserving
provenance and assessment history.

For the authoritative current stage and project priorities, see
[`docs/roadmap.md`](docs/roadmap.md). Test procedures and the latest observed
results are maintained only in [`docs/testing.md`](docs/testing.md).

## Project Overview

News Intelligence is an evidence-oriented system for preserving traceable
relationships between news articles, stories, claims, evidence, provenance,
and assessment history. Its goals and non-goals are defined in
[`docs/vision.md`](docs/vision.md); conceptual boundaries are defined in
[`docs/architecture.md`](docs/architecture.md).

The pipeline contract and implementation boundaries are documented in
[`docs/pipeline.md`](docs/pipeline.md). The actual database structure is
defined by [`database/schema.sql`](database/schema.sql) and
[`database/views.sql`](database/views.sql), with explanations in
[`docs/database-schema.md`](docs/database-schema.md).

## Repository Structure

```text
news-intelligence/
│
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── vision.md
│   ├── architecture.md
│   ├── pipeline.md
│   ├── database-schema.md
│   ├── decisions.md
│   ├── testing.md
│   └── roadmap.md
│
├── database/
│   ├── schema.sql
│   ├── views.sql
│   └── seeds/
│
├── src/
│   └── news_intelligence/
│       ├── rss_parser.py
│       ├── article_normalization.py
│       ├── title_normalization.py
│       ├── url_normalization.py
│       ├── article_validation.py
│       ├── article_ingestion.py
│       └── baseline_ingestion.py
│
├── tests/
│   ├── fixtures/
│   │   └── feeds/
│   │       ├── baseline.xml
│   │       └── invalid.xml
│   ├── unit/
│   └── integration_test_ingestion.py
│
├── scripts/
└── config/
```

## Development Environment

The Python project uses the local `.venv` environment and the package
configuration in [`pyproject.toml`](pyproject.toml).

Use [`docs/testing.md`](docs/testing.md) for test commands, test database
safeguards, and observed results.

## Project Documentation

The responsibilities and update rules for project documents are defined in
[`AGENTS.md`](AGENTS.md). The current stage and next work are maintained in
[`docs/roadmap.md`](docs/roadmap.md); consult that file rather than relying on
status summaries copied elsewhere.
