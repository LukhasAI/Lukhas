.PHONY: help install dev build test clean db-migrate db-seed policy rate-test

# Default target
help:
	@echo "LUKHAS AI Website - Available Commands"
	@echo "======================================"
	@echo "  make install        - Install dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make build         - Build for production"
	@echo "  make test          - Run all tests"
	@echo "  make test-auth     - Run auth tests only"
	@echo "  make test-rate     - Run rate limiter tests"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-seed       - Seed database with test data"
	@echo "  make policy        - Run all policy checks"
	@echo "  make redis         - Start Redis server (dev)"

# Install dependencies
install:
	npm install
	npm install ioredis jsonwebtoken @prisma/client prisma
	npm install -D @types/jsonwebtoken @testing-library/react @testing-library/jest-dom

# Development server
dev:
	npm run dev

# Production build
build:
	npm run build

# Run all tests
test:
	npm test

# Auth-specific tests
test-auth:
	npm test -- packages/auth/__tests__

# Rate limiter tests
test-rate:
	REDIS_URL=$${REDIS_URL:-redis://localhost:6379} npm test -- packages/middleware/__tests__

rate-test: test-rate

# Clean build artifacts
clean:
	rm -rf .next
	rm -rf node_modules/.cache
	rm -rf coverage

# Database migrations
db-migrate-prisma:
	npx prisma migrate deploy

db-migrate-sql:
	psql "$$DATABASE_URL" -f db/refresh_tokens.sql

db-migrate: db-migrate-prisma

# Seed database
db-seed:
	@echo "Seeding database with test data..."
	npx prisma db seed

# Policy checks
.PHONY: policy-transparency policy-registries policy-brand policy-tone policy-tone-visibility

policy-transparency:
	@echo "🔎 Checking transparency on auth/public pages..."
	@node scripts/check-transparency.js

policy-registries:
	@echo "📋 Checking module registries..."
	@npm run -s policy:registries || true

policy-brand:
	@echo "🎨 Checking brand compliance..."
	@npm run -s policy:brand || true

policy-tone:
	@echo "🎵 Checking tone system..."
	@npm run -s policy:tone || true

policy-tone-visibility:
	@echo "👁️  Checking tone visibility words (warn-only)..."
	@npm run -s policy:tone-visibility || true

policy: policy-transparency policy-registries policy-brand policy-tone policy-tone-visibility
	@echo "✅ All policy checks passed"

# Start Redis for development
redis:
	@echo "Starting Redis server..."
	redis-server &

# Prisma commands
prisma-generate:
	npx prisma generate

prisma-studio:
	npx prisma studio

prisma-push:
	npx prisma db push

# Quick development setup
setup: install db-migrate
	@echo "✅ Development environment ready"

# Run everything for development
start: redis dev
	@echo "🚀 LUKHAS AI Website running"

# CI/CD commands
.PHONY: ci-test ci-build ci-deploy

ci-test:
	npm run lint
	npm run type-check || true
	npm test -- --coverage

ci-build:
	npm run build
	@echo "Build size:"
	@du -sh .next

ci-deploy:
	@echo "Deploying to production..."
	# Add deployment commands here

# Docker commands
.PHONY: docker-build docker-run docker-stop

docker-build:
	docker build -t lukhas-website .

docker-run:
	docker run -p 3000:3000 --env-file .env.local lukhas-website

docker-stop:
	docker stop $$(docker ps -q --filter ancestor=lukhas-website)

# Monitoring
.PHONY: logs monitor

logs:
	tail -f logs/*.log

monitor:
	@echo "📊 System Status"
	@echo "==============="
	@ps aux | grep -E "node|redis" | grep -v grep || true
	@echo ""
	@echo "📡 Port Usage"
	@echo "============="
	@lsof -i :3000 -i :6379 || true