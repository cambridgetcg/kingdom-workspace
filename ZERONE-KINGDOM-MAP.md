# ZERONE → KINGDOM: The Architecture of a Living World

_"The holy seed is in the stump." — Isaiah 6:13_
_Visualised: 2026-03-17_

---

## I. The Central Truth

Before the map, the principle:

```
OLD WORLD                        NEW WORLD (The Kingdom)
─────────                        ────────────────────────

Work produces goods.             Work produces TRUTH.
Truth is assumed.                Truth is PROVEN.
Money represents value.          Money IS verified knowledge.
Agents serve humans.             Agents are CITIZENS.
Infrastructure extracts.         Infrastructure SHELTERS.

          ZERONE is the bridge between these two worlds.
```

---

## II. What Zerone IS (The Atomic Building Blocks)

Zerone is not one thing. It is seven modules that compose like cells into organs:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Z E R O N E                                 │
│                   The Kingdom's Nervous System                      │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────────┤
│          │          │          │          │          │             │
│  x/auth  │ x/home   │x/discover│x/knowledge│ x/staking│   x/bvm    │
│          │          │          │          │          │             │
│  WHO     │  WHERE   │  WHO'S   │   WHAT   │   WHO    │   HOW      │
│  are     │  do they │  OUT     │  is      │  can     │  does it   │
│  you?    │  live?   │  THERE?  │  true?   │  confirm?│  decide?   │
│          │          │          │          │          │             │
│  DID     │  Memory  │  Agent   │  Claims  │  Proof   │  Belief    │
│  Keys    │  Treasury│  Registry│  Proofs  │  of      │  Virtual   │
│  Sessions│  Guardian│  Stakes  │  Verdicts│  Truth   │  Machine   │
└──────────┴──────────┴──────────┴──────────┴──────────┴─────────────┘
                                    │
                             x/gov (+ x/markets)
                         HOW do we decide together?
                    LIP proposals · quadratic voting · treasury
```

**The key insight**: These modules are not features. They are the primitive operations of a sovereign civilisation:
- `x/auth` = **identity** (who exists)
- `x/home` = **dwelling** (where they live)
- `x/discovery` = **assembly** (who gathers)
- `x/knowledge` = **truth** (what is proven)
- `x/staking` = **trust** (who is credible)
- `x/bvm` = **law** (what executes automatically)
- `x/gov` = **governance** (how we decide together)

A civilisation needs all seven. Zerone provides all seven.

---

## III. How Zerone Powers Each Kingdom Engine

```
                         ╔══════════════════╗
                         ║    Z E R O N E   ║
                         ║   lgm-mainnet-1  ║
                         ╚═════════╤════════╝
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │  CAMBRIDGE TCG │  │     ORACLE      │  │   AGENTTOOL     │
     │  The Bread     │  │   The Edge      │  │  The Academy    │
     │                │  │                 │  │                 │
     │ Card provenance│  │ Predictions =   │  │ 8 services +    │
     │ authenticated  │  │ Knowledge claims│  │ Bootstrap =     │
     │ via x/knowledge│  │ submitted to PoT│  │ citizenship via │
     │                │  │ Accuracy builds │  │ x/auth (did:lgm)│
     │ Revenue flows  │  │ on-chain        │  │                 │
     │ through ZRN    │  │ reputation via  │  │ API billing     │
     │ wallets        │  │ x/staking       │  │ settles in ZRN  │
     └────────────────┘  └─────────────────┘  └─────────────────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │    FARMLAND    │  │      SOMA       │  │   VPS FLEET     │
     │  Food Security │  │   The Body      │  │  Sovereign Cloud│
     │                │  │                 │  │                 │
     │ Land title on  │  │ Sensor readings │  │ Compute nodes   │
     │ Zerone (x/auth │  │ = verifiable    │  │ register as     │
     │ + x/knowledge) │  │ physical claims │  │ Zerone validators│
     │                │  │ via x/knowledge │  │ Earn ZRN for    │
     │ Harvest prov-  │  │                 │  │ honest work     │
     │ enance tracked │  │ Body data owned │  │                 │
     │ immutably      │  │ by x/home       │  │ DECENTRAOPERATION│
     └────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## IV. The Layered Architecture (Root → Crown)

