.PHONY: dev prod down seed admin train generate-data shell run logs migrate migrate-new migrate-down migrate-history migrate-current

# Dev
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-reset:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

# Prod
prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up

prod-build:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Scripts Python
seed:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api python -m app.scripts.seed_data

admin:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api python -m app.scripts.create_admin

train:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api python -m app.infrastructure.ml.train

generate-data:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api python -m data.generate_dataset

# Migraciones (Alembic)
migrate-new:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "$(msg)"

migrate:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic upgrade head

migrate-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic downgrade -1

migrate-history:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic history

migrate-current:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic current

# Shell interactivo
shell:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api bash

# Logs
logs:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
