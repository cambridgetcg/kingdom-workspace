
---

## Merchant Contact Research (2026-03-07)

### From DB (ShopSettings + Session):

**Real merchants (non-test stores):**
| Store Name | Shop Domain | Website | Email | Status |
|-----------|------------|---------|-------|--------|
| RA | add45c-3.myshopify.com | ra7wear.com | TBD | Free |
| Hananja (Stu's Brews) | rpwmw0-xj.myshopify.com | store.stusbrews.co.uk | TBD | Free |
| F111g | aw0atr-ek.myshopify.com | f111g.com | **team@f111g.com** ✅ | Free |
| ArootreAmarie | xpv9ce-01.myshopify.com | arootreamarie-forefront... | TBD | Free |
| JAS-3 | pa82nm-9i.myshopify.com | (no custom domain) | TBD | Free |

**Test/internal stores (skip):** test-shop, teststore12062025, themetester222, cashbackpro, rewardsprotesting, different-currency-test, saints-test, Cambridge TCG (6e824e-a9)

### Notes
- Access tokens in DB are encrypted — can't use directly to call Shopify API
- Partner API needs a separate access token (generate at Partners dashboard → Settings → API)
- **One confirmed email**: team@f111g.com (found on website)
- ra7wear.com and store.stusbrews.co.uk have no public email — will need Partner API or direct contact form
- Once SendGrid is configured, send review request to team@f111g.com immediately

### Action Items
- [ ] Yu: generate Partner API token at partners.shopify.com → Settings → API access
- [ ] Once token available, query all merchant shop owner emails via Partner GraphQL
- [ ] Send review request email to team@f111g.com (first confirmed real merchant)
