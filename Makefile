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

help: ## Lista os comandos disponíveis no Makefile
	@grep -hE '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'



# SETUP & AMBIENTE

setup: ## Realiza a configuração inicial do projeto (Dependências, Env, Build)
	@echo "\n  Configurando o projeto..."
	@make check-deps
	@make env-init
	@make build
	@echo "\n  ✓ Configuração concluída com sucesso!"
	@echo "\n  ⚠ Próximos passos:"
	@echo "  - 1. Edite o arquivo .env e ajuste as variáveis de ambiente."
	@echo "  - 2. Suba o ambiente com 'make up'"
	@echo "  - 3. Rode 'make first-migrate' para garantir que o 0001 esteja aplicado."
	@echo "  - 4. Rode 'make migrate para aplicar as demais migrações"
	@echo "  - 5. Rode 'make admin' para criar o primeiro user admin."
	@echo "\n  Digite 'make help' para listar os comandos disponíveis.\n"

check-deps: ## Verifica se o Docker, Docker Compose e Git estão instalados
	@echo "\n  Verificando dependências...\n"
	@command -v docker >/dev/null 2>&1 || { echo "✗ docker não encontrado"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "✗ docker compose v2 não encontrado"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "✗ git não encontrado"; exit 1; }
	@echo "  ✓ Dependências OK"

env-init: ## Cria o arquivo .env a partir do .env.example (caso não exista)
	@echo "\n  Verificando .env...\n"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "  ✓ Criado arquivo .env"; \
		echo "  ⚠ Atenção: Edite o .env e ajuste suas credenciais antes de subir o ambiente.\n"; \
	else \
		echo "  - O arquivo .env já existe e não foi sobrescrito."; \
	fi

admin:
	@echo "\n  ⚠ Criando admin...\n"
	@docker compose exec backend python -m scripts.create_admin




# DOCKER (CICLO DE VIDA)

up: ## Sobe os serviços em background (Detached)
	@echo "\n  ⚠ Inicializando os serviços...\n"
	@docker compose --ansi always up -d
	@echo
	@echo "\n  ✓ Serviços iniciados com sucesso!"
	@echo "  - API (Backend):     http://localhost:8000"
	@echo "  - Swagger/Docs:      http://localhost:8000/docs"
	@echo "  - Frontend público:  http://localhost:3000"
	@echo "  - Frontend admin:    http://localhost:3000/login\n"

	@echo
down: ## Para e remove os containers (Mantém os volumes e dados do banco)
	@echo "\n  ⚠ Parando serviços...\n"
	@docker compose down
	@echo "\n  ✓ Serviços parados com sucesso!\n"

down-v: ## Para e remove os containers, destruindo também os volumes (APAGA OS DADOS)
	@echo "\n  ⚠ Removendo os serviços...\n"
	@docker compose down -v
	@echo "\n  ✓ Serviços e volumes removidos com sucesso!\n"

build: ## Constrói as imagens sem subir os containers
	@echo "\n  ⚠ Construindo imagens...\n"
	@docker compose build
	@echo "\n  ✓ imagens construídas com sucesso!\n"

rebuild: ## Reconstrói as imagens ignorando o cache (Útil após alterar Dockerfile)
	@echo "\n  ⚠ Reconstruindo imagens...\n"
	@docker compose build --no-cache
	@echo "\n  ✓ imagens reconstruídas com sucesso!\n"

restart: ## Reinicia os serviços do Docker Compose
	@echo "\n  ⚠ Reiniciando os serviços Docker...\n"
	@docker compose restart
	@echo "\n  ✓ serviços reiniciados com sucesso!\n"

status: ## Lista os containers do projeto e o status de cada um
	@echo "\n  - Checagem do status dos serviços:\n"
	@docker compose ps



# LOGS

logs: ## Acompanha os logs dos serviços simultaneamente
	@echo "\n  - Logs dos serviços:\n"
	@docker compose logs -f

logs-backend: ## Acompanha os logs apenas do serviço Backend
	@echo "\n  - Logs do backend:\n"
	@docker compose logs -f backend

