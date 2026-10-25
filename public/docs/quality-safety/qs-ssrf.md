---
title: SSRF Defenses
description: What the URL guard and fetcher block before any network request, and the residual risks that remain, documented plainly.
group: quality-safety
slug: qs-ssrf
order: 5
---

Before any network activity, every URL passes URLGuard in security/url_guard.py. Checks, in order: a scheme allowlist (only http and https; file, ftp, data, and other schemes are rejected), credential rejection (user:pass@host forms are refused), host presence, and resolution of the host with rejection of blocked address ranges. Any port is allowed but non-default ports are logged; this is a deliberate, documented tradeoff.

Blocked ranges. The guard resolves the host with socket.getaddrinfo and checks every returned address, IPv4 and IPv6, with the ipaddress module. Rejected: unspecified (0.0.0.0 and ::), loopback, link-local, multicast, reserved, and private addresses. If any resolved address is blocked, the URL is rejected. DNS results are cached per guard instance for the lifetime of one run.

Redirects. The fetcher never follows redirects automatically. It follows at most 3 hops manually, and every destination is revalidated by the guard through revalidate_redirect before the next request is made. If a redirect host cannot be resolved, the fetch fails closed. Redirect targets must be absolute and carry a scheme.

Fetcher caps. Responses are streamed in 64 KiB chunks and cut at 2,000,000 bytes per request or the run byte budget, whichever is lower; truncation is recorded in the result. The per-request timeout comes from the profile budget, 20 seconds by default. Only a small content-type allowlist is accepted: HTML, XHTML, JSON, plain text, and PDF, with PDF recorded but not parsed. fetch never raises; failures come back as structured results.

Residual risks, stated plainly: DNS rebinding between the guard's check and the HTTP client's own resolution can bypass the IP checks; exotic redirect chains and non-default ports widen the reachable surface; and the allow_private flag, intended for tests only, disables the range checks entirely if enabled in production. The defenses raise the cost of SSRF; they do not eliminate it.
