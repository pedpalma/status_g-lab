"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-17
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'tecnico',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT chk_users_role CHECK (role IN ('tecnico', 'admin'))
        );

        CREATE TABLE routes (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE incident_types (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE incident_status (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            sort_order SMALLINT NOT NULL UNIQUE,
            is_final BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE incidents (
            id BIGSERIAL PRIMARY KEY,
            type_id BIGINT NOT NULL REFERENCES incident_types(id),
            route_id BIGINT NOT NULL REFERENCES routes(id),
            status_id BIGINT NOT NULL REFERENCES incident_status(id),
            cep VARCHAR(9) NOT NULL,
            city VARCHAR(100),
            description TEXT NOT NULL,
            created_by BIGINT NOT NULL REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            closed_at TIMESTAMPTZ
        );

        CREATE INDEX idx_incidents_route_id  ON incidents(route_id);
        CREATE INDEX idx_incidents_status_id ON incidents(status_id);
        CREATE INDEX idx_incidents_type_id ON incidents(type_id);
        CREATE INDEX idx_incidents_city ON incidents(city);
        CREATE INDEX idx_incidents_created_at ON incidents(created_at);

        CREATE TABLE incident_updates (
            id BIGSERIAL PRIMARY KEY,
            incident_id BIGINT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
            status_id BIGINT NOT NULL REFERENCES incident_status(id),
            comment TEXT,
            created_by BIGINT NOT NULL REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_incident_updates_incident_id ON incident_updates(incident_id);

        CREATE TABLE incident_images (
            id BIGSERIAL PRIMARY KEY,
            incident_update_id BIGINT NOT NULL REFERENCES incident_updates(id) ON DELETE CASCADE,
            file_path VARCHAR(500) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_incident_images_update_id ON incident_images(incident_update_id);

        INSERT INTO incident_types (name) VALUES
            ('rompimento'),
            ('furto'),
            ('vandalismo'),
            ('incêndio'),
            ('troca_de_poste'),
            ('acidente'),
            ('falha_elétrica'),
            ('manutenção_programada'),
            ('outro');

        INSERT INTO incident_status (name, sort_order, is_final) VALUES
            ('aberto', 1, FALSE),
            ('equipe_acionada', 2, FALSE),
            ('equipe_deslocada', 3, FALSE),
            ('em_atendimento', 4, FALSE),
            ('material_aguardando', 5, FALSE),
            ('reparo_realizado', 6, FALSE),
            ('em_validação', 7, FALSE),
            ('concluído', 8, TRUE),
            ('cancelado', 9, TRUE);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS incident_images CASCADE;
        DROP TABLE IF EXISTS incident_updates CASCADE;
        DROP TABLE IF EXISTS incidents CASCADE;
        DROP TABLE IF EXISTS incident_status CASCADE;
        DROP TABLE IF EXISTS incident_types CASCADE;
        DROP TABLE IF EXISTS routes CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        """
    )