logs-frontend: ## Acompanha os logs apenas do serviço Frontend
	@echo "\n  - Logs do frontend:\n"
	@docker compose logs -f frontend

logs-db: ## Acompanha os logs apenas do serviço Postgres
	@echo "\n  - Logs da database:\n"
	@docker compose logs -f postgres




# SHELL & ACESSO

sh-backend: ## Abre o terminal (bash) dentro do container do Backend
	@echo "\n  ⚠ Criando shell para o container backend...\n"
	@docker compose exec backend bash
	@echo "\n  ✓ Saindo do shell...\n"

sh-frontend: ## Abre o terminal (sh) dentro do container do Frontend
	@echo "\n  ⚠ Criando shell para o container frontend...\n"
	@docker compose exec frontend sh
	@echo "\n  ✓ Saindo do shell...\n"


sh-db: ## Abre o terminal do PostgreSQL (psql) dentro do container do banco
	@echo "\n  ⚠ Criando shell de acesso para a database...\n"
	@docker compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
	@echo "\n  ✓ Saindo do shell..\n"



# BACKEND

test: ## Executa os testes automatizados do Backend (Pytest)
	@echo "\n  ⚠ Executando suíte de testes...\n"
	@docker compose exec backend python -m pytest -v

first-migrate: ## Aplica as migrações pendentes no banco de dados
	@echo "\n  ⚠ Garantindo que o db está na 0001...\n"
	@docker compose exec backend alembic stamp 0001

migrate:
	@echo "\n  ⚠ Executando migrações...\n"
	@docker compose exec backend alembic upgrade head

deps-outdated: ## Lista as dependências do Python que estão desatualizadas
	@echo "\n  - Verificando dependências desatualizadas...\n"
	@docker compose exec backend pip list --outdated

deps-compile: ## Recompila o requirements.txt a partir do requirements.in
	@echo "\n  ⚠ Recompilando requerimentos do projeto...\n"
	@docker compose exec backend pip-compile requirements.in --output-file requirements.txt

deps-upgrade: ## Atualiza as dependências do requirements.in para a última versão
	@echo "\n  ⚠ Atualizando requerimentos do projeto...\n"
	@docker compose exec backend pip-compile --upgrade requirements.in --output-file requirements.txt

deps-sync: ## Sincroniza os pacotes instalados com o requirements.txt
	@echo "\n  ⚠ Sincronizando pacotes instalados...\n"
	@docker compose exec backend pip-sync requirements.txt

deps-install: ## Instala as dependências listadas no requirements.txt
	@echo "\n  ⚠ Instalando requerimentos...\n"
	@docker compose exec backend pip install -r requirements.txt



# FRONTEND

frontend-update: ## Atualiza as dependências do Frontend (respeitando os ranges do package.json)
	@echo "\n  ⚠ Atualizando as dependências...\n"
	@docker compose exec frontend npm update



# LIMPEZA

clean: ## Remove containers, redes, volumes e imagens locais (Reset completo)
	@echo "\n  ⚠ Removendo projeto...\n"
	@docker compose down -v --rmi local



# Preguiça
lazy:
	@gum style \
		--foreground 11 \
		--bold \
		" - Lazy commit"
	@echo
	@if [ -z "$$(git status --porcelain)" ]; then \
		gum style --foreground 14 "  ⚠ Nenhuma alteração para commit."; \
		exit 1; \
	fi
	@echo
	@gum style --foreground 11 "  -> Selecione um commit base para editar (ou aperte ESC para começar do zero)."
	@base_msg=$$(git log -n 50 --pretty=format:"%s" | awk '!seen[$$0]++' | gum filter --height 10 --placeholder "Pesquise commits antigos..." || true); \
	msg=$$(gum input \
		--prompt "Commit > " \
		--placeholder "feat(scope): descrição" \
		--value "$$base_msg"); \
	[ -n "$$msg" ] || { echo; gum style --foreground 196 "❌ Operação cancelada."; exit 1; }; \
	git add . && \
	git commit -m "$$msg" && \
	git push