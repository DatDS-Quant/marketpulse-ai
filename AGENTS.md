# AI Coding Agent Instructions

This file defines the working rules for AI coding agents contributing to MarketPulse AI.

## Communication Style

When explaining code or project decisions:
- Explain clearly in Vietnamese.
- Be concise and practical.
- Do not over-explain with unnecessary theory.
- Use simple examples from this project.
- When giving commands, explain briefly what each command does in Vietnamese.

## Working Rules

- Keep changes small, focused, and easy to review.
- Do not build features outside the current task.
- Do not add secrets, API keys, tokens, private credentials, or local `.env` values.
- Do not create fake results, fake metrics, fake citations, or synthetic success logs unless the user explicitly asks for mock data.
- Do not over-engineer simple tasks.
- Prefer simple, readable Python over clever shortcuts.
- Keep each file focused on one purpose.
- Add dependencies only when they are required for the current module.
- Preserve existing behavior unless the task asks to change it.
- Update documentation when setup, commands, or behavior change.

## Development Flow

1. Confirm the task scope.
2. Inspect only the files needed for the task.
3. Make the smallest correct change.
4. Run the lightest useful verification command.
5. Report files changed, checks run, and remaining risks.

## Verification Commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run the Streamlit app:

```bash
streamlit run app/main.py
```

## Definition of Done

A task is done only when:

- The requested behavior is implemented.
- The change is limited to the agreed scope.
- The project still runs.
- Relevant tests or checks pass, or any inability to run them is clearly reported.
- Documentation is updated when needed.
- No secrets are added.
- No fake results are introduced.
- No unnecessary abstraction or over-engineering is added.

