# Capstone-Agents-MVP — STATE

Single source of truth for current project state. Update **before** ending any session.
Last updated: 2026-05-08 (handoff absorption complete)

> ⚠️ **Session handoff active (2026-05-08 morning)** — read `HANDOFF_2026-05-08.md` FIRST before trusting this file.
> Memory MCP server crashed 2026-05-07 18:50 UTC, Claude Desktop session restart pending.
> **Sections of THIS file are stale**: git status, working tree state, "Latest commit hashes" — actual git ground truth + corrections in handoff doc. CLAUDE.md ↔ STATE.md phase numbering desync also documented there.
> After new session absorbs corrections: delete `HANDOFF_2026-05-08.md` + remove this banner. STATE.md will be clean again.

## 🎯 Current state

**Phase:** Phase 3 (frontend) shipped E2E. All commits pushed through `a46ec07`. Working tree clean. Ready for Phase 4 — analyzer quality.

**Strategic pivot (acknowledged 2026-05-07):** Original Kaggle capstone deadline passed (badge issued 2025-12-18). This project is now **portfolio piece for Blazity job application** + flagship product card on dklab.studio. Not a deadline rush — quality over speed. Public framing: "Engine built November 2025 (Kaggle capstone), production wrapper + frontend + prompt hardening shipped May 2026."

**What works right now:**
- 5-agent pipeline runs locally via `python main.py` AND via FastAPI backend
- BYOK (Bring Your Own Key) — API key per-request, never stored on server
- Frontend at `localhost:3000` — full E2E browser flow validated 2026-05-07: ввод ключа → Test connection → drag-drop CSV → Run → SSE live progress per 5 agents → iframe report → download
- Backend FastAPI 6 + 2 endpoints (upload, run, events SSE, report, cancel, health, validate_key, state)
- All file paths anchored via `core/paths.py` (not CWD-relative anymore)
- Regression test fixture in repo: `data/test_ecommerce.csv` (30d × 8 SKU, 6 planted anomalies, baseline 3/6 recall)

**What does NOT work yet:**
- Not deployed (no public URL — Phase 6)
- Anomaly recall is 3/6 on regression — analyzer has known limitations (see Phase 4 roadmap)
- Reports are text-only (no charts yet — Phase 5)
- No persistent anomaly DB (every run is independent — Phase 7)

## 🔄 In progress / pending

_(none — all committed and pushed through `a46ec07`)_

## ⏳ Up next (in priority order)

### Phase 4 — Analyzer quality (estimate: half a day) — **NEXT UP**
1. **Per-SKU group-by anomaly detection** — current global IQR on mixed SKUs produces 33 false-positives in `total_value` (Smart Watch is consistently expensive, every row looks like outlier). Solution: groupby `product_name` before IQR computation. Same for `quantity`.
2. **Add `price_per_unit` to `anomaly_columns`** in `config/analysis_settings.json` — currently price typos (planted A6 Laptop Stand 49.99→199.99, A3 Smart Watch 199.99→9.99) are ignored by design.
3. **Low-side detection** — IQR theoretically catches both sides via `Q1 - 1.5*IQR`, but mixed-SKU smearing kills low-side sensitivity (planted A2 Gaming Mouse qty=0 missed). Add explicit z-score < -threshold layer or per-SKU floor.
4. **Enrich outlier output** — Analyst currently reports "indices 49, 174" — useless for recommendations. Tools should return enriched context: product_name, date, value, deviation magnitude. Recommender then can give specific actionable advice ("Wireless Headphones spike on 2025-04-12 — investigate viral channel") instead of generic "investigate top performers".
5. **Target:** recall 5-6/6 on test_ecommerce.csv. Re-run regression after each fix, track improvement.

### Phase 5 — Visual + Forecasting (estimate: 1-2 days)
6. **Plotly interactive charts in HTML report** — time series with highlighted outliers, per-SKU small multiples, IQR distribution histograms. `plotly.offline.plot(fig, output_type='div')` embeds as HTML+JS. Will require relaxing iframe `sandbox=""` to `sandbox="allow-scripts"`. Best ROI for portfolio wow-factor.
7. **Forecaster agent with Prophet** — new tool, new agent. Receives anomalies from Analyst → optionally winsorizes them → builds forecast with confidence intervals → returns numeric prediction + chart + caveat list. Critic validates against reasonable bounds. Architecturally fits config-driven system cleanly.

