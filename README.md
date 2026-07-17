# Status G-Lab Telecom

Plataforma de consulta publica de incidentes da rede da G-Lab Telecom.

Este README cobre apenas como rodar o ambiente local. Contexto de produto,
decisões de arquitetura e backlog estão em `docs/`.

## Pre requisitos

Docker e Docker Compose instalados. Nada mais precisa ser instalado na
maquina host, tudo roda dentro dos containers.

## Subindo o ambiente

```
make up
```

Isso sobe três containers:

- postgres, na porta 5432, com o schema em `db/migrations/0001_initial.sql`
  aplicado automaticamente na primeira subida.
- backend (FastAPI), na porta 8000. Endpoints disponíveis: `/health`,
  `/health/db` e `/docs` (documentação automática do FastAPI).
- frontend (Next.js), na porta 3000. A pagina inicial mostra o status do
  próprio frontend e a conectividade com o backend.

Para conferir se subiu corretamente, abrir `http://localhost:3000` e
verificar se os dois indicadores de status aparecem verdes.

O schema em `db/migrations/` só e aplicado automaticamente quando o
volume do postgres esta vazio (primeira subida). Para recriar o banco do
zero apos alterar o schema, usar `make down-v` seguido de `make up`.

## Comandos disponíveis

Rodar `make` (sem argumentos) ou `make help` lista todos os comandos com
uma descrição curta de cada um. Os principais:

```
make up               sobe os containers em background
make down             para os containers (mantém os dados do banco)
make logs             acompanha o log de todos os serviços
make test             roda os testes automatizados do backend
make backend-shell    abre um shell dentro do container do backend
make db-shell         abre o psql dentro do container do postgres
```

## Variáveis de ambiente

O arquivo `.env` ja vem preenchido com valores de desenvolvimento e não e
versionado no git. `.env.example` documenta todas as chaves esperadas.
Para gerar um `.env` novo do zero:

```
cp .env.example .env
```

e preencher os valores (usuário/senha do postgres e segredo do JWT).

## Estrutura do repositório

Ver `docs/file_structure.txt` para a estrutura alvo completa e
`docs/conventions.md` para convenções de nomenclatura e padrões de
código adotados no projeto.
