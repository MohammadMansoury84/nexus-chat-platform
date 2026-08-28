## Summary of the Full Journey

| Branch | Phase | Adds |
|--------|-------|------|
| `dev`  | 1 | Domain model, in-memory business logic, CLI, custom logging |
| `dev2` | 2 | Async TCP client/server, custom protocol, concurrency, pytest |
| `dev3` | 3 | FastAPI REST API, JWT auth, clean architecture, Swagger docs |
| `dev4` | 4 | PostgreSQL + async SQLAlchemy + Alembic migrations + Redis |
| `dev5` | 5 (bonus) | WebSocket real-time push + NiceGUI desktop/web client |




# Nexus Chat Platform — Branch `dev` (Phase 1)
### Core Business Logic, CLI Interface & Logging

## Overview

This branch is the foundation of the project. It implements the **core business logic** of the messenger as a plain, layered Python application driven by an interactive **command‑line interface (CLI)**. There is no networking and no database yet — everything runs inside a single process and all data lives in memory for the duration of the run.

The goal of this phase was to get the domain model, business rules, and a structured logging system right before adding any networking or persistence complexity.

## What This Phase Delivers

- User signup/login with in‑memory storage
- Private 1‑to‑1 messaging between logged‑in users, with chat history
- Group creation, adding members, group messaging, and group chat history
- A full interactive CLI menu (13 options) built on top of the same services that later phases reuse
- A custom logging system that writes structured, timestamped log lines to `logfile.log`
- Strict typing throughout the domain model, using Pydantic v2 models with `strict=True` validation

## Architecture

The code follows a classic layered/MVC‑ish structure so the same services can later be reused by a socket server (Phase 2) and a REST API (Phase 3) without rewriting business logic:

```
src/
├── entities/          Domain models (Pydantic BaseModel, validated, immutable-ish)
│   ├── User.py
│   ├── Group.py
│   ├── Message.py
│   ├── MessageStatus.py
│   ├── PrivateChat.py
│   ├── PrivateChatMessage.py
│   ├── GroupMessage.py
│   └── RequestType.py      (enum scaffolded here, put to use in Phase 2's protocol)
├── repository/         In-memory data access layer
│   ├── UserRepository.py
│   └── GroupRepository.py
├── service/            Business logic / use cases
│   ├── AuthService.py
│   ├── MessageService.py
│   └── GroupService.py
├── controllers/         Thin layer between the view and the services
│   ├── AuthController.py
│   ├── MessageController.py
│   └── GroupController.py
├── controllers_old/     Earlier controller iteration kept for reference
├── view/
│   └── userView.py       The interactive CLI (menu loop, input/output)
├── core/                 Custom logging infrastructure
│   ├── CustomeLogger.py
│   ├── ConsoleHandler.py
│   └── CustomFileHandler.py
├── Exceptions/           Domain-specific exception hierarchy
│   ├── ApplicationError.py
│   ├── AuthorizationError.py
│   ├── DuplicateEmailError.py
│   ├── DuplicateUsernameError.py
│   ├── GroupNotFoundError.py
│   ├── UserAlreadyInGroupError.py
│   └── UserNotFoundError.py
├── config.py              pydantic-settings configuration (.env driven)
└── main.py                Composition root — wires everything and starts the CLI
```

### Domain model

- **`User`** — `id` (UUID), `username` (4‑20 chars), `email` (validated via `EmailStr`), `password` (6‑150 chars, stored as given — hashing is introduced in a later phase), `created_at`, plus back‑references to `private_chats`, `groups_created`, and `joined_groups`.
- **`Group`**, **`Message`**, **`PrivateChat`**, **`PrivateChatMessage`**, **`GroupMessage`**, **`MessageStatus`** round out the chat domain.

All entities are Pydantic `BaseModel`s with `strict=True` and `validate_assignment=True`, so invalid data is rejected as soon as it is created or mutated, not just at the API boundary.

### Logging system

`CustomLogger` (in `src/core/CustomeLogger.py`) subclasses `logging.Logger` and adds a small structured‑logging convenience: any call like

