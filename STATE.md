# Capstone-Agents-MVP — STATE

Single source of truth for current project state. Update **before** ending any session.
Last updated: 2026-05-06

## 🎯 Current state

**Phase:** Phase 1 — Project plug-in (just opened)

The project exists as a Kaggle capstone (badge issued 2025-12-18). Repo on GitHub. Today (2026-05-06) plugged into DK AI LAB ecosystem alongside Legal Angel / Legal Expert / TMGG / DK_AI_LAB_Landing / HardwareHunter as project #6.

**What works right now:**
- 5-agent pipeline runs locally via `python main.py` on Daniil's machine (verified during Kaggle run)
- Outputs `output/analysis_report.html` with executive summary + anomalies + trends + recommendations + critic review
- Config-driven via `config/analysis_settings.json` — switching dataset = config edit, not code change

**What does NOT work yet:**
- No frontend (currently CLI only — runs only via terminal)
- No deployment (no public URL)
- No persistent storage (every analysis is one-off, no anomaly DB)

## 🔄 In progress

- Phase 1 — Project plug-in (this session)

## ⏳ Up next (in priority order)

1. **Save introduction entry to vector memory** — so all other agents in ecosystem know about new project
2. **Add product card data to dklab.studio products registry** — registry-only for now, card goes live after Phase 3 deploy
3. **Phase 2 — frontend MVP**: decide stack (Streamlit vs Next.js + FastAPI), build drag-drop UI
4. **Phase 3 — deploy**: subdomain, VPS, HTTPS

## 🗂 Backlog

- Phase 4: anomaly persistence + pattern recognition over time + cross-dataset correlation (from README future roadmap)
- API rate limit handling — Gemini free tier won't sustain heavy public traffic. Plan paid tier or request queueing for production.
- Cost ceiling per analysis — currently unbounded. Need per-run budget cap before public deploy.
- Auth on public deploy — anonymous use will burn API quota. Need at minimum email gate or own-key input.

## 📌 Decisions worth remembering

- **Repo stays public.** Kaggle capstone requirement. Don't switch to private without weighing impact on capstone visibility.
- **Gemini, not Anthropic, for this project.** Capstone was on Gemini per Google × Kaggle program. Don't swap to Sonnet "to be consistent with rest of stack" — would invalidate the capstone story.
- **Filepath passing is core architecture, not optimization.** It's what makes 10K+ row datasets feasible. Don't refactor agents to pass dataframes directly.
- **Critic agent is the moat.** Most multi-agent demos skip self-review. Keep it. It's also the most interesting talking point at interviews.
- **Project tag in memory:** `capstone_agents` (lowercase, underscore).

## ❌ Anti-patterns (don't propose)

- Switching LLM provider mid-project (Gemini → Anthropic). Capstone stays on Gemini.
- Adding more agents "because we can". Five is balanced. Sixth requires clear new responsibility, not "another opinion".
- Using FastAPI + Next.js for frontend if Streamlit can do it in 1/5 the time. MVP first, then scale.
- Deploying without a budget cap on Gemini API. Free tier is throttled but PAID tier with no cap = open wallet.

## 🛠 Technical reference

| | |
|---|---|
| **Path** | `C:\Projects_Local\Capstone-Agents-MVP` |
| **GitHub** | `https://github.com/Codedkv/capstone-agents-mvp` (public) |
| **Kaggle notebook** | `https://www.kaggle.com/code/daniilkiliakou/notebook0fefd2e146` |
| **Language** | Python 3.10+ |
| **LLM** | Google Gemini 2.5 Flash |
| **Key env vars** | `GOOGLE_API_KEY` / `GEMINI_API_KEY` (in `.env`, NEVER commit) |
| **Run command** | `python main.py` from project root |
| **Output** | `output/analysis_report.html` |
| **Project tag (memory)** | `capstone_agents` |

## How to use this file

When Daniil mentions the project ("продолжаем capstone", "что в агентах", "давай к analytics" or any natural reference) — **read this file first** via Desktop Commander, then summarize state and ask what to do next.

Update **before ending session**:
- Mark completed items in TODO (in CLAUDE.md, not here — keep STATE.md focused on snapshot, CLAUDE.md tracks task ledger)
- Add new decisions to "Decisions worth remembering"
- Add new anti-patterns if Daniil rejects an approach
- Update "What works / what does NOT" if state changes
