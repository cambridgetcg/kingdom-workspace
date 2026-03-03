# Batch N: News Intelligence Pipeline
# Automated Multi-Perspective News Ingestion for Prediction Markets
# Created: 2026-02-27

---

## N01: System Architecture & Tech Stack Decision

### Context
You are designing a fully automated news intelligence pipeline for a prediction markets trader. The pipeline must:
- Ingest real-time news from multiple global sources
- Cluster articles by event (same story, different perspectives)
- Tag each source with political/geographic bias
- Detect where perspectives diverge (= market uncertainty/opportunity)
- Extract an "objective kernel" from conflicting narratives
- Generate a prediction market signal (market ID + direction + confidence)
- Deliver signals automatically with no human trigger required

### Existing System Context
The prediction markets system uses:
- **B03**: Live Sentiment Signal — breaks news events into market signals
- **B05**: Source Bias Adjustment — credibility matrix and adjustment formula
- **R01**: Correlation Risk Rebalancing — concentration management
- **R04**: Fast Resolution Pipeline — calibration and speed improvements
- Positions on Polymarket (USDC, ~$1,000-2,000 deployed)
- Current calibration: Brier 0.230 vs market 0.349 | 75% beat market | NO: 7/7 ✓, YES: 2/5 ✗

### Your Task
Produce a complete Architecture Decision Record (ADR) containing:

1. **Data Flow Diagram** (ASCII or structured description)
   - From raw API → clustering → perspective matrix → truth extraction → signal → delivery

2. **Tech Stack Decisions** with rationale:
   - Language/runtime (Python recommended, justify or override)
   - Database (event store, signal log, source bias table)
   - Queue/orchestration (cron? Celery? Simple event loop?)
   - LLM integration (which model for truth extraction, why)

3. **API Selection** (commit to primary sources):
   - Primary ingestion (GDELT DOC 2.0 vs Event Registry vs hybrid)
   - Secondary sources (Polygon.io for market-correlated? NewsAPI for depth?)
   - Justify each with latency, cost, coverage tradeoffs

4. **Pipeline Stages** (name each, define input/output contract):
   - Stage 1: Ingest
   - Stage 2: Cluster
   - Stage 3: Tag perspectives
   - Stage 4: Detect divergence
   - Stage 5: Extract truth
   - Stage 6: Generate signal
   - Stage 7: Deliver

5. **Automation Level**:
   - Which stages run fully auto?
   - Which stages have a human-in-the-loop gate (if any)?
   - What are the override/pause conditions?

6. **State Management**:
   - What gets persisted? (processed event IDs, signal log, source bias scores)
   - How long is data retained?

### Output Format
Structured markdown ADR. Decisions must be explicit ("We use X because Y, not Z because W"). No vague recommendations — commit to choices.

---

## N02: GDELT Ingestion Layer Implementation

### Context
[Paste N01 architecture output here]

### GDELT DOC 2.0 API Reference
```
https://api.gdeltproject.org/api/v2/doc/doc
  ?query={QUERY_STRING}
  &mode=artlist
  &format=json
  &maxrecords=250
  &startdatetime={YYYYMMDDHHMMSS}
  &enddatetime={YYYYMMDDHHMMSS}
```
Key fields: `url`, `title`, `seendate`, `domain`, `language`, `sourcecountry`, `tone`, `themes`, `persons`, `organizations`, `locations`
Update cadence: every 15 minutes. No API key required. Free.

### Your Task
Produce production-ready Python code for:

1. **Article dataclass**:
   ```python
   @dataclass
   class Article:
       url: str
       title: str
       domain: str
       source_country: str
       language: str
       tone: float
       themes: list[str]
       persons: list[str]
       organizations: list[str]
       locations: list[str]
       seen_date: datetime
       raw: dict
   ```

2. **GDELTPoller class**:
   - `poll(query: str, lookback_minutes: int = 15) -> list[Article]`
   - Rate limit: ~1 req/sec (GDELT limit)
   - Deduplication by URL (SQLite seen-set)
   - Returns structured `Article` objects

3. **QueryBuilder**:
   - Build GDELT queries from keywords + entity filters
   - Boolean operators (AND, OR, NOT)
   - `sourcelang` and `sourcecountry` filters for perspective targeting

4. **Polling loop**:
   - Runs every 15 minutes
   - Persists last poll timestamp
   - On failure: exponential backoff, log, continue

5. **Tests** (pytest):
   - Mock GDELT API response
   - Test deduplication
   - Test query builder
   - Test error handling

### Output
Complete `gdelt_ingestor.py` + `test_gdelt_ingestor.py`. No pseudocode — working implementation.

---

## N03: Source Bias & Perspective Matrix

### Context
[Paste N01 architecture + N02 Article dataclass here]

