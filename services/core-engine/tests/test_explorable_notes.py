import pytest
from app.curriculum.explorable_notes_repository import (
    ExplorableNotesRepository,
    ExplorableNoteCard,
    MiniExercise,
)


@pytest.fixture
def repo():
    return ExplorableNotesRepository()


def test_dag_is_acyclic_and_valid(repo):
    assert repo.validate_dag_acyclic() is True


def test_all_notes_have_one_sentence_intuition(repo):
    notes = repo.get_all_notes()
    assert len(notes) >= 15
    for note in notes:
        assert len(note.one_sentence_intuition.strip()) > 0
        word_count = len(note.one_sentence_intuition.split())
        assert word_count <= 35, f"{note.node_id} sezgi cümlesi 35 kelimeden uzun: {word_count}"


def test_all_notes_have_exactly_three_step_recipe(repo):
    notes = repo.get_all_notes()
    for note in notes:
        assert len(note.solution_recipe) == 3, f"{note.node_id} reçetesi 3 adım olmalı!"
        for step in note.solution_recipe:
            assert len(step.strip()) > 5


def test_all_notes_have_mini_exercise(repo):
    notes = repo.get_all_notes()
    for note in notes:
        ex = note.mini_exercise
        assert len(ex.prompt.strip()) > 0
        assert len(ex.expected_answer.strip()) > 0
        assert len(ex.explanation.strip()) > 0


def test_prerequisite_chain_n15(repo):
    chain = repo.get_prerequisite_chain("N15")
    ids = [c.node_id for c in chain]
    # N01 must come before N04, and N04 must come before N15
    assert "N01" in ids
    assert "N04" in ids
    assert "N15" in ids
    assert ids[-1] == "N15"
    assert ids.index("N01") < ids.index("N04")
    assert ids.index("N04") < ids.index("N15")


def test_prerequisite_chain_calc04(repo):
    chain = repo.get_prerequisite_chain("CALC04")
    ids = [c.node_id for c in chain]
    assert "N01" in ids
    assert "N04" in ids
    assert "CALC01" in ids
    assert "CALC02" in ids
    assert "CALC04" in ids
    assert ids[-1] == "CALC04"


def test_prerequisite_chain_root_node(repo):
    chain = repo.get_prerequisite_chain("N01")
    assert len(chain) == 1
    assert chain[0].node_id == "N01"


def test_unknown_node_returns_none_and_empty_chain(repo):
    assert repo.get_note("NON_EXISTENT") is None
    assert repo.get_prerequisite_chain("NON_EXISTENT") == []


def test_verify_mini_exercise_exact_match(repo):
    is_correct, msg = repo.verify_mini_exercise("N04", "3")
    assert is_correct is True
    assert "Tebrikler" in msg


def test_verify_mini_exercise_cas_equivalent(repo):
    # N02 expected answer is 2x+10; entering 10 + 2x should pass via CAS
    is_correct, msg = repo.verify_mini_exercise("N02", "10 + 2*x")
    assert is_correct is True
    assert "Cebirsel olarak denk" in msg or "Tebrikler" in msg


def test_verify_mini_exercise_incorrect(repo):
    is_correct, msg = repo.verify_mini_exercise("N04", "99")
    assert is_correct is False
    assert "Tekrar dene" in msg
    assert "İpucu" in msg


def test_all_prerequisites_exist_in_catalog(repo):
    notes = repo.get_all_notes()
    all_ids = {n.node_id for n in notes}
    for n in notes:
        for p in n.prerequisites:
            assert p in all_ids, f"{n.node_id} önkoşulu {p} katalogda yok!"


def test_cycle_detection_raises_error(repo):
    # Artificially inject circular dependency: N01 -> N02 -> N01
    repo._notes["N01"].prerequisites.append("N02")
    with pytest.raises(ValueError, match="döngü tespit edildi"):
        repo.validate_dag_acyclic()
    # Cleanup
    repo._notes["N01"].prerequisites.remove("N02")


def test_missing_prerequisite_raises_error(repo):
    repo._notes["N01"].prerequisites.append("GHOST_NODE")
    with pytest.raises(ValueError, match="kataloğunda bulunamadı"):
        repo.validate_dag_acyclic()
    # Cleanup
    repo._notes["N01"].prerequisites.remove("GHOST_NODE")


def test_deep_insight_present_in_all_cards(repo):
    notes = repo.get_all_notes()
    for note in notes:
        assert len(note.deep_insight.strip()) > 0


def test_get_all_notes_count(repo):
    notes = repo.get_all_notes()
    assert len(notes) == 15


def test_trig_chain_hierarchy(repo):
    chain = repo.get_prerequisite_chain("TRIG02")
    ids = [c.node_id for c in chain]
    assert "N01" in ids
    assert "TRIG01" in ids
    assert "TRIG02" in ids
    assert ids.index("TRIG01") < ids.index("TRIG02")


def test_parabola_chain_hierarchy(repo):
    chain = repo.get_prerequisite_chain("N20")
    ids = [c.node_id for c in chain]
    assert "N15" in ids
    assert "N20" in ids
    assert ids.index("N15") < ids.index("N20")
