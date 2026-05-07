# Capstone-Agents-MVP — CLAUDE.md

> ⚠️ READ THIS FIRST. ENTIRELY. BEFORE WRITING A SINGLE LINE OF CODE.
> This file is the source of truth for this project.

> **Public brand:** Outlier
> **Planned domain:** outlier.dklab.studio
> **Internal/repo name:** Capstone-Agents-MVP (kept for Kaggle traceability — don't rename repo)

## What This Is

**Outlier** — multi-agent business analytics system. Config-driven 5-agent pipeline on Google Gemini 2.5 Flash that automates end-to-end business data analysis: ingestion → anomaly detection → trend analysis → strategic recommendations → critical review. Built as capstone for the Google × Kaggle 5-Day AI Agents Intensive 2025 (badge issued December 18, 2025).

**Why "Outlier":** the system's core analytical method (IQR-based anomaly detection) is literally outlier detection. Naming the product after its primary tool makes the function self-evident.

**Status:** working MVP. Runs locally via `python main.py`, ingests XLSX/CSV, outputs HTML report with executive summary + anomalies + recommendations + critic review.

**Current state:** Phase 1 (plug-in) and Phase 2 backend done. FastAPI app in `backend/` exposes 6 endpoints (upload / run / SSE events / report / cancel / health), single-worker queue, BYOK API-key model, slowapi rate-limiting. Pipeline E2E validated on `data/test_ecommerce.csv` (regression fixture, 30d × 8 SKU, 6 planted anomalies, baseline 3/6 recall). Frontend (`frontend/`) and deploy still pending.

GitHub: https://github.com/Codedkv/capstone-agents-mvp (public)
Kaggle notebook: https://www.kaggle.com/code/daniilkiliakou/notebook0fefd2e146

## Owner

Daniil, solo developer/architect in Poznań, Poland (DK AI LAB).
Architect-level — don't explain code, just do it.

## Communication Rules

- **Language:** Russian for conversation, English for ALL code/comments/variables/commits
- **Be direct** — no flattery, no sugarcoating, no filler
- **Comment on ALL user's points** — never skip parts of the message
- **Warn about pitfalls** — think through edge cases and warn before coding
- **No silent fallbacks** — if something breaks, throw error. User must know.
- **No hardcoded hacks** — fix root causes, not symptoms
- **Minimize user's manual work** — do it instead of asking
- **Concise responses** — no code explanations unless asked
- **NEVER commit** without explicit user approval
- **NEVER deploy** without explicit "deploy" command
- **No unsolicited changes** — only do what's explicitly asked
- **NEVER hardcode secrets** — env vars or credential store only

## Coding Discipline

- **No TODO, no placeholder code** — write complete, working files. No `// implement later`, no stub functions. If you can't finish, stop and ask, don't fake completion.
- **Before coding: state 3 key decisions and locked assumptions** — name the architectural choices and what you're assuming about input/data/edge cases. THEN write code.
- **Ambiguous request = one sharp question, then build** — don't fire off 5 clarifying questions. Pick the single most important blocker, ask it, then proceed.

## Ecosystem Context

You are project #6 in DK AI LAB. The others:

| # | Project | Path | What it is |
|---|---------|------|------------|
| 1 | Legal Angel | `C:\Projects_Local\LegaLAngel_Next` | Immigration SaaS (Next.js + MUI + Supabase) |
| 2 | Legal Expert | `C:\Projects_Local\LegalExpert` | AI legal expert with RAG (Next.js + pgvector) |
| 3 | TMGG | `C:\Projects_Local\TMGG` | Button football tournament app (Next.js + Tailwind + shadcn) |
| 4 | DK AI LAB Landing | `C:\Projects_Local\DK_AI_LAB_Landing` | Studio landing page at dklab.studio (Next.js 16 + Tailwind 4, EN/RU/PL) |
| 5 | HardwareHunter | `C:\Projects_Local\HardwareHunter` | n8n automation: hardware deals monitor (OLX/Allegro/IMAP → Haiku AI → Telegram) |
| 6 | Capstone-Agents-MVP | `C:\Projects_Local\Capstone-Agents-MVP` | **THIS PROJECT** — 5-agent Gemini-powered business analytics system |

Look at other projects for patterns. Do NOT modify them.

Shared infrastructure:
- **MCP Memory**: shared Supabase at `hcupfxtqrvswiglojqvn` — ALL projects read/write here
- **Servers**: Hetzner CX23 (46.225.128.70, Legal Angel + TMGG), Hetzner CAX21 (89.167.102.62, Legal Expert), CX22 (188.245.89.60, dklab.studio)
- **n8n (work)**: n8n.legalangel.help — Legal Angel workflows
- **n8n (personal)**: n8n.codedkv.xyz — personal projects (HardwareHunter)

## Infrastructure

- **VPS:** TBD — to be deployed alongside dklab.studio infra (CX22 188.245.89.60) or separate small instance
- **Domain:** TBD — planned subdomain on dklab.studio (e.g. `agents.dklab.studio`, `analyze.dklab.studio` — name TBD)
- **DB:** None currently. Future Phase 3 (anomaly persistence) will use PostgreSQL — likely Supabase or local Postgres on the deploy VPS.
- **Stack (current MVP):**
  - Language: Python 3.10+
  - LLM: Google Gemini 2.5 Flash via `google-generativeai`
  - Data: pandas, openpyxl, PyPDF2
  - Validation: pydantic
  - Output: HTML with CSS styling
- **Stack (frontend, decided 2026-05-07):** Next.js 16 + Tailwind 4 + Geist + next-intl, dark theme inherited from DK_AI_LAB_Landing, **orange accent** instead of lab's lime (Outlier as product differentiator within the lab brand family). Backend is FastAPI (`backend/`, already shipped).
- **GitHub:** https://github.com/Codedkv/capstone-agents-mvp (public — Kaggle requirement)
- **API key for Gemini:** stored locally in `.env` as `GOOGLE_API_KEY` / `GEMINI_API_KEY`. NEVER commit. NOT in shared MCP memory env (different from Voyage/Anthropic keys used by other projects).

## Architecture (current MVP)

### 5-Agent System

1. **Coordinator** — orchestrates the workflow, ensures final report generation, handles agent-to-agent handoff
2. **DataLoader** — validates file schema, prepares filepath pointers for downstream agents
3. **Analyst** — uses statistical tools (IQR, Z-Score) to detect anomalies and trends. **No LLM-driven number generation** — agents call Python tools, results come from pandas
4. **Recommender** — translates analytical findings into business recommendations
5. **Critic** — reviews the entire chain for logical consistency, catches hallucinations, signs off on the final report

### Filepath Passing Pattern

Agents do **not** pass raw data between each other (token-expensive). Instead they pass file paths. Each tool reads the file from disk, computes its result, and returns only a high-level summary to the LLM context. This allows processing 10K+ row datasets within a standard context window.

### Config-Driven Analysis

All analytical parameters live in `config/analysis_settings.json`. Switching from "Sales Data" to "IoT Sensor Data" = config edit, no code change. New use cases require new config schema, not new agents.

### Double-Safety Execution

Programmatic fallback ensures the final HTML report is generated even if the LLM agent fails to call the save tool. Two paths to the same outcome — the agent's tool call OR the deterministic post-pipeline save.

## Environment Gotchas

### Operational safety net (applies to any heavy local work)

If something on the dev machine starts leaking memory aggressively, Daniil has two PowerShell scripts in `C:\Users\coded\Documents\diagnostics\`:

- `mem_watch.ps1` — logs RAM + top-10 processes every 60 seconds. 7-day rotation. Use for post-mortem of crashes.
- `mem_guard.ps1` — kills runaway processes if RAM crosses 85%. Run in separate window when running long agent pipelines.

For this Python project, memory pressure is low (one Python process, no JS toolchain). Should be fine without `mem_guard.ps1`.

### Python on Windows — git PATH

Default PowerShell session does NOT have `git` in PATH. Use `C:\Program Files\Git\bin\git.exe` directly, or activate via `& 'C:\Program Files\Git\bin\git.exe'`. Same for `python` if not aliased — use `py` or full path.

### Frontend dev server — Next 16 + Tailwind 4 trap (READ BEFORE `npm run dev`)

Known bug across the lab: Next.js 16.1+ with `@tailwindcss/postcss` 4 enters an infinite Turbopack resolver loop. **RAM hits 100% in ~60 seconds, hard reset of the dev machine.** Same trap already burned `DK_AI_LAB_Landing` and `TMGG`.

**Workaround (mandatory):** in `frontend/package.json` set `"dev": "next dev --webpack"`. Do NOT set `turbopack.root` or any other turbopack config — Turbopack stays off entirely for dev.

Also run `mem_guard.ps1` from the operational safety net section above in a separate PowerShell window before the first `npm run dev`. Backup measure if anything else leaks.

### Gemini API rate limits

Free tier of Gemini 2.5 Flash: 15 RPM, 250K TPM, 500 RPD. The full 5-agent pipeline does ~20-40 LLM calls per analysis run. **Rate hits are visible if multiple runs back-to-back without backoff.** For production frontend deploy, plan for paid tier or request queueing.

## Voice Commands Protocol

Universal framework in RAG: `search_memory({ query: "universal voice commands protocol", project: "general" })`
Below are project-specific ADDITIONS.

### «Старт» (Start) — Session bootstrap

1. Read this CLAUDE.md fully
2. `search_memory({ query: "Capstone-Agents-MVP latest progress", project: "capstone_agents", limit: 5 })`
3. `list_recent({ days: 3, limit: 10, project: "capstone_agents" })`
4. Check project structure: `ls agents/ tools/ config/ 2>/dev/null`
5. Check Python env: `python --version` and verify `google-generativeai` installed
6. Report: "Готов. [summary of state]"

### «Сохранись» (Save) — Save knowledge + commit code

**Part 1 — Update knowledge base:**

1. Run `git diff --stat` to see what changed
2. `list_recent({ days: 1, limit: 5, project: "capstone_agents" })` to avoid duplicates
3. For each new piece of knowledge, save SEPARATE memory entries (categories: progress, bug, pitfall, decision, pattern, context)
4. If anything makes CLAUDE.md outdated — update it too
5. Don't merge unrelated items

**Part 2 — Commit code:**

6. `git add -A`
7. `git commit -m "<English message describing actual changes>"`
8. `git push origin main` (only if explicitly asked — do NOT push automatically, repo is public, kaggle reviewers may visit)

Report: "Сохранено: [memory entries] + [commit hash]"

### «Деплой» (Deploy) — Deploy to production

⚠️ **NOT YET DEFINED.** Deployment plan to be specified after frontend is built.

Planned approach (subject to revision):
1. Build frontend (Streamlit or Next.js + FastAPI — decision pending)
2. Provision subdomain on dklab.studio (Cloudflare DNS-only or proxied — decision pending)
3. Deploy to existing CX22 (188.245.89.60) or separate small instance
4. nginx reverse proxy + Let's Encrypt
5. PM2 (if Node) or systemd unit (if Python/Streamlit)
6. Verify HTTPS + agent pipeline runs end-to-end

When deploy plan is finalized, replace this section with concrete commands. Do NOT use "search memory" placeholder.

### Verification rule

After completing any task, PROVE it works. Run the pipeline. Show the output. Don't just say "done".

## Memory Rules

- project: `capstone_agents`, source: `agent`
- Tags: always include `capstone_agents`. Add specific tags per area: `agents`, `gemini`, `tools`, `frontend`, `deploy`, `bug`, etc.
- One bug = one memory. One feature = one memory.
- Auto-save if session >60% context used.

## Current TODO

### Phase 1 — Project plug-in (in progress, opened 2026-05-06)
- [x] Clone repo to `C:\Projects_Local\Capstone-Agents-MVP`
- [x] Apply project templates (.mcp.json, CLAUDE.md, STATE.md)
- [x] Add to ecosystem table in `_templates/CLAUDE.md` and `DK_AI_LAB_Landing/CLAUDE.md`
- [x] Save introduction memory entry to vector store (id `a222c415...`)
- [x] Public brand chosen: **Outlier** (subdomain: outlier.dklab.studio)
- [x] Add product card data to dklab.studio products registry (status: `in_progress`, url → GitHub fallback until deploy)

### Phase 2 — Frontend MVP
- [ ] Decide frontend stack: Streamlit (fast) or Next.js + FastAPI (consistent with ecosystem)
- [ ] Drag-drop file upload (CSV / XLSX / JSON)
- [ ] Live progress indicator while agent pipeline runs
- [ ] Render HTML report inline + download
- [ ] Live API key input (so user can use own Gemini key)
- [ ] Multi-format export (PDF, DOCX, email send)

### Phase 3 — Deploy
- [ ] Subdomain: **outlier.dklab.studio** (confirmed 2026-05-06)
- [ ] VPS placement (existing CX22 188.245.89.60 or new instance)
- [ ] Deploy pipeline (GitHub Actions or manual script)
- [ ] HTTPS + monitoring
- [ ] Update «Деплой» voice command in this file with concrete steps
- [ ] Atomic flip: products.ts URL update + status: in_progress → live + commit + deploy DK_AI_LAB_Landing

### Phase 4 — Anomaly Intelligence (future, from README roadmap)
- [ ] Persistent anomaly DB (PostgreSQL)
- [ ] Pattern recognition over time (seasonality, systemic degradation)
- [ ] Cross-dataset correlation