### Your Task
Build the **Perspective Tagging Layer** — assigns each article a position in the bias/perspective matrix.

### The Perspective Model
Two dimensions:
1. **Political Lean**: -2 (far left) → +2 (far right)
2. **Geographic Cluster**: Western | Russian | Chinese | Middle Eastern | Global South | Other

Aggregated into a **Perspective Matrix** per event cluster:
```json
{
  "Western_left":   {"articles": 4, "mean_tone": -1.2, "reliability_weighted_tone": -0.9},
  "Western_right":  {"articles": 3, "mean_tone": +0.8, "reliability_weighted_tone": +0.7},
  "Russian":        {"articles": 5, "mean_tone": -3.4, "reliability_weighted_tone": -2.8},
  "Middle_Eastern": {"articles": 2, "mean_tone": -2.1, "reliability_weighted_tone": -1.9}
}
```

### Requirements

1. **`source_bias.json`** — minimum 200 major domains:
   - Format: `{"bbc.co.uk": {"lean": -0.5, "reliability": 0.85, "geo": "Western"}}`
   - Include: BBC, Guardian, NYT, WaPo, Fox, Breitbart, RT, TASS, Al Jazeera, CGTN, Daily Mail, Reuters, AP, AFP, Xinhua, Sputnik, The Economist, FT, Bloomberg, CNN, MSNBC, Politico, The Hill, Zero Hedge, Daily Caller, HuffPost, Vox, The Atlantic, National Review, WSJ, and 170+ more
   - `default_by_country` fallback for unknown domains using GDELT `sourcecountry`

2. **PerspectiveTagger class**:
   - `tag(article: Article) -> TaggedArticle`
   - Domain lookup → country fallback
   - Returns `TaggedArticle` with `lean`, `geo_cluster`, `reliability` added

3. **PerspectiveMatrix builder**:
   - `build_matrix(articles: list[TaggedArticle]) -> PerspectiveMatrix`
   - Group by geo_cluster
   - Compute mean_tone, article count, reliability-weighted tone per cluster
   - Compute **divergence score**: max(mean_tone) - min(mean_tone) across clusters

4. **DivergenceDetector**:
   - `is_divergent(matrix: PerspectiveMatrix, threshold: float = 3.0) -> bool`
   - High divergence = genuine disagreement = uncertainty = potential opportunity

### Output
`perspective_tagger.py` + `source_bias.json` (200+ entries) + tests.

---

## N04: Event Clustering Engine

### Context
[Paste N01 architecture + N02 Article dataclass here]

### The Problem
GDELT returns a flat article list. Multiple articles discuss the same event (e.g., 15 articles about the Feb 26 Geneva Iran talks). They must be grouped into a single `EventCluster` before perspective analysis.

### Your Task

1. **Choose and justify one clustering approach**:
   - GDELT CAMEO codes (fast, coarse)
   - Title embedding similarity (accurate, costs embedding calls)
   - Entity + date overlap (simple, interpretable)
   - Hybrid (entity for speed, embedding for ambiguous cases)
   
   Justify based on: 15-min latency acceptable, cost control priority, accuracy requirements for PM signals.

2. **EventCluster dataclass**:
   ```python
   @dataclass
   class EventCluster:
       cluster_id: str           # deterministic hash of key entities + date
       event_summary: str        # auto-generated 1-line description
       first_seen: datetime
       last_updated: datetime
       articles: list[TaggedArticle]
       key_entities: list[str]   # persons + orgs + locations union
       cameo_codes: list[str]    # if available
       perspective_matrix: PerspectiveMatrix
       divergence_score: float
       is_divergent: bool
   ```

3. **EventClusterer class**:
   - `cluster(articles: list[TaggedArticle], existing: list[EventCluster]) -> list[EventCluster]`
   - Merges new articles into existing clusters if matched
   - Creates new cluster if no match
   - Deterministic `cluster_id`
   - Updates `perspective_matrix` and `divergence_score` on merge

4. **Cluster persistence** (SQLite):
   - Active clusters with full state
   - Expire after 72h of no new articles
   - History retained for calibration

5. **Tests**:
   - 10 articles on same event → 1 cluster
   - 10 articles on 3 events → 3 clusters
   - New article merges into existing cluster

### Output
`event_clusterer.py` + `schema.sql` (SQLite schema) + tests.

---

## N05: Truth Extraction Engine

### Context
[Paste N01 architecture + EventCluster dataclass + PerspectiveMatrix structure here]

### Philosophy
This is triangulation, not summarisation. Find what all perspectives agree on (= likely true), what they disagree on (= contested/uncertain), extract the prediction-market-relevant signal.

This is the LLM core of the pipeline. It operationalises B05 (Source Bias Adjustment) and B03 (Live Sentiment Signal) at scale.

### Your Task

