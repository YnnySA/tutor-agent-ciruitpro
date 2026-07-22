# Copilot instructions for this repository

## Build, test, and lint commands

Use Python 3.11 (matches CI) and install both runtime and dev dependencies:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Run the app locally:

```bash
streamlit run Chatbot.py
```

Run tests:

```bash
pytest -v --junit-xml=test-results.xml
```

Run a single test:

```bash
pytest -v app_test.py::test_Chatbot
```

Lint and format:

```bash
ruff check .
ruff format .
```

Optional (configured hooks):

```bash
pre-commit run --all-files
```

## MCP servers

- Playwright MCP is configured in `.vscode/mcp.json` as `playwright` using `npx -y @playwright/mcp@latest`.
- Use it for browser automation and UI validation of the Streamlit app flows.

## High-level architecture

- This is a Streamlit multipage app. `Chatbot.py` is the root app and `pages/` contains additional examples discovered by Streamlit.
- Each page in `pages/` is a self-contained LLM example (Anthropic file Q&A, LangChain search agent, LangChain quickstart, PromptTemplate, and Trubrics feedback flow).
- Chat-oriented pages keep conversation state in `st.session_state["messages"]` and render it with `st.chat_message(...)`.
- Tests in `app_test.py` use `streamlit.testing.v1.AppTest` to execute app scripts directly, and `unittest.mock.patch` to mock provider calls.
- CI (`.github/workflows/app-testing.yml`) runs on Python 3.11 and uses Streamlit's app action with Ruff and Pytest args.

## Key conventions in this codebase

- Keep each demo page as a single-file, executable Streamlit example instead of adding shared app abstractions.
- Put provider keys in the sidebar via `st.text_input(..., type="password")`; for chat examples use stable widget keys (for example `chatbot_api_key`, `feedback_api_key`) to avoid collisions.
- Gate model calls on missing credentials with `st.info("Please add ... API key to continue.")`; in chat flows this is followed by `st.stop()` before any API request.
- For chat UIs, represent each message as a dict with `role` and `content`, append to session state, and render user and assistant messages in order.
- Keep `pages/` filenames prefixed with numbers (`1_...`, `2_...`) to preserve sidebar order in Streamlit multipage navigation.
