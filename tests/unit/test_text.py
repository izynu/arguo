"""Tests for arguo.utilities.text."""

from __future__ import annotations

from arguo.utilities.text import (
    has_negation_conflict,
    normalize_whitespace,
    token_overlap,
    tokens,
    truncate_chars,
)


def test_normalize_whitespace_collapses_all_whitespace() -> None:
    assert normalize_whitespace(" a\n\t b  c ") == "a b c"
    assert normalize_whitespace("") == ""


def test_truncate_chars_appends_suffix_inside_limit() -> None:
    assert truncate_chars("abcdef", 5) == "ab..."
    assert truncate_chars("ab", 5) == "ab"
    assert truncate_chars("abcdefg", 6, "..") == "abcd.."
    assert len(truncate_chars("x" * 50, 10)) == 10


def test_tokens_lowercases_and_keeps_alphanumeric_runs() -> None:
    assert tokens("Hello, world! 42") == ["hello", "world", "42"]
    assert tokens("") == []


def test_token_overlap_identity_is_one() -> None:
    assert token_overlap("tree cover heat", "tree cover heat") == 1.0


def test_token_overlap_disjoint_is_zero() -> None:
    assert token_overlap("tree cover heat", "ocean salinity data") == 0.0


def test_token_overlap_partial_is_between() -> None:
    score = token_overlap("tree cover heat", "tree cover and shade")
    assert 0.0 < score < 1.0


def test_token_overlap_empty_inputs_are_zero() -> None:
    assert token_overlap("", "passage") == 0.0
    assert token_overlap("claim", "") == 0.0


def test_negation_conflict_true_case() -> None:
    assert has_negation_conflict(
        "The treatment is not effective", "The treatment is effective"
    )
    assert has_negation_conflict(
        "The treatment is effective", "The treatment is not effective"
    )


def test_negation_conflict_false_case() -> None:
    assert not has_negation_conflict(
        "The treatment is effective", "The treatment is effective"
    )
    assert not has_negation_conflict("Trees cool cities", "Canopy shade streets")
