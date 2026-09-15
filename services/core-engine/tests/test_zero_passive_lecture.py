import pytest
from app.root_pedagogy.zero_passive_lecture_guardrail import ZeroPassiveLectureGuardrail, GuardrailResult


def test_guardrail_accepts_short_actionable_prompt():
    text = "x'i yalnız bırakmak için 6'yı karşıya at. Kaç kalır?"
    result = ZeroPassiveLectureGuardrail.validate_and_sanitize(text)
    assert result.is_valid is True
    assert result.sentence_count <= 3
    assert result.word_count <= 40
    assert result.sanitized_text == text


def test_guardrail_rejects_passive_monologue_phrases():
    passive_text = "Şimdi bu konuyu dinleyelim ve kuralları öğrenelim."
    result = ZeroPassiveLectureGuardrail.validate_and_sanitize(passive_text)
    assert result.is_valid is False
    assert "Pasif monolog" in result.violation_reason


def test_guardrail_crops_excessive_sentences():
    long_text = "Birinci adım bu. İkinci adım şu. Üçüncü adım o. Dördüncü adım da bu. Beşinci adım nerede?"
    result = ZeroPassiveLectureGuardrail.validate_and_sanitize(long_text)
    assert result.is_valid is False
    assert "Cümle sayısı" in result.violation_reason
    assert result.sanitized_text.endswith("?")


def test_guardrail_crops_excessive_words():
    many_words = "Bu soru çok önemli bir sorudur çünkü lise matematiğinde karşımıza sürekli çıkan ve her öğrencinin bilmesi gereken temel bir ilkedir. Ayrıca cebirsel dönüşümlerde terazi modelini anlamak için her iki taraftan aynı sayıyı çıkarmamız gerekmektedir ve bu işlem denklem çözümünün omurgasıdır ve tam olarak burada durup düşünmemiz gerekir mi?"
    result = ZeroPassiveLectureGuardrail.validate_and_sanitize(many_words)
    assert result.is_valid is False
    assert "Kelime sayısı" in result.violation_reason
    assert len(result.sanitized_text.split()) <= 41


def test_guardrail_appends_action_directive_if_passive():
    statement = "Denklemde x'in katsayısı 2'dir"
    result = ZeroPassiveLectureGuardrail.validate_and_sanitize(statement)
    assert result.is_valid is False
    assert result.sanitized_text.endswith("Şimdi sen dene?")
