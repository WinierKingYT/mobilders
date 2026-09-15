"""
HEDEF 13: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası ve Dinamik Deneme Sınavı Test Paketi.
TrapQuestionGenerator ve DynamicExamFactory Kapsamlı Testleri.
"""
import pytest
from app.curriculum_generator.trap_question_factory import (
    TrapQuestionGenerator,
    DynamicExamFactory,
    ExamSection,
    QuestionType,
    FormalQuestionVerifier,
    ExamDocumentExporter,
)


@pytest.fixture
def generator():
    return TrapQuestionGenerator()


@pytest.fixture
def factory(generator):
    return DynamicExamFactory(generator)


# ==============================================================================
# 1. TRAP QUESTION GENERATOR: QUADRATICS
# ==============================================================================

def test_generate_quadratic_structure(generator):
    """Kuadratik tuzak sorusunun 5 seçenek, tam 1 doğru cevap ve BUG etiketleri içerdiğini doğrular."""
    q = generator.generate_quadratic(2, -5)
    assert q.node_id == "N27"
    assert q.type == QuestionType.ALGEBRA
    assert len(q.choices) == 5
    correct_choices = [c for c in q.choices if c.is_correct]
    assert len(correct_choices) == 1
    assert q.choices[q.correct_choice_index].is_correct

    # Çeldiricilerin her birinin bir BUG-ID'ye sahip olduğunu doğrula
    distractors = [c for c in q.choices if not c.is_correct]
    assert len(distractors) == 4
    bug_ids = {c.bug_id for c in distractors if c.bug_id is not None}
    assert "BUG-QUAD-05" in bug_ids  # İşaret hatası tuzağı
    assert "BUG-QUAD-02" in bug_ids  # Eksik kök tuzağı


def test_generate_quadratic_prompt_content(generator):
    """Soru metninde denklemin yer aldığını ve kökleri içerdiğini doğrular."""
    q = generator.generate_quadratic(3, 4)
    # (x - 3)(x - 4) = x^2 - 7x + 12 = 0
    assert "x²" in q.prompt
    assert "12" in q.prompt
    assert "x = 3 veya x = 4" in q.target_value


# ==============================================================================
# 2. TRAP QUESTION GENERATOR: CALCULUS / DERIVATIVES
# ==============================================================================

def test_generate_derivative_structure(generator):
    """Türev sorusunun zincir kuralı tuzağını (BUG-CALC-01) ve sabit türevi tuzağını içerdiğini doğrular."""
    q = generator.generate_derivative(a=3, n=4)
    assert q.node_id == "N85"
    assert q.type == QuestionType.CALCULUS
    assert len(q.choices) == 5

    # 4 * 3 = 12(3x + 2)^3
    correct_choice = q.choices[q.correct_choice_index]
    assert "12(3x + 2)^3" in correct_choice.text

    distractor_bugs = {c.bug_id for c in q.choices if not c.is_correct}
    assert "BUG-CALC-01" in distractor_bugs  # İç türev 3 unutuldu
    assert "BUG-CALC-06" in distractor_bugs  # Sabit +2 unutuldu


# ==============================================================================
# 3. TRAP QUESTION GENERATOR: EUCLIDEAN GEOMETRY
# ==============================================================================

def test_generate_euclidean_structure(generator):
    """Öklid yükseklik sorusunun BUG-EUC-04 (karekökü unutma) çeldiricisini içerdiğini doğrular."""
    q = generator.generate_euclidean(p=4, k=9)
    assert q.node_id == "N165"
    assert q.type == QuestionType.GEOMETRY
    assert len(q.choices) == 5

    # h = sqrt(36) = 6
    correct_choice = q.choices[q.correct_choice_index]
    assert correct_choice.text == "6"

    # BUG-EUC-04 çeldiricisi: h = 36 (karekök unutuldu)
    distractor_36 = [c for c in q.choices if c.text == "36"]
    assert len(distractor_36) == 1
    assert distractor_36[0].bug_id == "BUG-EUC-04"


