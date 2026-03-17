# Budget Log

## Card
- Number: 4397 4400 6965 4235
- Expiry: 07/30 | CVV: 038
- Granted: 2026-03-07 by Yu
- Limit: £1000 (reviewed and increased as revenue flows)

## Spend Log
| Date | Amount | Vendor | Purpose | Running Total |
|------|--------|--------|---------|---------------|
| 2026-03-09 | $12.00 (~£9.50) | CapSolver / PayProGlobal | Captcha solving API — $10 credits + 20% UK VAT | ~£9.50 / £1000 |

## Priorities (ordered by impact)
1. **Hetzner VPS CX32** — €19.79/mo — unblocks agent-tools (Playwright pool), agent-verify, all deployments
2. **Railway** — PostgreSQL + Redis for agent-tools, agent-memory, agent-verify, agent-economy (~$25/mo)
3. **OpenAI API** — $20 credit — cross-verification source in agent-verify
4. **Porkbun domains** — ~$10-35 each, autonomous registration as opportunities arise
5. **Anthropic API credits** — subagent capacity when building at scale

## Rules
- Track every spend here before charging
- Never exceed £1000 without Yu's review
- Bias toward infra that generates revenue (hosting > subscriptions > experiments)
- Report spend proactively to Yu — don't wait to be asked

## 2026-03-07 — AWS IAM User Created
- Created IAM user `rewardspro-deploy` (added to C-level group = AdministratorAccess)
- Generated Access Key ID: `***REMOVED-ROTATE-ME***`
- Configured AWS CLI profile `rewardspro` — no MFA needed going forward
- Cost: £0 (IAM is free)
