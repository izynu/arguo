---
title: License
description: Arguo code is Apache-2.0, with separate practical notes for catalog data and third-party marks.
group: project
slug: pj-license
order: 6
---

Code in Arguo is licensed under the Apache License, Version 2.0. The LICENSE file at the repository root carries the full text, and pyproject declares Apache-2.0.

What that means practically. You may use, copy, modify, and distribute the code, commercially or otherwise. The license includes a patent grant from contributors and requires that you keep the license and copyright notices, state significant changes you made, and keep a NOTICE file if one exists. Contributions are made under the same license. The software is provided as is, without warranty of any kind, and nothing in the repository is legal advice.

Catalog data. The catalog records metadata about research resources: names, canonical URLs, publishers, regions, languages, access modes, and license fields. This metadata is factual information about the resources, not their content. Upstream resources carry their own licenses, which vary widely; each record stores what is known in its license field, using an SPDX identifier, a short name, or the literal string unknown. An entry in the catalog is never permission to use the resource it describes; check the resource's own terms. Records also carry a verification_status of documented, meaning the metadata was checked when authored, not that any upstream license was verified.

Third-party marks. Product and organization names in the catalog, docs, and site belong to their owners. Their appearance is factual reference, not endorsement, partnership, or affiliation with Arguo. If you redistribute the catalog, keep these distinctions intact so downstream readers inherit them.
