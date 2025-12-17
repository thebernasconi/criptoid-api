# CRIPTOID — API Principal (FastAPI)

API principal do CRIPTOID. Responsável por:
- Expor rotas REST consumidas pelo Frontend (GET/POST/PUT/DELETE)
- Persistir dados no PostgreSQL (favoritos e snapshots)
- Orquestrar a chamada para a API secundária (Quotes Service)

## Arquitetura (fluxograma)

```mermaid
flowchart LR
  FE[Frontend] --> API[API Principal]
  API --> QS[Quotes Service]
  QS --> YF[Yahoo Finance]
  API --> PG[(Postgres)]