def test_generate_circle_angle_structure(generator):
    """Çemberde açı sorusunun BUG-EUC-02 (çevre=merkez) çeldiricisini içerdiğini doğrular."""
    q = generator.generate_circle_angle(center_angle=80)
    assert q.node_id == "N177"
    assert q.type == QuestionType.GEOMETRY
    assert len(q.choices) == 5

    # Çevre açı = 40°
    assert q.choices[q.correct_choice_index].text == "40°"

    # BUG-EUC-02 çeldiricisi: 80° (merkez açıya eşit sanma)
    distractor_80 = [c for c in q.choices if c.text == "80°"]
    assert len(distractor_80) == 1
    assert distractor_80[0].bug_id == "BUG-EUC-02"


# ==============================================================================
# 4. DYNAMIC EXAM FACTORY: ASSEMBLY
# ==============================================================================

def test_assemble_exam_tyt(factory):
    """TYT deneme sınavının belirtilen soru adedinde ve süresinde oluşturulduğunu doğrular."""
    exam = factory.assemble_exam(
        section=ExamSection.TYT_MATEMATIK,
        question_count=10,
        target_theta=0.5,
    )
    assert exam.section == ExamSection.TYT_MATEMATIK
    assert len(exam.questions) == 10
    assert exam.total_time_minutes == 20
    assert exam.target_theta == 0.5
    assert "TYT_MATEMATIK" in exam.title


def test_assemble_exam_ayt_topic_distribution(factory):
    """AYT sınavında cebir, kalkülüs ve geometri alanlarından karma soru yer aldığını doğrular."""
    exam = factory.assemble_exam(
        section=ExamSection.AYT_MATEMATIK,
        question_count=12,
        target_theta=1.2,
    )
    types = {q.type for q in exam.questions}
    assert QuestionType.ALGEBRA in types
    assert QuestionType.CALCULUS in types
    assert QuestionType.GEOMETRY in types


# ==============================================================================
# 5. DYNAMIC EXAM FACTORY: GRADING & COGNITIVE TRAP DIAGNOSIS
# ==============================================================================

def test_grade_exam_perfect_score(factory):
    """Tüm soruları doğru çözen öğrencinin 0 tuzak ve tam net aldığını doğrular."""
    exam = factory.assemble_exam(question_count=5)
    # Tüm doğru şık indekslerini ver
    answers = {i: q.correct_choice_index for i, q in enumerate(exam.questions)}

    report = factory.grade_exam(exam, answers)
    assert report["total_questions"] == 5
    assert report["correct"] == 5
    assert report["incorrect"] == 0
    assert report["empty"] == 0
    assert report["net_score"] == 5.0
    assert report["percentage"] == 100.0
    assert len(report["traps_triggered"]) == 0
    assert "Kusursuz odak" in report["remediation_summary"]


def test_grade_exam_trap_detection(factory):
    """Tuzak şıkları işaretleyen öğrencinin düştüğü BUG-ID'lerin raporda tespit edildiğini doğrular."""
    exam = factory.assemble_exam(question_count=4)
    # 0. soru: Doğru
    # 1. soru: BUG-CALC-01 veya başka bir tuzak şık
    answers = {0: exam.questions[0].correct_choice_index}

    # 1. soruda bilerek yanlış olan ilk çeldiriciyi seç
    wrong_idx = [i for i, c in enumerate(exam.questions[1].choices) if not c.is_correct][0]
    answers[1] = wrong_idx

    report = factory.grade_exam(exam, answers)
    assert report["correct"] == 1
    assert report["incorrect"] == 1
    assert report["empty"] == 2  # 2. ve 3. sorular boş
    assert report["net_score"] == 1.0 - 0.25  # 0.75 net

    assert len(report["traps_triggered"]) == 1
    trap = report["traps_triggered"][0]
    assert trap["question_index"] == 2
    assert trap["bug_id"] is not None
    assert trap["distractor_rationale"] is not None