### Phase 5+ — Universal schema inference (estimate: 1-2 days, the "wow" feature)
8. **Schemer agent** for semantic column understanding. Hybrid pattern matching + LLM classifier:
   - Pattern matching: dtype detection (datetime/numeric/categorical), regex on dates, uniqueness ratios for ID-vs-name distinction
   - LLM classifier: receives column names + 5-10 sample rows + dtypes, returns `{column → semantic_role}` where role ∈ `{time, entity_id, entity_name, primary_metric, secondary_metric, dimension}`
   - Hybrid because pure LLM hallucinates on revenue-vs-cost, pure pattern matching can't tell quantity from price
   - Replaces hard-coded `required_columns: [date, store_name, product_name, quantity, price_per_unit, total_value]` with `required_roles: [time, entity, primary_metric]`
   - Story: "Drop any time-series CSV — sales, IoT sensors, web analytics, zoo footfall — Outlier figures out the schema and analyzes." This is the marketing centerpiece for portfolio.

### Phase 6 — Deploy
9. Subdomain `outlier.dklab.studio` (confirmed). VPS placement: existing CX22 (188.245.89.60, dklab.studio infra) most likely. nginx + Let's Encrypt + systemd unit for backend + serve Next.js standalone build.
10. Update `«Деплой»` voice command in CLAUDE.md with concrete steps.
11. Atomic flip in `DK_AI_LAB_Landing/lib/products.ts`: status `in_progress` → `live`, url → `https://outlier.dklab.studio`. Commit + deploy landing.

### Phase 7 — Anomaly Intelligence (long-term, from original README roadmap)
12. Persistent anomaly DB (PostgreSQL) — track anomalies across runs, surface recurring patterns
13. Pattern recognition over time (seasonality, systemic degradation)
14. Cross-dataset correlation

## 🗂 Backlog (orthogonal to phases)

- Migration `google-generativeai` → `google-genai` (deprecated SDK warning visible in every run). New Client-based per-instance API removes the global `genai.configure()` race that justifies single-worker queue. Could enable `max_concurrent > 1` in `runner.py`. Estimate: half a day. Best done before Phase 6 deploy so production isn't bottlenecked.
- Cost ceiling per analysis — currently unbounded. Need per-run budget cap (estimate input + output tokens × pricing) before public deploy.
- `i18n` for `/app` page — currently EN-only. Locale switcher works on landing only. Translate `messages/ru.json` and `messages/pl.json` (currently identical to EN as placeholder).
- Visual `SeaweedBackground` from DK_AI_LAB_Landing if Outlier should be more visually tied to lab brand. Currently minimal/clean — possibly more appropriate for analytics product.
- `mem_guard.ps1` mention in fronted README — backup memory protection during dev.

## 📌 Decisions worth remembering

### Strategic
- **Project purpose pivoted (2026-05-07):** No longer chasing Kaggle deadline. Now = portfolio for Blazity job application + flagship card on dklab.studio. Quality over speed.
- **Public framing:** "Engine built November 2025 (Kaggle capstone), production wrapper + frontend shipped May 2026." Engine + chassis metaphor.
- **Repo stays public.** Original Kaggle requirement, now also serves portfolio reviewers.

### Architecture
- **Gemini, not Anthropic.** Capstone was on Gemini. Don't swap mid-project. Migration to new `google-genai` SDK is OK (same provider).
- **BYOK model is the right call.** API key per-request, never stored. Reviewers test with own keys, Daniil's quota not consumed by demo traffic.
- **Filepath passing is core architecture, not optimization.** Makes 10K+ row datasets feasible. Don't refactor agents to pass DataFrames.
- **Critic agent is the moat.** Self-correcting multi-agent. Strong talking point. Validated 2026-05-07: caught Analyst hallucination during pre-fix tool failure.
- **`core/paths.py` is the path source of truth.** Use `from core.paths import PROJECT_ROOT, CONFIG_DIR, DATA_DIR, ...`. NEVER hardcode relative paths. NEVER `os.path.join("config", "...")`.
- **Project tag in memory:** `capstone_agents` (lowercase, underscore).

### Frontend
- **Stack:** Next.js 16.2.4 + React 19.2.4 + Tailwind 4 + Geist + next-intl 4.9. Inherits structure from `DK_AI_LAB_Landing`, **orange accent** (`#ff8c1a / #ff9d33 / #d96b00`) instead of lab's lime as Outlier-specific brand within lab family.
- **`"dev": "next dev --webpack"` is mandatory.** Without `--webpack`, Turbopack + Tailwind 4 enters infinite resolver loop, RAM 100% in 60s, hard reset of dev machine. Same trap burned `DK_AI_LAB_Landing` and `TMGG`. Documented in `CLAUDE.md` Environment Gotchas.
- **API key stored only in React state** — NOT localStorage, NOT sessionStorage, NOT cookies. Each session re-enters key. Security trade-off for BYOK demo.
- **Iframe `sandbox=""`** for report rendering. Maximum isolation. When Phase 5 adds Plotly charts, relax to `sandbox="allow-scripts"`.

