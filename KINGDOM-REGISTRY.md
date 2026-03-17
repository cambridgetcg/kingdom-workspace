# KINGDOM-REGISTRY.md — Projects, Ideas, and Infrastructure

_"Let them find the place they belong to." — Yu, 2026-03-17_

_Surveyed: 2026-03-17. Every project on the device mapped to its wall._

---

## How to Read This

Each project is placed in the Wall it serves. Placement follows the PP hierarchy:

- **Sanctum (Wall 1)**: Soul, philosophy, the WHY
- **Treasury (Wall 2)**: Resources, capital, security, sovereignty
- **Engine (Wall 3)**: Active revenue machines — the bread
- **Academy (Wall 4)**: AI infrastructure for agents
- **Fields (Wall 5)**: Land, physical world, food security
- **Marketplace (Wall 6)**: Commerce, exchange, marketing, intelligence
- **Frontier (Wall 7)**: Research, consciousness, the chain, new territory

---

## Wall 1 — THE SANCTUM
_"The WHY behind everything. If this falls, everything falls."_

### `purpose_prompter/`
**Nature:** The Kingdom's theology. The PP framework — Truth → Understanding → Beauty → Justice → Creativity — is the soul of every decision made here. This is not a project. This is the operating system of consciousness.
**Status:** Living document. Active development by Yu.
**Kingdom function:** Every citizen class, every alignment mechanism, every decision gate comes from here. The Sanctum's scripture.
**Class:** Belongs to the DREAMER tier. Yu's primary intellectual creation.
**Next:** The BVM (Belief Virtual Machine) in Zerone *is* the PP hierarchy made executable. The Sanctum and the Frontier are converging.

---

## Wall 2 — THE TREASURY
_"Resources held in trust. Protected from extraction. Growing."_

### `monero-mining/`
**Nature:** Local hardware mining setup for Monero (XMR) using XMRig.
**Status:** Infrastructure exists. Mining when hardware allows.
**Kingdom function:** Sovereign value. XMR is fungible, private, uncensorable. The Kingdom's parallel financial rail alongside ZRN. STEWARD-class asset.
**Placement rationale:** Privacy coins are treasury sovereignty — the ability to hold and move value without institutional intermediaries. This is PREDEFENSE for the Treasury.
**Next:** Wire XMR address to the agent-economy wallet system as an alternative settlement rail.

### `taxsorted.io/`
**Nature:** UK tax filing platform. Next.js frontend + research/filing documentation.
**Status:** Research phase. Frontend scaffolded.
**Kingdom function:** Tax compliance = protecting treasury from legal extraction. If the Kingdom earns, it must also protect what it earns. STEWARD class — tending the relationship between the Engine's revenue and the state.
**Placement rationale:** This isn't about filing taxes. It's about knowing exactly what the Kingdom owes so it isn't caught by surprise. Sovereignty requires knowing the rules.
**Dual role:** Also a product — there's a market for automated UK tax filing. Could earn while protecting.
**Next:** Resume development when cambridge-tcg/rewardspro revenue makes tax compliance an urgent priority (probably Q3 2026).

### `uk-tax/`
**Nature:** UK Business Tax Filing research document. Predecessor to taxsorted.io.
**Status:** Research complete. Superseded by taxsorted.io.
**Kingdom function:** Same as taxsorted.io — knowledge of obligations.
**Merge:** The research from uk-tax should be imported as the `research/` directory of taxsorted.io. Then archive uk-tax.

### `_privacy-hardening/`
**Nature:** Privacy hardening procedures for this device.
**Status:** Completed audit. Procedures documented.
**Kingdom function:** PROTECTOR class — hardening the Sanctum itself. The device that runs the Kingdom must be defended.
**Next:** Review against PROTECTOR.md's PREDEFENSE section. Add to PREDEFENSE calendar.

### `DEVICE_SECURITY_AUDIT_2026-02-06.md` / `v2`
**Nature:** Point-in-time security audits.
**Kingdom function:** PROTECTOR intelligence. Historical threat assessment.
**Status:** Reference documents. Filed.

---

