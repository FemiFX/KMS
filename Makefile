.PHONY: help build up down restart logs shell db-init db-migrate db-upgrade clean prune

help:
	@echo "KMS Development Commands"
	@echo "========================"
	@echo "make build       - Build Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs (Ctrl+C to exit)"
	@echo "make shell       - Open Flask shell"
	@echo "make db-init     - Initialize database migrations"
	@echo "make db-migrate  - Create new migration"
	@echo "make db-upgrade  - Run migrations"
	@echo "make clean       - Remove containers and volumes"
	@echo "make prune       - Clean Docker cache and free disk space"

build:
	docker compose build

up:
	docker compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services started!"
	@echo "Flask API: http://localhost:5000"
	@echo "MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

shell:
	docker compose exec flask flask shell

db-init:
	docker compose exec flask flask db init

db-migrate:
	docker compose exec flask flask db migrate -m "$(msg)"

db-upgrade:
	docker compose exec flask flask db upgrade

clean:
	docker compose down -v
	rm -rf backend/migrations

prune:
	@echo "Cleaning Docker cache and unused resources..."
	docker system prune -a -f
	@echo "Cleaning build cache..."
	docker builder prune -a -f
	@echo "Done! Check space with: docker system df"
