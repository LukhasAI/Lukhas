# External Dependencies

This document lists the external services and libraries that LUKHAS depends on for full functionality. While the core system can run without these, certain features will be disabled.

## Core Services

These services are required for key features like caching, persistence, and cloud integration.

### Redis

- **Purpose**: Used for caching, rate limiting, and session management.
- **Setup**:
  - **Docker (Recommended)**: `docker run -d -p 6379:6379 redis:latest`
  - **macOS**: `brew install redis && brew services start redis`
  - **Ubuntu**: `sudo apt-get install redis-server && sudo systemctl enable --now redis-server`
- **Python Library**: `pip install redis`

### PostgreSQL

- **Purpose**: Primary database for persistent storage.
- **Setup**:
  - **Docker (Recommended)**: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres:latest`
  - **macOS**: `brew install postgresql && brew services start postgresql`
  - **Ubuntu**: `sudo apt-get install postgresql && sudo systemctl enable --now postgresql`
- **Python Library**: `pip install psycopg2-binary asyncpg`

### Amazon S3

- **Purpose**: Used for cloud storage of large assets and artifacts.
- **Setup**: Requires an AWS account and configured credentials.
- **Python Library**: `pip install boto3`

## Python Libraries

These are additional Python libraries that enable specific functionalities.

### SQLAlchemy

- **Purpose**: ORM for interacting with the PostgreSQL database.
- **Installation**: `pip install SQLAlchemy`

### CloudConsolidation

- **Purpose**: Internal library for cloud integration.
- **Installation**: (Instructions to be added)
