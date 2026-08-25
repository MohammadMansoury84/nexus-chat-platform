"""
/messenger — the main realtime chat screen.

Connection architecture:
- A single WebSocket connection per user is shared by ALL browser tabs
  connected to this NiceGUI server (module-level _USER_HUBS).
- Every page instance registers an asyncio.Queue; incoming events are
  fanned out to every live tab and handled in each tab's own UI context.
- This prevents the "connection storm" caused by page rebuilds, server
  reloads, or multiple open tabs.
"""

import asyncio
import base64
import json
import random
from datetime import datetime

import httpx
import websockets
from nicegui import ui

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
WS_BASE_URL = "ws://127.0.0.1:8000/api/v1/ws"

PRIMARY_BUTTON_CLASSES = (
    "rounded-xl bg-gradient-to-r from-purple-600 to-blue-500 "
    "hover:from-purple-500 hover:to-blue-400 active:scale-[0.98] "
    "!text-white text-sm font-semibold shadow-lg shadow-purple-500/30 "
    "transition-all duration-200 ease-out hover:shadow-xl hover:shadow-purple-500/40"
)

AVATAR_GRADIENTS = [
    "from-purple-500 to-pink-400",
    "from-blue-500 to-cyan-400",
    "from-emerald-500 to-teal-400",
    "from-orange-500 to-amber-400",
    "from-rose-500 to-pink-400",
    "from-indigo-500 to-purple-400",
    "from-sky-500 to-blue-400",
    "from-fuchsia-500 to-purple-400",
]

CUSTOM_CSS = """
<style>
:root {
  --bg-app: #F4F5F9;
  --bg-panel: #FFFFFF;
  --bg-panel-soft: #F8F9FC;
  --bg-input: #F2F3F7;
  --bg-hover: #F3F4F8;
  --border-soft: #E9EBF2;
  --text-1: #111827;
  --text-2: #6B7280;
  --text-3: #9CA3AF;
  --bubble-in: #FFFFFF;
  --bubble-in-border: #E9EBF2;
  --active-bg: rgba(139,92,246,.09);
  --active-border: rgba(139,92,246,.30);
  --active-text: #6D28D9;
  --toast-bg: rgba(255,255,255,.97);
  --toast-border: rgba(139,92,246,.15);
  --scroll-thumb: rgba(139,92,246,.28);
  --msg-a: rgba(167,139,250,.08);
  --msg-b: rgba(96,165,250,.08);
  --tab-active: #7C3AED;
  --tab-inactive: #9CA3AF;
  --tab-bg: rgba(139,92,246,.10);
  --input-text: #111827;
  --overlay: rgba(15,23,42,.45);
}
html.theme-dark {
  --bg-app: #0D0F16;
  --bg-panel: #161926;
  --bg-panel-soft: #1B1F2E;
  --bg-input: #1F2434;
  --bg-hover: #1D2231;
  --border-soft: #262B3B;
  --text-1: #F3F4F6;
  --text-2: #A5ADC0;
  --text-3: #6B7280;
  --bubble-in: #1F2432;
  --bubble-in-border: #2A3042;
  --active-bg: rgba(139,92,246,.16);
  --active-border: rgba(139,92,246,.38);
  --active-text: #A78BFA;
  --toast-bg: rgba(22,25,38,.97);
  --toast-border: #2A3042;
  --scroll-thumb: rgba(139,92,246,.35);
  --msg-a: rgba(139,92,246,.07);
  --msg-b: rgba(59,130,246,.07);
  --tab-active: #A78BFA;
  --tab-inactive: #6B7280;
  --tab-bg: rgba(139,92,246,.15);
  --input-text: #F3F4F6;
  --overlay: rgba(0,0,0,.60);
}

html, body {
  margin: 0; background: var(--bg-app); overflow: hidden;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  transition: background-color .3s ease;
}

.bg-app        { background: var(--bg-app) !important; }
.bg-panel      { background: var(--bg-panel) !important; }
.bg-panel-soft { background: var(--bg-panel-soft) !important; }
.bg-input      { background: var(--bg-input) !important; color: var(--input-text); border-radius: 12px; }
.border-soft   { border-color: var(--border-soft) !important; }
.text-1        { color: var(--text-1) !important; }
.text-2        { color: var(--text-2) !important; }
.text-3        { color: var(--text-3) !important; }
.text-active   { color: var(--active-text) !important; }

.hover-row            { transition: background-color .15s ease; }
.hover-row:hover      { background: var(--bg-hover); }
.active-row           { background: var(--active-bg) !important; border-color: var(--active-border) !important; }
.bubble-in            { background: var(--bubble-in) !important; border: 1px solid var(--bubble-in-border) !important; }
.toast-surface        { background: var(--toast-bg) !important; border: 1px solid var(--toast-border) !important; backdrop-filter: blur(10px); }
.dot-ring             { border: 2px solid var(--bg-panel); }

.msg-bg {
  background-color: var(--bg-app);
  background-image:
    radial-gradient(at 15% 15%, var(--msg-a) 0, transparent 45%),
    radial-gradient(at 85% 85%, var(--msg-b) 0, transparent 45%);
}

.bg-panel, .bg-panel-soft, .bg-app, .bubble-in, .toast-surface {
  transition: background-color .3s ease, border-color .3s ease;
}
.text-1, .text-2, .text-3, .text-active { transition: color .3s ease; }

/* Tabs */
.messenger-tabs .q-tab { border-radius: 12px; min-height: 38px; color: var(--tab-inactive); transition: all .2s ease; }
.messenger-tabs .q-tab--active { color: var(--tab-active); background: var(--tab-bg); }
.messenger-tabs .q-tab__indicator { display: none; }
.messenger-tabs .q-tab__icon { font-size: 18px; }
.messenger-tabs .q-tab__label { text-transform: none; font-weight: 600; font-size: 13px; }

/* Quasar tweaks */
.q-field__native, .q-field__prefix, .q-field__suffix, .q-field__input { color: var(--input-text); }
.q-field__label { color: var(--text-3) !important; }
.q-field--outlined .q-field__control:before { border-color: var(--border-soft) !important; }
.q-dialog__backdrop { background: var(--overlay); }
html.theme-dark .q-menu { background: var(--bg-panel-soft) !important; }
html.theme-dark .q-item, html.theme-dark .q-item__label { color: var(--text-1) !important; }

/* Scrollbar */
.nice-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
.nice-scroll::-webkit-scrollbar-track { background: transparent; }
.nice-scroll::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 999px; }

/* Animations */
@keyframes toast-in {
  from { opacity: 0; transform: translateX(48px) scale(.95); }
  to   { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes toast-out {
  from { opacity: 1; transform: translateX(0) scale(1); }
  to   { opacity: 0; transform: translateX(48px) scale(.95); }
}
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(34,197,94,.45); }
  70%  { box-shadow: 0 0 0 7px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.toast-card         { animation: toast-in .35s cubic-bezier(.21,1.02,.73,1) both; }
.toast-card.leaving { animation: toast-out .25s ease-in both; }
.pulse-online       { animation: pulse-ring 2s infinite; }
</style>
<script>
(function () {
  try {
    if ((localStorage.getItem('theme') || 'light') === 'dark')
      document.documentElement.classList.add('theme-dark');
  } catch (e) {}
})();
</script>
"""


