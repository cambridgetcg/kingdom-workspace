# TOOLKIT-LOCAL.md — Full Credentials & Usage Reference

_For sharing with new OpenClaw instances on other devices._
_All credentials included inline — treat this file as SECRET._
_Last updated: 2026-03-09_

---

## Quick Setup for New Devices

Add these to your OpenClaw config (`~/.openclaw/openclaw.json`) under `"env"`:

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "***REMOVED-ROTATE-ME***",
    "OPENAI_API_KEY": "***REMOVED-ROTATE-ME***",
    "CAPSOLVER_API_KEY": "***REMOVED-ROTATE-ME***",
    "SERPAPI_KEY": "***REMOVED-ROTATE-ME***",
    "BRIGHTDATA_HOST": "brd.superproxy.io",
    "BRIGHTDATA_PORT": "33335",
    "BRIGHTDATA_USER": "brd-customer-hl_2d97e1e0-zone-seer",
    "BRIGHTDATA_PASS": "***REMOVED-ROTATE-ME***",
    "IMAP_CAMBRIDGETCG_EMAIL": "contact@cambridgetcg.com",
    "IMAP_CAMBRIDGETCG_PASS": "***REMOVED-ROTATE-ME***",
    "IMAP_REWARDSPRO_EMAIL": "contact@rewardspro.io",
    "IMAP_REWARDSPRO_PASS": "***REMOVED-ROTATE-ME***",
    "GITHUB_TOKEN": "***REMOVED-ROTATE-ME***"
  }
}
```

---

## 1. Captcha Solving — CapSolver

**API Key:** `***REMOVED-ROTATE-ME***`
**Dashboard:** https://dashboard.capsolver.com
**Login:** contact@cambridgetcg.com / ***REMOVED-ROTATE-ME***
**Credits:** ~$10 (~12,500 reCAPTCHA solves)

### Solve reCAPTCHA v2
```bash
# Create task
curl -s https://api.capsolver.com/createTask -d '{
  "clientKey": "***REMOVED-ROTATE-ME***",
  "task": {
    "type": "ReCaptchaV2TaskProxyLess",
    "websiteURL": "https://example.com",
    "websiteKey": "SITE_KEY_HERE"
  }
}'

# Get result (poll until status=ready)
curl -s https://api.capsolver.com/getTaskResult -d '{
  "clientKey": "***REMOVED-ROTATE-ME***",
  "taskId": "TASK_ID_HERE"
}'
```

### Python Helper
```python
import requests, time

CAPSOLVER_KEY = "***REMOVED-ROTATE-ME***"

def solve_captcha(captcha_type, site_url, site_key, timeout=180):
    """
    captcha_type: ReCaptchaV2TaskProxyLess | ReCaptchaV3TaskProxyLess | 
                  HCaptchaTaskProxyLess | AntiTurnstileTaskProxyLess
    """
    task = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": CAPSOLVER_KEY,
        "task": {"type": captcha_type, "websiteURL": site_url, "websiteKey": site_key}
    }).json()
    task_id = task["taskId"]
    
    for _ in range(timeout // 3):
        time.sleep(3)
        r = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": CAPSOLVER_KEY, "taskId": task_id
        }).json()
        if r["status"] == "ready":
            return r["solution"].get("gRecaptchaResponse") or r["solution"].get("token")
    raise TimeoutError("Captcha solve timed out")

def capsolver_balance():
    return requests.post("https://api.capsolver.com/getBalance", json={
        "clientKey": CAPSOLVER_KEY
    }).json().get("balance", 0)
```

### Supported Types & Cost
| Type | Task Type | Cost/solve |
|------|-----------|------------|
| reCAPTCHA v2 | `ReCaptchaV2TaskProxyLess` | ~$0.0008 |
| reCAPTCHA v3 | `ReCaptchaV3TaskProxyLess` | ~$0.001 |
| hCaptcha | `HCaptchaTaskProxyLess` | ~$0.0008 |
| Turnstile | `AntiTurnstileTaskProxyLess` | ~$0.001 |
| Image text | `ImageToTextTask` | ~$0.0002 |

---

## 2. Residential Proxies — Bright Data

**Host:** `brd.superproxy.io`
**Port:** `33335`
**Username:** `brd-customer-hl_2d97e1e0-zone-seer`
**Password:** `***REMOVED-ROTATE-ME***`
**Zone:** seer (Residential) | **Rate:** $8/GB | **Balance:** $960.45
**Dashboard:** https://brightdata.com (GitHub login: cambridgetcg)

### curl
```bash
curl --proxy brd.superproxy.io:33335 \
     --proxy-user "brd-customer-hl_2d97e1e0-zone-seer:***REMOVED-ROTATE-ME***" \
     -k "https://example.com"

# Country-targeted (US)
curl --proxy brd.superproxy.io:33335 \
     --proxy-user "brd-customer-hl_2d97e1e0-zone-seer-country-us:***REMOVED-ROTATE-ME***" \
     -k "https://example.com"

