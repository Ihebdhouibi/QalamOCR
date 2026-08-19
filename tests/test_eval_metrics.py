import pytest

from qalamocr.eval.metrics import cer, normalize_text, wer

ARABIC_PRICE_WORD = "السعر"  # "the price"
ARABIC_CURRENCY_WORD = "دولار"  # "dollar"

# LRM = U+200E, RLM = U+200F: invisible bidi marks that text pipelines commonly
# emit or omit around an embedded LTR run inside RTL text. Built via chr()
# rather than embedded as literals to keep source files free of invisible
# Unicode control characters.
LRM = chr(0x200E)
RLM = chr(0x200F)

# Harakat (diacritics): kasra (U+0650), fatha (U+064E).
KASRA = "ِ"
FATHA = "َ"

# Tatweel / kashida elongation character.
TATWEEL = "ـ"


def _diacritize(word: str) -> str:
    return word[0] + KASRA + word[1] + FATHA + word[2:]


def test_cer_identical_ascii() -> None:
    assert cer("hello world", "hello world") == 0.0


def test_wer_identical_ascii() -> None:
    assert wer("hello world", "hello world") == 0.0


def test_cer_detects_real_substitution_error() -> None:
    assert cer("hemlo", "hello") == pytest.approx(1 / 5)


def test_wer_detects_real_word_error() -> None:
    assert wer("the slow fox", "the quick fox") == pytest.approx(1 / 3)


def test_cer_ignores_diacritics_by_default() -> None:
    diacritized = _diacritize(ARABIC_PRICE_WORD)
    assert diacritized != ARABIC_PRICE_WORD
    assert cer(diacritized, ARABIC_PRICE_WORD) == 0.0
    assert cer(ARABIC_PRICE_WORD, diacritized) == 0.0


def test_cer_ignores_tatweel_elongation() -> None:
    elongated = ARABIC_PRICE_WORD[0] + TATWEEL + ARABIC_PRICE_WORD[1:]
    assert elongated != ARABIC_PRICE_WORD
    assert cer(elongated, ARABIC_PRICE_WORD) == 0.0


def test_cer_ignores_invisible_bidi_marks() -> None:
    line = f"{ARABIC_PRICE_WORD} 100 {ARABIC_CURRENCY_WORD}"
    line_with_marks = f"{ARABIC_PRICE_WORD} {LRM}100{LRM} {ARABIC_CURRENCY_WORD}"
    assert line_with_marks != line
    assert cer(line_with_marks, line) == 0.0


def test_mixed_arabic_latin_number_line_no_false_penalty() -> None:
    # A logical-order line mixing Arabic text with an embedded LTR number run
    # (numbers run LTR inside RTL text). Comparing identical logical-order
    # strings must never be penalized just because the content is
    # mixed-direction.
    line = f"{ARABIC_PRICE_WORD} {RLM}100{RLM} {ARABIC_CURRENCY_WORD}"
    assert cer(line, line) == 0.0
    assert wer(line, line) == 0.0


def test_cer_empty_reference_raises() -> None:
    with pytest.raises(ValueError):
        cer("something", "")


def test_wer_empty_reference_raises() -> None:
    with pytest.raises(ValueError):
        wer("something", "")


def test_normalize_text_is_idempotent() -> None:
    diacritized = _diacritize(ARABIC_PRICE_WORD)
    once = normalize_text(diacritized)
    twice = normalize_text(once)
    assert once == twice
