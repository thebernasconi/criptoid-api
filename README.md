# CRIPTOID — API Principal (FastAPI)

A **API Principal** do **CRIPTOID** expõe endpoints REST consumidos pelo Frontend e é responsável por:

- Orquestrar a obtenção de cotações (chamando a **API Secundária / Quotes Service**)
- Persistir dados em **PostgreSQL** (favoritos e cotações)
- Disponibilizar documentação via **Swagger (OpenAPI)**

> Este repositório contém **apenas** a API Principal. O Frontend e a API Secundária estão em repositórios separados.

---

## Arquitetura (fluxograma)

```mermaid
flowchart LR
  FE[Frontend (Nginx + SPA)\n:8080] -->|HTTP /api/*| API[API Principal (FastAPI)\n:8000]
  API -->|HTTP| QS[API Secundária Quotes Service (Node)\n:9000]
  QS -->|HTTP| YF[API Externa: Yahoo Finance]
  API -->|SQL| PG[(PostgreSQL\n:5432)] 
``` 

## Repositórios do projeto

Substitua SEU_USUARIO pelo seu usuário do GitHub:

API Principal (este): https://github.com/SEU_USUARIO/criptoid-api

Frontend: https://github.com/SEU_USUARIO/criptoid-frontend

API Secundária (Quotes Service): https://github.com/SEU_USUARIO/criptoid-quotes-service

Endpoints expostos (principais)
Saúde e documentação

GET /health
Retorna {"message":"ok"}

GET /docs
Swagger UI (documentação e testes)

Preços

POST /api/v1/prices/refresh
Busca cotações via Quotes Service (que consulta Yahoo Finance), persiste no Postgres e retorna as cotações.

Exemplo de body:

{ "symbols": ["BTC-USD", "ETH-USD"] }


GET /api/v1/prices/latest?symbols=BTC-USD,ETH-USD
Retorna as últimas cotações persistidas para os símbolos solicitados.

Favoritos

GET /api/v1/favorites
Lista favoritos.

PUT /api/v1/favorites/{symbol}
Adiciona um símbolo aos favoritos (ex.: BTC-USD).

DELETE /api/v1/favorites/{symbol}
Remove um símbolo dos favoritos (desfavoritar).

Variáveis de ambiente

Esta API depende de duas variáveis (passadas no docker run):

DATABASE_URL
String de conexão do Postgres.

Exemplo:

postgresql+psycopg2://criptoid:criptoid@criptoid-db:5432/criptoid


QUOTES_SERVICE_URL
URL da API secundária (Quotes Service) dentro da mesma Docker network.

Exemplo:

http://criptoid-quotes:9000


Dica: use um arquivo .env.example no repositório e nunca suba .env com segredos.

Pré-requisitos

Docker Desktop instalado e funcionando

Git (para clonar os repositórios)

Portas livres no host:

8000 (API principal)

9000 (Quotes Service)

5432 (Postgres)

Como rodar o projeto completo (sem docker compose)

As instruções abaixo sobem todos os componentes para esta API funcionar de ponta a ponta.

0) Estrutura recomendada no seu computador
CRIPTOID/
  criptoid-frontend/
  criptoid-api/
  criptoid-quotes-service/

1) Criar a network e o volume (apenas 1 vez)
docker network create criptoid-net
docker volume create criptoid_pgdata

2) Subir o Postgres
docker run -d --name criptoid-db --network criptoid-net `
  --restart unless-stopped `
  -e POSTGRES_DB=criptoid `
  -e POSTGRES_USER=criptoid `
  -e POSTGRES_PASSWORD=criptoid `
  -v criptoid_pgdata:/var/lib/postgresql/data `
  -p 5432:5432 `
  postgres:16-alpine

3) Subir a API Secundária (Quotes Service)

Na pasta criptoid-quotes-service:

docker build -t criptoid-quotes-service .
docker run -d --name criptoid-quotes --network criptoid-net `
  --restart unless-stopped `
  -p 9000:9000 `
  criptoid-quotes-service


Teste:

curl http://localhost:9000/health

4) Build + Run da API Principal (este repositório)

Na pasta criptoid-api:

docker build -t criptoid-api .
docker run -d --name criptoid-api --network criptoid-net `
  --restart unless-stopped `
  -e DATABASE_URL="postgresql+psycopg2://criptoid:criptoid@criptoid-db:5432/criptoid" `
  -e QUOTES_SERVICE_URL="http://criptoid-quotes:9000" `
  -p 8000:8000 `
  criptoid-api

Testes rápidos (iniciante)
1) Confirmar que a API está rodando
curl http://localhost:8000/health

2) Abrir o Swagger

Abra no navegador:

http://localhost:8000/docs

3) Testar refresh de preços via PowerShell
$body = @{ symbols = @("BTC-USD","ETH-USD") } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/prices/refresh" -ContentType "application/json" -Body $body

4) Listar favoritos
curl http://localhost:8000/api/v1/favorites

API Externa (Yahoo Finance)

A API Principal não consulta diretamente o Yahoo Finance. Ela chama a API Secundária (criptoid-quotes-service), que realiza a consulta no Yahoo Finance e devolve os dados normalizados.

Cadastro: não é necessário para o MVP.

Observação: o consumo é feito dentro do sistema (sem redirecionar o usuário para outro app).

Troubleshooting (problemas comuns)
Ver status
docker ps

Ver logs
docker logs criptoid-api --tail 200

Reiniciar a API
docker restart criptoid-api

Parar e remover tudo (containers)
docker rm -f criptoid-api criptoid-quotes criptoid-db


Observação: o volume criptoid_pgdata mantém os dados do Postgres entre reinícios.

::contentReference[oaicite:0]{index=0}
