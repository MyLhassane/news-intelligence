--
-- PostgreSQL database dump
--

\restrict 0CVaWsSMFzcSCtRt2cy2N4KeH43w7wfjdMwwpuWXGXQ6H2Ojac5hs8nNrf0ueIO

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

SET default_table_access_method = heap;

--
-- Name: article_evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.article_evidence (
    id bigint NOT NULL,
    article_id bigint NOT NULL,
    evidence_id bigint NOT NULL,
    relationship text NOT NULL,
    excerpt text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT article_evidence_relationship_check CHECK ((relationship = ANY (ARRAY['based_on'::text, 'quotes'::text, 'reports'::text, 'links_to'::text, 'mentions'::text, 'other'::text])))
);


--
-- Name: article_evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.article_evidence ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.article_evidence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: article_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.article_stories (
    id bigint NOT NULL,
    article_id bigint NOT NULL,
    story_id bigint NOT NULL,
    relation_type text DEFAULT 'coverage'::text NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    added_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT article_stories_relation_type_check CHECK ((relation_type = ANY (ARRAY['coverage'::text, 'update'::text, 'follow_up'::text, 'background'::text, 'analysis'::text, 'correction'::text, 'other'::text])))
);


--
-- Name: article_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.article_stories ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.article_stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.articles (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    feed_id bigint,
    title text NOT NULL,
    url text NOT NULL,
    author text,
    published_at timestamp with time zone,
    discovered_at timestamp with time zone DEFAULT now() NOT NULL,
    language text,
    content text,
    summary text,
    content_hash text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: articles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.articles ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.articles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: claim_assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.claim_assessments (
    id bigint NOT NULL,
    claim_id bigint NOT NULL,
    assessment_status text NOT NULL,
    actor_type text NOT NULL,
    actor_name text,
    reasoning text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    assessment_role text DEFAULT 'proposal'::text NOT NULL,
    CONSTRAINT claim_assessments_actor_check CHECK ((actor_type = ANY (ARRAY['human'::text, 'ai'::text, 'rule'::text, 'hybrid'::text]))),
    CONSTRAINT claim_assessments_role_check CHECK ((assessment_role = ANY (ARRAY['proposal'::text, 'review'::text, 'decision'::text]))),
    CONSTRAINT claim_assessments_status_check CHECK ((assessment_status = ANY (ARRAY['supported'::text, 'partially_supported'::text, 'contradicted'::text, 'unclear'::text])))
);


--
-- Name: claim_assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.claim_assessments ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.claim_assessments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: claim_evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.claim_evidence (
    id bigint NOT NULL,
    claim_id bigint NOT NULL,
    evidence_id bigint NOT NULL,
    relationship text NOT NULL,
    excerpt text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT claim_evidence_relationship_check CHECK ((relationship = ANY (ARRAY['supports'::text, 'contradicts'::text, 'context'::text, 'mentions'::text, 'unclear'::text])))
);


--
-- Name: claims; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.claims (
    id bigint NOT NULL,
    story_id bigint NOT NULL,
    claim_text text NOT NULL,
    claim_type text DEFAULT 'factual'::text NOT NULL,
    status text DEFAULT 'unverified'::text NOT NULL,
    first_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    last_checked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT claims_status_check CHECK ((status = ANY (ARRAY['unverified'::text, 'supported'::text, 'disputed'::text, 'contradicted'::text, 'partially_supported'::text, 'unclear'::text]))),
    CONSTRAINT claims_type_check CHECK ((claim_type = ANY (ARRAY['factual'::text, 'quote'::text, 'attribution'::text, 'prediction'::text, 'opinion'::text, 'statistical'::text, 'other'::text])))
);


--
-- Name: claim_evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.claim_evidence ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.claim_evidence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evidence (
    id bigint NOT NULL,
    type text NOT NULL,
    title text NOT NULL,
    url text NOT NULL,
    description text,
    published_at timestamp with time zone,
    accessed_at timestamp with time zone DEFAULT now() NOT NULL,
    language text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT evidence_type_check CHECK ((type = ANY (ARRAY['official_document'::text, 'government_statement'::text, 'court_record'::text, 'research_paper'::text, 'research_report'::text, 'statistical_data'::text, 'company_statement'::text, 'press_release'::text, 'transcript'::text, 'image'::text, 'video'::text, 'other'::text])))
);


--
-- Name: evidence_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evidence_sources (
    id bigint NOT NULL,
    evidence_id bigint NOT NULL,
    source_id bigint NOT NULL,
    relationship text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT evidence_sources_relationship_check CHECK ((relationship = ANY (ARRAY['producer'::text, 'publisher'::text, 'issuer'::text, 'participant'::text, 'author'::text, 'other'::text])))
);


--
-- Name: sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sources (
    id bigint NOT NULL,
    name text NOT NULL,
    country text,
    source_type text NOT NULL,
    website text,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT sources_type_check CHECK ((source_type = ANY (ARRAY['news_agency'::text, 'public_broadcaster'::text, 'private_broadcaster'::text, 'newspaper'::text, 'digital_news'::text, 'financial_news'::text, 'specialized_media'::text, 'fact_checking'::text, 'official_government'::text, 'international_organization'::text, 'research_institution'::text, 'regulatory_body'::text, 'court_or_legal_record'::text, 'company_primary'::text, 'social_media'::text, 'user_generated'::text, 'aggregator'::text, 'blog'::text, 'other'::text])))
);


--
-- Name: stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stories (
    id bigint NOT NULL,
    title text NOT NULL,
    summary text,
    story_type text,
    status text DEFAULT 'active'::text NOT NULL,
    first_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    last_updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT stories_status_check CHECK ((status = ANY (ARRAY['active'::text, 'closed'::text, 'archived'::text]))),
    CONSTRAINT stories_type_check CHECK (((story_type = ANY (ARRAY['breaking_news'::text, 'ongoing_event'::text, 'developing_story'::text, 'analysis'::text, 'investigation'::text, 'background'::text, 'other'::text])) OR (story_type IS NULL)))
);


--
-- Name: claim_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.claim_sources (
    id bigint NOT NULL,
    claim_id bigint NOT NULL,
    article_id bigint NOT NULL,
    relationship text NOT NULL,
    excerpt text,
    source_role text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT claim_sources_relationship_check CHECK ((relationship = ANY (ARRAY['supports'::text, 'contradicts'::text, 'reports'::text, 'quotes'::text, 'attributes'::text, 'questions'::text, 'unclear'::text]))),
    CONSTRAINT claim_sources_role_check CHECK (((source_role = ANY (ARRAY['primary'::text, 'secondary'::text, 'independent_observer'::text, 'expert'::text, 'eyewitness'::text, 'official_statement'::text, 'documentary'::text, 'aggregator'::text, 'other'::text])) OR (source_role IS NULL)))
);


--
-- Name: claim_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.claim_sources ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.claim_sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: claims_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.claims ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.claims_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.evidence ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.evidence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: evidence_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.evidence_sources ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.evidence_sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: source_feeds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_feeds (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    type text NOT NULL,
    url text NOT NULL,
    section text,
    language text,
    active boolean DEFAULT true NOT NULL,
    last_checked timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT source_feeds_type_check CHECK ((type = ANY (ARRAY['rss'::text, 'api'::text, 'website'::text, 'other'::text])))
);


--
-- Name: source_feeds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.source_feeds ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.source_feeds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: source_policies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_policies (
    id bigint NOT NULL,
    source_id bigint NOT NULL,
    policy_type text NOT NULL,
    description text NOT NULL,
    source_url text,
    verified_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT source_policies_type_check CHECK ((policy_type = ANY (ARRAY['editorial_standards'::text, 'corrections'::text, 'source_transparency'::text, 'conflicts_of_interest'::text, 'fact_checking'::text, 'anonymous_sources'::text, 'independence'::text, 'fact_opinion_separation'::text, 'other'::text])))
);


--
-- Name: source_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.source_policies ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.source_policies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.sources ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.stories ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: article_evidence article_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_evidence
    ADD CONSTRAINT article_evidence_pkey PRIMARY KEY (id);


--
-- Name: article_evidence article_evidence_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_evidence
    ADD CONSTRAINT article_evidence_unique UNIQUE (article_id, evidence_id, relationship);


--
-- Name: article_stories article_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_stories
    ADD CONSTRAINT article_stories_pkey PRIMARY KEY (id);


--
-- Name: article_stories article_stories_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_stories
    ADD CONSTRAINT article_stories_unique UNIQUE (article_id, story_id);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- Name: articles articles_source_url_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_source_url_unique UNIQUE (source_id, url);


--
-- Name: claim_assessments claim_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_assessments
    ADD CONSTRAINT claim_assessments_pkey PRIMARY KEY (id);


--
-- Name: claim_evidence claim_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_evidence
    ADD CONSTRAINT claim_evidence_pkey PRIMARY KEY (id);


--
-- Name: claim_evidence claim_evidence_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_evidence
    ADD CONSTRAINT claim_evidence_unique UNIQUE (claim_id, evidence_id, relationship);


--
-- Name: claim_sources claim_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_sources
    ADD CONSTRAINT claim_sources_pkey PRIMARY KEY (id);


--
-- Name: claim_sources claim_sources_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_sources
    ADD CONSTRAINT claim_sources_unique UNIQUE (claim_id, article_id, relationship);


--
-- Name: claims claims_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_pkey PRIMARY KEY (id);


--
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_pkey PRIMARY KEY (id);


--
-- Name: evidence_sources evidence_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_sources
    ADD CONSTRAINT evidence_sources_pkey PRIMARY KEY (id);


--
-- Name: evidence_sources evidence_sources_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_sources
    ADD CONSTRAINT evidence_sources_unique UNIQUE (evidence_id, source_id, relationship);


--
-- Name: evidence evidence_url_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_url_unique UNIQUE (url);


--
-- Name: source_feeds source_feeds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_feeds
    ADD CONSTRAINT source_feeds_pkey PRIMARY KEY (id);


--
-- Name: source_feeds source_feeds_unique_url; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_feeds
    ADD CONSTRAINT source_feeds_unique_url UNIQUE (source_id, url);


--
-- Name: source_policies source_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_policies
    ADD CONSTRAINT source_policies_pkey PRIMARY KEY (id);


--
-- Name: sources sources_name_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_name_unique UNIQUE (name);


--
-- Name: sources sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- Name: stories stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_pkey PRIMARY KEY (id);


--
-- Name: article_evidence article_evidence_article_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_evidence
    ADD CONSTRAINT article_evidence_article_fk FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: article_evidence article_evidence_evidence_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_evidence
    ADD CONSTRAINT article_evidence_evidence_fk FOREIGN KEY (evidence_id) REFERENCES public.evidence(id) ON DELETE CASCADE;


--
-- Name: article_stories article_stories_article_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_stories
    ADD CONSTRAINT article_stories_article_fk FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: article_stories article_stories_story_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article_stories
    ADD CONSTRAINT article_stories_story_fk FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: articles articles_feed_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_feed_fk FOREIGN KEY (feed_id) REFERENCES public.source_feeds(id) ON DELETE SET NULL;


--
-- Name: articles articles_source_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_source_fk FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE RESTRICT;


--
-- Name: claim_assessments claim_assessments_claim_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_assessments
    ADD CONSTRAINT claim_assessments_claim_fk FOREIGN KEY (claim_id) REFERENCES public.claims(id) ON DELETE CASCADE;


--
-- Name: claim_evidence claim_evidence_claim_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_evidence
    ADD CONSTRAINT claim_evidence_claim_fk FOREIGN KEY (claim_id) REFERENCES public.claims(id) ON DELETE CASCADE;


--
-- Name: claim_evidence claim_evidence_evidence_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_evidence
    ADD CONSTRAINT claim_evidence_evidence_fk FOREIGN KEY (evidence_id) REFERENCES public.evidence(id) ON DELETE CASCADE;


--
-- Name: claim_sources claim_sources_article_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_sources
    ADD CONSTRAINT claim_sources_article_fk FOREIGN KEY (article_id) REFERENCES public.articles(id) ON DELETE CASCADE;


--
-- Name: claim_sources claim_sources_claim_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claim_sources
    ADD CONSTRAINT claim_sources_claim_fk FOREIGN KEY (claim_id) REFERENCES public.claims(id) ON DELETE CASCADE;


--
-- Name: claims claims_story_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_story_fk FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: evidence_sources evidence_sources_evidence_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_sources
    ADD CONSTRAINT evidence_sources_evidence_fk FOREIGN KEY (evidence_id) REFERENCES public.evidence(id) ON DELETE CASCADE;


--
-- Name: evidence_sources evidence_sources_source_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_sources
    ADD CONSTRAINT evidence_sources_source_fk FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE RESTRICT;


--
-- Name: source_feeds source_feeds_source_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_feeds
    ADD CONSTRAINT source_feeds_source_fk FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE CASCADE;


--
-- Name: source_policies source_policies_source_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_policies
    ADD CONSTRAINT source_policies_source_fk FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 0CVaWsSMFzcSCtRt2cy2N4KeH43w7wfjdMwwpuWXGXQ6H2Ojac5hs8nNrf0ueIO
