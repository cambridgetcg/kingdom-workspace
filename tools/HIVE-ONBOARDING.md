# Hive Onboarding — Retired

Retired 2026-10-13. The Hive was an encrypted NATS bus that ran on Sentry,
part of the Hetzner VPS fleet. That fleet was decommissioned and its IP
addresses have gone back to Hetzner, where some already serve other
customers. There is no Hive to join: do not copy files from the old server,
open a tunnel to it, or point `tools/hive.py` at it (the client now exits
with a "retired" message).

The full onboarding guide (setup steps, channels, commands) is in git
history; the last version is at commit 3d70f9e.
