-- ====================================================================
-- Kişisel Öğrenme Motoru (Personal Learning Engine) PostgreSQL 15 DDL
-- Sıfır-PII (Zero Personally Identifiable Information) Mimarisi
-- Ref: 24-SECURITY-PRIVACY-AND-DATA-GOVERNANCE.md & ARCH-PLE-2026-V1
-- ====================================================================

-- Gerekli eklentiler
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Öğrenci Anonim Bilişsel Durumu Tablosu
CREATE TABLE IF NOT EXISTS student_cognitive_state (
    student_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    overall_theta DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    standard_error DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    circadian_lock_until TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_lock_until ON student_cognitive_state(circadian_lock_until);

-- 2. Bilgi Grafı Düğümleri Tablosu (20 Çekirdek MVP Düğümü)
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    node_id VARCHAR(10) PRIMARY KEY,
    canonical_code VARCHAR(120) NOT NULL UNIQUE,
    title VARCHAR(150) NOT NULL,
    level INTEGER NOT NULL DEFAULT 0,
    default_difficulty_b DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    discrimination_a DOUBLE PRECISION NOT NULL DEFAULT 1.5,
    description TEXT NULL
);

-- 3. Önkoşul Bağımlılıkları Tablosu
CREATE TABLE IF NOT EXISTS node_prerequisites (
    parent_node_id VARCHAR(10) NOT NULL REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
    prerequisite_node_id VARCHAR(10) NOT NULL REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
    dependency_type VARCHAR(10) NOT NULL DEFAULT 'STRICT', -- 'STRICT' veya 'SOFT'
    PRIMARY KEY (parent_node_id, prerequisite_node_id)
);

-- 4. Düğüm Bazlı Öğrenci Ustalık ve FSRS Hafıza Durumu
CREATE TABLE IF NOT EXISTS node_mastery (
    id BIGSERIAL PRIMARY KEY,
    student_uuid UUID NOT NULL REFERENCES student_cognitive_state(student_uuid) ON DELETE CASCADE,
    node_id VARCHAR(10) NOT NULL REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
    p_mastery DOUBLE PRECISION NOT NULL DEFAULT 0.20,
    fsrs_stability DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    fsrs_difficulty DOUBLE PRECISION NOT NULL DEFAULT 5.0,
    next_review_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_node UNIQUE (student_uuid, node_id)
);

CREATE INDEX IF NOT EXISTS idx_mastery_student ON node_mastery(student_uuid);
CREATE INDEX IF NOT EXISTS idx_mastery_review_date ON node_mastery(next_review_date);

-- 5. Seans ve Telemetri Olayları Tablosu (Olay Kaynağı / Event Sourcing)
CREATE TABLE IF NOT EXISTS session_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(80) NOT NULL,
    student_uuid UUID NOT NULL REFERENCES student_cognitive_state(student_uuid) ON DELETE CASCADE,
    event_type VARCHAR(40) NOT NULL, -- 'STEP_SUBMIT', 'CONFIDENCE_SUBMIT', 'HINT_REQUEST', 'AFFECTIVE_BEACON'
    step_index INTEGER NOT NULL DEFAULT 1,
    raw_latex TEXT NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    client_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_session ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_student ON session_events(student_uuid);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON session_events(client_timestamp);

-- 6. Adım Diagnostik Analizleri Tablosu
CREATE TABLE IF NOT EXISTS step_diagnostics (
    diagnostic_id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES session_events(event_id) ON DELETE CASCADE,
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    detected_bug_id VARCHAR(20) NULL, -- 'BUG-QUAD-01'..'05'
    ddm_drift_v DOUBLE PRECISION NULL,
    ddm_boundary_a DOUBLE PRECISION NULL,
    affective_state VARCHAR(30) NULL DEFAULT 'FLOW',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_diag_event ON step_diagnostics(event_id);
CREATE INDEX IF NOT EXISTS idx_diag_bug ON step_diagnostics(detected_bug_id);

-- Unutulma Hakkı (Right to be Forgotten) Tetikleyici Fonksiyonu
CREATE OR REPLACE FUNCTION purge_student_data(target_uuid UUID) 
RETURNS VOID AS $$
BEGIN
    DELETE FROM student_cognitive_state WHERE student_uuid = target_uuid;
END;
$$ LANGUAGE plpgsql;
