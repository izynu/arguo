# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

Only the latest 0.1.x release receives security fixes.

## Reporting a vulnerability

Please report privately. Do not open a public issue for a security problem.

1. Preferred: open a private GitHub Security Advisory on this repository (Security tab, "Report a vulnerability") if that feature is available for this repository.
2. If Security Advisories are not available: contact the maintainer directly through GitHub at [@izynu](https://github.com/izynu), or ask a co-maintainer ([@xhraddha](https://github.com/xhraddha)) to relay the report privately.

Include: a description of the issue, the steps or inputs that trigger it, the affected component (`python/arguo`, `scripts/`, `skill/`, `src/`), and any logs with secrets removed.

## Scope

The following are in scope:

- SSRF defenses in the fetcher and URL guard: bypasses of the scheme allowlist, private and link-local address blocking, credential stripping, redirect revalidation, hop limits, or response size caps
- Prompt injection failures that cause secret leakage or execution of attacker-controlled instructions against the operator's environment
- Secret leakage: API keys or credentials appearing in logs, run artifacts, cache files, or reports when the secret scrubbing should have removed them
- Unsafe redirects followed outside the revalidation rules
- Catalog validation bypass: ways to get malformed or fabricated records past the validators or the build dedupe

## Out of scope

- The upstream research sites listed in the catalog. Issues with those services belong to their operators.
- The static docs site when someone self-hosts it with a misconfigured server, reverse proxy, or custom domain setup. The repository ships a static build pipeline; the hosting environment is the operator's responsibility.
- Reports from automated scanners that do not include a working proof of impact.

## What to include

- Affected version (from `pyproject.toml` or the CLI version output)
- Minimal reproduction steps or a small script
- Expected behavior versus observed behavior
- Whether the issue reproduces in offline mode or requires live providers

## Safe harbor

We consider good-faith security research to be authorized and helpful. If you act on vulnerabilities you find in this repository in a way that avoids privacy violations, data destruction, and service degradation, and you report what you find through the channels above, we will not pursue or support action against you for that work.

## Bounties

There is no bug bounty program and no monetary reward. Fixes are credited in the changelog if you would like.