```python
logger.info("New client connected", client_address=addr)
```

is rendered as `New client connected | client_address: addr` with a timestamp and level, and can go to two places:

- **`CustomFileHandler`** → always writes to `logfile.log` (level `INFO` and above)
- **`ConsoleHandler`** → only attached if `SHOW_LOG_IN_CLI=true` in `.env` (level `DEBUG` and above)

This means log verbosity in the terminal is configurable without touching code, while the file log always keeps a full record.

## Tech Stack

| Concern            | Choice                          |
|---------------------|----------------------------------|
| Language            | Python ≥ 3.13                   |
| Data validation     | Pydantic 2.13                   |
| Configuration       | pydantic-settings (`.env`)      |
| Package manager     | [uv](https://docs.astral.sh/uv/)|
| Linting/formatting  | Ruff (+ pre-commit hook)        |
| Email validation    | `email-validator`               |

## Configuration

Create a `.env` file in the project root (one already exists in the branch as an example):

```env
SHOW_LOG_IN_CLI=false
```

## How to Run

```bash
# 1. Install dependencies (creates/uses the uv-managed virtual environment)
uv sync

# 2. Run the CLI application
uv run python -m src.main
```

You'll be greeted with the main menu:

```
====== Messenger ======
1. Signup
2. Login
3. Send Private Message
4. Show Private Chat
5. Change Current User
6. Show Logged-in Users
7. Show Groups
8. Create Group
9. Add User to Group
10. Send Message to Group
11. Show Group Chat
12. Logout Current User
13. Exit
```

Multiple users can "log in" within the same CLI session (the app tracks a list of logged‑in users and a "current user"), which lets you simulate a conversation between two accounts without leaving the terminal.

## Error Handling

Business‑rule violations are raised as typed exceptions (`DuplicateUsernameError`, `DuplicateEmailError`, `UserNotFoundError`, `GroupNotFoundError`, `UserAlreadyInGroupError`, `AuthorizationError`, …) defined under `src/Exceptions/`. The CLI view catches generic exceptions around each menu action and prints a friendly message instead of crashing.

## Known Limitations (by design, addressed in later phases)

- All data (users, groups, messages) lives in memory — restarting the app loses everything.
- Single process, single machine — no real networking; "multiple users" only means multiple in‑memory sessions in the same CLI run.
- Passwords are not yet hashed.
- No automated tests yet (introduced in Phase 2).

## Code Quality Tooling

- **Ruff** is configured via `ruff.toml` for linting and formatting.
- **pre-commit** (`.pre-commit-config.yaml`) runs `ruff-check --fix` and `ruff-format` on every commit.


# Nexus Chat Platform — Branch `dev2` (Phase 2)
### Networking & Concurrency: a Live, Multi‑Client Chat Server

## Overview

This branch evolves the single‑process CLI from Phase 1 into a genuine **client/server chat system**. The same business logic (`AuthService`, `MessageService`, `GroupService`, and their controllers) is reused unchanged — what's new is a networking layer built on Python's `asyncio` sockets that lets a server handle **many concurrent clients** at once, each in a separate coroutine.

A `pytest` test suite is also introduced in this phase to cover the business logic in isolation.

## What This Phase Delivers

- A standalone **async TCP server** (`src/run_server.py`) that multiple clients can connect to simultaneously
- A standalone **async TCP client** (`src/run_client.py`) that reuses the Phase‑1 CLI (`UserView`) but talks to the server over the network instead of calling services directly
- A small, custom **request/response protocol** over newline‑delimited JSON
- Per‑connection **concurrency safety**: each client is served by its own coroutine, and writes to a socket are serialized with an `asyncio.Lock` so responses/broadcasts never interleave
- A first automated **unit test suite** (`tests/test_services.py`, 330 lines) using `pytest` and mocked repositories

## Architecture

```
src/
├── ServerNetwork/
│   ├── AsyncServer.py            asyncio.start_server + per-client coroutine loop
│   ├── AsyncClient.py            asyncio client that connects to the server
│   ├── ConnectionManagement.py   tracks writer <-> user_id, per-connection locks, send()/broadcast
│   ├── RequestRouter.py          maps RequestType -> handler coroutine
│   └── RequestHandler.py         adapts network requests to the existing controllers
├── entities/
│   ├── RequestType.py            enum of all protocol actions (see below)
│   └── DTO/
│       ├── Request/*             one Pydantic model per request type (validated on receipt)
│       └── Response/ResponseModel.py
├── controllers/, service/, repository/, entities/*, core/, Exceptions/   (unchanged from Phase 1)
├── view/userView.py               same CLI menu, now driven by network calls via AsyncClient
├── run_server.py                  entry point: boots the server and registers all routes
├── run_client.py                  entry point: boots a client and starts the CLI menu
└── tests/
    ├── conftest.py
    └── test_services.py
```

### How the protocol works

1. A client sends one JSON object per line, shaped like `{"request_type": "...", "request_id": "...", "data": {...}}`.
2. `AsyncServer._handle_client` reads a line, parses it, and hands it to `RequestRouter.dispatch`.
3. `RequestRouter` looks up the `RequestType` enum value and calls the registered handler (from `RequestHandler`, which in turn calls the same `AuthController` / `MessageController` / `GroupController` used in Phase 1).
4. The result is wrapped in a `ResponseModel` (`status`, `data`, `request_id`) and written back to the same connection.
5. `ConnectionManagement` keeps a `user_id -> writer` map so the server can also **push** a message to a specific logged‑in user (used for delivering messages to a recipient even if they didn't ask for them).

### Supported request types (`RequestType` enum)

```
signup, login, logout, get_all_users_for_show_users,
send_private_message, get_private_chat,
create_group, get_all_groups_for_show_users, add_user_to_group,
send_message_to_group, get_group_chat, delete_group_by_id,
leave_private_chat, leave_group_chat, show_group_members,
delete_private_chat_history, delete_group_chat_history,
remove_user_from_group, leave_group
```

### Concurrency model

- The server is built on `asyncio.start_server`, so it's single‑threaded but non‑blocking — every connected client is handled by its own `asyncio` task (`_handle_client`), and the event loop interleaves them.
- `ConnectionManagement` keeps one `asyncio.Lock` per writer; every write to a socket (`send`) is performed inside that lock, which prevents two concurrent responses/broadcasts to the same client from corrupting each other's output.
- This satisfies the "group chat with several simultaneous clients" requirement without needing OS threads.

## Tech Stack (additions over Phase 1)

| Concern         | Choice                          |
|------------------|----------------------------------|
| Networking       | `asyncio` streams (raw TCP)     |
| Wire format      | newline-delimited JSON          |
| Testing          | `pytest` 9.x                    |
| (prep for Phase 3)| `fastapi[standard]` dependency added, not yet used for serving |

## How to Run

```bash
uv sync
```

**Start the server** (one terminal):

```bash
uv run python -m src.run_server
# Server listens on 127.0.0.1:65432
```

**Start one or more clients** (one terminal per simulated user):

```bash
uv run python -m src.run_client
```

Each client presents the same CLI menu as Phase 1, but now every action is a network round‑trip to the shared server, so messages sent from one client's terminal are actually delivered to another connected client in real time.

## Running the Tests

```bash
uv run pytest
```

`tests/test_services.py` exercises `AuthService`, `MessageService`, and `GroupService` against mocked repositories, verifying business rules such as:

- Signup rejects duplicate usernames/emails
- Sending a message to a non‑existent user raises `UserNotFoundError`
- Group operations enforce membership/ownership rules

## Known Limitations (addressed in later phases)

- Storage is still entirely in‑memory (`UserRepository` / `GroupRepository` hold Python lists) — restarting the server loses all data.
- The protocol is a custom TCP/JSON format, not HTTP — no browser, `curl`, or Postman access yet (that arrives in Phase 3).
- No authentication token/session mechanism yet — a client's identity is remembered only by which live connection sent `login`.


# Nexus Chat Platform — Branch `dev3` (Phase 3)
### Migration to a REST API (FastAPI) + JWT Auth + Clean Architecture

## Overview

This branch replaces the custom raw‑TCP protocol from Phase 2 with a standard, discoverable **HTTP REST API** built on **FastAPI**, and takes the opportunity to reorganize the codebase into a clean/layered ("onion") architecture: `domain → application → infrastructure → api`. Authentication moves from "whichever socket sent `login`" to a proper **JWT access token**. Storage is still **in‑memory** at this stage — persistence lands in Phase 4.

## What This Phase Delivers

- A FastAPI app exposing all messenger functionality under `/api/v1`
- Automatic interactive API docs at **`/docs`** (Swagger UI) and **`/redoc`**
- Request validation via Pydantic request schemas (e.g. enforced username length, email format)
- JWT‑based authentication: `POST /auth/login` returns a bearer token; protected endpoints require `Authorization: Bearer <token>`
- Password hashing via `pwdlib` (Argon2), replacing the plain‑text passwords of earlier phases
- A centralized `GlobalExceptionHandler` that maps every domain exception to the correct HTTP status code and a consistent JSON error shape
- Alembic scaffolding (`alembic.ini`, `alembic/env.py`) added ahead of time, ready to be wired to a real database in Phase 4

## Architecture

The project is restructured into a clean‑architecture layout under `app/src/`:

```
app/src/
├── domain/                      Framework-agnostic core
│   ├── entities/                 User, Group, Message, PrivateChat, token_payload, ...
│   └── repositories_Interface/   Abstract repository contracts (ports)
├── application/                  Use cases / business rules
│   ├── DTO/                      Internal data-transfer objects (group, user, message)
│   ├── security/                 password_hasher & token_service interfaces
│   └── service/
│       ├── service_Interface/          AuthService, UserService, GroupService, MessageService (contracts)
│       └── services_implementation/    concrete business logic
├── infrastructure/               Adapters — the only layer allowed to know about frameworks/storage
│   ├── repositories_implementation/    in-memory implementations of the domain interfaces
│   └── security/                       Argon2 password hasher + JWT token service implementations
├── api/                           FastAPI-specific layer
│   ├── v1/
│   │   ├── router.py                    aggregates all routers under prefix /api/v1
│   │   └── endpoints/
│   │       ├── auth_router.py           /auth
│   │       ├── user_router.py           /users
│   │       ├── group_router.py          /groups
│   │       └── message_router.py        /messages
│   ├── schemas/
│   │   ├── Request/{user,group,message}/    Pydantic request bodies
│   │   └── Response/{user,group,message}/   Pydantic response bodies + generic Response[T] envelope
│   ├── dependencies/               FastAPI Depends() wiring (dependency injection)
│   └── GlobalExceptionHandler/     exception -> HTTP response mapping
├── core/
│   ├── config/Setting.py           pydantic-settings config (.env)
│   ├── logger/                     same custom logging system carried over from Phase 1/2
│   └── exceptions/                 domain exception hierarchy (expanded: token/credential errors)
└── main.py                          FastAPI app factory / entry point
```

This mirrors classic **Clean Architecture / Hexagonal Architecture**: `domain` has zero dependencies on FastAPI or any storage tech; `application` orchestrates use cases against `domain` interfaces; `infrastructure` provides concrete implementations (still in‑memory here); `api` is a thin HTTP adapter on top of `application`.

## API Reference

All routes are mounted under the prefix **`/api/v1`**.

| Method | Path                                   | Description                          |
|--------|-----------------------------------------|---------------------------------------|
| POST   | `/auth/signup`                          | Create a new account                  |
| POST   | `/auth/login`                           | Authenticate, returns a JWT           |
| GET    | `/users/by-id/{user_id}`                | Get a user by id                      |
| GET    | `/users/logged-in`                      | List currently logged-in users        |
| GET    | `/users/all`                            | List all users                        |
| POST   | `/groups/create_group`                  | Create a group                        |
| POST   | `/groups/{group_id}/members`            | Add a user to a group                 |
| POST   | `/groups/{group_id}/messages`           | Send a message to a group             |
| GET    | `/groups/{group_id}/messages`           | Get a group's chat history            |
| GET    | `/groups/by-id/{group_id}`              | Get a group by id                     |
| GET    | `/groups/my-groups`                     | List groups the current user belongs to |
| GET    | `/groups/all`                           | List all groups                       |
| DELETE | `/groups/{group_id}`                    | Delete a group                        |
| GET    | `/groups/{group_id}/members`            | List a group's members                |
| DELETE | `/groups/{group_id}/messages`           | Clear a group's chat history          |
| DELETE | `/groups/{group_id}/members/{user_id}`  | Remove a member from a group          |
| POST   | `/messages/send_message`                | Send a private message                |
| GET    | `/messages/chat/{user2_id}`             | Get private chat history with a user  |
| DELETE | `/messages/chat/{user2_id}`             | Delete private chat history           |

Every successful response is wrapped in a generic envelope:

```json
{ "data": { /* the resource */ }, "message": "Human-readable confirmation" }
```

## Tech Stack (additions over Phase 2)

| Concern              | Choice                                   |
|------------------------|--------------------------------------------|
| Web framework          | FastAPI ≥ 0.141                            |
| ASGI server             | Uvicorn                                     |
| Auth tokens             | PyJWT                                       |
| Password hashing        | `pwdlib[argon2]`                           |
| Config                  | pydantic-settings (`.env`)                 |
| Migrations (scaffolded) | Alembic (activated in Phase 4)             |

## Configuration

Copy `app/.env.example` to `app/.env` and fill in the secret:

```env
SHOW_LOG_IN_CLI=true
JWT_SECRET_KEY=<generate a long random string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20
```

## How to Run

```bash
# from the project root
uv sync

cd app
uvicorn src.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for the interactive Swagger UI, where every endpoint can be exercised directly from the browser (use the "Authorize" button with the token returned from `/auth/login`).

## Error Handling

`GlobalExceptionHandler` (registered once in `main.py`) attaches a dedicated FastAPI exception handler for each domain exception — `DuplicateUsernameError`, `DuplicateEmailError`, `UserNotFoundError`, `GroupNotFoundError`, `UserAlreadyInGroupError`, `AuthorizationError`, `InvalidCredentialsError`, `ExpiredAccessTokenError`, `InvalidAccessTokenError`, `PrivateChatNotFoundError`, `ResponseError`, `EmptyDataException`, `UserNotInGroupError` — so clients always receive a predictable JSON error body and the correct HTTP status code instead of a generic 500.

## Known Limitations (addressed in Phase 4)

- Repositories under `infrastructure/repositories_implementation/` are still in‑memory Python lists — all data is lost on restart.
- Alembic is present but has no models/migrations to run against yet (there's no real database).
- No real‑time push — a client has to poll the REST endpoints to see new messages (solved by the WebSocket layer added later).


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

# Nexus Chat Platform — Branch `dev5` (Phase 5 — Bonus)
### Real‑Time WebSocket Layer & a NiceGUI Client Application

## Overview

This branch goes beyond the original four‑phase plan. Built on top of the Phase 4 backend (FastAPI + PostgreSQL + Redis), it adds a **persistent WebSocket channel** so clients receive messages, presence updates, and group‑membership events **in real time**, instead of having to poll the REST API. It also ships a **graphical client application** built with [NiceGUI](https://nicegui.io/), which can run either in a browser or as a native desktop window (via `pywebview`).

This is the most complete, "product‑shaped" version of the project in the repository: REST API + real‑time push + persistent storage + a working UI.

## What This Phase Delivers

- An authenticated WebSocket endpoint: **`WS /api/v1/ws`**
- A connection manager that tracks every live socket per `user_id`, supporting both `send_personal` (to one user) and `broadcast_to_users` (to many)
- A heartbeat mechanism (ping every 20s, 30s timeout) that proactively closes dead connections
- A parallel, socket‑based **request router** for real‑time actions (sending a private/group message, marking a message as read, etc.) that reuses the same `application` services as the REST layer
- A `RealTimePublisher`, used from the REST‑side services so that state changes made over plain HTTP (e.g. "add member to group") are still pushed live to everyone who is currently connected over WebSocket
- A typed WebSocket protocol (`api/schemas/WebSocket/...`): request/response envelopes, an `action`/`event` enum, and a structured error format
- A desktop/web UI (`app/UI/`) built with NiceGUI: signup/login pages and a messenger page, wired to the REST + WebSocket backend

## Architecture (what's new vs. Phase 4)

```
app/src/api/
├── v1/endpoints/websocket_router.py         WS /api/v1/ws  (auth via query-token dependency)
└── schemas/WebSocket/
    ├── websocket_action.py                   enum of client -> server actions
    ├── websocket_error_code.py                enum of structured error codes
    ├── websocket_request/                     typed payloads: send_private_message_data,
    │                                            send_group_message_data, message_read_data, ...
    └── websocket_response/                    websocket_response.py, webSocket_error_data.py

app/src/infrastructure/websocket/
├── connection_manager.py         user_id -> set[WebSocket]; send_personal / broadcast_to_users
├── WebSocketHandler.py           connection lifecycle: connect -> heartbeat + listen loop -> disconnect
├── request_router.py             action -> handler coroutine dispatch (mirrors the REST routers)
├── realtime_publisher.py         RealTimePublisher: pushes live events from REST-side services
├── websocket_error_mapper.py     domain exception -> WebSocketErrorCode
└── websocket_router_config.py    registers all socket actions with the router

app/UI/
├── main.py                        entry point — registers pages and starts the NiceGUI server
├── auth_pages.py                  /signup and /login pages
└── messenger_page.py              /messenger page (chat UI, talks to REST + WebSocket)
```

### Connection lifecycle (`WebSocketHandler.handle`)

1. Client connects to `/api/v1/ws` with a valid access token; `get_current_websocket_user_id` resolves the `user_id`.
2. `ConnectionManager.connect()` registers the socket; a `user_online` event is broadcast to everyone else currently connected.
3. A heartbeat task pings the client every 20 seconds; if no `pong` is received within 30 seconds, the connection is closed.
4. Incoming JSON messages are validated against `WebSocketRequest`, dispatched through the socket `RequestRouter`, and committed to the database; results are sent back to the sender and, depending on the event type, relayed to the other participant(s):
   - `private_message` → also sent to the receiver
   - `message_read` → also sent to the original sender
   - `group_message` → broadcast to all other group members
5. On disconnect, the socket is unregistered and a `user_offline` event is broadcast.

### Events pushed over the socket

`user_online`, `user_offline`, `private_message`, `message_read`, `group_message`, `group_member_added`, `group_member_removed`, `group_member_left`, `group_deleted`, `group_chat_deleted`, `private_chat_deleted`, plus a structured `error` event for validation/domain failures.

## Tech Stack (additions over Phase 4)

| Concern              | Choice                                  |
|------------------------|--------------------------------------------|
| Real-time transport     | FastAPI `WebSocket` (via `websockets`)     |
| Desktop/web UI           | NiceGUI                                     |
| Native window wrapper    | `pywebview`                                 |
| HTTP client (UI -> API) | `httpx`                                     |

## Configuration

Same `.env` as Phase 4 (JWT + database + pool settings). No new required variables were introduced for the WebSocket layer itself; it reuses the existing JWT token service to authenticate the socket connection.

## How to Run

**1. Backend** (same as Phase 4 — Postgres + Redis + migrations):

```bash
uv sync
docker run -d --name nexus-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
docker run -d --name nexus-redis -p 6379:6379 redis:7
alembic upgrade head

cd app
uvicorn src.main:app --reload
```

This exposes both the REST API (`/api/v1/...`, docs at `/docs`) and the WebSocket endpoint (`/api/v1/ws`).

**2. Graphical client (NiceGUI UI):**

```bash
cd app/UI
uv run python main.py
```

By default this starts a NiceGUI server on `127.0.0.1:8080` and opens a window (native, via `pywebview`) pointed at the `/signup` page. From there you can sign up, log in, and chat — messages sent by one running UI instance appear instantly in another thanks to the WebSocket layer, without any manual refresh.


