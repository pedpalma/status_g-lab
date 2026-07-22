SHELL := /bin/sh
-include .env
export

.DEFAULT_GOAL := help



.PHONY: help setup check-deps env-init up up-build down down-v build rebuild restart status clean \
        logs logs-backend logs-frontend logs-db \
        sh-backend sh-frontend sh-db \
        backend-test backend-migrate backend-deps-compile backend-deps-upgrade backend-deps-sync backend-deps-install backend-outdated \
        frontend-update


# AJUDA

help: ## Lista todos os comandos disponíveis no Makefile
	@grep -hE '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'



# SETUP & AMBIENTE

setup: ## Realiza a configuração inicial do projeto (Dependências, Env, Build)
	@echo "Configurando o projeto..."
	@make check-deps
	@make env-init
	@make build
	@echo "\n  ✓ Configuração concluída com sucesso!"
	@echo "Próximos passos:"
	@echo "  1. Edite o arquivo .env e ajuste as variáveis de ambiente."
	@echo "  2. Suba o ambiente com 'make up'"
	@echo "  3. Rode 'make backend-migrate' para aplicar as migrações."
	@echo "\nDigite 'make help' para listar os comandos disponíveis.\n"

check-deps: ## Verifica se o Docker, Docker Compose e Git estão instalados
	@echo "Verificando dependências..."
	@command -v docker >/dev/null 2>&1 || { echo "✗ docker não encontrado"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "✗ docker compose v2 não encontrado"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "✗ git não encontrado"; exit 1; }
	@echo "✓ Dependências OK"

env-init: ## Cria o arquivo .env a partir do .env.example (caso não exista)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Criado arquivo .env"; \
		echo "⚠ Atenção: Edite o .env e ajuste suas credenciais antes de subir o ambiente."; \
	else \
		echo "ℹ O arquivo .env já existe e não foi sobrescrito."; \
	fi



# DOCKER (CICLO DE VIDA)

up: ## Sobe os serviços em background (Detached)
	docker compose up -d
	@echo "\n  ✓ Serviços iniciados com sucesso"
	@echo "  API (Backend): http://localhost:8000"
	@echo "  Swagger/Docs:  http://localhost:8000/docs"
	@echo "  Frontend:      http://localhost:3000\n"

up-build: ## Reconstrói as imagens e sobe os containers em background
	docker compose up -d --build
	@echo "\n  ✓ Serviços reconstruídos e iniciados com sucesso"

down: ## Para e remove os containers (Mantém os volumes e dados do banco)
	docker compose down
	@echo "\n  ✓ Serviços parados com sucesso"

down-v: ## Para e remove os containers, destruindo também os volumes (APAGA OS DADOS)
	docker compose down -v
	@echo "\n  ⚠ Serviços e volumes removidos com sucesso"

build: ## Constrói as imagens sem subir os containers
	docker compose build

rebuild: ## Reconstrói as imagens ignorando o cache (Útil após alterar Dockerfile)
	docker compose build --no-cache

restart: ## Reinicia os serviços do Docker Compose
	docker compose restart

status: ## Lista os containers do projeto e o status de cada um
	docker compose ps



# LOGS

logs: ## Acompanha os logs dos serviços simultaneamente
	docker compose logs -f

logs-backend: ## Acompanha os logs apenas do serviço Backend
	docker compose logs -f backend

logs-frontend: ## Acompanha os logs apenas do serviço Frontend
	docker compose logs -f frontend

logs-db: ## Acompanha os logs apenas do serviço Postgres
	docker compose logs -f postgres




# SHELL & ACESSO

sh-backend: ## Abre o terminal (bash) dentro do container do Backend
	docker compose exec backend bash

sh-frontend: ## Abre o terminal (sh) dentro do container do Frontend
	docker compose exec frontend sh

sh-db: ## Abre o terminal do PostgreSQL (psql) dentro do container do banco
	docker compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)



# BACKEND

test: ## Executa os testes automatizados do Backend (Pytest)
	docker compose exec backend python -m pytest -v

migrate: ## Aplica as migrações pendentes no banco de dados
	docker compose exec backend python manage.py migrate

deps-outdated: ## Lista as dependências do Python que estão desatualizadas
	docker compose exec backend pip list --outdated

deps-compile: ## Recompila o requirements.txt a partir do requirements.in
	docker compose exec backend pip-compile requirements.in --output-file requirements.txt

deps-upgrade: ## Atualiza as dependências do requirements.in para a última versão
	docker compose exec backend pip-compile --upgrade requirements.in --output-file requirements.txt

deps-sync: ## Sincroniza os pacotes instalados com o requirements.txt
	docker compose exec backend pip-sync requirements.txt

deps-install: ## Instala as dependências listadas no requirements.txt
	docker compose exec backend pip install -r requirements.txt



# FRONTEND

frontend-update: ## Atualiza as dependências do Frontend (respeitando os ranges do package.json)
	docker compose exec frontend npm update



# LIMPEZA

clean: ## Remove containers, redes, volumes e imagens locais (Reset completo)
	docker compose down -v --rmi local