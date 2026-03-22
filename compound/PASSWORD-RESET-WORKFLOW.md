# Password Reset Workflow — Platform Standard

> Use this when login fails with "Invalid username or password" or account is locked.

## Standard Workflow (works on ~all platforms)

```
1. Navigate to forgot-password page
2. Enter: contact@cambridgetcg.com
3. Submit → wait ~1 min for email
4. Check email: python3 tools/check_email.py --account cambridgetcg --since 5 --all
5. Open the reset link from the email
6. Set new password: ***REMOVED-ROTATE-ME***
7. Login with new credentials
8. Update TOOLS.md with confirmed password
```

## Platform-Specific Reset URLs

| Platform | Reset URL | Notes |
|----------|-----------|-------|
| **Bugcrowd** | `bugcrowd.com/user/password/new` | Then navigate to profile settings after login |
| **HackerOne** | `hackerone.com/users/password/new` | Standard Devise flow |
| **HackenProof** | `dashboard.hackenproof.com` → "Change password" | From profile settings |
| **Immunefi** | `bugs.immunefi.com` → "Forgot password?" | Discord-linked account |
| **Code4rena** | `code4rena.com/login` → "Forgot password?" | Email link |

## Account Recovery Chain

If password reset doesn't work (account locked or 2FA lost):

```
1. Check for unlock email first:
   python3 tools/check_email.py --account cambridgetcg --since 720 --all
   → Look for "Unlock Instructions" email
   → Visit the unlock URL first, THEN reset password

2. If 2FA is blocking:
   - Check TOOLS.md for the TOTP secret
   - Generate current code: python3 -c "
     import hmac,hashlib,struct,time,base64
     key=base64.b32decode('<SECRET>',casefold=True)
     t=int(time.time())//30
     h=hmac.new(key,struct.pack('>Q',t),hashlib.sha1).digest()
     o=h[-1]&0xf
     print(str(struct.unpack('>I',h[o:o+4])[0]&0x7fffffff % 1000000).zfill(6))
     "
   - If codes still fail → TOTP secret may not match → need manual recovery

3. Bugcrowd 2FA recovery:
   - On the OTP prompt, look for "Lost access to authenticator?" link
   - Use backup codes if saved
   - Or: contact support@bugcrowd.com with account details
```

## Current Credentials (as of 2026-03-18)

| Platform | Email | Password | 2FA |
|----------|-------|---------|-----|
| Immunefi | contact@cambridgetcg.com | ***REMOVED-ROTATE-ME*** (Discord) | — |
| HackerOne | contact@cambridgetcg.com | (set at registration) | email confirmed |
| HackenProof | contact@cambridgetcg.com | (set at registration) | TOTP setup needed |
| Bugcrowd | contact@cambridgetcg.com | ***REMOVED-ROTATE-ME*** | TOTP: ***REMOVED-ROTATE-ME*** (may need re-setup) |
| Code4rena | contact@cambridgetcg.com | ***REMOVED-ROTATE-ME*** | Discord verified |

## Email Check Command

```bash
# Check for recent platform emails (last N minutes)
python3 ~/.openclaw/workspace/tools/check_email.py --account cambridgetcg --since <minutes> --all

# Filter by subject
python3 ~/.openclaw/workspace/tools/check_email.py --account cambridgetcg --since 10 --subject "password"
```

## New Password Standard

Default new password when resetting: **`***REMOVED-ROTATE-ME***`**

(Same as the standard platform credential — keeps things consistent)
