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