def avatar_gradient(seed: str) -> str:
    seed = seed or "?"
    return AVATAR_GRADIENTS[sum(ord(c) for c in seed) % len(AVATAR_GRADIENTS)]


_USER_HUBS: dict[str, dict] = {}


def _ws_reject_status(exc: Exception):
    """Extract the HTTP status code from a websockets connection error."""
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    return status


def _token_exp(token: str) -> int:
    try:
        parts = token.split(".")
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return int(payload.get("exp") or 0)
    except Exception:
        return 0


class ChatState:
    def __init__(self, token: str, my_id: str, my_username: str) -> None:
        self.token = token
        self.my_id = my_id
        self.my_username = my_username
        self.dark = False
        self.connected = False

        self.users: list[dict] = []
        self.groups: list[dict] = []
        self.online_ids: set[str] = set()

        self.active_kind: str | None = None  
        self.active_id: str | None = None
        self.active_name: str | None = None

        self.messages: list[dict] = []


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def format_timestamp(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return ""


@ui.page("/messenger")
async def messenger_page():
    ui.add_head_html(CUSTOM_CSS)
    ui.colors(primary="#8B5CF6", secondary="#60A5FA", accent="#A78BFA")

    boot = await ui.run_javascript(
        "JSON.stringify({token: localStorage.getItem('access_token'),"
        " theme: localStorage.getItem('theme') || 'light'})",
        timeout=5.0,
    )
    try:
        boot_info = json.loads(boot) if boot else {}
    except Exception:
        boot_info = {}

    token = boot_info.get("token")
    if not token:
        ui.navigate.to("/login")
        return

    my_id, my_username = _decode_token_payload(token)
    if not my_id:
        ui.run_javascript("localStorage.removeItem('access_token')")
        ui.navigate.to("/login")
        return

    state = ChatState(token=token, my_id=my_id, my_username=my_username)
    state.dark = boot_info.get("theme") == "dark"


    def update_theme_icon():
        theme_icon_holder.clear()
        with theme_icon_holder:
            ui.icon("light_mode" if state.dark else "dark_mode").classes("text-[18px]")

    async def toggle_theme():
        try:
            dark = await ui.run_javascript("""
                (() => {
                    const el = document.documentElement;
                    const dark = el.classList.toggle('theme-dark');
                    try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
                    return dark;
                })()
            """)
        except Exception:
            return
        state.dark = bool(dark)
        update_theme_icon()


    with ui.element("div").classes("h-screen w-full flex bg-app overflow-hidden"):
        with ui.column().classes(
            "w-[330px] h-full bg-panel border-r border-soft flex flex-col gap-0 p-0 "
            "shadow-[6px_0_24px_rgba(17,24,39,0.04)] z-10"
        ):
            with ui.row().classes(
                "items-center justify-between w-full px-5 py-4 border-b border-soft"
            ):
                with ui.row().classes("items-center gap-3"):
                    with ui.element("div").classes(
                        "w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500 via-violet-500 to-sky-400 "
                        "flex items-center justify-center shadow-lg shadow-purple-500/30"
                    ):
                        ui.icon("forum").classes("text-white text-lg")
                    with ui.column().classes("gap-0"):
                        ui.label(my_username).classes(
                            "text-sm font-bold text-1 leading-tight"
                        )
                        ui.label("F3 Messenger").classes("text-[11px] text-3")
                with ui.row().classes("items-center gap-1"):
                    theme_btn = (
                        ui.button(on_click=toggle_theme)
                        .props("flat round dense size=sm")
                        .classes("text-3 hover:text-purple-500")
                        .tooltip("Toggle dark / light theme")
                    )
                    with theme_btn:
                        theme_icon_holder = ui.element("span").classes(
                            "flex items-center justify-center"
                        )
                    connection_dot = ui.element("div").classes(
                        "w-2.5 h-2.5 rounded-full bg-red-500"
                    ).tooltip("Connection status")

            update_theme_icon()

            with ui.tabs().classes(
                "w-full bg-transparent px-4 pt-3 messenger-tabs"
            ) as tabs:
                users_tab = ui.tab("Chats", icon="chat_bubble").classes("flex-1")
                groups_tab = ui.tab("Groups", icon="groups").classes("flex-1")

            with ui.tab_panels(tabs, value=users_tab).classes(
                "w-full flex-1 bg-transparent p-0 nice-scroll"
            ).style("overflow-y: auto;"):
                with ui.tab_panel(users_tab).classes("p-2 gap-1"):
                    users_list_container = ui.column().classes("w-full gap-1")
                with ui.tab_panel(groups_tab).classes("p-2 gap-2"):
                    ui.button(
                        "New group",
                        icon="add",
                        on_click=lambda: create_group_dialog(state, refresh_groups),
                    ).props("flat no-caps").classes(
                        "w-full text-active justify-start text-sm font-semibold rounded-xl"
                    )
                    groups_list_container = ui.column().classes("w-full gap-1 mt-1")


        with ui.column().classes("flex-1 h-full bg-app flex flex-col"):
            chat_header = ui.row().classes(
                "items-center justify-between w-full px-6 py-3.5 border-b border-soft bg-panel z-[5]"
            )
            with chat_header:
                with ui.row().classes("items-center gap-2.5"):
                    ui.icon("chat_bubble_outline").classes("text-3 text-xl")
                    ui.label("Select a chat").classes("text-3 font-medium text-sm")

            messages_area = ui.column().classes(
                "flex-1 w-full px-6 py-5 gap-2.5 nice-scroll msg-bg"
            ).style("overflow-y: auto;").props('id="messages-scroll-area"')

            with ui.row().classes(
                "items-center gap-3 w-full px-5 py-3.5 border-t border-soft bg-panel"
            ):
                message_input = (
                    ui.input(placeholder="Type a message…")
                    .props("outlined dense rounded")
                    .classes("flex-1 bg-input")
                )
                send_btn = (
                    ui.button()
                    .props("round dense unelevated")
                    .style(
                        "background:linear-gradient(135deg,#8B5CF6,#3B82F6);"
                        "box-shadow:0 10px 22px -8px rgba(139,92,246,0.65);"
                    )
                    .classes("hover:scale-105 active:scale-95 transition-transform")
                )
                with send_btn:
                    ui.html(
                        '''<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
                            <path d="M0 0h24v24H0z" fill="none" />
                            <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9.912 12H4L2.023 4.135A.7.7 0 0 1 2 3.995c-.022-.721.772-1.221 1.46-.891L22 12L3.46 20.896c-.68.327-1.464-.159-1.46-.867a.7.7 0 0 1 .033-.186L3.5 15" />
                        </svg>'''
                    ).classes("text-white text-[19px] leading-none flex items-center justify-center")


    toast_container = ui.element("div").classes(
        "fixed top-5 right-5 z-[9999] flex flex-col gap-2.5 w-[330px] pointer-events-none"
    )


    def show_toast(icon: str, title: str, message: str = "", tone: str = "info"):
        tones = {
            "info": "from-purple-500 to-blue-500",
            "success": "from-emerald-500 to-teal-400",
            "warning": "from-amber-500 to-orange-400",
            "danger": "from-rose-500 to-pink-500",
        }
        grad = tones.get(tone, tones["info"])

        with toast_container:
            with ui.row().classes(
                f"toast-card toast-surface pointer-events-auto items-center gap-3 w-full "
                f"rounded-2xl px-3.5 py-3 shadow-[0_12px_32px_-8px_rgba(17,24,39,0.18)]"
            ) as card:
                with ui.element("div").classes(
                    f"w-10 h-10 rounded-xl bg-gradient-to-br {grad} "
                    f"flex items-center justify-center shrink-0 shadow-md"
                ):
                    ui.icon(icon).classes("text-white text-sm")
                with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                    ui.label(title).classes(
                        "text-sm font-semibold text-1 leading-snug break-words"
                    )
                    if message:
                        ui.label(message).classes(
                            "text-xs text-2 leading-snug break-words"
                        )
                ui.button(icon="close", on_click=lambda: card.delete()).props(
                    "flat round dense size=xs"
                ).classes("text-3 hover:text-2 shrink-0")

        async def _auto_remove():
            try:
                await asyncio.sleep(3.0)
                card.classes(add="leaving")
                await asyncio.sleep(0.25)
                card.delete()
            except Exception:
                pass

        asyncio.create_task(_auto_remove())


    def get_username(user_id: str) -> str:
        for u in state.users:
            if u["id"] == user_id:
                return u["username"]
        return "Unknown"

    def get_group_name(group_id) -> str:
        return next(
            (g["group_name"] for g in state.groups if g["group_id"] == group_id),
            "A group",
        )

    def render_users_list():
        users_list_container.clear()
        with users_list_container:
            if not state.users:
                with ui.column().classes("w-full items-center gap-2 py-10"):
                    ui.icon("person_off").classes("text-3xl text-3")
                    ui.label("No other users yet").classes("text-3 text-xs")
            for u in state.users:
                is_online = u["id"] in state.online_ids
                is_active = (
                    state.active_kind == "user" and state.active_id == u["id"]
                )
                with ui.row().classes(
                    "w-full items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer "
                    "transition-all duration-150 border "
                    + (
                        "active-row shadow-sm shadow-purple-500/10"
                        if is_active
                        else "border-transparent hover-row"
                    )
                ).on(
                    "click",
                    lambda e, u=u: open_chat(
                        state, "user", u["id"], u["username"]
                    ),
                ):
                    with ui.element("div").classes("relative shrink-0"):
                        with ui.element("div").classes(
                            f"w-10 h-10 rounded-full bg-gradient-to-br {avatar_gradient(u['username'])} "
                            "flex items-center justify-center shadow-sm"
                        ):
                            ui.label(u["username"][:1].upper()).classes(
                                "text-sm font-bold text-white"
                            )
                        ui.element("div").classes(
                            "dot-ring absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full "
                            + ("bg-green-500" if is_online else "bg-gray-300")
                        )
                    ui.label(u["username"]).classes(
                        "text-sm font-medium text-1 truncate"
                        + (" text-active" if is_active else "")
                    )

    def render_groups_list():
        groups_list_container.clear()
        with groups_list_container:
            if not state.groups:
                with ui.column().classes("w-full items-center gap-2 py-10"):
                    ui.icon("group_off").classes("text-3xl text-3")
                    ui.label("No groups yet").classes("text-3 text-xs")
            for g in state.groups:
                is_active = (
                    state.active_kind == "group"
                    and state.active_id == g["group_id"]
                )
                with ui.row().classes(
                    "w-full items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer "
                    "transition-all duration-150 border "
                    + (
                        "active-row shadow-sm shadow-purple-500/10"
                        if is_active
                        else "border-transparent hover-row"
                    )
                ).on(
                    "click",
                    lambda e, g=g: open_chat(
                        state, "group", g["group_id"], g["group_name"]
                    ),
                ):
                    with ui.element("div").classes(
                        "w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 "
                        "flex items-center justify-center shrink-0 shadow-sm"
                    ):
                        ui.icon("groups").classes("text-white text-sm")
                    ui.label(g["group_name"]).classes(
                        "text-sm font-medium text-1 truncate"
                        + (" text-active" if is_active else "")
                    )

    def render_chat_header():
        chat_header.clear()
        with chat_header:
            if not state.active_kind:
                with ui.row().classes("items-center gap-2.5"):
                    ui.icon("chat_bubble_outline").classes("text-3 text-xl")
                    ui.label("Select a chat to start messaging").classes(
                        "text-3 font-medium text-sm"
                    )
                return

            with ui.row().classes("items-center gap-3 flex-1 min-w-0"):
                if state.active_kind == "group":
                    with ui.row().classes(
                        "items-center gap-3 cursor-pointer select-none rounded-xl "
                        "px-2 py-1.5 -ml-2 hover-row"
                    ).on("click", lambda e: open_group_info()):
                        with ui.element("div").classes(
                            "w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-500 "
                            "flex items-center justify-center shadow-md shadow-blue-500/25 shrink-0"
                        ):
                            ui.icon("groups").classes("text-white text-sm")
                        with ui.column().classes("gap-0 min-w-0"):
                            ui.label(state.active_name or "").classes(
                                "text-1 font-semibold text-[15px] leading-tight truncate"
                            )
                            ui.label("Tap to view group info").classes(
                                "text-[11px] text-3"
                            )
                        ui.icon("expand_more").classes("text-3")
                else:
                    online = state.active_id in state.online_ids
                    with ui.element("div").classes("relative shrink-0"):
                        with ui.element("div").classes(
                            f"w-10 h-10 rounded-full bg-gradient-to-br {avatar_gradient(state.active_name or '')} "
                            "flex items-center justify-center shadow-md"
                        ):
                            ui.label((state.active_name or "?")[:1].upper()).classes(
                                "text-sm font-bold text-white"
                            )
                        ui.element("div").classes(
                            "dot-ring absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full "
                            + ("bg-green-500" if online else "bg-gray-300")
                        )
                    with ui.column().classes("gap-0 min-w-0"):
                        ui.label(state.active_name or "").classes(
                            "text-1 font-semibold text-[15px] leading-tight truncate"
                        )
                        ui.label("Private chat").classes("text-[11px] text-3")

            if state.active_kind == "user":
                with ui.row().classes("items-center gap-0.5"):
                    ui.button(
                        icon="delete_outline",
                        on_click=lambda: delete_private_chat(state),
                    ).props("flat round dense").classes(
                        "text-3 hover:text-rose-500"
                    ).tooltip("Delete chat")

    def render_messages():
        messages_area.clear()
        with messages_area:
            if not state.active_kind:
                with ui.column().classes("w-full items-center gap-3 pt-20"):
                    with ui.element("div").classes(
                        "w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/15 to-blue-500/15 "
                        "flex items-center justify-center"
                    ):
                        ui.icon("forum").classes("text-5xl text-purple-400/70")
                    ui.label("Welcome to F3 Messenger").classes(
                        "text-lg font-semibold text-1"
                    )
                    ui.label("Select a chat to start messaging").classes(
                        "text-sm text-3"
                    )
                return

            if not state.messages:
                with ui.column().classes("w-full items-center gap-2 pt-20"):
                    ui.icon("waving_hand").classes("text-3xl text-purple-400/70")
                    ui.label("No messages yet").classes(
                        "text-sm font-medium text-2"
                    )
                    ui.label("Be the first to say hi!").classes(
                        "text-xs text-3"
                    )
                return

            for m in state.messages:
                mine = m.get("sender_id") == state.my_id
                sender_name = m.get("username") or (
                    state.my_username if mine else get_username(m.get("sender_id"))
                )
                time_str = format_timestamp(m.get("created_at", ""))

                with ui.row().classes(
                    "w-full items-end gap-2 "
                    + ("justify-end" if mine else "justify-start")
                ):
                    if not mine and state.active_kind == "group":
                        with ui.element("div").classes(
                            f"w-8 h-8 rounded-full bg-gradient-to-br {avatar_gradient(sender_name)} "
                            "flex items-center justify-center shrink-0 mb-1 shadow-sm"
                        ):
                            ui.label((sender_name or "?")[:1].upper()).classes(
                                "text-[11px] font-bold text-white"
                            )

                    with ui.column().classes(
                        "max-w-[68%] rounded-2xl px-4 py-2.5 gap-1 "
                        + (
                            "bg-gradient-to-br from-purple-600 to-blue-500 rounded-br-md "
                            "shadow-md shadow-purple-500/20"
                            if mine
                            else "bubble-in rounded-bl-md shadow-sm shadow-gray-900/5"
                        )
                    ):
                        if not mine and state.active_kind == "group":
                            ui.label(sender_name or "Unknown").classes(
                                "text-[11px] font-bold text-active"
                            )
                        ui.label(m.get("content", "")).classes(
                            "text-sm leading-relaxed break-words whitespace-pre-wrap "
                            + ("text-white" if mine else "text-1")
                        )
                        with ui.row().classes("items-center gap-1 justify-end"):
                            if time_str:
                                ui.label(time_str).classes(
                                    "text-[10px] "
                                    + ("text-white/70" if mine else "text-3")
                                )
                            if mine:
                                if m.get("status") == "read":
                                    ui.icon("done_all").classes(
                                        "text-[13px] text-sky-200"
                                    )
                                else:
                                    ui.icon("done").classes(
                                        "text-[13px] text-white/60"
                                    )

            ui.timer(0.05, lambda: ui.run_javascript(
                """
                const el = document.getElementById('messages-scroll-area');
                if (el) { el.scrollTop = el.scrollHeight; }
                """
            ), once=True)

    async def load_users():
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE_URL}/users/all", headers=auth_headers(state.token)
            )
        if resp.status_code == 200:
            data = resp.json().get("data") or []
            state.users = [u for u in data if u["id"] != state.my_id]
        render_users_list()

    async def load_online_users():
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE_URL}/users/logged-in", headers=auth_headers(state.token)
            )
        if resp.status_code == 200:
            data = resp.json().get("data") or []
            state.online_ids = {u["id"] for u in data}
        render_users_list()

    async def refresh_groups():
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE_URL}/groups/my-groups", headers=auth_headers(state.token)
            )
        if resp.status_code == 200:
            state.groups = resp.json().get("data") or []
        render_groups_list()

    async def load_private_chat(other_user_id: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE_URL}/messages/chat/{other_user_id}",
                headers=auth_headers(state.token),
            )
        state.messages = resp.json().get("data") or [] if resp.status_code == 200 else []
        render_messages()

    async def load_group_chat(group_id: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE_URL}/groups/{group_id}/messages",
                headers=auth_headers(state.token),
            )
        state.messages = resp.json().get("data") or [] if resp.status_code == 200 else []
        render_messages()

    def open_chat(state: ChatState, kind: str, chat_id: str, name: str):
        state.active_kind = kind
        state.active_id = chat_id
        state.active_name = name
        render_users_list()
        render_groups_list()
        render_chat_header()

        if kind == "user":
            asyncio.create_task(load_private_chat(chat_id))
        else:
            asyncio.create_task(load_group_chat(chat_id))

    async def leave_group(state: ChatState, on_updated):
        if state.active_kind != "group" or not state.active_id:
            return
        group_name = state.active_name or "group"

        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{API_BASE_URL}/groups/{state.active_id}/members/{state.my_id}",
                headers=auth_headers(state.token),
            )

        if resp.status_code in (200, 204):
            state.groups = [g for g in state.groups if g["group_id"] != state.active_id]
            state.active_kind = None
            state.active_id = None
            state.active_name = None
            state.messages = []
            render_groups_list()
            render_chat_header()
            render_messages()
            show_toast("logout", "You left the group", group_name)
            await on_updated()
        else:
            try:
                detail = resp.json().get("detail", "Failed to leave group.")
            except Exception:
                detail = "Failed to leave group."
            show_toast("error_outline", "Couldn't leave group", detail, "danger")

    async def delete_group(state: ChatState, on_updated):
        if state.active_kind != "group" or not state.active_id:
            return
        group_name = state.active_name or "group"

        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{API_BASE_URL}/groups/{state.active_id}",
                headers=auth_headers(state.token),
            )

        if resp.status_code == 200:
            state.groups = [g for g in state.groups if g["group_id"] != state.active_id]
            state.active_kind = None
            state.active_id = None
            state.active_name = None
            state.messages = []
            render_groups_list()
            render_chat_header()
            render_messages()
            show_toast("delete_forever", "Group deleted", group_name, "danger")
            await on_updated()
        else:
            try:
                detail = resp.json().get("detail", "Failed to delete group.")
            except Exception:
                detail = "Failed to delete group."
            show_toast("error_outline", "Couldn't delete group", detail, "danger")

    async def delete_private_chat(state: ChatState):
        if not state.active_id or state.active_kind != "user":
            return
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{API_BASE_URL}/messages/chat/{state.active_id}",
                headers=auth_headers(state.token),
            )
        state.messages = []
        render_messages()
        show_toast("delete_outline", "Chat history deleted", state.active_name or "")

    async def delete_group_chat_history(state: ChatState):
        if not state.active_id or state.active_kind != "group":
            return
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{API_BASE_URL}/groups/{state.active_id}/messages",
                headers=auth_headers(state.token),
            )
        state.messages = []
        render_messages()
        show_toast("cleaning_services", "History cleared", state.active_name or "")

    def open_group_info():
        if state.active_kind != "group" or not state.active_id:
            return
        gid = state.active_id

        with ui.dialog() as dialog, ui.card().classes(
            "bg-panel !p-0 w-[400px] max-w-[92vw] rounded-3xl overflow-hidden "
            "border border-soft shadow-2xl"
        ):
            content = ui.column().classes("w-full gap-0")

        async def fetch_members() -> tuple[list[dict], bool]:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{API_BASE_URL}/groups/{gid}/members",
                        headers=auth_headers(state.token),
                    )
                if resp.status_code == 200:
                    return resp.json().get("data") or [], True
                return [], False
            except Exception:
                return [], False

        async def remove_member(user_id: str):
            async with httpx.AsyncClient() as client:
                resp = await client.delete(
                    f"{API_BASE_URL}/groups/{gid}/members/{user_id}",
                    headers=auth_headers(state.token),
                )
            if resp.status_code in (200, 204):
                show_toast("person_remove", "Member removed", "", "success")
                await render_info()
            else:
                try:
                    detail = resp.json().get("detail", "Failed to remove member.")
                except Exception:
                    detail = "Failed to remove member."
                show_toast("error_outline", "Couldn't remove member", detail, "danger")

        async def do_clear_history():
            dialog.close()
            await delete_group_chat_history(state)

        async def do_leave():
            dialog.close()
            await leave_group(state, refresh_groups)

        async def do_delete():
            dialog.close()
            await delete_group(state, refresh_groups)

        def _member_row(m: dict):
            online = m["id"] in state.online_ids
            with ui.row().classes("w-full items-center gap-3 px-3 py-2 rounded-xl hover-row"):
                with ui.element("div").classes("relative shrink-0"):
                    with ui.element("div").classes(
                        f"w-9 h-9 rounded-full bg-gradient-to-br {avatar_gradient(m['username'])} "
                        "flex items-center justify-center shadow-sm"
                    ):
                        ui.label(m["username"][:1].upper()).classes(
                            "text-xs font-bold text-white"
                        )
                    ui.element("div").classes(
                        "dot-ring absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full "
                        + ("bg-green-500" if online else "bg-gray-400")
                    )
                with ui.column().classes("gap-0 min-w-0 flex-1"):
                    ui.label(m["username"]).classes(
                        "text-sm font-medium text-1 truncate"
                    )
                    ui.label("online" if online else "offline").classes(
                        "text-[11px] " + ("text-green-500" if online else "text-3")
                    )
                if m["id"] == state.my_id:
                    ui.label("You").classes(
                        "text-[10px] font-bold text-3 border border-soft "
                        "px-2 py-0.5 rounded-full"
                    )
                else:
                    ui.button(
                        icon="person_remove",
                        on_click=lambda e, uid=m["id"]: asyncio.create_task(
                            remove_member(uid)
                        ),
                    ).props("flat round dense size=sm").classes(
                        "text-3 hover:text-rose-500"
                    ).tooltip("Remove from group")

        def _action_row(icon_name: str, label: str, cls: str, fn):
            with ui.row().classes(
                "w-full items-center gap-3 px-3 py-2.5 rounded-xl hover-row cursor-pointer"
            ).on("click", lambda e: asyncio.create_task(fn())):
                ui.icon(icon_name).classes(f"text-[18px] {cls}")
                ui.label(label).classes(f"text-sm font-medium {cls}")

        async def render_info():
            content.clear()
            members, ok = await fetch_members()
            member_ids = {m["id"] for m in members}
            with content:
                with ui.element("div").classes(
                    "relative w-full flex flex-col items-center gap-2 px-6 pt-7 pb-5 "
                    "bg-panel-soft border-b border-soft"
                ):
                    ui.button(icon="close", on_click=dialog.close).props(
                        "flat round dense size=sm"
                    ).classes("absolute top-3 right-3 text-3 hover:text-rose-400")
                    with ui.element("div").classes(
                        "w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500 via-violet-500 to-purple-500 "
                        "flex items-center justify-center shadow-xl shadow-purple-500/30"
                    ):
                        ui.icon("groups").classes("text-white text-3xl")
                    ui.label(state.active_name or "Group").classes(
                        "text-lg font-bold text-1 text-center pt-1"
                    )
                    ui.label(
                        f"{len(members)} member" + ("" if len(members) == 1 else "s")
                    ).classes("text-xs text-3")

                with ui.element("div").classes(
                    "w-full px-3 py-2 nice-scroll max-h-[300px]"
                ).style("overflow-y: auto;"):
                    if not ok:
                        ui.label("Failed to load members.").classes(
                            "text-xs text-3 px-3 py-4 text-center"
                        )
                    else:
                        with ui.row().classes(
                            "w-full items-center gap-3 px-3 py-2.5 rounded-xl hover-row cursor-pointer"
                        ).on("click", lambda e: render_add(member_ids)):
                            with ui.element("div").classes(
                                "w-9 h-9 rounded-full border-2 border-dashed border-purple-400/70 "
                                "flex items-center justify-center shrink-0"
                            ):
                                ui.icon("person_add").classes("text-purple-500 text-[18px]")
                            ui.label("Add member").classes(
                                "text-sm font-semibold text-active"
                            )
                        for m in members:
                            _member_row(m)

                with ui.element("div").classes("w-full border-t border-soft px-3 py-2"):
                    _action_row(
                        "cleaning_services", "Clear chat history",
                        "text-2", do_clear_history,
                    )
                    _action_row("logout", "Leave group", "text-amber-500", do_leave)
                    _action_row(
                        "delete_forever", "Delete group", "text-rose-500", do_delete
                    )

        def render_add(existing_ids: set):
            content.clear()
            with content:
                with ui.row().classes(
                    "items-center gap-2 w-full px-4 pt-4 pb-3 border-b border-soft"
                ):
                    ui.button(
                        icon="arrow_back",
                        on_click=lambda e: asyncio.create_task(render_info()),
                    ).props("flat round dense").classes("text-2")
                    ui.label("Add member").classes("text-base font-bold text-1")

                with ui.column().classes("w-full px-5 py-4 gap-3"):
                    options = {
                        u["id"]: u["username"]
                        for u in state.users
                        if u["id"] not in existing_ids
                    }
                    if not options:
                        with ui.column().classes("w-full items-center gap-2 py-8"):
                            ui.icon("celebration").classes("text-3xl text-3")
                            ui.label("Everyone is already here").classes(
                                "text-sm text-2"
                            )
                    else:
                        select = (
                            ui.select(options, label="Choose a user")
                            .props("outlined dense")
                            .classes("w-full bg-input rounded-xl")
                        )
                        error_label = ui.label("").classes(
                            "text-red-400 text-xs min-h-4"
                        )

                        async def submit():
                            if not select.value:
                                error_label.text = "Pick a user first."
                                return
                            async with httpx.AsyncClient() as client:
                                resp = await client.post(
                                    f"{API_BASE_URL}/groups/{gid}/members",
                                    json={"user_id": select.value},
                                    headers=auth_headers(state.token),
                                )
                            if resp.status_code == 200:
                                ui.notify("Member added", type="positive")
                                await render_info()
                            else:
                                try:
                                    error_label.text = resp.json().get(
                                        "detail", "Failed to add member."
                                    )
                                except Exception:
                                    error_label.text = "Failed to add member."

                        ui.button(
                            "Add to group", icon="person_add", on_click=submit
                        ).props("no-caps unelevated").classes(
                            PRIMARY_BUTTON_CLASSES + " w-full mt-1"
                        )

        dialog.open()
        asyncio.create_task(render_info())


    async def send_current_message():
        text = message_input.value.strip() if message_input.value else ""
        if not text or not state.active_kind:
            return

        message_input.value = ""

        if state.active_kind == "user":
            await ws_send(
                action="send_private_message",
                data={"receiver_id": state.active_id, "content": text},
            )
            state.messages.append({
                "sender_id": state.my_id,
                "username": state.my_username,
                "content": text,
                "status": "sent",
                "created_at": datetime.now().isoformat(),
            })
            render_messages()
        else:
            await ws_send(
                action="send_group_message",
                data={"group_id": state.active_id, "content": text},
            )
            state.messages.append({
                "sender_id": state.my_id,
                "username": state.my_username,
                "content": text,
                "created_at": datetime.now().isoformat(),
            })
            render_messages()

    send_btn.on_click(send_current_message)
    message_input.on("keydown.enter", send_current_message)

    hub = _USER_HUBS.setdefault(state.my_id, {
        "token": state.token,
        "task": None,
        "ws": None,
        "connected": False,
        "queues": set(),
    })

    if _token_exp(state.token) >= _token_exp(hub["token"]):
        hub["token"] = state.token

    event_queue: asyncio.Queue = asyncio.Queue()

    def broadcast_event(event: dict):
        """Fan an event out to every live tab of this user."""
        for q in list(hub["queues"]):
            try:
                q.put_nowait(event)
            except Exception:
                pass

    def push_to_me(event: dict):
        try:
            event_queue.put_nowait(event)
        except Exception:
            pass

    async def ws_send(action: str, data: dict):
        ws = hub.get("ws")
        if not ws or not hub.get("connected"):
            ui.notify("Not connected — reconnecting...", type="warning")
            return
        try:
            await ws.send(
                json.dumps({"action": action, "request_id": None, "data": data})
            )
        except Exception:
            hub["connected"] = False
            broadcast_event({"event": "__status", "data": {"connected": False}})

    async def mark_read(chat_partner_id: str):
        await ws_send(
            action="message_read", data={"chat_partner_id": chat_partner_id}
        )

    def update_connection_dot():
        connection_dot.classes(
            replace="w-2.5 h-2.5 rounded-full "
            + ("bg-green-500 pulse-online" if state.connected else "bg-red-500")
        )

    async def handle_ws_event(event: dict):
        name = event.get("event")
        data = event.get("data") or {}

        if name == "ping":
            ws = hub.get("ws")
            if ws and hub.get("connected"):
                try:
                    await ws.send(json.dumps({"action": "pong"}))
                except Exception:
                    pass
            return

        if name == "connected":
            return

        if name == "user_online":
            uid = data.get("user_id")
            is_new_user = uid is not None and not any(
                u["id"] == uid for u in state.users
            )
            state.online_ids.add(uid)
            if is_new_user:
                await load_users()
            else:
                render_users_list()
            render_chat_header()

        elif name == "user_offline":
            state.online_ids.discard(data.get("user_id"))
            render_users_list()
            render_chat_header()

        elif name == "private_message":
            sender_id = data.get("sender_id")
            sender_name = data.get("username") or get_username(sender_id)
            is_current_chat = (
                state.active_kind == "user"
                and state.active_id in (sender_id, data.get("receiver_id"))
            )
            if sender_id == state.my_id:
                pass
            elif is_current_chat:
                if "username" not in data or not data["username"]:
                    data["username"] = sender_name
                state.messages.append(data)
                render_messages()
                await mark_read(sender_id)
            else:
                preview = (data.get("content") or "").strip()
                show_toast(
                    "chat_bubble",
                    f"New message from {sender_name}",
                    preview[:60] + ("…" if len(preview) > 60 else ""),
                )

        elif name == "group_message":
            group_id = data.get("group_id")
            if "username" not in data or not data["username"]:
                data["username"] = get_username(data.get("sender_id"))
            sender_name = data["username"] or "Someone"

            if state.active_kind == "group" and state.active_id == group_id:
                if data.get("sender_id") != state.my_id:
                    state.messages.append(data)
                    render_messages()
            elif data.get("sender_id") != state.my_id:
                group_name = get_group_name(group_id)
                preview = (data.get("content") or "").strip()
                show_toast(
                    "groups",
                    group_name,
                    f"{sender_name}: {preview[:50]}"
                    + ("…" if len(preview) > 50 else ""),
                )

        elif name == "message_read":
            reader_id = data.get("reader_id")
            if state.active_kind == "user" and state.active_id == reader_id:
                updated = False
                for m in state.messages:
                    if m.get("sender_id") == state.my_id and m.get("status") != "read":
                        m["status"] = "read"
                        updated = True
                if updated:
                    render_messages()

        elif name in (
            "group_member_added",
            "group_member_removed",
            "group_member_left",
            "group_deleted",
            "group_chat_deleted",
        ):
            group_id = data.get("group_id")
            am_i_the_target = data.get("user_id") == state.my_id

            if name == "group_member_added" and am_i_the_target:

                await refresh_groups()
                group_name = data.get("group_name") or get_group_name(group_id)
            else:
                group_name = data.get("group_name") or get_group_name(group_id)
                await refresh_groups()

            if name == "group_member_added":
                if am_i_the_target:
                    adder = get_username(data.get("added_by"))
                    show_toast(
                        "person_add", group_name,
                        f"{adder} added you to the group", "success",
                    )
                else:
                    who = (
                        data.get("username")
                        or get_username(data.get("user_id"))
                        or "Someone"
                    )
                    show_toast(
                        "person_add", group_name,
                        f"{who} was added to the group", "success",
                    )
            elif name == "group_member_removed":
                if am_i_the_target:
                    remover = get_username(data.get("removed_by"))
                    show_toast(
                        "person_remove", group_name,
                        (
                            f"You were removed from the group by {remover}"
                            if remover != "Unknown"
                            else "You were removed from the group"
                        ),
                        "warning",
                    )
                else:
                    who = (
                        data.get("username")
                        or get_username(data.get("user_id"))
                        or "Someone"
                    )
                    show_toast(
                        "person_remove", group_name,
                        f"{who} was removed from the group", "warning",
                    )
            elif name == "group_member_left":
                who = (
                    data.get("username")
                    or get_username(data.get("user_id"))
                    or "Someone"
                )
                show_toast(
                    "logout", group_name,
                    f"{who} left the group", "warning",
                )

            if name == "group_deleted":
                if state.active_id == group_id:
                    state.active_kind = None
                    state.active_id = None
                    state.active_name = None
                    state.messages = []
                    render_chat_header()
                    render_messages()
                show_toast(
                    "delete_forever", "Group deleted",
                    f"{group_name} has been deleted", "danger",
                )
            elif name == "group_chat_deleted":
                if state.active_id == group_id:
                    state.messages = []
                    render_messages()
                show_toast(
                    "cleaning_services", "History cleared",
                    f"Chat history of {group_name} was cleared", "warning",
                )

        elif name == "private_chat_deleted":
            other_id = data.get("deleted_by")
            if state.active_kind == "user" and state.active_id == other_id:
                state.messages = []
                render_messages()
                show_toast(
                    "delete_outline",
                    "Chat cleared",
                    f"{get_username(other_id)} cleared your chat history",
                    "warning",
                )

        elif name == "error":
            ui.notify(data.get("message", "Something went wrong"), type="negative")

    async def event_dispatch_loop():
        while True:
            event = await event_queue.get()
            try:
                if event.get("event") == "__status":
                    state.connected = bool(
                        (event.get("data") or {}).get("connected")
                    )
                    update_connection_dot()
                elif event.get("event") == "__auth_failed":
                    ui.run_javascript("localStorage.removeItem('access_token')")
                    ui.navigate.to("/login")
                    return
                else:
                    await handle_ws_event(event)
            except asyncio.CancelledError:
                raise
            except Exception:

                continue

    async def ws_listen_loop():
        backoff = 1.0
        while True:
            used_token = hub["token"]
            try:
                url = f"{WS_BASE_URL}?token={used_token}"
                async with websockets.connect(url) as ws:
                    hub["ws"] = ws
                    hub["connected"] = True
                    backoff = 1.0
                    broadcast_event({"event": "__status", "data": {"connected": True}})

                    async for raw in ws:
                        try:
                            event = json.loads(raw)
                        except (ValueError, TypeError):
                            continue
                        broadcast_event(event)

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                hub["connected"] = False
                broadcast_event({"event": "__status", "data": {"connected": False}})

                status = _ws_reject_status(exc)
                if status in (401, 403):
                    if hub["token"] != used_token:

                        continue
                    broadcast_event({"event": "__auth_failed", "data": {}})
                    if _USER_HUBS.get(state.my_id) is hub:
                        _USER_HUBS.pop(state.my_id, None)
                    return

                await asyncio.sleep(backoff + random.uniform(0, 0.4))
                backoff = min(backoff * 2, 15)

    def ensure_ws_alive():
        if _USER_HUBS.get(state.my_id) is not hub:
            return
        if hub["queues"] and (hub["task"] is None or hub["task"].done()):
            hub["task"] = asyncio.create_task(ws_listen_loop())

    hub["queues"].add(event_queue)
    dispatch_task = asyncio.create_task(event_dispatch_loop())
    if hub["task"] is None or hub["task"].done():
        hub["task"] = asyncio.create_task(ws_listen_loop())


    push_to_me({"event": "__status", "data": {"connected": hub["connected"]}})
    ui.timer(5.0, ensure_ws_alive)

    async def cleanup():
        hub["queues"].discard(event_queue)
        dispatch_task.cancel()
        if not hub["queues"]:
            await asyncio.sleep(2.0)
            if not hub["queues"] and _USER_HUBS.get(state.my_id) is hub:
                _USER_HUBS.pop(state.my_id, None)
                if hub["task"]:
                    hub["task"].cancel()
                if hub["ws"]:
                    try:
                        await hub["ws"].close()
                    except Exception:
                        pass

    ui.context.client.on_disconnect(cleanup)

    await load_users()
    await load_online_users()
    await refresh_groups()
    render_chat_header()
    render_messages()