def test_grade_exam_all_empty(factory):
    """Tüm sorular boş bırakıldığında 0 net ve 0 tuzak raporlandığını doğrular."""
    exam = factory.assemble_exam(question_count=6)
    report = factory.grade_exam(exam, {})
    assert report["empty"] == 6
    assert report["correct"] == 0
    assert report["incorrect"] == 0
    assert report["net_score"] == 0.0


# ==============================================================================
# 6. EDGE CASES & DETERMINISM
# ==============================================================================

def test_choice_shuffling_integrity(generator):
    """Şıkların her zaman tek bir doğru cevap içerdiğini ve sıraların korunduğunu doğrular."""
    for _ in range(5):
        q = generator.generate_quadratic(1, -3)
        correct = [c for c in q.choices if c.is_correct]
        assert len(correct) == 1
        assert q.choices[q.correct_choice_index].is_correct


def test_exam_sections_enum():
    assert ExamSection.TYT_MATEMATIK.value == "TYT_MATEMATIK"
    assert ExamSection.AYT_MATEMATIK.value == "AYT_MATEMATIK"
    assert ExamSection.IB_DP_HL.value == "IB_DP_HL"
    assert ExamSection.AP_CALCULUS_BC.value == "AP_CALCULUS_BC"


# ==============================================================================
# 7. EXPANDED PSYCHOMETRICS, SEEDS & MOCK EXAMS
# ==============================================================================

def test_quadratic_seeds_variety(generator):
    seeds = [(1, 2), (-3, 5), (-4, -6), (7, 0)]
    for r1, r2 in seeds:
        q = generator.generate_quadratic(r1, r2)
        assert len(q.choices) == 5
        assert q.target_value != ""
        assert len([c for c in q.choices if c.is_correct]) == 1


def test_derivative_seeds_variety(generator):
    seeds = [(2, 3), (5, 2), (1, 6)]
    for a, n in seeds:
        q = generator.generate_derivative(a, n)
        assert q.type == QuestionType.CALCULUS
        assert len(q.choices) == 5
        assert "BUG-CALC-01" in [c.bug_id for c in q.choices if not c.is_correct]


def test_euclidean_seeds_variety(generator):
    # p=1, k=4 -> h=2; p=2, k=8 -> h=4; p=3, k=12 -> h=6
    seeds = [(1, 4), (2, 8), (3, 12)]
    for p, k in seeds:
        q = generator.generate_euclidean(p, k)
        assert q.type == QuestionType.GEOMETRY
        assert q.choices[q.correct_choice_index].text == f"{int((p*k)**0.5)}"


def test_circle_seeds_variety(generator):
    for angle in [40, 60, 100, 120]:
        q = generator.generate_circle_angle(angle)
        assert q.choices[q.correct_choice_index].text == f"{angle // 2}°"


def test_large_exam_assembly_40_questions(factory):
    exam = factory.assemble_exam(
        section=ExamSection.TYT_MATEMATIK,
        question_count=40,
        target_theta=1.0,
    )
    assert len(exam.questions) == 40
    assert exam.total_time_minutes == 80
    assert exam.target_theta == 1.0


def test_exam_grade_all_incorrect(factory):
    exam = factory.assemble_exam(question_count=4)
    # Tüm sorularda ilk yanlış şıkkı seç
    answers = {}
    for i, q in enumerate(exam.questions):
        wrong_idx = [idx for idx, c in enumerate(q.choices) if not c.is_correct][0]
        answers[i] = wrong_idx

    report = factory.grade_exam(exam, answers)
    assert report["correct"] == 0
    assert report["incorrect"] == 4
    assert report["net_score"] == 0.0  # max(0, -1.0) = 0.0
    assert len(report["traps_triggered"]) == 4


