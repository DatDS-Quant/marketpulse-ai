# Learning Log

Use this file to track what was learned while building MarketPulse AI.

## Module 0 - Project Operating System

Date: 2026-06-16

What was created:

- A clean Python project structure.
- Documentation for setup, scope, and development rules.
- A minimal Streamlit app.
- A smoke test for package imports.

What to understand before Module 1:

- Why a stable project structure matters.
- How `requirements.txt` and `pyproject.toml` support reproducible development.
- How `pytest` discovers and runs tests.
- How Streamlit runs an app from `app/main.py`.
- Why secrets belong in `.env`, not in git.


## Module 1 - Data Ingestion

Date: 2026-06-17

What I built:
- RSS collector for Google News
- Sample data fallback mechanism
- JSON normalization schema
- Structured logging to JSONL

What I learned:
- Working with the feedparser library.
- The importance of stable hashing (SHA-256) for generating deterministic IDs.
- How to structure fallback mechanisms that gracefully degrade.

Bugs and fixes:
- None encountered yet.

Interview explanation:
- Built the ingestion layer first because data is the foundation of the platform. Used RSS as an accessible source, decoupled collection from storage to keep things simple, and introduced fallback data to ensure the demo works reliably anywhere.

## Module 2 - ETL & Data Quality

Date: 2026-06-17

What I built:
- Pydantic models for data schema validation
- Data cleaning logic for handling missing values and text truncation
- Data quality reporting to track missing/invalid fields
- Deduplication logic to ensure idempotency

What I learned:
- How to separate pure logic (cleaning) from business rules (validation) and orchestration (ETL script).
- Leveraging Pydantic for strict typing and validation while applying flexible rules before instantiation.

Bugs and fixes:
- The `test_valid_raw_record` test originally failed because `content_length` became 30 when adding a valid summary to fix a quality flag. Fixed by explicitly defining expected content length in test assertions.

Trade-offs:
- Used Python standard library for basic date parsing and logging instead of importing heavy frameworks, which keeps the ETL pipeline extremely fast and beginner-friendly, but might lack advanced timezone edge-case handling.

Interview explanation:
- I implemented a lightweight ETL layer that bridges data ingestion and intelligence. The focus is on robust data quality: we don't just silently drop bad data, but we track metrics (missing titles, invalid URLs) via quality flags and reports. This creates an auditable data pipeline necessary for reliable AI outputs.

## Strategic Roadmap Update

Date: 2026-06-18

### Pivot Rationale
- **Why a Professional Web BI Dashboard?** Streamlit and Power BI are excellent for prototyping and standalone business analytics, but they do not scale well as customizable SaaS products. To deliver a unified, premium, and highly responsive user experience, we are transitioning to a dedicated web application stack (FastAPI backend and Next.js frontend). This ensures maximum control over custom UI components, responsive charts, and interactive AI grounding workflows.
- **Why is Power BI Export Optional?** Many enterprise users still require the ability to run custom ad-hoc analyses. Keeping Power BI compatibility via clean CSV exports guarantees interoperability without locking the main product interface into Microsoft's ecosystem.
- **Why Rule-Based Fallback for AI Insights?** Relying purely on LLM APIs creates single points of failure (network drops, API rate limits, pricing constraints, or key configuration errors). A rule-based fallback ensures that the dashboard remains fully functional and informative, generating deterministic analytical insights even when `GEMINI_API_KEY` is not provided.
- **Why Gemini/API Integration Only After Analytics Metrics Stability?** LLMs are highly dependent on the quality and structure of their input context. Integrating LLMs before analytics tables and trend calculation scores are fully mature would result in brittle prompts, excessive hallucinations, and frequent schema updates. Stabilizing the math first guarantees that the AI has clean, validated, and structured evidence to summarize.

## Module 3 - Analytics Data Mart

Date: 2026-06-18

What I built:
- Analytics data mart runner converting processed JSON logs to clean CSV files.
- Daily keyword metrics aggregation computing rates and data quality score.
- Source metrics aggregation for source quality analysis.
- Deterministic, rule-based insight seeds generation to ground future AI models.

What I learned:
- How to efficiently map error flags (list of strings) into Boolean feature columns in pandas.
- The value of separating data ingestion schemas (Pydantic) from analytical aggregations (pandas DataFrame).
- Standardizing and clamping derived quality scores (0 to 100) based on simple penalty math instead of complex black-box logic.

Bugs and fixes:
- The boolean flags returned by pandas (`numpy.bool_`) broke native python `assert X is True` checks in pytest. This was fixed by explicitly casting them to standard `bool()`.
- Floating point inaccuracies caused tests checking `1/3` to fail against `0.3333`. This was fixed by using a bounded tolerance check (`abs(val - target) < 0.001`).

