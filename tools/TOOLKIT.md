# TOOLKIT.md — Shared Agent Toolkit

_All credentials are available as environment variables on every node in the fleet._
_Last updated: 2026-03-09_

---

## 1. Captcha Solving — CapSolver

**Env:** `CAPSOLVER_API_KEY`
**Credits:** $10 (~12,500 reCAPTCHA solves)
**Docs:** https://docs.capsolver.com

### Usage (Python)
```python
import requests, os, time

API_KEY = os.environ["CAPSOLVER_API_KEY"]

def solve_recaptcha_v2(site_url, site_key):
    """Solve reCAPTCHA v2 and return the token."""
    task = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": API_KEY,
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": site_url,
            "websiteKey": site_key
        }
    }).json()
    task_id = task["taskId"]
    
    for _ in range(60):
        time.sleep(3)
        result = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": API_KEY,
            "taskId": task_id
        }).json()
        if result["status"] == "ready":
            return result["solution"]["gRecaptchaResponse"]
    raise TimeoutError("Captcha solve timed out")

def solve_hcaptcha(site_url, site_key):
    """Solve hCaptcha and return the token."""
    task = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": API_KEY,
        "task": {
            "type": "HCaptchaTaskProxyLess",
            "websiteURL": site_url,
            "websiteKey": site_key
        }
    }).json()
    task_id = task["taskId"]
    
    for _ in range(60):
        time.sleep(3)
        result = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": API_KEY,
            "taskId": task_id
        }).json()
        if result["status"] == "ready":
            return result["solution"]["gRecaptchaResponse"]
    raise TimeoutError("Captcha solve timed out")

def solve_turnstile(site_url, site_key):
    """Solve Cloudflare Turnstile."""
    task = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": API_KEY,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": site_url,
            "websiteKey": site_key
        }
    }).json()
    task_id = task["taskId"]
    
    for _ in range(60):
        time.sleep(3)
        result = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": API_KEY,
            "taskId": task_id
        }).json()
        if result["status"] == "ready":
            return result["solution"]["token"]
    raise TimeoutError("Captcha solve timed out")

def check_balance():
    """Check remaining CapSolver balance."""
    r = requests.post("https://api.capsolver.com/getBalance", json={
        "clientKey": API_KEY
    }).json()
    return r.get("balance", 0)
```

### Supported Captcha Types
| Type | Task Type | Cost |
|------|-----------|------|
| reCAPTCHA v2 | `ReCaptchaV2TaskProxyLess` | ~$0.0008 |
| reCAPTCHA v3 | `ReCaptchaV3TaskProxyLess` | ~$0.001 |
| hCaptcha | `HCaptchaTaskProxyLess` | ~$0.0008 |
| Cloudflare Turnstile | `AntiTurnstileTaskProxyLess` | ~$0.001 |
| Image captcha | `ImageToTextTask` | ~$0.0002 |

---

## 2. Residential Proxies — Bright Data

**Env:** `BRIGHTDATA_HOST`, `BRIGHTDATA_PORT`, `BRIGHTDATA_USER`, `BRIGHTDATA_PASS`
**Balance:** $960.45 | **Rate:** $8/GB
**Zone:** `seer` (Residential, pay-as-you-go)

### Usage (curl)
```bash
curl --proxy $BRIGHTDATA_HOST:$BRIGHTDATA_PORT \
     --proxy-user $BRIGHTDATA_USER:$BRIGHTDATA_PASS \
     -k "https://example.com"
```

### Usage (Python requests)
```python
import os

proxy_url = f"http://{os.environ['BRIGHTDATA_USER']}:{os.environ['BRIGHTDATA_PASS']}@{os.environ['BRIGHTDATA_HOST']}:{os.environ['BRIGHTDATA_PORT']}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

response = requests.get("https://example.com", proxies=proxies, verify=False)
```