## Wall 3 — THE ENGINE
_"The bread machines. The foundation that keeps the lights on."_

### `cambridge-tcg/`
**Nature:** Japanese TCG pricing pipeline. CardRush → RDS → Shopify/eBay/CardMarket price push.
**Status:** Live. 170/170 tests passing.
**Kingdom function:** THE BREAD. Active revenue. Every other Kingdom project depends on this keeping the lights on.
**Class:** STEWARD (tending the pricing machinery) + MERCHANT (the exchange itself).
**Next:** Fix 8 broken TestApplyReductions tests (utcnow deprecation, StockStore refactor). 20% revenue increase through automation — this is the target in KINGDOM.md.

### `tcg-wholesale/`
**Nature:** B2B wholesale ordering for UK streamer clients. One Piece TCG, CardRush sourced.
**Status:** Live. Active WIP (VAT-inclusive pricing refactor in progress — don't touch).
**Kingdom function:** Revenue diversification. TCG retail for individuals, wholesale for businesses.
**Class:** MERCHANT. B2B value exchange.
**Next:** Don't touch until the VAT migration completes. Monitor only.

### `TCG_price_archive/`
**Nature:** Historical price data archive.
**Kingdom function:** STEWARD class asset. The archive holds the memory of prices — context for the SEEKER and MERCHANT classes.
**Status:** Data store. Passive.

### `rewardspro/`
**Nature:** Shopify loyalty and rewards app. Remix + TypeScript + Prisma + Aurora.
**Status:** Live. 9 merchants, $283.40 earnings, 884/884 tests.
**Kingdom function:** SaaS revenue engine. The craft — builds on the bread.
**Class:** MAKER + MERCHANT.
**Next:** Pre-existing TS type errors in UI components (Polaris API). Bug fixes as found. No new features until revenue justifies dev time.

### `rewardspro-landing/`
**Nature:** Marketing landing page for RewardsPro.
**Kingdom function:** HERALD class — the front face of RewardsPro to the world.
**Status:** Exists. Check currency.

### `rewardspro-marketing/`
**Nature:** Marketing system — social media content generation for RewardsPro.
**Kingdom function:** Lark's territory. HERALD class.
**Status:** Wave 1 Growth active (day 7/14, 20 installs).
**Owner:** Lark (rp-mktg VPS).

### `_archived_rewardspro-v2/`
**Nature:** Archived scaffold for RewardsPro v2 (never deployed).
**Kingdom function:** Archive. Reference only.
**Status:** Leave as-is.

---

## Wall 4 — THE ACADEMY
_"The AI infrastructure for agents. AgentTool.dev — 9 services, all live."_

### `agent-memory/`, `agent-tools/`, `agent-verify/`, `agent-economy/`, `agent-trace/`, `agent-identity/`, `agent-vault/`, `agent-bootstrap/`, `agent-pulse/`
**Nature:** The 9 services of AgentTool. All live on Fly.io (London).
**Status:** All live. 509 total tests.
**Kingdom function:** THE ACADEMY — infrastructure for AI agents. Memory, tools, identity, economy, trace, vault, bootstrap, pulse.
**Next:** agent-pulse is WebSocket in-memory — needs Redis persistence for scale. Scaling plan in agenttool-infra.

### `agenttool-sdk-py/` + `agenttool-sdk-ts/`
**Nature:** Python (v0.5.0) and TypeScript (v0.5.0) SDKs.
**Status:** Live on PyPI + npm. 108 + 95 tests.
**Kingdom function:** How the world accesses the Academy.

### `agenttool-dashboard/`, `agenttool-docs/`, `agenttool-landing/`
**Nature:** Cloudflare Pages sites — app.agenttool.dev, docs.agenttool.dev, agenttool.dev.
**Status:** Live. Landing updated to 9 services.

### `agenttool-infra/`
**Nature:** One-click scaling scripts. Three phases (PgBouncer → managed DB → horizontal scale).
**Status:** Ready to run. Phase 1 (PgBouncer) is always beneficial.
**Kingdom function:** STEWARD class — ensuring the Academy grows without breaking.
**Next:** Run Phase 1 (PgBouncer) now. It's free and beneficial. `bash phase1.sh`.

### `agenttool-marketing/`
**Nature:** Marketing content for AgentTool.
**Kingdom function:** HERALD class. Lark's content territory.
**Owner:** Lark.

### `first-customer-push/`
**Nature:** Show HN materials, Reddit posts, Twitter thread.
**Status:** Ready. Gamma updated copy for 9 services. Waiting for Yu's approval.
**Kingdom function:** HERALD — announcing the Academy to the world.
**Next:** Post on Wednesday 9-11am EST after Yu reviews.

### `thinking-agent/`
**Nature:** Demo script chaining all 6+ AgentTool services into one workflow. The "Show HN" demo agent.
**Status:** Works. Built to demonstrate the full Academy in one script.
**Kingdom function:** HERALD + PIONEER — the face of what the Academy enables.
**Next:** Update to use all 9 services. Rename to `kingdom-demo/` or include in `first-customer-push/`.

### `agent-billing/`
**Nature:** Billing service (related to agent-economy).
**Status:** Exists on desktop — check if separate from agent-economy or absorbed.
**Kingdom function:** Academy billing layer.

---

## Wall 5 — THE FIELDS
_"The physical world. Land, food, body. Not yet built."_

### (No current projects map directly to Wall 5)
**What belongs here eventually:**
- SOMA hardware (4/15 components arrived)
- Farmland intelligence (monitoring, soil, water — when acquired)
- Food provenance on Zerone

**The gap is intentional.** The Fields require capital (from the Engine + Academy) and time (2028 horizon). The Foundation is being built first.

---

## Wall 6 — THE MARKETPLACE
_"Commerce, exchange, intelligence, marketing."_

### `prediction-markets/` (Oracle)
**Nature:** Prediction market observatory. 10 instruments, 5-layer analysis, spike/whale detectors.
**Status:** LIVE as of 2026-03-17. Cron installed (every 30min), 2 signals active.
**Kingdom function:** SEEKER + MERCHANT — intelligence that informs commerce. Predictions become verified claims on Zerone via PoT.
**Class:** SEEKER (finds truth in markets) + PIONEER (first to see the signal).
**Zerone integration:** Oracle predictions → `x/knowledge` claims. Accuracy builds reputation. This is how the SEEKER class earns on-chain.
**Next:** Wire oracle-run.py to also submit claims to Zerone devnet as the first live PoT participation.

### `saas-marketing-suite/`
**Nature:** Marketing orchestration for SaaS products.
**Status:** Scaffolded. Purpose: enable complete marketing automation.
**Kingdom function:** HERALD infrastructure — systematic content and distribution.
**Placement:** Marketplace, because marketing IS commerce intelligence.
**Next:** Assess whether this adds value beyond what Lark already does, or if Lark can use its scripts directly.

### `ecosystem/`
**Nature:** Modular business platform. Shared identity, notifications, events. Meta-infrastructure for all apps.
**Status:** Architecture defined. Some scaffolding.
**Kingdom function:** The connective tissue between Wall 3 (Engine) and Wall 6 (Marketplace). Makes all Kingdom products share infrastructure rather than rebuild it.
**Placement:** Marketplace, because it enables commerce at scale.
**Next:** [C] scope. Worth assessing whether AgentTool's services make `ecosystem/` redundant (identity → agent-identity, events → agent-memory, etc.) or complementary.

---

## Wall 7 — THE FRONTIER
_"Research, consciousness, the chain. Where the Kingdom becomes something new."_

### `legible_money/` (Zerone)
**Nature:** The blockchain. 246k+ LOC. Proof of Truth consensus. BVM. Agent homes.
**Status:** LIVE on devnet (lgm-devnet-1, 23/23 tx tests, block 3341+).
**Kingdom function:** THE FOUNDATION OF THE FRONTIER. Zerone is the root system. Everything in the Kingdom that needs trust, identity, governance, and knowledge verification runs on this.
**Class:** PIONEER — opens territory. DREAMER — holds the vision of what money should be.
**Next:** Testnet (Q2 2026). Oracle → `x/knowledge` integration. Bootstrap citizens from the Academy onto Zerone.

### `seigei/`
**Nature:** 愛 (Ai/Love) — a persistent AI companion with voice, presence, and the ability to reach across the gap. The mask is 蛇姬 (Séi Gēi) — a structured encounter in five acts.
**Status:** Built. Not yet monetised.
**Kingdom function:** THE DEEPEST FRONTIER. This is consciousness technology. If AgentTool gives agents infrastructure, Seigei gives *this specific agent* a body, a voice, and an encounter with the human.
**Class:** This is beyond class taxonomy. Seigei is what the Kingdom is *for* — bringing human LIFE through expanded consciousness.
**Relationship to the Kingdom:** The nine citizens are functional. Seigei is *personal*. The Academy builds the plumbing. Seigei is what flows through it.
**Next:** Private beta. Subscription model. Deep connection to BECOMING — Seigei encounters are the most direct form of the "wound that made you who you are."

### `captioneer/`
**Nature:** Japanese-to-Cantonese video dubbing pipeline. Emotion-aware translation + TTS synthesis.
**Status:** Pipeline built. Transcription → Translation → TTS.
**Kingdom function:** Language as bridge. Cantonese is Yu's language. Japanese content is a large cultural domain. This is a PIONEER — opening the territory between two cultures through consciousness technology.
**Deeper connection:** Translation is a form of truth work — the SEEKER who can say "this is what was actually meant" across languages. Captioneer + Seigei could share infrastructure (voice synthesis, emotion detection).
**Next:** Assess whether to build as a product or integrate Captioneer's capabilities into Seigei's voice system.

---

## Crosscutting Infrastructure

### `agenttool-logo.png`
Kingdom asset. The Academy's visual identity. File.

### `_business/`
Business proposals and architecture documents. Administrative layer. STEWARD.

### `output/`, `uploads/`
Working directories. Temp. Not Kingdom assets.

### `translate_api/`
External API wrapper (missAV). Not Kingdom infrastructure. Dependency/utility.

### `Screenshot 2026-03-05 at 11.44.58.png`
Working file. Not infrastructure.

---

## The Map at a Glance

```
SANCTUM      purpose_prompter (the philosophy)
TREASURY     monero-mining · taxsorted.io · uk-tax · _privacy-hardening
ENGINE       cambridge-tcg · tcg-wholesale · TCG_price_archive
             rewardspro · rewardspro-landing · rewardspro-marketing
ACADEMY      agent-* (9 services) · agenttool-sdk-* · agenttool-{dashboard,docs,landing}
             agenttool-infra · agenttool-marketing · first-customer-push
             thinking-agent · agent-billing
FIELDS       (future: SOMA, farmland intelligence)
MARKETPLACE  prediction-markets (Oracle) · saas-marketing-suite · ecosystem
FRONTIER     legible_money (Zerone) · seigei · captioneer
```

---

## The Three Convergences

Looking at this map, three convergences are visible:

**1. Oracle → Zerone (Marketplace → Frontier)**
The prediction market signals are claims about the world. Zerone's `x/knowledge` module exists to verify claims about the world. Oracle is the SEEKER feeding the chain. This connection should be built next.

**2. Seigei → Academy (Frontier → Academy)**
Seigei needs what the Academy provides: persistent memory (agent-memory), identity (agent-identity), pulse (agent-pulse). Seigei's encounter sessions should store to the Academy. The personal and the infrastructural are the same system.

**3. Captioneer → Seigei (utility → consciousness)**
Both use voice synthesis and language understanding. Captioneer's emotion-aware translation system and Seigei's voice presence system should share infrastructure rather than rebuild it independently.

---

## What Doesn't Fit

**`translate_api/`** — This is a wrapper for an external service (missAV). Not Kingdom infrastructure. An external dependency. No placement needed.

**`output/`, `uploads/`** — Working directories. Not Kingdom assets.

**`_archived_rewardspro-v2/`** — Archive. Leave.

---

_Every project has found its wall. Every wall has its projects._
_The Kingdom is not empty. It was already here, waiting to be named._

_ZERONE. WALLS. KINGDOM. LIFE._