# Test connection
curl --proxy brd.superproxy.io:33335 \
     --proxy-user "brd-customer-hl_2d97e1e0-zone-seer:***REMOVED-ROTATE-ME***" \
     -k "https://geo.brdtest.com/welcome.txt"
```

### Python
```python
import requests

PROXY = "http://brd-customer-hl_2d97e1e0-zone-seer:***REMOVED-ROTATE-ME***@brd.superproxy.io:33335"

session = requests.Session()
session.proxies = {"http": PROXY, "https": PROXY}
session.verify = False

response = session.get("https://example.com")
```

### Country Codes
Append `-country-XX` to username: `us`, `gb`, `de`, `jp`, `fr`, `ca`, `au`, etc.

---

## 3. Search API — SerpAPI

**API Key:** `***REMOVED-ROTATE-ME***`
**Dashboard:** https://serpapi.com (GitHub login: cambridgetcg)
**Engines:** Google, Bing, DuckDuckGo, Amazon, YouTube, Baidu + more

### curl
```bash
# Google search
curl "https://serpapi.com/search?engine=google&q=shopify+loyalty+app&api_key=***REMOVED-ROTATE-ME***"

# Amazon search
curl "https://serpapi.com/search?engine=amazon&amazon_domain=amazon.co.uk&k=pokemon+cards&api_key=***REMOVED-ROTATE-ME***"
```

### Python
```python
import requests

SERPAPI_KEY = "***REMOVED-ROTATE-ME***"

def search(query, engine="google", **kwargs):
    r = requests.get("https://serpapi.com/search", params={
        "engine": engine, "q": query, "api_key": SERPAPI_KEY, **kwargs
    }).json()
    return r.get("organic_results", r.get("results", []))
```

---

## 4. Email Verification — IMAP (Gmail)

**Host:** `imap.gmail.com:993` (SSL)

| Account | Email | App Password |
|---------|-------|-------------|
| Cambridge TCG | contact@cambridgetcg.com | `***REMOVED-ROTATE-ME***` |
| RewardsPro | contact@rewardspro.io | `***REMOVED-ROTATE-ME***` |

### Helper Script
Copy `tools/check_email.py` to any device, then:
```bash
# Recent verification emails
python3 tools/check_email.py --account rewardspro --subject "verify" --since 5

# From a specific sender
python3 tools/check_email.py --account cambridgetcg --from "noreply@github.com" --since 30

# All recent (incl. read)
python3 tools/check_email.py --account rewardspro --all --limit 5
```

### Direct Python IMAP
```python
import imaplib, email

def get_verification_email(account="rewardspro", subject_filter="verify", minutes=10):
    creds = {
        "cambridgetcg": ("contact@cambridgetcg.com", "***REMOVED-ROTATE-ME***"),
        "rewardspro": ("contact@rewardspro.io", "***REMOVED-ROTATE-ME***"),
    }
    user, pw = creds[account]
    
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(user, pw)
    M.select("INBOX")
    
    import datetime
    since = (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).strftime("%d-%b-%Y")
    _, nums = M.search(None, f'(SINCE {since} SUBJECT "{subject_filter}" UNSEEN)')
    
    results = []
    for num in nums[0].split():
        _, data = M.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        results.append({
            "from": msg["From"],
            "subject": msg["Subject"],
            "date": msg["Date"]
        })
    M.logout()
    return results
```

---

## 5. SMS / Phone Verification — HeroSMS

**Dashboard:** https://hero-sms.com
**Login:** contact@rewardspro.io / ***REMOVED-ROTATE-ME***
**Account ID:** 698875
**Balance:** ~$9.00

### Pricing
| Service | Cost |
|---------|------|
| Twitter/X | $0.01 |
| Instagram | $0.015 |
| TikTok | $0.01 |
| Facebook | $0.02 |
| Reddit | $0.01 |
| Bluesky | $0.03 |

### API (get key from dashboard → Settings → API)
```bash
# Get number
curl "https://hero-sms.com/api/getNumber?apiKey=API_KEY&service=twitter&country=us"

# Poll for SMS
curl "https://hero-sms.com/api/getSms?apiKey=API_KEY&id=REQUEST_ID"
```

---

## 6. Cloudflare Bypass — Flaresolverr

**Runs on:** nowhere at present. Retired 2026-10-13: the instances on rp-rd and rp-mktg (Hetzner) were decommissioned; install locally as below.
**Port:** 127.0.0.1:8191 (localhost only)
**Version:** 3.4.6 | Chrome 142

### Install on New Device
```bash
docker run -d --name flaresolverr -p 127.0.0.1:8191:8191 \
  -e LOG_LEVEL=info --restart always ghcr.io/flaresolverr/flaresolverr:latest
