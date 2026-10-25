---
title: Python Tutorial
description: Using settings, profiles, the orchestrator, and the EvidenceLedger class directly from Python.
group: getting-started
slug: gs-python-tutorial
order: 6
---

## Settings and profiles

`get_settings` resolves environment variables once and caches the result. Pass `reload=True` to re-read the environment, or an explicit `env` dict for tests.

```python
from arguo.config import PROFILES, get_settings

settings = get_settings()
print(settings.search_provider, settings.output_dir)

profile = PROFILES["quick"]
print(profile.subquestion_target, profile.budget.max_sources)
```

`PROFILES` is a plain dict of `ProfileConfig` objects. The standard profile targets 5 subquestions with 15 sources; deep targets 8 subquestions with 30 sources. Construct your own `ProfileConfig` if the presets do not fit.

## An offline orchestrator run

```python
import asyncio
import json
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

settings = get_settings()
orchestrator = ResearchOrchestrator(settings, PROFILES["quick"])
run_dir = Path(asyncio.run(
    orchestrator.run_offline("What do fixture sources say about citation audits?")
))

manifest = json.loads((run_dir / "manifest.json").read_text())
ledger = json.loads((run_dir / "evidence.json").read_text())
print(manifest["run_id"], len(ledger["evidence"]), "evidence records")
```

The offline run is deterministic: the same question and profile produce the same plan and fixture results. Read `evidence.json` as three arrays, `sources`, `evidence`, and `claims`, and join them with `source_id` and `evidence_ids`.

## Direct ledger usage

You can use `EvidenceLedger` without any search or model provider:

```python
from arguo.evidence.ledger import EvidenceLedger
from arguo.models import SupportRelation

ledger = EvidenceLedger()
source = ledger.add_source("https://example.org/report", title="Example report")
ev = ledger.add_evidence(
    source.source_id,
    source.url,
    "The program reduced measured losses by 12 percent.",
    supports_or_contradicts=SupportRelation.SUPPORTS,
)
claim = ledger.add_claim("The program reduced measured losses by 12 percent.")
ledger.link(claim.claim_id, ev.evidence_id)

groups = ledger.corroboration_groups()[claim.claim_id]
print(groups["distinct_independent_domains"], groups["syndication_suspected"])
```

Ids are sequential per ledger: `S1`, `E1`, `C1`. `link` enforces referential integrity in both directions and raises `InvalidSourceError` for unknown ids. `corroboration_groups` groups evidence by registrable domain, flags probable syndication when passages are near identical, and never deletes suspected duplicates; it annotates them. `to_json` serializes with explicit nulls and sorted keys, and `from_dict` rebuilds a ledger with counters restored.
