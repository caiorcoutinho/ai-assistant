# AI Assistant

Stack em Docker Compose:

| Serviço    | Tecnologia          | Porta (host)        | Descrição                                  |
|------------|---------------------|---------------------|--------------------------------------------|
| `nginx`    | Nginx (gateway)     | `80`                | Reverse proxy: `/` → React, `/api/` → API  |
| `frontend` | React + Vite        | interna             | SPA buildada e servida por nginx           |
| `backend`  | FastAPI (Python)    | interna             | API, conecta ao Postgres e Qdrant          |
| `postgres` | PostgreSQL 16       | `5432`              | Banco relacional                           |
| `qdrant`   | Qdrant              | `6333` / `6334`     | Banco vetorial (REST/gRPC + dashboard)     |

## Estrutura

```
.
├── docker-compose.yml
├── .env               # variáveis de ambiente (não versionar)
├── .env.example
├── backend/           # FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/main.py
├── frontend/          # React + Vite
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── src/
└── nginx/
    └── nginx.conf     # reverse proxy / gateway
```

## Como rodar

```bash
cp .env.example .env   # ajuste as senhas
docker compose up --build
```

Depois:

- App React → http://localhost/
- API (health) → http://localhost/api/health
- Swagger → http://localhost/api/docs
- Dashboard do Qdrant → http://localhost:6333/dashboard

## Desenvolvimento

**Frontend (hot reload local):**

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173  (proxy /api → localhost:8000)
```

**Backend (hot reload no container):** descomente o bloco `volumes` do serviço
`backend` no `docker-compose.yml` e adicione `--reload` ao comando do uvicorn.