def _decode_token_payload(token: str) -> tuple[str | None, str]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None, ""
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
        username = payload.get("username", "")
        return (str(user_id) if user_id else None), username
    except Exception:
        return None, ""



def create_group_dialog(state: ChatState, on_created):
    with ui.dialog() as dialog, ui.card().classes(
        "bg-panel border border-soft rounded-3xl p-6 w-96 shadow-2xl"
    ):
        with ui.row().classes("items-center gap-3 mb-5"):
            with ui.element("div").classes(
                "w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-500 "
                "flex items-center justify-center shadow-lg shadow-purple-500/25"
            ):
                ui.icon("group_add").classes("text-white")
            ui.label("Create a new group").classes("text-1 font-semibold text-lg")

        name_input = (
            ui.input(label="Group name", placeholder="e.g. Weekend Squad")
            .props("outlined dense")
            .classes("w-full bg-input rounded-xl")
        )
        error_label = ui.label("").classes("text-red-400 text-xs min-h-4 mt-1")

        async def submit():
            name = (name_input.value or "").strip()
            if not name:
                error_label.text = "Group name is required."
                return
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{API_BASE_URL}/groups/create_group",
                    json={"name": name},
                    headers=auth_headers(state.token),
                )
            if resp.status_code == 201:
                dialog.close()
                ui.notify("Group created 🎉", type="positive")
                await on_created()
            else:
                try:
                    error_label.text = resp.json().get("detail", "Failed to create group.")
                except Exception:
                    error_label.text = "Failed to create group."

        with ui.row().classes("w-full justify-end gap-2 mt-5"):
            ui.button("Cancel", on_click=dialog.close).props("flat no-caps").classes(
                "text-2"
            )
            ui.button("Create", on_click=submit).props("no-caps").classes(
                PRIMARY_BUTTON_CLASSES
            )

    dialog.open()