Trade-offs:
- Decided to compute scores explicitly within Python/pandas instead of relying on a database engine like SQLite/DuckDB. This keeps dependencies low, eliminates schema migration issues for now, and fulfills the Power BI CSV requirements perfectly.

Interview explanation:
- For this module, I focused on building the foundational analytical layer. I converted the raw pipeline data into structured, multi-dimensional tables (articles, keywords, sources). Instead of jumping straight to LLMs, I built deterministic insight seeds and calculated transparent quality scores. This ensures any downstream dashboard or AI generator has mathematically sound facts to rely on, preventing hallucinations.

## Module 4 - Trend Detection & Insight Metrics

Date: 2026-06-18

What I built:
- A deterministic trend scoring engine calculating volume, growth, source diversity, quality, and freshness scores.
- A signal classification module to tag keywords (e.g., `rising_keyword`, `high_volume_keyword`, `stale_data_warning`).
- A top trends ranking mechanism providing structured explanation seeds for downstream LLM/Dashboard ingestion.
- Comprehensive `pytest` coverage validating mathematical bounds and avoiding division-by-zero edge cases.

What I learned:
- Leveraging pandas vectorized operations (`groupby`, `shift`, `transform`, `clip`) simplifies complex window calculations and ensures robust fallback behaviors.
- The importance of mathematically clamping scores (0 to 100) to keep indicators predictable and visually uniform on a dashboard.
- How to strictly separate insight rule-based fallbacks (generating summary explanation seeds) from stochastic LLM calls.

Bugs and fixes:
- The initial testing logic assumed the highest overall count would rank first, but an edge case keyword (`content automation`) with 0 previous articles experienced a 12.0x growth rate, legitimately pushing it to rank 1 via the growth_score constraint. Fixed by updating the test assertion to correctly reflect the mathematical truth.

Trade-offs:
- Decided to compute metrics sequentially on `daily_keyword_metrics.csv` instead of using a time-series forecasting model. This prevents black-box AI logic, keeps the pipeline highly deterministic, and allows exact auditing of why a keyword spiked.

Interview explanation:
- For this module, I built the Trend Detection core entirely using deterministic math. I deliberately avoided introducing LLMs or heavy ML forecasting models here. By calculating precise, bounded scores for growth, volume, and data freshness using Pandas, we guarantee that the upcoming Web Dashboard and AI Insights generator will be driven by validated, auditable, and interpretable market facts rather than black-box assumptions.

## Module 5 - FastAPI Analytics API

Date: 2026-06-19

What I built:
- A high-performance REST API backend using FastAPI.
- Endpoints serving trend metrics, source tracking, system health, and chart data formats.
- Pydantic models designed specifically for generating UI-friendly chart configurations.
- API integration tests using `TestClient`.

What I learned:
- How to structure backend responses to make frontend chart rendering extremely simple, by passing down `ChartConfig` metadata.
- Using FastAPI `yield` dependencies to safely provide mock data if CSV/JSON metrics are missing or unavailable.

Bugs and fixes:
- CORS needed to be configured to allow Next.js on `localhost:3000` to fetch data. Fixed by adding `CORSMiddleware`.

Interview explanation:
- For this module, I built a bridging API layer using FastAPI. Rather than having the frontend tightly coupled to a database or reading raw files, I structured the API to act as a "Presenter". It returns pre-formatted chart data, meaning the frontend only needs to render components without computing aggregations. This decoupled architecture allows us to easily scale the backend processing independently from the web dashboard.

## Module 6 - Professional Web BI Dashboard

Date: 2026-06-19

What I built:
- A full-stack Next.js application (App Router) using Tailwind CSS v4 and TypeScript.
- A modern, dark-mode intelligence console designed for high-level business metrics.
- Recharts visualizations for top market trends and historical tracking.
- Client-side data fetching directly interacting with the FastAPI backend.

What I learned:
- Working with Tailwind v4 requires slightly different global config than v3, but simplifies theming significantly.
- Strict React hooks rules require careful state management, particularly when combining data fetching (`loading` state changes) within `useEffect`.
- `Recharts` is highly effective when paired with backend-driven configurations, eliminating the need to write custom chart logic for every endpoint.

Bugs and fixes:
- The initial `npm install` encountered `ECONNRESET` issues likely due to registry instability. Fixed by enforcing standard npm registry and cleaning cache.
- Strict ESLint and TypeScript rules caught `any` type usage and synchronous state updates in `useEffect`. Fixed by enforcing proper `Record<string, unknown>` interfaces and removing redundant state calls.