1. **Truth Extraction Prompt Template** (`prompts/truth_extraction.txt`):
   
   Write the complete system + user prompt that takes an `EventCluster` and returns structured output. The prompt must instruct the model to:
   
   a. **Consensus facts** — what ALL perspectives agree on (= likely true)
   b. **Contested claims** — where perspectives split and why
   c. **Motivated omissions** — what each cluster is NOT saying (and why)
   d. **Objective kernel** — most likely true account, given all evidence
   e. **Prediction market relevance**:
      - Which market categories does this affect?
      - Direction shift (YES/NO probability) and magnitude
      - Confidence (0-1)
      - Key remaining uncertainty

   Format: present articles GROUPED BY PERSPECTIVE CLUSTER (not flat). Show tone scores and divergence explicitly in the prompt.

2. **TruthExtractor class**:
   - `extract(cluster: EventCluster, model: str = "claude-opus-4") -> TruthExtractionResult`
   - Formats cluster → prompt template
   - Calls Anthropic API
   - Parses structured JSON output
   - Retry × 2 on failure, then `requires_human_review = True`

3. **TruthExtractionResult dataclass**:
   ```python
   @dataclass
   class TruthExtractionResult:
       cluster_id: str
       consensus_facts: list[str]
       contested_claims: list[str]
       motivated_omissions: dict[str, str]   # cluster_name → what they're not saying
       objective_kernel: str
       market_relevance: list[MarketSignal]
       confidence: float
       requires_human_review: bool
       extracted_at: datetime
   ```

4. **Extraction triggers**:
   - Only for `is_divergent=True` clusters
   - Rate limit: max 20 extractions/hour (LLM cost control)
   - Skip if same cluster extracted in last 60 min

5. **Calibration logging**:
   - Log every extraction with cluster snapshot
   - Later: label whether signal led to profitable trade

### Output
`truth_extractor.py` + `prompts/truth_extraction.txt` (the full prompt) + tests with mocked LLM.

---

## N06: Signal Generator & Prediction Markets Integration

### Context
[Paste N01 architecture + TruthExtractionResult dataclass here]
[Paste active S-series strategy list]
[Paste B03 Live Sentiment Signal output format]
[Paste B05 Source Bias Adjustment formula]

### Your Task
Convert truth extraction output into actionable Polymarket signals, routed through the existing strategy framework.

### Requirements

1. **Market Identification**:
   - Match signal to active Polymarket markets via CLOB API keyword search
   - `https://clob.polymarket.com/markets` — filter by keyword/category
   - Return top 3 candidate markets with current prices

2. **Signal Scoring**:
   Apply existing calibration (Brier 0.230, 75% beat market):
   - Base probability from truth extraction confidence
   - Adjust via B05 bias formula
   - Adjust for applicable S-series strategy edge
   - Compare to current market price → Kelly-sized position suggestion

3. **Strategy Routing**:
   Map signal type to strategies:
   - Geopolitical → S04 + R01 (correlation check)
   - Economic data → S06 (macro)
   - Political → S01/S07
   - Resolution < 7 days → R04 (fast resolution pipeline)

4. **GeneratedSignal dataclass**:
   ```python
   @dataclass
   class GeneratedSignal:
       signal_id: str
       cluster_id: str
       market_id: str
       market_question: str
       direction: str                 # YES | NO
       current_price: float           # current market probability
       suggested_probability: float   # our estimate
       edge: float                    # suggested - current
       kelly_fraction: float
       strategy_code: str
       confidence: float
       generated_at: datetime
       status: str                    # pending | approved | rejected | executed
   ```

5. **Guardrails**:
   - Reject if edge < 0.05
   - Reject if adds to over-concentrated cluster (R01 check)
   - Flag for human review if confidence < 0.6
   - Max 3 pending signals awaiting approval at once

### Output
`signal_generator.py` + Polymarket market matching utility + tests.

---

## N07: Orchestration, State & Delivery

### Context
[Paste N01 architecture + all previous module summaries here]

### Pipeline Execution Flow
```
Every 15 minutes:
  1. Poll GDELT (N02)
  2. Tag perspectives (N03)
  3. Cluster into events (N04)
  4. For divergent clusters not recently extracted:
       Extract truth (N05)
       Generate signals (N06)
  5. Deliver pending signals

Continuously:
  6. Monitor signal status (pending → executed/rejected)
  7. Log outcomes for calibration
```

### Requirements

1. **Orchestrator class**:
   - `Orchestrator.run()` (blocking loop) or `Orchestrator.tick()` (single cycle)
   - State via SQLite
   - Graceful shutdown on SIGTERM/SIGINT
   - Optional: Prometheus metrics endpoint

