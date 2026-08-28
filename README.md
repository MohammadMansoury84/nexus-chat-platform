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