Interview explanation:
- In Module 6, I completed the product vision by building a fully interactive Next.js dashboard. The key architectural decision here was to maintain strict separation of concerns: the Next.js app handles zero business logic. It simply fetches JSON from FastAPI and dynamically maps it to KPI cards and Recharts components. This makes the frontend extremely lightweight and allows the UI to stay perfectly synchronized with the underlying Python analytical engine.
# #   M o d u l e   6   -   M u l t i - p a g e   B I   C o n s o l e   R e f a c t o r i n g 
 
 D a t e :   2 0 2 6 - 0 6 - 1 9 
 
 W h a t   I   b u i l t : 
 -   R e f a c t o r e d   t h e   s i n g l e - p a g e   N e x t . j s   d a s h b o a r d   i n t o   a   p r o f e s s i o n a l ,   6 - p a g e   M a r k e t   I n t e l l i g e n c e   C o n s o l e   ( O v e r v i e w ,   T r e n d s ,   S o u r c e s ,   E v i d e n c e ,   I n s i g h t s ,   S y s t e m ) . 
 -   I m p l e m e n t e d   a   c l e a n   S i d e b a r N a v   u s i n g   N e x t . j s   A p p   R o u t e r . 
 -   R e f i n e d   I n s i g h t   C a r d s   t o   s e p a r a t e   F a c t u a l   E x p l a n a t i o n ,   L i m i t a t i o n s ,   a n d   P r a c t i c a l   N e x t   S t e p s ,   p r e v e n t i n g   h a l l u c i n a t i o n s . 
 -   A d d e d   M e t r i c E x p l a i n e r s   t o   e d u c a t e   u s e r s   o n   d a t a   d e r i v a t i o n . 
 -   F i x e d   m a p p i n g   i s s u e s   b e t w e e n   t h e   b a c k e n d   a r t i c l e   s c h e m a   a n d   t h e   f r o n t e n d   E v i d e n c e   t a b l e . 
 
 W h a t   I   l e a r n e d : 
 -   B r e a k i n g   a   d e n s e   d a s h b o a r d   i n t o   a   m u l t i - p a g e   s t o r y   s i g n i f i c a n t l y   i m p r o v e s   r e a d a b i l i t y   a n d   u s e r   f o c u s . 
 -   A   w e l l - s t r u c t u r e d   A P I   r e s p o n s e   ( c h a r t _ c o n f i g )   m a k e s   m i g r a t i n g   c h a r t s   a c r o s s   p a g e s   s e a m l e s s . 
 -   H a n d l i n g   e m p t y / f a l l b a c k   s t a t e s   g r a c e f u l l y   a c r o s s   m u l t i p l e   p a g e s   i s   c r u c i a l   f o r   a   p r o f e s s i o n a l   f e e l . 
