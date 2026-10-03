    -- News Intelligence
-- Synthetic test data only.
-- This file must never be treated as production or real-world evidence.

BEGIN;

-- ============================================================
-- Sources
-- ============================================================

INSERT INTO sources (
    name,
    country,
    source_type,
    website
)
VALUES
    (
        'Test News Agency A',
        'Testland',
        'news_agency',
        'https://example.org/test-news-a'
    ),
    (
        'Test News Agency B',
        'Testland',
        'news_agency',
        'https://example.org/test-news-b'
    ),
    (
        'Test Research Institution',
        'Testland',
        'research_institution',
        'https://example.org/test-research'
    );

-- ============================================================
-- Story
-- ============================================================

INSERT INTO stories (
    title,
    summary,
    story_type,
    status
)
VALUES (
    'Test: conflicting evidence',
    'Synthetic story used to test evidence relationships and historical assessments.',
    'developing_story',
    'active'
);

-- ============================================================
-- Articles
-- ============================================================

INSERT INTO articles (
    source_id,
    title,
    url,
    published_at,
    language,
    content
)
SELECT
    s.id,
    'Test Article A',
    'https://example.org/test-article-a',
    '2026-01-01 10:00:00+00',
    'en',
    'Synthetic article A. It reports the result of a fictional experiment.'
FROM sources s
WHERE s.name = 'Test News Agency A';

INSERT INTO articles (
    source_id,
    title,
    url,
    published_at,
    language,
    content
)
SELECT
    s.id,
    'Test Article B',
    'https://example.org/test-article-b',
    '2026-01-01 11:00:00+00',
    'en',
    'Synthetic article B. It reports the same underlying fictional evidence.'
FROM sources s
WHERE s.name = 'Test News Agency B';

-- ============================================================
-- Link articles to the story
-- ============================================================

INSERT INTO article_stories (
    article_id,
    story_id,
    relation_type,
    is_primary
)
SELECT
    a.id,
    s.id,
    'coverage',
    CASE
        WHEN a.title = 'Test Article A' THEN TRUE
        ELSE FALSE
    END
FROM articles a
CROSS JOIN stories s
WHERE s.title = 'Test: conflicting evidence'
  AND a.title IN ('Test Article A', 'Test Article B');

-- ============================================================
-- Claim
-- ============================================================

INSERT INTO claims (
    story_id,
    claim_text,
    claim_type,
    status
)
SELECT
    s.id,
    'The test subject completed the experiment successfully.',
    'factual',
    'unverified'
FROM stories s
WHERE s.title = 'Test: conflicting evidence';

-- ============================================================
-- Primary evidence
-- ============================================================

INSERT INTO evidence (
    type,
    title,
    url,
    description,
    published_at,
    language
)
VALUES (
    'research_report',
    'Test Evidence A',
    'https://example.org/test-evidence-a',
    'Synthetic research report supporting the test claim.',
    '2026-01-01 09:00:00+00',
    'en'
);

-- ============================================================
-- Contradicting evidence
-- ============================================================

INSERT INTO evidence (
    type,
    title,
    url,
    description,
    published_at,
    language
)
VALUES (
    'research_report',
    'Test Evidence B',
    'https://example.org/test-evidence-b',
    'Synthetic research report contradicting the test claim.',
    '2026-01-01 12:00:00+00',
    'en'
);

-- ============================================================
-- Evidence produced by the research institution
-- ============================================================

INSERT INTO evidence_sources (
    evidence_id,
    source_id,
    relationship
)
SELECT
    e.id,
    s.id,
    'producer'
FROM evidence e
CROSS JOIN sources s
WHERE e.title IN ('Test Evidence A', 'Test Evidence B')
  AND s.name = 'Test Research Institution';

-- ============================================================
-- Link evidence to claim
-- ============================================================

INSERT INTO claim_evidence (
    claim_id,
    evidence_id,
    relationship,
    excerpt
)
SELECT
    c.id,
    e.id,
    CASE
        WHEN e.title = 'Test Evidence A' THEN 'supports'
        WHEN e.title = 'Test Evidence B' THEN 'contradicts'
    END,
    CASE
        WHEN e.title = 'Test Evidence A'
            THEN 'Synthetic evidence directly supports successful completion.'
        WHEN e.title = 'Test Evidence B'
            THEN 'Synthetic evidence directly contradicts successful completion.'
    END
FROM claims c
CROSS JOIN evidence e
WHERE c.claim_text = 'The test subject completed the experiment successfully.'
  AND e.title IN ('Test Evidence A', 'Test Evidence B');

