"""
Entry point. Run this file (not auth_pages.py or messenger_page.py
directly) — it imports both page modules so their @ui.page routes get
registered, then starts the NiceGUI server exactly once.
"""

from nicegui import ui

import auth_pages  # noqa: F401  (registers /signup and /login)
import messenger_page  # noqa: F401  (registers /messenger)


@ui.page("/")
def index():
    ui.navigate.to("/signup")


ui.run(
    host="127.0.0.1",
    port=8080,
    title="Messenger",
    show=True,
)