# #   M o d u l e   6   -   M u l t i - p a g e   B I   C o n s o l e   R e f a c t o r i n g 
 
 D a t e :   2 0 2 6 - 0 6 - 1 9 
 
 W h a t   I   b u i l t : 
 -   R e f a c t o r e d   t h e   s i n g l e - p a g e   N e x t . j s   d a s h b o a r d   i n t o   a   p r o f e s s i o n a l ,   6 - p a g e   M a r k e t   I n t e l l i g e n c e   C o n s o l e   ( O v e r v i e w ,   T r e n d s ,   S o u r c e s ,   E v i d e n c e ,   I n s i g h t s ,   S y s t e m ) . 
 -   I m p l e m e n t e d   a   c l e a n   S i d e b a r N a v   u s i n g   N e x t . j s   A p p   R o u t e r . 
 -   R e f i n e d   I n s i g h t   C a r d s   t o   s e p a r a t e   F a c t u a l   E x p l a n a t i o n ,   L i m i t a t i o n s ,   a n d   P r a c t i c a l   N e x t   S t e p s ,   p r e v e n t i n g   h a l l u c i n a t i o n s . 
 -   A d d e d   M e t r i c E x p l a i n e r s   t o   e d u c a t e   u s e r s   o n   d a t a   d e r i v a t i o n . 
 -   F i x e d   m a p p i n g   i s s u e s   b e t w e e n   t h e   b a c k e n d   a r t i c l e   s c h e m a   a n d   t h e   f r o n t e n d   E v i d e n c e   t a b l e . 
 
 W h a t   I   l e a r n e d : 
 -   B r e a k i n g   a   d e n s e   d a s h b o a r d   i n t o   a   m u l t i - p a g e   s t o r y   s i g n i f i c a n t l y   i m p r o v e s   r e a d a b i l i t y   a n d   u s e r   f o c u s . 
 -   A   w e l l - s t r u c t u r e d   A P I   r e s p o n s e   ( c h a r t _ c o n f i g )   m a k e s   m i g r a t i n g   c h a r t s   a c r o s s   p a g e s   s e a m l e s s . 
 -   H a n d l i n g   e m p t y / f a l l b a c k   s t a t e s   g r a c e f u l l y   a c r o s s   m u l t i p l e   p a g e s   i s   c r u c i a l   f o r   a   p r o f e s s i o n a l   f e e l . 
 
 B u g s   a n d   f i x e s : 
 -   T h e   E v i d e n c e   t a b l e   p r e v i o u s l y   s h o w e d   ' - '   f o r   M a t c h e d   E n t i t y   b e c a u s e   i t   w a s   m a p p e d   t o     r t i c l e . m a t c h e d _ k e y w o r d s .   I   f i x e d   t h i s   b y   i n s p e c t i n g   t h e   C S V   s c h e m a   a n d   m a p p i n g   i t   a c c u r a t e l y   t o     r t i c l e . k e y w o r d . 
 -   T h e   S o u r c e s   c h a r t   m a p p e d   r e l i a b i l i t y   s c o r e s   i n c o r r e c t l y   f o r   s c o r e   b o u n d s   ( 0 - 1 0 0   i n s t e a d   o f   0 - 1 ) .   I   c o r r e c t e d   t h e   t h r e s h o l d   m a p p i n g   t o   u s e   \ s o u r c e _ q u a l i t y _ s c o r e \   n a t i v e l y . 
 
 I n t e r v i e w   e x p l a n a t i o n : 
 -   F o r   t h e   f i n a l   p h a s e   o f   M o d u l e   6 ,   I   t r a n s f o r m e d   t h e   i n i t i a l   p r o t o t y p e   d a s h b o a r d   i n t o   a   p o l i s h e d ,   r e c r u i t e r - f a c i n g   m u l t i - p a g e   B I   C o n s o l e .   R a t h e r   t h a n   d u m p i n g   a l l   d a t a   o n   o n e   p a g e ,   I   s t r u c t u r e d   i t   l o g i c a l l y   s o   e a c h   p a g e   a n s w e r s   a   s p e c i f i c   b u s i n e s s   q u e s t i o n :   ' W h a t   a r e   t h e   t r e n d s ? ' ,   ' A r e   t h e   s o u r c e s   r e l i a b l e ? ' ,   ' W h a t ' s   t h e   e v i d e n c e ? ' .   I   a l s o   s t r i c t l y   m a i n t a i n e d   t h e   b a r r i e r   b e t w e e n   d e t e r m i n i s t i c   a n a l y t i c a l   i n s i g h t s   a n d   s p e c u l a t i v e   A I   t o   e n s u r e   a b s o l u t e   t r u s t   i n   t h e   d a t a .  
 
## Module 9 - Evaluation, Quality Gates & Observability

Date: 2026-06-20

What I built:
- A lightweight, deterministic local evaluation layer evaluating data quality, pipeline health, and insight quality.
- Defined Quality Gates that return PASS, WARN, or FAIL statuses.
- A FastAPI endpoint `/api/v1/evaluation/summary` to serve evaluation summaries safely.
- `pytest` unit testing checking logic without depending on live generated data.

What I learned:
- Graceful error handling (returning None and dealing with it properly) ensures an evaluation layer never crashes the main pipeline.
- Strict bounding of evaluation conditions (banned phrases, threshold logic) offers a deterministic baseline for AI outputs.
- Maintaining separation of concerns allows us to evaluate everything from raw ingestion up to AI insights without entangling business logic.

Bugs and fixes:
- Ensured timestamps are safely parsed even when crossing timezones by strictly utilizing UTC for difference calculations.

Interview explanation:
- In Module 9, I built the observability and evaluation layer. Instead of adding heavy components like MLflow or Prometheus at this stage, I focused on high-value, deterministic pipeline health checks: are the files there, is the data fresh, are there any banned phrases generated by AI? This approach acts as a robust Quality Gate for recruiters or stakeholders to visually confirm that the pipeline is currently healthy and the AI outputs are secure.
### Module 8: Evidence Retrieval
- **Learned**: Implemented deterministic lexical retrieval system for evidence grounding without using embeddings or vector databases.
- **Learned**: Strict separation of generated output files from tracked repository files using .gitignore.
- **Decision**: Built a custom scoring mechanism that incorporates keyword matching, source quality, and recency for retrieving reliable citations.

### Module 8B: Lightweight RAG
- **Learned**: Designing a localized RAG system without vector databases relies heavily on robust lexical fallback scoring.
- **Learned**: Graceful error handling (503 Service Unavailable) is critical in AI pipelines when preceding dependencies fail.
- **Decision**: Implemented an explicit safety checker that immediately defaults to a safe rule-based answer if the AI attempts to forecast revenue, use banned promotional phrases, or hallucinate citations.
