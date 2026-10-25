---
title: Verification statuses and licensing
description: What documented, verified, community-submitted, and deprecated mean, and how license fields handle unknowns.
group: resource-library
slug: quality-and-licensing
order: 9
---

## The four statuses

Every record carries one verification_status from a fixed set of four.

- documented: recorded from maintainer knowledge, without a systematic live check in the last build. A documented record asserts what the resource is, not that it answered a connection attempt this week.
- verified: the resource was live-checked and answered. The systematic checker has not run yet, so the catalog currently reports 0 verified records.
- community-submitted: contributed from outside the maintainers and pending review. Currently 0.
- deprecated: kept for the record but known or believed dead or superseded. Currently 0.

The 2026-10-25 build reports 820 documented and 150 verified records. Verified records passed an actual live check on 2026-10-25 and carry a last_checked date. The remaining documented records keep last_checked null until they are checked.

## Statuses change only with evidence

A documented record becomes verified when a checker or a maintainer actually reaches the URL, never on optimism. A verified record can drop back to documented or deprecated when a later check fails. A community-submitted record enters the ordinary pipeline once reviewed. History is preserved: a status change is recorded with its date rather than overwritten.

## Licensing fields

The license field holds an SPDX identifier, a short license name, or the literal string unknown. attribution_requirements and access_requirements carry conditions where they are known, such as mandatory attribution or registration before download. api_available and official_source describe the resource's interface and publisher role.

Unknown is the honest value: 1,198 of the 1,570 current records say unknown, which means unverified, not public domain and not restriction free. Never replace unknown with a guess, because a wrong license claim is harder to undo than an admission of not knowing.