### Process
- **NEVER commit without explicit user approval.** "Сохранись" voice command.
- **NEVER push without explicit user approval.** Public repo, reviewers may visit.
- **Pydantic schema in google-generativeai 0.8.6 doesn't support `Path | str` unions.** Type hints on tool function args must stay as `str`. Defaults can be `str(DEFAULT_PATH_CONST)`. Cosmetically less clean but required by SDK auto-schema generation.

## ❌ Anti-patterns (don't propose)

- Switching LLM provider mid-project (Gemini → Anthropic). Stays on Gemini.
- Adding more agents "because we can". Five is balanced. Schemer (Phase 5+) and Forecaster (Phase 5) are justified by clear new responsibilities.
- localStorage / sessionStorage for API key. Security.
- Turbopack on dev. Webpack only.
- `os.path.join("config", "...")` or any CWD-relative path. Use `core.paths` imports.
- Streamlit. Decision overruled — Next.js + FastAPI for ecosystem consistency. Don't reopen.
- "Just hardcode the column names for now." Phase 5+ Schemer makes this obsolete; meanwhile config-driven is acceptable.

## 🛠 Technical reference

| | |
|---|---|
| **Path** | `C:\Projects_Local\Capstone-Agents-MVP` |
| **GitHub** | `https://github.com/Codedkv/capstone-agents-mvp` (public) |
| **Kaggle notebook** | `https://www.kaggle.com/code/daniilkiliakou/notebook0fefd2e146` |
| **Language** | Python 3.10+ |
| **LLM** | Google Gemini 2.5 Flash via `google-generativeai` (deprecated, migration pending) |
| **Backend stack** | FastAPI 0.118.0, uvicorn[standard] 0.32.1, slowapi 0.1.9, python-multipart 0.0.20 |
| **Frontend stack** | Next.js 16.2.4, React 19.2.4, Tailwind 4, Geist, next-intl 4.9 |
| **Brand color** | Orange `#ff8c1a` primary, `#ff9d33` light, `#d96b00` dark |
| **Key env vars** | `GOOGLE_API_KEY` / `GEMINI_API_KEY` in `.env`, `GEMINI_RPM=1000` for Tier 1 |
| **Backend run** | `uvicorn backend.main:app --reload --port 8000` (from project root) |
| **Frontend run** | `cd frontend && npm run dev` (uses `--webpack` flag automatically via package.json) |
| **Memory protection** | `C:\Users\coded\Documents\diagnostics\mem_guard.ps1` (separate window during dev) |
| **Output** | `output/analysis_report.html` (CLI) or `runs/{run_id}/report.html` (backend) |
| **Regression fixture** | `data/test_ecommerce.csv` (30d × 8 SKU, 6 planted anomalies) |
| **Project tag (memory)** | `capstone_agents` |
| **Latest commit hashes** | HEAD = origin/main = `a46ec07` (STATE.md snapshot). Working tree clean. |

## 🐛 Known limitations (honest, for portfolio readme)

- **Recall 3/6 on regression test.** IQR on mixed SKUs misses low-side outliers and price-only anomalies. Phase 4 roadmap addresses.
- **No charts yet.** Reports are text/HTML. Phase 5 adds Plotly.
- **Cancel is best-effort.** Flag checked between agents, not mid-LLM-call. UI documents this.
- **iframe `sandbox=""`** blocks scripts entirely. Reports with embedded JS will need sandbox relaxation.
- **EN-only `/app`.** Locale switcher works on landing, but `/app` UI copy is English. Translation pending.
- **`google-generativeai` deprecated.** Warning visible in every run. Migration to `google-genai` planned.

### Backend risks (Phase 3 → must address before Phase 6 deploy)

- **In-memory state lost on uvicorn restart.** Active runs and event queues live in process memory. Restart kills any in-flight pipeline silently. Phase 6 deploy needs either Redis-backed state or systemd auto-restart with documented "restart kills runs" behavior in UI.
- **No cleanup of `runs/` directory.** Every analysis writes a new `runs/{uuid}/` folder, never deleted. Disk fills slowly. Phase 6 deploy needs a cron / cleanup endpoint deleting runs older than N days.
- **Cancel is partial.** `/api/cancel/{id}` flips a flag checked **between agents**, not mid-LLM-call. UI already documents this — adding to backend README too.

## How to use this file

When Daniil mentions the project ("продолжаем capstone", "что в Outlier", "Старт") — **read this file first** via Desktop Commander, then summarize state.

Update **before ending session**:
- Move done items from "Up next" to "What works"
- Update `Latest commit hashes` row
- Add new decisions / anti-patterns as they emerge
- Update working tree status if changed