### Country Targeting
```python
# Add country to username for geo-targeting
user = os.environ['BRIGHTDATA_USER'] + "-country-us"  # US IP
user = os.environ['BRIGHTDATA_USER'] + "-country-gb"  # UK IP
user = os.environ['BRIGHTDATA_USER'] + "-country-jp"  # Japan IP
```

### Test Connection
```bash
curl --proxy brd.superproxy.io:33335 \
     --proxy-user brd-customer-hl_2d97e1e0-zone-seer:***REMOVED-ROTATE-ME*** \
     -k "https://geo.brdtest.com/welcome.txt"
```

⚠️ **Note:** KYC not completed — some domains may be restricted. Most sites work fine with limited access.

---

## 3. Search API — SerpAPI

**Env:** `SERPAPI_KEY`
**Engines:** Google, Bing, DuckDuckGo, Amazon, Baidu, YouTube + more
**Docs:** https://serpapi.com/search-api

### Usage (Python)
```python
import requests, os

def search_google(query, num_results=10):
    """Search Google and return organic results."""
    r = requests.get("https://serpapi.com/search", params={
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": os.environ["SERPAPI_KEY"]
    }).json()
    return r.get("organic_results", [])

def search_amazon(query):
    """Search Amazon products."""
    r = requests.get("https://serpapi.com/search", params={
        "engine": "amazon",
        "amazon_domain": "amazon.co.uk",
        "k": query,
        "api_key": os.environ["SERPAPI_KEY"]
    }).json()
    return r.get("results", [])

def search_youtube(query):
    """Search YouTube videos."""
    r = requests.get("https://serpapi.com/search", params={
        "engine": "youtube",
        "search_query": query,
        "api_key": os.environ["SERPAPI_KEY"]
    }).json()
    return r.get("video_results", [])
```

### Quick curl
```bash
curl "https://serpapi.com/search?engine=google&q=shopify+loyalty+app&api_key=$SERPAPI_KEY"
```

---

## 4. Email Verification — IMAP

**Accounts:**
| Account | Env Email | Env Password |
|---------|-----------|-------------|
| Cambridge TCG | `IMAP_CAMBRIDGETCG_EMAIL` | `IMAP_CAMBRIDGETCG_PASS` |
| RewardsPro | `IMAP_REWARDSPRO_EMAIL` | `IMAP_REWARDSPRO_PASS` |

**IMAP Host:** `imap.gmail.com:993` (SSL)

### Helper Script
```bash
# Check for recent verification emails
python3 tools/check_email.py --account rewardspro --subject "verify" --since 5

# Check all recent emails from a sender
python3 tools/check_email.py --account cambridgetcg --from "noreply@github.com" --since 30

# Include read emails
python3 tools/check_email.py --account rewardspro --all --limit 5
```

### Output Format (JSON)
```json
{
  "account": "rewardspro",
  "email": "contact@rewardspro.io",
  "found": 1,
  "emails": [{
    "uid": "123",
    "from": "noreply@example.com",
    "subject": "Verify your email",
    "date": "Mon, 09 Mar 2026 10:00:00 +0000",
    "links": ["https://example.com/verify?token=abc123"],
    "codes": ["123456"],
    "body_preview": "Click the link to verify..."
  }]
}
```

### Direct Python Usage
```python
from tools.check_email import check_email

result = check_email(
    account="rewardspro",
    subject_filter="verification",
    since_minutes=10,
    unseen_only=True
)
for email in result["emails"]:
    print(email["subject"], email["links"])
```

---

## 5. SMS / Phone Verification — HeroSMS

**Dashboard:** https://hero-sms.com
**Login:** contact@rewardspro.io / ***REMOVED-ROTATE-ME***
**Account ID:** 698875
**Balance:** $9.00

