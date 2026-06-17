# AI Coding Agent Instructions

This file defines the working rules for AI coding agents contributing to MarketPulse AI.

## Communication Style

When explaining code or project decisions:
- Explain clearly in Vietnamese.
- Be concise and practical.
- Do not over-explain with unnecessary theory.
- Use simple examples from this project.
- When giving commands, explain briefly what each command does in Vietnamese.

## Critical Inception Rules
- **Always read**: `README.md`, `SPEC.md`, `TASKS.md`, `AGENTS.md`, and `LEARNING_LOG.md` before writing any code.
- **Always plan first**: Create or update the `implementation_plan.md` artifact in the brain, request feedback, and wait for confirmation before implementing any code.
- **Keep scope strict**: Strictly implement the current module only. Do not build ahead or guess requirements.

## Working Rules

- Keep changes small, focused, and easy to review.
- Do not build features outside the current task.
- Do not add secrets, API keys, tokens, private credentials, or local `.env` values. Keep all keys in `.env` only (never committed to git).
- Do not create fake results, fake metrics, fake citations, or synthetic success logs unless the user explicitly asks for mock data.
- Do not over-engineer simple tasks.
- Prefer simple, readable Python/TypeScript over clever shortcuts.
- Keep each file focused on one purpose.
- Add dependencies only when they are required for the current module.
- Preserve existing behavior unless the task asks to change it.
- Update documentation when setup, commands, or behavior change.
- Never commit generated raw, processed, analytics, or log files (e.g. check `.gitignore`).

## Architectural Boundaries

- **No Streamlit Expansion**: Do not build Streamlit features unless explicitly requested. Streamlit is now just a minimal internal skeleton.
- **No Primary Power BI UI**: Do not make Power BI the main product UI. It is an optional compatibility target through CSV exports.
- **Order of Frontend & API**: Do not build the web dashboard (Next.js) before the analytics metrics data mart and FastAPI backend are ready.
- **Order of AI Insights**: Do not integrate Gemini or any LLM API before the rule-based insight generation logic is completed and verified.
- **No Direct LLM UI Calls**: Do not call LLM APIs directly from the frontend. All AI generations must go through the FastAPI backend API layer.

## Development Flow

1. Confirm the task scope.
2. Read all documentation (`README.md`, `SPEC.md`, `TASKS.md`, `AGENTS.md`, `LEARNING_LOG.md`).
3. Formulate a plan, write `implementation_plan.md`, and wait for user approval.
4. Inspect only the files needed for the task.
5. Make the smallest correct change.
6. Run the lightest useful verification command (`pytest` and relevant e2e scripts).
7. Report files changed, checks run, and remaining risks.

## Verification Commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run data ingestion:

```bash
python -m src.collectors.run_ingestion
```

Run ETL process:

```bash
python -m src.processing.run_etl
```

Run the FastAPI backend (when implemented):

```bash
uvicorn src.api.main:app --reload
```

## Definition of Done

A task is done only when:

- The requested behavior is implemented.
- The change is limited to the agreed scope.
- The project still runs.
- Relevant tests (`pytest`) and end-to-end execution commands pass cleanly.
- Documentation is updated when needed.
- No secrets are added.
- No fake results are introduced.
- No unnecessary abstraction or over-engineering is added.


