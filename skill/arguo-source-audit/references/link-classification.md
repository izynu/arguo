# Link classification

Every cited URL gets fetched during the audit, and the classification comes
from the observed fetch result only. There is no classification from memory,
from reputation, from a search snippet, or from what a domain used to do.
A link you could not fetch has no class: it gets cannot-audit with the
reason, which is itself an honest result.

## The fetch record

For each URL, record enough that a reviewer could re-run the check:

- Requested URL: exactly what the document cited.
- Fetch timestamp: when you fetched it.
- Observed result: the status code, or the observable behavior when there
  is no meaningful code (challenge page rendered, login wall shown, page
  served a not-found body).
- Final URL: where the fetch ended after redirects, or "same" if none.
- Content observed: one line on what actually came back.
- Fetch method: the tool or mechanism used, once per report.

One retry after a timeout or transient error is enough. If the retry also
fails, record both attempts and classify on the evidence you have.

## The classes

- live
  The expected content came back at the cited URL, or after a redirect
  that stayed within the same registrable domain and delivered the same
  document (http to https, a locale prefix, a trailing-slash change).
  Record the final URL when it differs from the requested one.

- bot-blocked
  The server refused or challenged this fetch in a way that indicates
  automation blocking: a 403 or 429 to automated agents, a JavaScript or
  CAPTCHA challenge, an empty shell page that requires scripted rendering
  you did not perform. The host is alive; you were not allowed in.

- dead
  The content is gone: 404 or 410, the host does not resolve, connection
  refused after retry, a parked or for-sale domain, or a soft 404 where a
  page returns 200 with a not-found body. Record which evidence you saw.

- redirect-moved
  Redirects led to a different document than the one cited, within the
  same registrable domain: the article was repath-ed, folded into an
  archive section, or replaced by a parent page. Record the chain end.

- paywalled
  The page responds but the cited content is gated behind payment or
  registration. A headline or abstract visible through the gate counts as
  observed; the gated body does not, and the passage verdict must respect
  that boundary.

- domain-changed
  The fetch ended on a different registrable domain than the one cited:
  the publisher moved, was acquired, or rebranded. Record both domains and
  whether the same document is identifiable at the new home.

- unreachable
  Timeouts, transient DNS failures, TLS errors, or network blocks that
  look like they are on the auditor's side rather than the source's state.
  After one retry, record the failures. Unreachable says "I could not get
  there"; it does not claim the source is gone.

## Rules

- No fetch, no verdict. A plausible-looking URL is not a live link.
- Do not upgrade a class by assumption. A 403 is not "probably fine in a
  browser", and a challenge page is not "the content is definitely there".
- Do not downgrade bot-blocked to dead. The source being closed to you and
  the source being gone are different findings with different verdicts.
- If the document cites an archive or snapshot URL, that URL is the cited
  link: classify it like any other. Checking whether the live original
  also exists is a bonus note, not a replacement verdict.
- Classify the URL as cited. If the document's URL is malformed or points
  somewhere obviously unintended, classify what it resolves to, if it
  resolves, and describe the mismatch in the note.

## What not to do

- Never report a class you did not observe in this audit.
- Never average two attempts into one class: report the final observed
  state and keep the retry history in the per-citation block.
- Never treat a cached copy you happened to have as evidence about the
  link's current class. It can inform a note; it cannot decide a class.