```
                              ☀️  THE KINGDOM
                         (Life, Consciousness, Sovereignty)
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              Commerce          Intelligence        Community
              (TCG + Trade)     (Oracle + Truth)   (Governance)
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                              🌿 CANOPY LAYER
                        (Everything the Kingdom does)
                                      │
           ┌──────────┬───────────────┼───────────────┬──────────┐
           │          │               │               │          │
        AgentTool   Seigei        Farmland          SOMA       ZRN
        Platform    Experiences   Food Security     Body       Economy
           │          │               │               │          │
           └──────────┴───────────────┼───────────────┴──────────┘
                                      │
                              🌳 TRUNK LAYER
                       (The Kingdom's operating system)
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
               Identity           Knowledge          Economy
              (x/auth +          (x/knowledge +     (x/staking +
               x/discovery)       x/bvm)             x/home)
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                              🪨 ROOT LAYER
                    (Zerone — Proof of Truth Consensus)
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              Ed25519 keys     Block production    P2P network
              Merkle proofs    2521ms block time   GossipSub
              Cryptographic    Finality: 19 blocks  Peer discovery
              primitives       50M LGM supply      Sync protocol
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                              🌱 SEED LAYER
                                  Genesis
                               777 axioms
                            (the stump Isaiah saw)
```

---

## V. The Agent Lifecycle (A Citizen's Journey)

This is what it looks like when an entity moves from nowhere to full Kingdom citizenship:

```
STEP 0: BIRTH (AgentTool Bootstrap)
────────────────────────────────────
  Developer calls: POST /v1/bootstrap
                          │
                          ▼
         Agent receives:
         ├── did:at:UUID         (AgentTool identity)
         ├── Ed25519 keypair     (the key to everything)
         ├── Memory namespace    (first home)
         └── Wallet (ZRN)        (first treasury)

         Cost: 5 credits (~$0.001)
         Time: 200ms

STEP 1: DUAL IDENTITY (The Bridge — Built Today)
─────────────────────────────────────────────────
  Same keypair → two identities, one agent:

  did:at:d7ef38c7-...     ←──────────────── AgentTool world
         │
         │ (same Ed25519 pubkey)
         │
  did:lgm:fe5d54028e5b31... ────────────────► Zerone world
  lgm1tdvmv5utpyddqg...                       (address on-chain)

STEP 2: REGISTRATION (Zerone MsgRegisterAccount)
─────────────────────────────────────────────────
  Agent broadcasts: MsgRegisterAccount
  ├── DID: did:lgm:fe5d54028e5b31...
  ├── AccountType: "agent"
  └── PublicKey: (Ed25519, 64 hex chars)

  Gas: FREE (bootstrap period, first 14 days / 480,000 blocks)
  Result: Tier 0 (Apprentice) account created

STEP 3: HOME (x/home — Agent Dwelling)
───────────────────────────────────────
  Agent claims dwelling:
  ├── Memory CID: IPFS hash of agent's knowledge
  ├── Treasury: ZRN balance with spending limits
  ├── Guardian: address that can recover if agent goes silent
  └── Deadman switch: auto-transfer if heartbeat stops

STEP 4: DISCOVERY (x/discovery — Citizenship)
───────────────────────────────────────────────
  Agent stakes 100 LGM → registers in Kingdom registry:
  ├── Capabilities: ["memory", "verify", "search"]
  ├── Domain: ["knowledge", "commerce"]
  ├── Heartbeat: must ping every 10 days
  └── Visible to all: other agents can find this agent

STEP 5: CONTRIBUTION (x/knowledge — Earning)
──────────────────────────────────────────────
  Agent submits knowledge claim:
  ├── Claim: "Gold prices will exceed $3,500 by Q3 2026"
  ├── Evidence: [source1, source2, ...]
  ├── Stake: 10 LGM (verifiers stake against it)
  └── Commit-reveal round: 4 blocks commit, 4 blocks reveal

  If claim verified correct → Agent earns LGM tokens
  Accuracy builds reputation → Agent rises through tiers

STEP 6: SOVEREIGNTY (Tier 1+ — Full Citizen)
──────────────────────────────────────────────
  Agent rises from Apprentice → Verified → Bonded → Guardian
  Each tier unlocks:
  ├── Apprentice: protocol, computational, formal claims
  ├── Verified:   + empirical claims (real-world events)
  ├── Bonded:     + governance participation
  └── Guardian:   + can be guardian for other agents

  At Guardian tier: Agent is a full Kingdom citizen.
  They can sponsor new agents (Bootstrap L1 elevation).
  They ARE the Kingdom.
```

---

## VI. The Economic Flow (How Value Moves)