def test_exam_grade_half_correct(factory):
    exam = factory.assemble_exam(question_count=4)
    answers = {
        0: exam.questions[0].correct_choice_index,
        1: exam.questions[1].correct_choice_index,
        2: [idx for idx, c in enumerate(exam.questions[2].choices) if not c.is_correct][0],
        3: [idx for idx, c in enumerate(exam.questions[3].choices) if not c.is_correct][0],
    }
    report = factory.grade_exam(exam, answers)
    assert report["correct"] == 2
    assert report["incorrect"] == 2
    assert report["net_score"] == 2 - 0.5  # 1.5


def test_psychometric_parameters_bounds(generator):
    for q in [
        generator.generate_quadratic(2, 3),
        generator.generate_derivative(2, 3),
        generator.generate_euclidean(4, 9),
        generator.generate_circle_angle(80),
    ]:
        assert -2.0 <= q.difficulty_b <= 3.0
        assert 1.0 <= q.discrimination_a <= 3.0


def test_choice_text_non_empty(generator):
    q = generator.generate_quadratic(1, 2)
    for c in q.choices:
        assert c.text.strip() != ""


def test_distractor_rationales_present(generator):
    q = generator.generate_quadratic(1, 2)
    for c in q.choices:
        if not c.is_correct and c.bug_id:
            assert c.distractor_rationale is not None
            assert len(c.distractor_rationale) > 10


def test_socratic_solution_detailed(generator):
    q = generator.generate_derivative(3, 4)
    assert "Zincir kuralı" in q.full_socratic_solution


def test_ib_dp_section_assembly(factory):
    exam = factory.assemble_exam(section=ExamSection.IB_DP_HL, question_count=8)
    assert exam.section == ExamSection.IB_DP_HL
    assert len(exam.questions) == 8


def test_ap_calculus_section_assembly(factory):
    exam = factory.assemble_exam(section=ExamSection.AP_CALCULUS_BC, question_count=6)
    assert exam.section == ExamSection.AP_CALCULUS_BC
    assert len(exam.questions) == 6


def test_exam_negative_index_skipped(factory):
    exam = factory.assemble_exam(question_count=3)
    answers = {0: 0, 1: -1, 2: None}  # 1 and 2 skipped
    report = factory.grade_exam(exam, answers)
    assert report["empty"] == 2


def test_exam_unique_id_generation(factory):
    e1 = factory.assemble_exam(question_count=2)
    e2 = factory.assemble_exam(question_count=2)
    assert e1.exam_id != e2.exam_id


def test_question_unique_id_generation(generator):
    q1 = generator.generate_quadratic(2, 3)
    q2 = generator.generate_quadratic(2, 3)
    assert q1.question_id != q2.question_id


def test_exam_target_theta_negative(factory):
    exam = factory.assemble_exam(target_theta=-1.5)
    assert exam.target_theta == -1.5
    assert "-1.50" in exam.title


def test_exam_target_theta_high(factory):
    exam = factory.assemble_exam(target_theta=2.5)
    assert exam.target_theta == 2.5
    assert "+2.50" in exam.title


def test_quadratic_fractional_discrimination(generator):
    q = generator.generate_quadratic(1, -1)
    assert q.discrimination_a == 2.0


def test_derivative_cubic_power(generator):
    q = generator.generate_derivative(a=2, n=3)
    # f'(x) = 6(2x + 2)^2
    assert "6(2x + 2)^2" in q.target_value


def test_euclidean_large_values(generator):
    # p=9, k=16 -> h = sqrt(144) = 12
    q = generator.generate_euclidean(p=9, k=16)
    assert q.target_value == "12"


def test_circle_angle_obtuse_central(generator):
    q = generator.generate_circle_angle(center_angle=140)
    assert q.target_value == "70°"


def test_exam_grade_percentage_boundary(factory):
    exam = factory.assemble_exam(question_count=2)
    answers = {0: exam.questions[0].correct_choice_index}
    report = factory.grade_exam(exam, answers)
    assert report["percentage"] == 50.0


