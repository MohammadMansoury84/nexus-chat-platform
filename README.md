# Nexus Chat Platform — Branch `dev4` (Phase 4)
### Real Persistence: PostgreSQL, Async SQLAlchemy, Alembic Migrations & Redis

## Overview

This branch is where the messenger stops losing its data on every restart. The in‑memory repositories from Phase 3 are replaced with real, asynchronous **SQLAlchemy 2.0** repositories backed by **PostgreSQL**, schema changes are managed with **Alembic** migrations, and a lightweight **Redis** store is introduced to track which users are currently online. The HTTP API surface itself (routes, request/response shapes) is **unchanged from Phase 3** — this phase is a clean demonstration of the payoff from the clean‑architecture split introduced earlier: only the `infrastructure` layer had to change.

## What This Phase Delivers

- Async SQLAlchemy ORM models for every entity, wired together with proper relationships and cascades
- An async engine + session factory, injected into request handlers via a FastAPI dependency
- A real Alembic migration (`74478750e70d_initial_tables.py`) that creates all tables
- Redis‑backed online‑user tracking, replacing the ad‑hoc in‑memory set used in earlier phases
- "Brief" projection objects (`infrastructure/Brief/...`) for read‑optimized queries that don't need to hydrate a full ORM graph

## Architecture (what changed vs. Phase 3)

```
app/src/infrastructure/
├── database/
│   ├── detabase_set_up.py           create_async_engine(...) from Setting
│   ├── session_db.py                async_sessionmaker -> get_async_session_local()
│   └── orm_models/
│       ├── base.py                   declarative Base
│       ├── user_model.py             UserModel (users table)
│       ├── group_model.py            GroupModel (groups table)
│       ├── group_members_model.py    GroupMembersModel (membership join table)
│       ├── group_message_model.py    GroupMessageModel
│       ├── private_chat_model.py     PrivateChatModel
│       └── private_message_model.py  PrivateMessageModel
├── repositories_implementation/       now issue real async SQL queries against the ORM models
│   ├── user_repository_impl.py
│   ├── group_repository_impl.py
│   ├── group_message_repository_impl.py
│   ├── private_chat_repositiry_impl.py
│   ├── message_repository_impl.py
│   └── group_member_repository_impl.py
├── Brief/                             lightweight read-model DTOs for list/summary endpoints
│   ├── user/{get_by_id_brief,get_by_username_brief,list_all_brief}.py
│   └── group/{get_group_by_id_brief,get_all_groups_for_show_users_brief,get_group_member_brief,group_chat_message_brief}.py
│   └── private_chat/private_chat_message_brief.py
├── redis.py                            aioredis client factory
└── repositories_implementation/redis_online_user_repository_impl.py   online-presence storage in Redis

alembic/
├── env.py                              loads Setting().database_url, targets Base.metadata
└── versions/74478750e70d_initial_tables.py   the initial schema migration

app/src/api/dependencies/
└── database_dependency.py              yields an AsyncSession per request
```

### Data model (tables created by the initial migration)

- **users** — id, username (unique), email (unique), hashed_password, created_at
- **groups** — with a `creator` relationship back to `users`
- **group_members** — join table between `users` and `groups`
- **group_messages** — messages scoped to a group
- **private_chats** — a chat thread between two users (`user1`, `user2`)
- **private_messages** — messages scoped to a private chat

All relationships use SQLAlchemy 2.0 typed `Mapped[...]` / `mapped_column` style, with `cascade="all, delete-orphan"` where appropriate (e.g. deleting a user cascades to the groups they created).

## Tech Stack (additions over Phase 3)

| Concern             | Choice                              |
|-----------------------|---------------------------------------|
| ORM                    | SQLAlchemy 2.0 (async)               |
| Database driver        | `asyncpg` / `psycopg[binary]`        |
| Database               | PostgreSQL                            |
| Migrations              | Alembic                               |
| Online-presence store   | Redis (`redis.asyncio`)              |

## Configuration

`app/.env` now needs the database connection and pool settings on top of the Phase 3 JWT settings:

```env
SHOW_LOG_IN_CLI=true
JWT_SECRET_KEY=<generate a long random string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20

DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<db_name>
POOL_TIMEOUT=10
POOL_SIZE=10
ECHO=true
ISOLATED_LEVEL=READ COMMITTED
MAX_OVERFLOW=20
```

> Redis connection is currently hard‑coded to `redis://localhost:6379` in `app/src/infrastructure/redis.py`; make sure a Redis instance is reachable there (or update the URL).

## How to Run

```bash
uv sync

# 1. Start PostgreSQL and Redis (e.g. via Docker):
docker run -d --name nexus-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
docker run -d --name nexus-redis -p 6379:6379 redis:7

# 2. Apply the database schema
alembic upgrade head

# 3. Run the API (same as Phase 3)
cd app
uvicorn src.main:app --reload
```

The REST API itself behaves exactly as documented in the Phase 3 README (same endpoints under `/api/v1`, same Swagger docs at `/docs`) — the only difference is that data now survives a restart, and "online users" queries are backed by Redis instead of memory.

## Known Limitations (addressed in Phase 5)

- Clients still have to poll REST endpoints to discover new messages — there is no push channel yet.
- Redis connection settings are hard-coded rather than pulled from `Setting`.
