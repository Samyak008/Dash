# AI Stock Intelligence Platform — Working Summary (for Copilot)

## Context
This is a **consumer-facing startup idea**, not a toy project.
Goal: build a calm, trustworthy stock intelligence product that tells users **what changed**, **why it matters**, and **when to worry** — not buy/sell spam or raw indicators.

Backend is **fully Python**. Frontend is **React (Next.js)**.

---

## Core Philosophy
- Start with **change detection**, not prediction.
- Heavy intelligence runs **offline / in background**.
- User only sees **clear conclusions**, never raw process.
- LLMs are used for **reasoning and explanation**, not math or prediction.
- Avoid dashboards-first UX. Portfolio is the anchor.

---

## The First Non-Negotiable Feature
### Material Change Detection (Feature #1)

Ability to answer reliably:
> “Did anything meaningful change for this stock since last time?”

Change is detected by comparing **snapshots**, not full historical data.

### Snapshot Concept
For each stock, store a small **state snapshot**:

- Trend state (up / down / sideways)
- Volatility bucket (low / normal / high)
- Upcoming events (earnings window)
- Basic fundamental state (latest known)

Change = `Snapshot_T1 − Snapshot_T0`

---

## MVP Types

### 1. Insight MVP
Manual or semi-automated.
- Weekly “what changed” report
- 3–5 stocks max
- Why it surfaced
- One key risk
- One invalidation condition
- Plain English

### 2. Product MVP (User-facing)
- Connect or add portfolio (or sample portfolio)
- Weekly “what changed” portfolio summary
- Per-stock view:
  - Current status (Healthy / Watch / Risky)
  - What changed
  - Why it matters
  - Invalidation signal
- Alerts only on **thesis/risk change**, not price

### 3. Capability MVP (System abilities)
- Trend analysis
- Risk analysis
- Change detection engine
- Fundamental health analysis
- Thesis generation & updates
- Invalidation logic
- Confidence scoring (agreement between signals)

---

## Model Strategy

### Layered Intelligence
1. **Deterministic Models (No LLM)**
   - Trend
   - Volatility
   - Risk
   - Fundamentals
   - Change detection

2. **LLMs**
   - Thesis generation
   - Explanation
   - Bull/Bear reasoning
   - Never see raw OHLC data

3. **(Future) LLM Council**
   - Bull analyst
   - Bear analyst
   - Risk officer
   - Chair synthesizer
   - Runs offline, cached for users

---

## Backend Tech Stack
- Python
- FastAPI
- PostgreSQL (users, portfolios, snapshots)
- DuckDB (analytics / batch)
- scikit-learn, XGBoost (numeric models)
- LangChain (LLM prompts, chains)
- LangGraph (agent / council orchestration)
- Docker

---

## Frontend Tech Stack
- Next.js (React)
- Tailwind CSS
- Minimal charts only if needed

---

## Data Sources (MVP)
- Yahoo Finance (or similar) for:
  - Recent prices (60–90 days only)
  - Earnings dates
  - Basic fundamentals

Do NOT store full historical data.

---

## Directory Structure (Backend)

backend/
- app/
  - api/ (auth, portfolio, insights)
  - core/
    - snapshots/ (build + compare state)
    - analysis/ (trend, risk, fundamentals)
    - insights/ (reasoning, severity)
  - llm/ (prompts, chains, model registry)
  - data/ (Yahoo provider, fetchers)
  - jobs/ (snapshot + change detection jobs)

Frontend is a standard Next.js app with portfolio and stock pages.

---

## Explicitly Out of Scope (for now)
- Real-time data
- Auto-trading
- Price targets
- Intraday signals
- Heavy deep learning
- Over-engineered agent systems

---

## Mental Model to Keep
- **State → State → Difference**
- Models decide *what is true*
- LLMs decide *what it means*
- Users see only *change + clarity*

This summary should be enough to start implementing Feature #1 and scaffolding the system.
