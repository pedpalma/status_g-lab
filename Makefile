SHELL := /bin/sh
include .env
export

.DEFAULT_GOAL := help

.PHONY: help up down up-build build restart logs logs-backend logs-frontend logs-db ps \
        backend-shell frontend-shell db-shell test backend-outdated frontend-update clean

help: ## lista os comandos disponíveis
	@grep -hE '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-18s %s\n", $$1, $$2}'

up: ## Sobe os serviços em background
	docker compose up -d
	@echo ""
	@echo "  ✓ Serviços iniciados com sucesso"
	@echo "  API:      http://localhost:8000"
	@echo "  Docs:     http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"

up-build: ## reconstrói as imagens e sobe os containers
	docker compose up -d --build

down: ## para e remove os containers (mantém o volume do banco)
	docker compose down

down-v: ## para e remove os containers e o volume do banco (apaga os dados)
	docker compose down -v

build: ## reconstrói as imagens sem subir os containers
	docker compose build

restart: ## reinicia os serviços
	docker compose restart

logs: ## acompanha o log dos serviços
	docker compose logs -f

logs-backend: ## acompanha o log apenas do backend
	docker compose logs -f backend

logs-frontend: ## acompanha o log apenas do frontend
	docker compose logs -f frontend

logs-db: ## acompanha o log apenas do postgres
	docker compose logs -f postgres

ps: ## lista os containers e o status de cada um
	docker compose ps

backend-shell: ## abre um shell dentro do container do backend
	docker compose exec backend bash

frontend-shell: ## abre um shell dentro do container do frontend
	docker compose exec frontend sh

db-shell: ## abre o psql dentro do container do postgres
	docker compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

test: ## executa os testes automatizados do backend
	docker compose exec backend pytest -v

backend-outdated: ## lista dependências desatualizadas do backend (nao instala nada)
	docker compose exec backend pip list --outdated

frontend-update: ## atualiza dependencies do frontend dentro dos ranges do package.json
	docker compose exec frontend npm update

clean: ## remove containers, volumes e imagens locais do projeto
	docker compose down -v --rmi local
