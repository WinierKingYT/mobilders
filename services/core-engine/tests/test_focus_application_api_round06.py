from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import (
    create_focus_router,
    install_focus_api,
)
from app.focus_domain.application import (
    FocusAttemptInputKind,
    FocusServiceFacade,
)
from app.focus_domain.models import AttemptJudgment, KCId, StageId
from app.focus_domain.persistence import FocusEpisodePersistenceService


def _service():
    return FocusServiceFacade(FocusEpisodePersistenceService())


def _start(service, episode_id="api-ep"):
    return service.start_ctqf1_episode(
        episode_id=episode_id,
        b=5,
        c=6,
        idempotency_key=f"{episode_id}:start",
    )


def test_server_derives_ctqf1_context_and_never_trusts_client_factor_pair_truth():
    service = _service()
    started = _start(service)

    assert started.stream_version == 1
    assert started.state.current_stage == StageId.S1_FACTOR
    assert started.state.workspace_kc == KCId.F2
    assert started.state.task_context.factor_pair == (2, 3)
    assert started.state.task_context.expected_roots == (-3, -2)


def test_correct_s1_factor_pair_advances_server_owned_stage_and_workspace_kc():
    service = _service()
    _start(service)

    result = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    assert result.judgment == AttemptJudgment.VALID_EXPECTED
    assert result.stream_version == 2
    assert result.state.current_stage == StageId.S2_BRANCH
    assert result.state.workspace_kc == KCId.Z1
    assert result.decision.action.value == "ADVANCE"


def test_one_correct_s2_branch_is_valid_incomplete_and_does_not_advance():
    service = _service()
    _start(service)
    service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    result = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.BRANCH_DECOMPOSITION,
        raw_input="x+2=0",
        idempotency_key="api-ep:a2",
        expected_previous_sequence=2,
    )

    assert result.judgment == AttemptJudgment.VALID_INCOMPLETE
    assert result.state.current_stage == StageId.S2_BRANCH
    assert result.state.workspace_kc == KCId.Z1
    assert result.decision.action.value == "REQUEST_COMPLETION"
    assert result.composite_failure is not None


def test_complete_solution_set_at_s2_is_server_judged_valid_shortcut():
    service = _service()
    _start(service)
    service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    result = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.SOLUTION_SET,
        raw_input=["x=-2", "x=-3"],
        idempotency_key="api-ep:a2",
        expected_previous_sequence=2,
    )

    assert result.judgment == AttemptJudgment.VALID_SHORTCUT
    assert result.decision.action.value == "COMPLETE_TASK"
    assert result.state.phase.value == "COMPLETED"


def test_wrong_factor_pair_produces_server_side_observation_and_probe_request():
    service = _service()
    _start(service)

    result = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[1, 6],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    assert result.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-FACTOR-PAIR-SUM-MISMATCH" in result.observations
    assert result.decision.action.value == "REQUEST_PROBE"
    assert result.decision.probe_id == "PR-F2-01"


def test_attempt_retry_after_later_progress_returns_historical_original_result():
    service = _service()
    _start(service)
    first = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )
    assert first.stream_version == 2

    second = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.BRANCH_DECOMPOSITION,
        raw_input="x+2=0 or x+3=0",
        idempotency_key="api-ep:a2",
        expected_previous_sequence=2,
    )
    assert second.stream_version == 3
    assert second.state.current_stage == StageId.S3_SOLVE_FACTOR_EQUATIONS

    retried = service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    assert retried.stream_version == 2
    assert retried.state.current_stage == StageId.S2_BRANCH
    assert retried.judgment == AttemptJudgment.VALID_EXPECTED


def test_same_attempt_idempotency_key_with_different_raw_command_conflicts():
    service = _service()
    _start(service)
    service.submit_attempt(
        episode_id="api-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="api-ep:a1",
        expected_previous_sequence=1,
    )

    try:
        service.submit_attempt(
            episode_id="api-ep",
            input_kind=FocusAttemptInputKind.FACTOR_PAIR,
            raw_input=[1, 6],
            idempotency_key="api-ep:a1",
            expected_previous_sequence=1,
        )
    except Exception as exc:
        assert "different Focus command" in str(exc)
    else:
        raise AssertionError("Expected idempotency conflict")


def _client(enabled=True):
    app = FastAPI()
    install_focus_api(app, enabled=enabled, service=_service())
    return TestClient(app)


def test_feature_flag_disabled_registers_no_focus_routes():
    client = _client(enabled=False)
    response = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "x"},
        json={"episode_id": "e", "b": 5, "c": 6},
    )
    assert response.status_code == 404