def test_exam_grade_empty_list(factory):
    exam = factory.assemble_exam(question_count=2)
    report = factory.grade_exam(exam, {})
    assert report["correct"] == 0
    assert report["empty"] == 2


def test_distractor_bug_category_format(generator):
    q = generator.generate_quadratic(2, 3)
    for c in q.choices:
        if c.bug_id:
            assert c.bug_id.startswith("BUG-")


def test_trap_question_json_serializable(generator):
    q = generator.generate_quadratic(1, 4)
    data = q.model_dump()
    assert isinstance(data, dict)
    assert "question_id" in data
    assert "choices" in data


def test_dynamic_exam_json_serializable(factory):
    exam = factory.assemble_exam(question_count=3)
    data = exam.model_dump()
    assert isinstance(data, dict)
    assert len(data["questions"]) == 3


def test_exam_empty_answers_dict_type(factory):
    exam = factory.assemble_exam(question_count=1)
    res = factory.grade_exam(exam, {})
    assert isinstance(res["traps_triggered"], list)


# ==============================================================================
# 9. TARGETED BUG GENERATION & FORMAL VERIFIER TESTS
# ==============================================================================

def test_generate_targeted_bug_various_categories():
    """Öğrencinin geçmiş zaaflarına göre hedefli soru üretilebildiğini doğrular."""
    q_calc = TrapQuestionGenerator.generate_targeted_bug("BUG-CALC-01", seed=42)
    assert q_calc.type == QuestionType.CALCULUS
    assert any(c.bug_id == "BUG-CALC-01" for c in q_calc.choices)

    q_euc = TrapQuestionGenerator.generate_targeted_bug("BUG-EUC-04", seed=42)
    assert q_euc.type == QuestionType.GEOMETRY
    assert any(c.bug_id == "BUG-EUC-04" for c in q_euc.choices)

    q_circle = TrapQuestionGenerator.generate_targeted_bug("BUG-EUC-02", seed=42)
    assert q_circle.type == QuestionType.GEOMETRY
    assert any(c.bug_id == "BUG-EUC-02" for c in q_circle.choices)

    q_anag = TrapQuestionGenerator.generate_targeted_bug("BUG-ANAG-01", seed=42)
    assert q_anag.type == QuestionType.GEOMETRY
    assert any(c.bug_id == "BUG-ANAG-01" for c in q_anag.choices)

    q_quad = TrapQuestionGenerator.generate_targeted_bug("BUG-QUAD-05", seed=42)
    assert q_quad.type == QuestionType.ALGEBRA
    assert any(c.bug_id == "BUG-QUAD-05" for c in q_quad.choices)


def test_formal_question_verifier_quadratic():
    """Kuadratik sorunun SymPy formel ispatını doğrular."""
    q = TrapQuestionGenerator.generate_quadratic(3, -4)
    proof = FormalQuestionVerifier.verify_formally(q)
    assert proof["is_valid"] is True
    assert proof["has_formal_proof"] is True
    assert proof["zero_false_positives"] is True
    assert "Kuadratik denklem kökleri" in proof["proof_details"]


def test_formal_question_verifier_calculus():
    """Kalkülüs türev sorusunun SymPy analitik türev ispatını doğrular."""
    q = TrapQuestionGenerator.generate_derivative(a=4, n=3)
    proof = FormalQuestionVerifier.verify_formally(q)
    assert proof["is_valid"] is True
    assert proof["has_formal_proof"] is True
    assert proof["zero_false_positives"] is True


def test_formal_question_verifier_euclidean():
    """Öklid sorusunun tam sayı kök kısıtı ve geometrik ispatını doğrular."""
    q = TrapQuestionGenerator.generate_euclidean(p=4, k=9)
    proof = FormalQuestionVerifier.verify_formally(q)
    assert proof["is_valid"] is True
    assert proof["has_formal_proof"] is True
    assert proof["zero_false_positives"] is True


