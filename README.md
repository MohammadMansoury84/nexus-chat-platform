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
