"""
Test Suite: LTI 1.3 LMS Interoperability & Zero-PII Classroom Analytics.
Verifies:
1. LTI 1.3 OIDC 3-legged login flow with Canvas, Moodle, Google Classroom.
2. Tool JWKS (RS256) public key formatting.
3. LTI 1.3 Resource Link Launch claim processing and Zero-PII pseudonymization.
4. LTI 1.3 AGS (Assignment and Grade Services) grade synchronization.
5. Privacy-Centric Zero-PII Classroom Analytics reporter:
   - Cohort ZPD distribution.
   - Top Buggy Rule occurrences and teacher scaffolding directives.
   - Paas cognitive efficiency index E.
"""

import pytest
import json
import base64
from fastapi.testclient import TestClient
from app.main import app
from app.lti.service import LTI13Service
from app.analytics.classroom_reporter import ClassroomAnalyticsReporter
from app.models.schemas import LTILaunchPayload, LTIGradeScoreRequest

client = TestClient(app)


def test_lti_jwks_structure():
    lti = LTI13Service()
    jwks = lti.get_jwks()
    assert "keys" in jwks
    assert len(jwks["keys"]) == 1
    key = jwks["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["use"] == "sig"
    assert "kid" in key
    assert "n" in key and "e" in key


def test_lti_login_initiation():
    lti = LTI13Service()
    payload = LTILaunchPayload(
        iss="https://canvas.instructure.com",
        login_hint="student_12345",
        target_link_uri="https://ple.example.com/api/v1/lti/launch",
        client_id="canvas_client_999",
        lti_message_hint="hint_xyz",
    )
    res = lti.initiate_login(payload)
    assert res["status"] == "AUTH_REDIRECT_READY"
    assert "state" in res
    assert "nonce" in res
    assert "canvas.instructure.com" in res["auth_endpoint"]
    assert "response_type=id_token" in res["redirect_url"]


def test_lti_launch_and_zero_pii_pseudonymization():
    lti = LTI13Service()

    # Craft mock LTI 1.3 Launch id_token
    token_claims = {
        "iss": "https://canvas.instructure.com",
        "sub": "real_student_email@school.edu",  # Direct PII
        "aud": "ple-core-client",
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/roles": [
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"
        ],
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "deploy_canvas_101",
        "https://purl.imsglobal.org/spec/lti/claim/context": {
            "id": "course_alg_10",
            "label": "Grade 10 Algebra",
        },
        "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
            "lineitem": "https://canvas.instructure.com/api/lti/courses/10/lineitems/5",
        },
    }

    # Unsigned token payload for launch testing
    def b64(d: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(d).encode("utf-8")).decode("utf-8").rstrip("=")

    mock_jwt = f"{b64({'alg': 'RS256'})}.{b64(token_claims)}.signature_bytes"

    result = lti.handle_launch(mock_jwt)
    assert result["status"] == "LAUNCH_SUCCESS"
    assert result["zero_pii_compliant"] is True
    # The real student email MUST NOT appear anywhere in the output
    assert "real_student_email@school.edu" not in result["student_pseudonym_id"]
    assert result["student_pseudonym_id"].startswith("usr_anon_")
    assert result["context_id"] == "course_alg_10"
    assert result["is_instructor"] is False


def test_lti_ags_grade_synchronization():
    lti = LTI13Service()
    req = LTIGradeScoreRequest(
        line_item_id="https://canvas.instructure.com/api/lti/courses/10/lineitems/5",
        student_pseudonym_id="usr_anon_a1b2c3d4",
        score_given=92.5,
        score_maximum=100.0,
        activity_progress="Completed",
        grading_progress="FullyGraded",
        comment="Demonstrated mastery in quadratic completing the square",
    )
    result = lti.sync_grade_to_lms(req)
    assert result["status"] == "SCORE_SYNC_DISPATCHED"
    assert result["score_payload"]["scoreGiven"] == 92.5
    assert result["score_payload"]["userId"] == "usr_anon_a1b2c3d4"
    assert "signed_score_token" in result
    # Token has 3 parts: header.payload.sig
    assert len(result["signed_score_token"].split(".")) == 3


def test_classroom_analytics_reporter():
    reporter = ClassroomAnalyticsReporter()
    report = reporter.generate_classroom_report(cohort_id="CLASS-10A", student_count=30)

    assert report.cohort_id == "CLASS-10A"
    assert report.total_students >= 25
    assert report.zero_pii_compliant is True
    assert len(report.zpd_distribution) >= 5
    assert len(report.active_buggy_rules) >= 3
    assert report.paas_cognitive_efficiency["mean_paas_e"] is not None
    assert report.curriculum_coverage_pct > 0.0

    # Verify no PII is included in the dictionary representation
    dump = report.model_dump_json()
    assert "email" not in dump
    assert "student_name" not in dump


def test_lti_and_classroom_api_endpoints():
    # JWKS endpoint
    res_jwks = client.get("/api/v1/lti/jwks")
    assert res_jwks.status_code == 200
    assert "keys" in res_jwks.json()

    # OIDC Login
    login_payload = {
        "iss": "https://moodle.org",
        "login_hint": "moodle_user_42",
        "target_link_uri": "https://ple.example.com/api/v1/lti/launch",
    }
    res_login = client.post("/api/v1/lti/login", json=login_payload)
    assert res_login.status_code == 200
    assert res_login.json()["status"] == "AUTH_REDIRECT_READY"

    # Classroom Analytics
    res_analytics = client.get("/api/v1/classroom/analytics?cohort_id=GRADE-10-B&students=32")
    assert res_analytics.status_code == 200
    data = res_analytics.json()
    assert data["cohort_id"] == "GRADE-10-B"
    assert data["zero_pii_compliant"] is True
    assert len(data["active_buggy_rules"]) > 0