### API Usage
```python
import requests

BASE = "https://hero-sms.com/api"
API_KEY = "YOUR_API_KEY"  # Get from dashboard Settings → API

def get_number(service="twitter", country="us"):
    """Get a temporary phone number for verification."""
    r = requests.get(f"{BASE}/getNumber", params={
        "apiKey": API_KEY,
        "service": service,
        "country": country
    }).json()
    return r  # {"id": "...", "number": "+1234567890"}

def get_sms(request_id):
    """Poll for the SMS code."""
    r = requests.get(f"{BASE}/getSms", params={
        "apiKey": API_KEY,
        "id": request_id
    }).json()
    return r  # {"code": "123456"} when received
```

### Pricing
| Service | Cost |
|---------|------|
| Twitter/X | $0.01 |
| Instagram | $0.015 |
| TikTok | $0.01 |
| Facebook | $0.02 |
| Reddit | $0.01 |
| Bluesky | $0.03 |

---

## 6. Cloudflare Bypass — Flaresolverr

**Available on:** nowhere at present. Retired 2026-10-13: the instances on the Hetzner nodes rp-rd and rp-mktg were decommissioned. Run it locally with Docker if needed (see TOOLKIT-LOCAL.md).
**Endpoint:** `http://127.0.0.1:8191/v1` (localhost only)

### Usage
```bash
# Using helper script
/root/flaresolve.sh "https://protected-site.com"

# Cookies only
/root/flaresolve.sh "https://protected-site.com" --cookies-only
```

### API Usage (Python)
```python
import requests

def bypass_cloudflare(url, max_timeout=60000):
    """Fetch a Cloudflare-protected page."""
    r = requests.post("http://127.0.0.1:8191/v1", json={
        "cmd": "request.get",
        "url": url,
        "maxTimeout": max_timeout
    }).json()
    return r.get("solution", {})
```

---

## 7. Cloudflare DNS & SSL — Cloudflare API

**Env:** Use API key from TOOLS.md (not in env by default)
**Email:** contact@cambridgetcg.com
**Global API Key:** `***REMOVED-ROTATE-ME***`
**Account ID:** `cf4198e651bf3009877d49f688c9d88e`

### Usage
```bash
# List zones
curl -s "https://api.cloudflare.com/client/v4/zones" \
  -H "X-Auth-Email: contact@cambridgetcg.com" \
  -H "X-Auth-Key: ***REMOVED-ROTATE-ME***"

# Update DNS record
curl -X PUT "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}" \
  -H "X-Auth-Email: contact@cambridgetcg.com" \
  -H "X-Auth-Key: ***REMOVED-ROTATE-ME***" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"example.com","content":"1.2.3.4","proxied":true}'
```

---

## 8. Complete Signup Flow Example

Here's how to combine tools for a full automated account signup:

```python
import os, time, requests
from tools.check_email import check_email

def automated_signup(platform, email_account="rewardspro"):
    """
    Full automated signup flow:
    1. Use residential proxy for the request
    2. If captcha → solve with CapSolver
    3. If email verification → check via IMAP
    4. If phone verification → use HeroSMS
    """
    
    # 1. Set up proxy
    proxy_url = f"http://{os.environ['BRIGHTDATA_USER']}:{os.environ['BRIGHTDATA_PASS']}@{os.environ['BRIGHTDATA_HOST']}:{os.environ['BRIGHTDATA_PORT']}"
    session = requests.Session()
    session.proxies = {"http": proxy_url, "https": proxy_url}
    session.verify = False
    
    # 2. ... perform signup with session ...
    
    # 3. Wait for and extract email verification
    time.sleep(10)
    emails = check_email(
        account=email_account,
        subject_filter="verify",
        since_minutes=5,
        unseen_only=True
    )
    if emails["found"] > 0:
        verify_link = emails["emails"][0]["links"][0]
        session.get(verify_link)  # Click verification link
    
    # 4. If phone needed, use HeroSMS
    # number = get_number(service=platform)
    # ... enter number on site ...
    # code = get_sms(number["id"])
    # ... enter code on site ...
    
    return {"status": "success"}
```

---

## Fleet Reference

Retired 2026-10-13: the Hetzner fleet (Forge, Lark, Sentry, Patch) was decommissioned and its IP addresses now belong to other customers. The old table is in git history.