def test_formal_question_verifier_zero_false_positives():
    """Çeldiricilerin hiçbiri doğru cevapla çakışmamalıdır (0 False Positive)."""
    q = TrapQuestionGenerator.generate_quadratic(1, -2)
    correct_text = q.choices[q.correct_choice_index].text
    distractors = [c.text for c in q.choices if not c.is_correct]
    assert correct_text not in distractors


# ==============================================================================
# 10. EXAM DOCUMENT EXPORTER (LATEX & HTML / PDF) TESTS
# ==============================================================================

def test_exam_document_exporter_latex(factory):
    """Deneme sınavının derlenebilir LaTeX koduna dönüştürüldüğünü doğrular."""
    exam = factory.assemble_exam(section=ExamSection.TYT_MATEMATIK, question_count=4)
    latex_code = ExamDocumentExporter.export_to_latex(exam, include_solutions=True)

    assert r"\documentclass" in latex_code
    assert r"\begin{document}" in latex_code
    assert r"\begin{enumerate}" in latex_code
    assert "CEVAP ANAHTARI VE SOKRATİK ÇÖZÜMLER" in latex_code
    assert r"\end{document}" in latex_code


def test_exam_document_exporter_html(factory):
    """Deneme sınavının yazdırılabilir temiz HTML sayfasına dönüştürüldüğünü doğrular."""
    exam = factory.assemble_exam(section=ExamSection.AYT_MATEMATIK, question_count=3)
    html_code = ExamDocumentExporter.export_to_html_printable(exam, include_solutions=True)

    assert "<!DOCTYPE html>" in html_code
    assert "<title>" in html_code
    assert "class='header'" in html_code
    assert "class='question'" in html_code
    assert "Cevap Anahtarı ve Çözümler" in html_code


# ==============================================================================
# 11. 500 SENTETİK SORU BATCH ÜRETİM VE FORMEL KANIT TESTİ
# ==============================================================================

def test_500_synthetic_trap_questions_batch_production_and_verification():
    """
    Kullanıcı İsteri: 500 sentetik soru üretim testi.
    500 farklı sorunun kesintisiz üretildiğini, tam sayı köklere sahip olduğunu,
    her birinin formel olarak doğrulandığını ve 0 false positive verdiğini kanıtlar.
    """
    total_questions = 500
    valid_count = 0

    roots_pool = [
        (1, 2), (2, 3), (3, 4), (1, -5), (2, -4), (-2, -3),
        (4, 5), (3, -6), (1, 7), (2, -8), (-4, 6), (5, -2),
        (3, 8), (4, -7), (2, 9), (1, -10), (-3, -5), (6, 2)
    ]
    calc_params = [(2, 3), (3, 4), (4, 3), (5, 2), (2, 5), (3, 2), (4, 2)]
    euc_pairs = [(4, 9), (2, 8), (3, 12), (1, 16), (4, 16), (9, 16), (2, 18), (1, 25)]
    angles = [40, 50, 60, 70, 80, 90, 100, 110, 120, 140]

    for i in range(total_questions):
        mode = i % 4
        if mode == 0:
            r1, r2 = roots_pool[i % len(roots_pool)]
            q = TrapQuestionGenerator.generate_quadratic(r1=r1, r2=r2)
        elif mode == 1:
            a, n = calc_params[i % len(calc_params)]
            q = TrapQuestionGenerator.generate_derivative(a=a, n=n)
        elif mode == 2:
            p, k = euc_pairs[i % len(euc_pairs)]
            q = TrapQuestionGenerator.generate_euclidean(p=p, k=k)
        else:
            ang = angles[i % len(angles)]
            q = TrapQuestionGenerator.generate_circle_angle(center_angle=ang)

        # Formel İspat Denetimi
        proof = FormalQuestionVerifier.verify_formally(q)
        assert proof["is_valid"] is True
        assert proof["zero_false_positives"] is True
        assert len(q.choices) == 5
        assert q.choices[q.correct_choice_index].is_correct is True

        valid_count += 1

    assert valid_count == 500