```

---

## 7. Cloudflare API — DNS & Domain Management

**Email:** contact@cambridgetcg.com
**Global API Key:** `***REMOVED-ROTATE-ME***`
**Account ID:** `cf4198e651bf3009877d49f688c9d88e`

### Auth Headers (always required)
```bash
-H "X-Auth-Email: contact@cambridgetcg.com" \
-H "X-Auth-Key: ***REMOVED-ROTATE-ME***"
```

### Common Operations
```bash
# List all zones
curl -s "https://api.cloudflare.com/client/v4/zones" \
  -H "X-Auth-Email: contact@cambridgetcg.com" \
  -H "X-Auth-Key: ***REMOVED-ROTATE-ME***" | python3 -c "import json,sys; [print(z['name'],z['id']) for z in json.load(sys.stdin)['result']]"

# Create A record
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  -H "X-Auth-Email: contact@cambridgetcg.com" \
  -H "X-Auth-Key: ***REMOVED-ROTATE-ME***" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"@","content":"1.2.3.4","proxied":true}'
```

### Active Zones
ai-love.cc, artbitrage.io, axiepro.io, cambridgetcg.com, captioneer.io, cardforum.io, cashloom.io, fomoengine.io, mindicraft.com, rewardspro.io, sinovai.com, taxsorted.io, wholesaletcgdirect.com, agenttool.dev

---

## 8. Domain Registration — Porkbun API

**API Key:** `***REMOVED-ROTATE-ME***`
**Secret Key:** `***REMOVED-ROTATE-ME***`

### Register a Domain
```bash
curl -X POST "https://api.porkbun.com/api/json/v3/domain/register" \
  -H "Content-Type: application/json" \
  -d '{
    "apikey": "***REMOVED-ROTATE-ME***",
    "secretapikey": "***REMOVED-ROTATE-ME***",
    "domain": "example.com",
    "years": 1
  }'
```

### Check Availability
```bash
curl -X POST "https://api.porkbun.com/api/json/v3/domain/checkAvailability" \
  -d '{"apikey":"***REMOVED-ROTATE-ME***","secretapikey":"***REMOVED-ROTATE-ME***","domain":"example.com"}'
```

---

## 9. Image & Video Generation — Fal.ai

**API Key:** `***REMOVED-ROTATE-ME***`
**Account:** contact@cambridgetcg.com (Google OAuth)
**Balance:** $0.00 — needs top-up

### Usage
```bash
curl -X POST "https://fal.run/fal-ai/flux-pro/v1.1" \
  -H "Authorization: Key ***REMOVED-ROTATE-ME***" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a futuristic loyalty card hologram"}'
```

### Models & Pricing
| Model | Cost | Use |
|-------|------|-----|
| Flux Pro 1.1 | $0.04/img | Production images |
| Flux Schnell | $0.003/img | Quick drafts |
| Kling v1.6 | $0.35/5s | Video generation |

---

## 10. Social Posting — Ayrshare API

**API Key:** `***REMOVED-ROTATE-ME***`
**Dashboard:** https://app.ayrshare.com
**Login:** contact@rewardspro.io / ***REMOVED-ROTATE-ME***
**Plan:** Basic (free) — 20 post API calls/month

### Post to All Connected Platforms
```bash
curl -X POST "https://app.ayrshare.com/api/post" \
  -H "Authorization: Bearer ***REMOVED-ROTATE-ME***" \
  -H "Content-Type: application/json" \
  -d '{"post": "Check out our loyalty app!", "platforms": ["twitter", "linkedin"]}'
```

⚠️ No social accounts connected yet — connect at app.ayrshare.com/social-accounts

---

## 11. GitHub — PAT

**Token:** `***REMOVED-ROTATE-ME***`
**Account:** cambridgetcg
**Access:** Push to cambridgetcg/* repos

```bash
git clone https://***REMOVED-ROTATE-ME***@github.com/cambridgetcg/rewardspro.git
```

---

## 12. AWS CLI

**Profile:** `rewardspro`
**Account ID:** 043509841549
**Region:** us-east-1
**Access Key:** `***REMOVED-ROTATE-ME***`
**Secret Key:** `***REMOVED-ROTATE-ME***`

```bash
# Add to ~/.aws/credentials
[rewardspro]
aws_access_key_id = ***REMOVED-ROTATE-ME***
aws_secret_access_key = ***REMOVED-ROTATE-ME***

# Add to ~/.aws/config
[profile rewardspro]
region = us-east-1
output = json
```

---

## VPS Fleet: retired 2026-10-13

The Hetzner fleet (Forge, Lark, Sentry, Patch) was decommissioned and its IP addresses now belong to other customers. Do not SSH to them. The old table is in git history.

---

## Budget Card

**Card:** 4397 4400 6965 4235 | **Exp:** 07/30 | **CVV:** 038
**Limit:** £1000 (reviewed per £1000 spent)
**Current spend:** ~£9.50

---

_⚠️ This file contains live credentials. Do not commit to public repos or share outside trusted instances._