2. **Complete SQLite Schema**:
   - `articles`: url, seen_date, cluster_id, domain, tone, geo_cluster
   - `clusters`: cluster_id, summary, created, updated, article_count, divergence_score, is_divergent
   - `extractions`: cluster_id, result JSON, extracted_at, requires_human_review
   - `signals`: all GeneratedSignal fields, status, outcome, resolved_at
   - `poll_state`: query_name, last_poll_time, articles_seen_count

3. **Query Configuration** (`config.yaml`):
   ```yaml
   queries:
     - name: geopolitical
       keywords: ["Iran", "Israel", "Russia", "Ukraine", "Gaza", "Taiwan", "China"]
       interval_minutes: 15
     - name: us_politics
       keywords: ["Congress", "Senate", "Trump", "tariff", "executive order", "Supreme Court"]
       interval_minutes: 15
     - name: markets
       keywords: ["Fed", "interest rate", "inflation", "GDP", "recession", "DOGE", "budget"]
       interval_minutes: 30
   ```

4. **Delivery Layer** (via OpenClaw/Telegram):
   Signal message format:
   ```
   🔔 NEW SIGNAL — [Market Question]
   Direction: YES/NO | Edge: +X.X% | Confidence: X%
   Kelly size: $XXX
   Strategy: S04 (Geopolitical)
   
   Truth kernel: [3-sentence summary]
   
   Perspective split: Western +1.2 | Russian -4.3 | ME -3.1 | Divergence: 5.5
   
   Approve? Reply A to approve, R to reject.
   ```
   
   On approval: log status, provide manual execution instruction (market link + size)

5. **Error Handling**:
   - Each stage: try/except with structured logging
   - Circuit breaker: GDELT fails 3× → pause + alert
   - Dead letter queue for failed extractions

6. **Deployment**:
   - `Dockerfile` (Python 3.12, slim)
   - `docker-compose.yml` with SQLite volume mount
   - `systemd` service file
   - `.env.example` with all required env vars

### Output
`orchestrator.py` + `config.yaml` + `schema.sql` (complete) + `Dockerfile` + `docker-compose.yml` + `.env.example`.

---

## N08: Calibration, Feedback Loop & Evaluation

### Context
[Paste N01 architecture + GeneratedSignal dataclass here]
Current baseline: Brier 0.230 vs market 0.349 | NO: 7/7 ✓ | YES: 2/5 ✗ | Feb 28 = major resolution day.

### Your Task
Build the measurement and improvement layer — so the pipeline gets better over time.

### Metrics

1. **Signal Quality**:
   - Brier score of `suggested_probability` vs resolution
   - Edge accuracy: edge > 0 → correct direction correlation
   - By strategy code: which routes perform best?
   - By source cluster: which perspective weightings are most predictive?

2. **Pipeline Health**:
   - Articles/hour (GDELT availability)
   - Clusters created vs dissolved/day
   - Extraction success rate (divergent clusters → successful extraction)
   - Signal acceptance rate (human approval %)
   - False positive rate (signals rejected as not market-relevant)

3. **Drift Detection**:
   - Rolling 30-day Brier score
   - Alert if drops below market baseline (0.349)
   - Track YES/NO asymmetry — currently systemic weakness on YES

### Requirements

1. **CalibrationEngine class**:
   - `record_outcome(signal_id, resolved_yes: bool, resolution_price: float)`
   - `compute_brier(window_days: int = 30) -> float`
   - `compute_edge_accuracy(by_strategy: bool = False) -> dict`
   - `generate_calibration_report() -> str`  ← markdown, run weekly

2. **Feedback → Perspective Tagger**:
   - Track which source bias weights produced accurate extractions
   - Simple gradient update: wrong signal → increase weight of minority perspective
   - Monthly update to `source_bias.json`

3. **Feedback → Signal Generator**:
   - Track Kelly sizing accuracy (did wins cover losses?)
   - Adjust confidence threshold for human-review gate based on track record
   - YES bias correction: if YES accuracy stays below 50%, apply systematic discount

4. **Weekly Calibration Prompt** (`prompts/weekly_calibration.md`):
   ```
   Run every Sunday.
   Input: Last 7 days pipeline output (signals, outcomes, Brier scores, perspective matrices)
   
   Analyse:
   1. Which news clusters generated the best signals? Common features?
   2. Which perspective divergences were real (resolved as predicted) vs noise?
   3. Source bias adjustments recommended? (specific domains)
   4. Strategy routing changes recommended? (S-series mapping)
   5. YES bias: what systematic corrections to apply?
   6. Brier trajectory — improving or degrading?
   
   Output: Calibration report + 3 specific parameter change recommendations
   ```

5. **Ground Truth Collection**:
   - Polymarket resolution polling (market status → auto-label signal outcomes)
   - CLI: `python label_signal.py --id S001 --resolved yes`
   - Feed labels into calibration engine automatically

### Output
`calibration_engine.py` + `prompts/weekly_calibration.md` + `label_signal.py` CLI + tests.
