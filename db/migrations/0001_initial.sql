-- Migration: 0001_initial
-- Projeto: Status G-Lab Telecom
-- Descrição: DDL base do banco de dados. Cria as tabelas fundamentais para
-- usuários, rotas, tipos/status de incidente, incidentes,
-- atualizações (timeline) e imagens.

-- Banco: PostgreSQL

BEGIN;

-- users
-- Domínio privado. Papéis: técnico (opera incidentes) e admin (gerencia
-- usuários, rotas e tipos/status).
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

-- routes
-- Cadastro de rotas da rede (ex: "Backbone SP-RJ"). Gerenciado pelo admin.
CREATE TABLE routes (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- incident_types
-- Tipos de incidente (rompimento, furto, vandalismo, etc). Gerenciado pelo
-- admin para permitir ajuste de rótulos sem deploy.
CREATE TABLE incident_types (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- incident_status
-- Estados possíveis de um incidente. Coluna "sort_order" define a ordem
-- lógica do fluxo (usada na timeline e para validar transições no backend).
-- Inclui "cancelado" para incidentes abertos por engano/duplicados, fora do
-- fluxo sequencial principal.
CREATE TABLE incident_status (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    sort_order SMALLINT NOT NULL UNIQUE,
    is_final BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- incidents
-- Registro principal do incidente. "cep" é informado no cadastro; "city" é
-- derivado automaticamente do CEP (via serviço externo) no momento da
-- criação, e fica congelado a partir daí (não é recalculado depois).
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

CREATE INDEX idx_incidents_route_id ON incidents(route_id);
CREATE INDEX idx_incidents_status_id ON incidents(status_id);
CREATE INDEX idx_incidents_type_id ON incidents(type_id);
CREATE INDEX idx_incidents_city ON incidents(city);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);

-- incident_updates
-- Timeline do incidente. Cada atualização registra a mudança de status e um
-- comentário do técnico. As fotos ficam presas à atualização (não ao
-- incidente diretamente), refletindo o fluxo real: "técnico atualiza e
-- anexa fotos daquele momento".
CREATE TABLE incident_updates (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    status_id BIGINT NOT NULL REFERENCES incident_status(id),
    comment TEXT,
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_incident_updates_incident_id ON incident_updates(incident_id);

-- incident_images
-- Fotos anexadas a uma atualização. "file_path" aponta para o arquivo em
-- storage local (volume Proxmox).
CREATE TABLE incident_images (
    id BIGSERIAL PRIMARY KEY,
    incident_update_id BIGINT NOT NULL REFERENCES incident_updates(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_incident_images_update_id ON incident_images(incident_update_id);

-- Seed inicial: tipos e status (necessários para o sistema funcionar desde
-- o primeiro deploy, não são dados de teste).
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

COMMIT;
