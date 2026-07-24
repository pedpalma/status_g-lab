# Status G-Lab Telecom

Plataforma de consulta pública de incidentes das rotas da G-Lab Telecom.

Este README cobre como rodar o ambiente local.

## Pré requisitos

Docker e Docker Compose instalados. Nada mais precisa ser instalado na
maquina host, tudo roda dentro dos containers.

## Subindo o ambiente

```
make setup
```

### O que o setup faz:

- Valida se o docker, docker-compose e git estão instalados
- Cria o arquivo `.env`.
- Constrói as imagens docker do backend, frontend e db.

### O que fazer após o setup:

- Editar o arquivo `.env` e preencher as variáveis de ambiente (usuário/senha do postgres e segredo do JWT).
- Subir o ambiente com `make up`. Isso sobe os 3 containers:
  - Postgres, na porta 5432.
  - Backend (FastAPI), na porta 8000.
  - Frontend (Next.js), na porta 3000 (público) e 3000/login (técnico).
- Rodar `make first-migrate`, que garante o 0001 aplicado.
- Rodar `make migrate` para aplicar as migrations do banco de dados.
- Rodar `make admin` para criar o usuário admin do sistema.

## Obtendo logs:

- Para acompanhar os logs de todos os serviços, rode `make logs`.
- Para acompanhar os logs de um serviço em específico, rode `make logs-backend` ou `make logs-frontend` ou `make logs-db`.

## Acessar shell:

- Para acessar o shell do backend, rode `make sh-backend`.
- Para acessar o shell do banco de dados, rode `make sh-db`.
- Para acessar o shell do frontend, rode `make sh-frontend`.

## Comandos mais usados:

```
make up - sobe os containers em background
make down - para os containers (mantém os dados do banco)
make logs - acompanha o log de todos os serviços
make test - roda os testes automatizados do backend
make sh-backend - abre um shell dentro do container do backend
make sh-db - abre o psql dentro do container do postgres
```

### Para mais detalhes dos comandos:

Rodar `make` (sem argumentos) ou `make help` lista todos os comandos com
uma descrição curta de cada um.

## Créditos:

Desenvolvido para [G-Lab Telecom](https://www.g-labtelecom.com.br/) - Todos os direitos reservados.

Dev: [@pedpalma](https://github.com/pedpalma).
