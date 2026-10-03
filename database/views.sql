--
-- PostgreSQL database dump
--

\restrict Zuj5u7GbjZCWtrQakdI1Z8NzBihvdfHsvh5LhhYSms37elOGiFQymmlMA1Qpq3n

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: claim_evidence_conflicts; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.claim_evidence_conflicts AS
 SELECT c.id AS claim_id,
    c.story_id,
    c.claim_text,
    c.status AS claim_status,
    count(DISTINCT
        CASE
            WHEN (ce.relationship = 'supports'::text) THEN ce.evidence_id
            ELSE NULL::bigint
        END) AS supporting_evidence_count,
    count(DISTINCT
        CASE
            WHEN (ce.relationship = 'contradicts'::text) THEN ce.evidence_id
            ELSE NULL::bigint
        END) AS contradicting_evidence_count
   FROM (public.claims c
     LEFT JOIN public.claim_evidence ce ON ((ce.claim_id = c.id)))
  GROUP BY c.id, c.story_id, c.claim_text, c.status
 HAVING ((count(DISTINCT
        CASE
            WHEN (ce.relationship = 'supports'::text) THEN ce.evidence_id
            ELSE NULL::bigint
        END) > 0) AND (count(DISTINCT
        CASE
            WHEN (ce.relationship = 'contradicts'::text) THEN ce.evidence_id
            ELSE NULL::bigint
        END) > 0));


--
-- Name: claim_intelligence; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.claim_intelligence AS
 SELECT s.id AS story_id,
    s.title AS story_title,
    s.story_type,
    s.status AS story_status,
    c.id AS claim_id,
    c.claim_text,
    c.claim_type,
    c.status AS claim_status,
    c.first_seen_at AS claim_first_seen_at,
    c.last_checked_at AS claim_last_checked_at,
    e.id AS evidence_id,
    e.type AS evidence_type,
    e.title AS evidence_title,
    e.url AS evidence_url,
    e.published_at AS evidence_published_at,
    ce.relationship AS evidence_relationship,
    ce.excerpt AS evidence_excerpt,
    es.source_id AS evidence_source_id,
    src.name AS evidence_source,
    es.relationship AS evidence_source_relationship,
    ca.id AS assessment_id,
    ca.assessment_status,
    ca.actor_type AS assessment_actor_type,
    ca.actor_name AS assessment_actor_name,
    ca.assessment_role,
    ca.reasoning AS assessment_reasoning,
    ca.created_at AS assessment_created_at
   FROM ((((((public.claims c
     JOIN public.stories s ON ((s.id = c.story_id)))
     LEFT JOIN public.claim_evidence ce ON ((ce.claim_id = c.id)))
     LEFT JOIN public.evidence e ON ((e.id = ce.evidence_id)))
     LEFT JOIN public.evidence_sources es ON ((es.evidence_id = e.id)))
     LEFT JOIN public.sources src ON ((src.id = es.source_id)))
     LEFT JOIN LATERAL ( SELECT ca_1.id,
            ca_1.claim_id,
            ca_1.assessment_status,
            ca_1.actor_type,
            ca_1.actor_name,
            ca_1.reasoning,
            ca_1.created_at,
            ca_1.assessment_role
           FROM public.claim_assessments ca_1
          WHERE (ca_1.claim_id = c.id)
          ORDER BY ca_1.created_at DESC, ca_1.id DESC
         LIMIT 1) ca ON (true));


--
-- Name: claim_overview; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.claim_overview AS
 SELECT c.id AS claim_id,
    c.story_id,
    s.title AS story_title,
    s.story_type,
    s.status AS story_status,
    c.claim_text,
    c.claim_type,
    c.status AS claim_status,
    c.first_seen_at,
    c.last_checked_at,
    count(DISTINCT ce.evidence_id) AS evidence_count,
    count(DISTINCT
        CASE
            WHEN (es.relationship = 'producer'::text) THEN es.source_id
            ELSE NULL::bigint
        END) AS producer_count,
    count(DISTINCT
        CASE
            WHEN (es.relationship = 'issuer'::text) THEN es.source_id
            ELSE NULL::bigint
        END) AS issuer_count,
    count(DISTINCT
        CASE
            WHEN (es.relationship = 'publisher'::text) THEN es.source_id
            ELSE NULL::bigint
        END) AS publisher_count,
    latest.assessment_status AS latest_assessment_status,
    latest.actor_type AS latest_assessment_actor_type,
    latest.assessment_role AS latest_assessment_role,
    latest.created_at AS latest_assessment_at
   FROM ((((public.claims c
     JOIN public.stories s ON ((s.id = c.story_id)))
     LEFT JOIN public.claim_evidence ce ON ((ce.claim_id = c.id)))
     LEFT JOIN public.evidence_sources es ON ((es.evidence_id = ce.evidence_id)))
     LEFT JOIN LATERAL ( SELECT ca.assessment_status,
            ca.actor_type,
            ca.assessment_role,
            ca.created_at
           FROM public.claim_assessments ca
          WHERE (ca.claim_id = c.id)
          ORDER BY ca.created_at DESC, ca.id DESC
         LIMIT 1) latest ON (true))
  GROUP BY c.id, c.story_id, s.title, s.story_type, s.status, c.claim_text, c.claim_type, c.status, c.first_seen_at, c.last_checked_at, latest.assessment_status, latest.actor_type, latest.assessment_role, latest.created_at;


--
-- PostgreSQL database dump complete
--

\unrestrict Zuj5u7GbjZCWtrQakdI1Z8NzBihvdfHsvh5LhhYSms37elOGiFQymmlMA1Qpq3n
