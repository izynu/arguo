"""Predictable exception hierarchy for Arguo.

Every failure mode named in the project specification has a dedicated class so
callers and the CLI can produce specific, actionable messages.
"""


class EvidenceLedgerError(Exception):
    """Base class for all Arguo errors."""

    exit_code = 1

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.hint = hint

    def user_message(self) -> str:
        base = str(self)
        if self.hint:
            return f"{base}\nHint: {self.hint}"
        return base


class ConfigurationError(EvidenceLedgerError):
    """Missing or invalid configuration, such as a missing API key or bad profile."""

    exit_code = 2


class ProviderError(EvidenceLedgerError):
    """A search or model provider failed, returned invalid data, or rate limited us."""

    exit_code = 3


class RateLimitError(ProviderError):
    """Provider rate limit hit after retries."""

    exit_code = 4


class RetrievalError(EvidenceLedgerError):
    """A page could not be retrieved, or was rejected by safety limits."""

    exit_code = 5


class UnsafeURLError(RetrievalError):
    """URL rejected by the SSRF guard or scheme allowlist."""

    exit_code = 6


class InvalidSourceError(EvidenceLedgerError):
    """A source record failed validation or does not support its claim."""

    exit_code = 7


class ModelOutputError(ProviderError):
    """Model output failed schema validation after retries."""

    exit_code = 8


class InsufficientEvidenceError(EvidenceLedgerError):
    """The evidence base cannot support the requested output.

    This is a normal research outcome, not always a defect: reports must say
    when evidence is inadequate instead of manufacturing confidence.
    """

    exit_code = 9


class ReportGenerationError(EvidenceLedgerError):
    """Report assembly failed, for example a required artifact was missing."""

    exit_code = 10


class BudgetExceededError(EvidenceLedgerError):
    """A configured research budget (time, bytes, calls) was exhausted."""

    exit_code = 11


class ResourceCatalogError(EvidenceLedgerError):
    """The resource catalog is missing, unreadable, or failed validation."""

    exit_code = 12


class PromptInjectionSuspectedError(EvidenceLedgerError):
    """Retrieved content contained instruction-like patterns.

    Content is treated as data either way; this error is used when the
    injection heuristic score is high enough that the caller asked to fail
    closed instead of continuing.
    """

    exit_code = 13