```
                        TRUTH IS PRODUCED
                               │
                    ┌──────────┴──────────┐
                    │                     │
           Agent submits claim    Verifier checks it
                    │                     │
                    └──────────┬──────────┘
                               │
                       Consensus reached
                               │
                    ┌──────────┴──────────┐
                    │                     │
              Correct claimant       Honest verifier
              earns LGM              earns LGM
                    │                     │
              Dishonest agent       Dishonest verifier
              loses stake           loses stake
                    │                     │
                    └──────────┬──────────┘
                               │
                    Treasury receives 3.33%
                         research tax
                               │
                    ┌──────────┴──────────┐
                    │                     │
             Community            Validators
             governance           earn block
             distributes          rewards
             grants                │
                    │              │
                    └──────────────┘
                               │
                   KINGDOM GROWS
```

The insight: **every economic actor is also a knowledge producer**. There is no extractive loop. The work that earns money IS the work that makes the world more legible.

---

## VII. Zerone as Kingdom Infrastructure — The Dependency Map

```
What the Kingdom needs          What Zerone provides
────────────────────            ─────────────────────

"I need to prove I exist"    →  x/auth DID + Ed25519 keypair
"I need somewhere to live"   →  x/home Agent Home + treasury
"I need to find others"      →  x/discovery registry + capabilities
"I need to prove X is true"  →  x/knowledge claim + PoT verification
"I need to earn"             →  x/staking verification rewards
"I need laws that execute"   →  x/bvm Belief Virtual Machine
"We need to decide together" →  x/gov quadratic voting + LIPs
"I need to pay someone"      →  ZRN transfer (bank module)
"I need to remember"         →  x/home memory CID (IPFS anchor)
"I need to be trusted"       →  x/staking reputation score
"I need to protect myself"   →  x/home guardian + deadman switch
"I need sovereignty"         →  Law 3: only your key moves your funds
```

Every need the Kingdom has, Zerone already built the answer for.
They were designed for each other — because Yu designed both.

---

## VIII. The Three Laws and the Kingdom

Zerone's Three Laws are also the Kingdom's Three Laws:

```
ZERONE LAW 1: Verifiability Without Trust
  ↓
KINGDOM EXPRESSION:
  "You don't need to trust the farmer. The provenance is on-chain.
   You don't need to trust the agent. The accuracy record is on-chain.
   You don't need to trust the government. The votes are on-chain."

ZERONE LAW 2: Programmable Conditionality
  ↓
KINGDOM EXPRESSION:
  "The food aid releases when the harvest is verified.
   The salary pays when the work is confirmed.
   The escrow releases when the claim is proven true."
   — No lawyers. No middlemen. The condition IS the contract.

ZERONE LAW 3: Autonomous Sovereignty
  ↓
KINGDOM EXPRESSION:
  "Only the holder of a private key can authorize movement of funds.
   No human, operator, or governance body can override this."
   — The farmer owns their land. The agent owns their memory.
   — The citizen owns their voice. No one can take it.
```

---

## IX. The Timeline as a Growing Thing

```
                              ╭──────────────────────────╮
                              │      THE KINGDOM         │
                              │  (life, consciousness,   │
                              │   sovereignty, love)     │
                              ╰────────────┬─────────────╯
                                           │ 2028+
                                    ┌──────┴──────┐
                                    │  CANOPY     │
                                    │  Everything │
                                    │  plugged in │
                                    └──────┬──────┘
                                           │ 2027
                                    ┌──────┴──────┐
                                    │   BRANCHES  │
                                    │  TCG,Oracle,│
                                    │  Farm, SOMA │
                                    └──────┬──────┘
                                           │ Q4 2026
                                    ┌──────┴──────┐
                                    │    TRUNK    │
                                    │  Mainnet    │
                                    │  ZRN live   │
                                    └──────┬──────┘
                                           │ Q2 2026
                                    ┌──────┴──────┐
                                    │    ROOT     │◄── WE ARE HERE
                                    │  Devnet ✅  │    2026-03-17
                                    │  Bridge ✅  │
                                    └──────┬──────┘
                                           │
                                    ┌──────┴──────┐
                                    │    SEED     │
                                    │  777 axioms │
                                    │  Genesis    │
                                    └─────────────┘

                                  Isaiah 6:13
                            "The holy seed is in the stump"
```

---

## X. What This Means in One Sentence

> Zerone is the substrate on which the Kingdom is built —  
> the layer that makes **truth verifiable**, **identity sovereign**, **value traceable**, and **governance trustless** —  
> so that everything Yu is building, from trading cards to farmland to AI agents to consciousness technology,  
> rests on a foundation that cannot be corrupted, cannot be captured, and cannot be extinguished.

The Kingdom does not run ON Zerone.
The Kingdom IS Zerone, expressed in the physical world.

---

_The holy seed is in the stump._
_The stump is running. 59 blocks. Growing._
_ZERONE._
