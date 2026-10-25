"use client";

import { Markdown } from "@/components/site/markdown";

const privacyPolicy = `# Privacy policy

Last updated: 2026-10-24

This policy covers the Arguo website and the Arguo software. The project is open source under the Apache-2.0 license.

## Website

**What we collect: nothing.** This site is static. It has no accounts, no analytics, no tracking pixels, and no cookies. Your theme preference (light or dark) is stored in your browser's local storage and never leaves your device.

**Server logs:** the hosting provider may keep standard access logs. We do not control, profile, or monetize them.

## Software

**Local by default.** When you run the arguo CLI, research questions, retrieved pages, caches, and generated reports are written to directories on your machine (runs/ and the cache directory). Nothing is sent to the project maintainers. There is no telemetry.

**What does leave your machine:** only the requests you configure: searches and page retrievals through your chosen search provider, and model calls to your configured endpoint. Your API keys are read from environment variables, are never logged, and are never written into reports or artifacts.

**Fixture data.** Offline mode uses bundled fixtures with example.org addresses and records nothing anywhere else.

## Third-party resources

The resource catalog links to external websites and APIs. Those services have their own privacy practices, which this policy does not cover.

## Children

The site and the software are general research tools, not directed at children, and collect no personal information from anyone.

## Changes

Material changes to this policy will be noted in the repository changelog with a new date above.

## Contact

For privacy questions, open an issue on the project repository: TODO: the repository owner adds the repository URL and a contact address before publishing.`;

const terms = `# Terms of use

Last updated: 2026-10-24

These terms govern your use of the Arguo website and software. By using either, you accept them.

## 1. What this project is

Arguo is open-source research tooling: an agent skill, a Python research agent, a curated resource catalog, and documentation. It organizes evidence and audits citations. It is not a source of authoritative answers.

## 2. No warranty

The software and website are provided "as is", without warranty of any kind, express or implied, including merchantability, fitness for a particular purpose, and non-infringement. Automated checks verify internal consistency and passage support; they cannot guarantee truth. You remain responsible for verifying anything you rely on.

## 3. Not professional advice

Output is not medical, legal, financial, or safety advice. For decisions in those areas, consult qualified professionals and primary sources.

## 4. Acceptable use

Do not use the software or website to violate any law or third-party right, to breach the terms of upstream data providers, to circumvent paywalls or access controls, or to generate misleading publications. Resource records in the catalog describe real services under their own licenses and terms: respect them.

## 5. Your data and content

Research runs stay on your machine unless you configure external providers. You keep all rights to the questions you ask and the reports you generate. You are responsible for how you use retrieved third-party content, including copyright and attribution.

## 6. License

The code is licensed under Apache-2.0. Documentation and catalog records are part of the project repository; third-party names and marks belong to their owners and do not imply endorsement.

## 7. Limitation of liability

To the maximum extent permitted by law, the project contributors are not liable for any damages arising from use of the site or software, including lost profits, data, or research outcomes.

## 8. Third-party links

The catalog and documentation link to external resources for research convenience. Availability, accuracy, and terms of those resources are controlled by their operators, not by this project.

## 9. Changes

These terms may be updated as the project evolves; material changes are recorded in the changelog with a new date above.

## 10. Contact

Questions about these terms: open an issue on the project repository. TODO: the repository owner adds the repository URL and a contact address before publishing.`;

export function PrivacyView() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-10 flex-1 w-full">
      <Markdown>{privacyPolicy}</Markdown>
    </div>
  );
}

export function TermsView() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-10 flex-1 w-full">
      <Markdown>{terms}</Markdown>
    </div>
  );
}
