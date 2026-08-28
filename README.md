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

This mirrors classic **Clean Architecture**: `domain` has zero dependencies on FastAPI or any storage tech; `application` orchestrates use cases against `domain` interfaces; `infrastructure` provides concrete implementations (still in‑memory here); `api` is a thin HTTP adapter on top of `application`.

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