-- ============================================================
-- Articles report the same underlying evidence
-- ============================================================

INSERT INTO article_evidence (
    article_id,
    evidence_id,
    relationship,
    excerpt
)
SELECT
    a.id,
    e.id,
    'based_on',
    'Synthetic test: article is based on the same underlying evidence.'
FROM articles a
CROSS JOIN evidence e
WHERE a.title IN ('Test Article A', 'Test Article B')
  AND e.title = 'Test Evidence A';

-- ============================================================
-- Articles report the claim
-- ============================================================

INSERT INTO claim_sources (
    claim_id,
    article_id,
    relationship,
    excerpt,
    source_role
)
SELECT
    c.id,
    a.id,
    'reports',
    'Synthetic article reports the test claim.',
    'secondary'
FROM claims c
CROSS JOIN articles a
WHERE c.claim_text = 'The test subject completed the experiment successfully.'
  AND a.title IN ('Test Article A', 'Test Article B');

-- ============================================================
-- Historical assessment 1
-- Initial state: evidence conflict -> unclear
-- ============================================================

INSERT INTO claim_assessments (
    claim_id,
    assessment_status,
    actor_type,
    actor_name,
    reasoning,
    assessment_role
)
SELECT
    c.id,
    'unclear',
    'human',
    'manual_test_review',
    'Two available synthetic evidence items directly conflict.',
    'decision'
FROM claims c
WHERE c.claim_text = 'The test subject completed the experiment successfully.';

-- Current claim status after first assessment
UPDATE claims
SET
    status = 'unclear',
    last_checked_at = NOW()
WHERE claim_text = 'The test subject completed the experiment successfully.';

-- ============================================================
-- Original experiment record
-- ============================================================

INSERT INTO evidence (
    type,
    title,
    url,
    description,
    published_at,
    language
)
VALUES (
    'official_document',
    'Test Evidence C',
    'https://example.org/test-evidence-c',
    'Synthetic original experiment record confirming successful completion.',
    '2026-01-02 09:00:00+00',
    'en'
);

INSERT INTO evidence_sources (
    evidence_id,
    source_id,
    relationship
)
SELECT
    e.id,
    s.id,
    'issuer'
FROM evidence e
CROSS JOIN sources s
WHERE e.title = 'Test Evidence C'
  AND s.name = 'Test Research Institution';

INSERT INTO claim_evidence (
    claim_id,
    evidence_id,
    relationship,
    excerpt
)
SELECT
    c.id,
    e.id,
    'supports',
    'Synthetic original experiment record directly confirms completion.'
FROM claims c
CROSS JOIN evidence e
WHERE c.claim_text = 'The test subject completed the experiment successfully.'
  AND e.title = 'Test Evidence C';

-- ============================================================
-- Historical assessment 2
-- New evidence -> supported
-- ============================================================

INSERT INTO claim_assessments (
    claim_id,
    assessment_status,
    actor_type,
    actor_name,
    reasoning,
    assessment_role
)
SELECT
    c.id,
    'supported',
    'human',
    'manual_test_review',
    'A newly available original experiment record directly confirms successful completion.',
    'decision'
FROM claims c
WHERE c.claim_text = 'The test subject completed the experiment successfully.';

UPDATE claims
SET
    status = 'supported',
    last_checked_at = NOW()
WHERE claim_text = 'The test subject completed the experiment successfully.';

-- ============================================================
-- Independent evidence
-- ============================================================

INSERT INTO evidence (
    type,
    title,
    url,
    description,
    published_at,
    language
)
VALUES (
    'official_document',
    'Test Independent Evidence',
    'https://example.org/test-independent-evidence',
    'Synthetic independent test record supporting the claim.',
    '2026-01-03 09:00:00+00',
    'en'
);

INSERT INTO evidence_sources (
    evidence_id,
    source_id,
    relationship
)
SELECT
    e.id,
    s.id,
    'producer'
FROM evidence e
CROSS JOIN sources s
WHERE e.title = 'Test Independent Evidence'
  AND s.name = 'Test News Agency B';

INSERT INTO claim_evidence (
    claim_id,
    evidence_id,
    relationship,
    excerpt
)
SELECT
    c.id,
    e.id,
    'supports',
    'Synthetic independent evidence supports the claim.'
FROM claims c
CROSS JOIN evidence e
WHERE c.claim_text = 'The test subject completed the experiment successfully.'
  AND e.title = 'Test Independent Evidence';

COMMIT;