def test_api_start_get_and_attempt_contract():
    client = _client(enabled=True)

    started = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http:start"},
        json={"episode_id": "http-1", "b": 5, "c": 6},
    )
    assert started.status_code == 201
    assert started.json()["stream_version"] == 1

    fetched = client.get("/focus/v1/episodes/http-1")
    assert fetched.status_code == 200
    assert fetched.json()["state"]["current_stage"] == "S1_FACTOR"

    attempt = client.post(
        "/focus/v1/episodes/http-1/attempts",
        headers={
            "Idempotency-Key": "http:a1",
            "X-Focus-Expected-Sequence": "1",
        },
        json={"input_kind": "FACTOR_PAIR", "input": [2, 3]},
    )
    assert attempt.status_code == 200
    body = attempt.json()
    assert body["judgment"] == "VALID_EXPECTED"
    assert body["state"]["current_stage"] == "S2_BRANCH"


def test_api_stale_stream_version_maps_to_409():
    client = _client(enabled=True)
    client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http:start"},
        json={"episode_id": "http-1", "b": 5, "c": 6},
    )
    ok = client.post(
        "/focus/v1/episodes/http-1/attempts",
        headers={
            "Idempotency-Key": "http:a1",
            "X-Focus-Expected-Sequence": "1",
        },
        json={"input_kind": "FACTOR_PAIR", "input": [2, 3]},
    )
    assert ok.status_code == 200

    stale = client.post(
        "/focus/v1/episodes/http-1/attempts",
        headers={
            "Idempotency-Key": "http:a2",
            "X-Focus-Expected-Sequence": "1",
        },
        json={"input_kind": "BRANCH_DECOMPOSITION", "input": "x+2=0"},
    )
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "FOCUS_STREAM_CONFLICT"


def test_api_invalid_alpha_problem_is_422_not_cognitive_failure():
    client = _client(enabled=True)
    response = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http:start"},
        json={"episode_id": "bad-task", "b": 4, "c": 4},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "FOCUS_UNSUPPORTED_TASK"


def test_api_missing_concurrency_or_idempotency_headers_is_422():
    client = _client(enabled=True)
    client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http:start"},
        json={"episode_id": "http-1", "b": 5, "c": 6},
    )
    response = client.post(
        "/focus/v1/episodes/http-1/attempts",
        json={"input_kind": "FACTOR_PAIR", "input": [2, 3]},
    )
    assert response.status_code == 422


def test_public_api_supports_full_expected_s1_to_s4_path():
    service = _service()
    _start(service, episode_id="full-path")

    s1 = service.submit_attempt(
        episode_id="full-path",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="full-path:a1",
        expected_previous_sequence=1,
    )
    assert s1.state.current_stage == StageId.S2_BRANCH

    s2 = service.submit_attempt(
        episode_id="full-path",
        input_kind=FocusAttemptInputKind.BRANCH_DECOMPOSITION,
        raw_input="x+2=0 or x+3=0",
        idempotency_key="full-path:a2",
        expected_previous_sequence=2,
    )
    assert s2.judgment == AttemptJudgment.VALID_EXPECTED
    assert s2.state.current_stage == StageId.S3_SOLVE_FACTOR_EQUATIONS
    assert s2.state.workspace_kc == KCId.Q1

    s3 = service.submit_attempt(
        episode_id="full-path",
        input_kind=FocusAttemptInputKind.BRANCH_WORK,
        raw_input={
            "x+2=0": "x=-2",
            "x+3=0": "x=-3",
        },
        idempotency_key="full-path:a3",
        expected_previous_sequence=3,
    )
    assert s3.judgment == AttemptJudgment.VALID_EXPECTED
    assert s3.state.current_stage == StageId.S4_COMPLETE_SOLUTION_SET

    s4 = service.submit_attempt(
        episode_id="full-path",
        input_kind=FocusAttemptInputKind.SOLUTION_SET,
        raw_input=["x=-2", "x=-3"],
        idempotency_key="full-path:a4",
        expected_previous_sequence=4,
    )
    assert s4.judgment == AttemptJudgment.VALID_EXPECTED
    assert s4.decision.action.value == "COMPLETE_TASK"
    assert s4.state.phase.value == "COMPLETED"
    assert s4.stream_version == 5


def test_s3_one_branch_work_item_is_valid_incomplete():
    service = _service()
    _start(service, episode_id="partial-s3")
    service.submit_attempt(
        episode_id="partial-s3",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="partial-s3:a1",
        expected_previous_sequence=1,
    )
    service.submit_attempt(
        episode_id="partial-s3",
        input_kind=FocusAttemptInputKind.BRANCH_DECOMPOSITION,
        raw_input="x+2=0 or x+3=0",
        idempotency_key="partial-s3:a2",
        expected_previous_sequence=2,
    )

    result = service.submit_attempt(
        episode_id="partial-s3",
        input_kind=FocusAttemptInputKind.BRANCH_WORK,
        raw_input={"x+2=0": "x=-2"},
        idempotency_key="partial-s3:a3",
        expected_previous_sequence=3,
    )
    assert result.judgment == AttemptJudgment.VALID_INCOMPLETE
    assert result.state.current_stage == StageId.S3_SOLVE_FACTOR_EQUATIONS
    assert result.decision.action.value == "REQUEST_COMPLETION"
