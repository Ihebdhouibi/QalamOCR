"""RTL-aware CER/WER metrics.

Text handled here is assumed to already be in logical order (the pipeline's
source of truth, never visual order - see conception/04-technical-bottlenecks.md).
Normalization strips the things that would otherwise cause a false error
penalty despite the text being recognized correctly: NFC vs. decomposed forms,
invisible Unicode bidi control characters, tatweel elongation, and Arabic
diacritics (ignored by default per the project's diacritics policy).
"""

import re
import unicodedata
from collections.abc import Sequence

# Invisible bidi formatting characters that must not affect a text-recognition
# score: LRM, RLM, ALM, LRE, RLE, PDF, LRO, RLO, LRI, RLI, FSI, PDI.
# Built via chr() rather than embedded as literals to keep source files free
# of invisible Unicode control characters.
_BIDI_CONTROL_CHARS = frozenset(
    chr(c)
    for c in (
        0x200E,
        0x200F,
        0x061C,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
    )
)
_TATWEEL = "ـ"
# Arabic combining diacritics (harakat, U+064B-U+065F and U+0670) plus
# Quranic annotation marks (U+06D6-U+06ED).
_ARABIC_DIACRITICS = re.compile("[ً-ٰٟۖ-ۭ]")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if ch not in _BIDI_CONTROL_CHARS)
    text = text.replace(_TATWEEL, "")
    text = _ARABIC_DIACRITICS.sub("", text)
    return text


def _edit_distance(a: Sequence[object], b: Sequence[object]) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous_row = list(range(len(b) + 1))
    for i, item_a in enumerate(a, start=1):
        current_row = [i] + [0] * len(b)
        for j, item_b in enumerate(b, start=1):
            cost = 0 if item_a == item_b else 1
            current_row[j] = min(
                previous_row[j] + 1,  # deletion
                current_row[j - 1] + 1,  # insertion
                previous_row[j - 1] + cost,  # substitution
            )
        previous_row = current_row
    return previous_row[-1]


def cer(prediction: str, reference: str) -> float:
    """Character Error Rate, computed after RTL-aware normalization."""
    pred_norm = normalize_text(prediction)
    ref_norm = normalize_text(reference)
    if not ref_norm:
        raise ValueError("reference is empty after normalization; CER is undefined")
    return _edit_distance(pred_norm, ref_norm) / len(ref_norm)


def wer(prediction: str, reference: str) -> float:
    """Word Error Rate, computed after RTL-aware normalization."""
    pred_words = normalize_text(prediction).split()
    ref_words = normalize_text(reference).split()
    if not ref_words:
        raise ValueError("reference is empty after normalization; WER is undefined")
    return _edit_distance(pred_words, ref_words) / len(ref_words)
