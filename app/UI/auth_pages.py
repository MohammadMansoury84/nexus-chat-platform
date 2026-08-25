import httpx

from nicegui import ui


API_BASE_URL = "http://127.0.0.1:8000/api/v1"


PRIMARY_BUTTON_CLASSES = (
    "w-full h-11 mt-3 rounded-xl "
    "bg-gradient-to-r from-purple-600 to-blue-500 "
    "hover:from-purple-500 hover:to-blue-400 "
    "active:scale-[0.98] "
    "!text-white text-sm font-semibold "
    "shadow-lg shadow-purple-500/30 "
    "transition-all duration-200 ease-out "
    "hover:shadow-xl hover:shadow-purple-500/40"
)

INPUT_CLASSES = "w-full"

CARD_WIDTH = "880px"
CARD_HEIGHT = "560px"

FEATURES = [
    ("lock", "Private by design"),
    ("bolt", "Real-time messaging"),
    ("groups", "Built for conversations"),
]


def set_page_background():
    ui.query("body").style(
        """
        margin: 0;
        background: #F7F7FA;
        font-family: Inter, sans-serif;
        overflow: hidden;
        """
    )
    ui.colors(primary="#8B5CF6", secondary="#60A5FA", accent="#A78BFA")


def brand_logo():
    with ui.row().classes("items-center gap-2.5"):
        with ui.element("div").classes(
            "w-9 h-9 rounded-xl "
            "bg-gradient-to-br from-purple-500 to-sky-400 "
            "flex items-center justify-center "
            "shadow-lg shadow-purple-500/30 "
            "ring-1 ring-white/40"
        ):
            ui.label("F3").classes("text-sm font-bold text-white")

        ui.label("Messenger").classes("text-base font-semibold text-gray-900")


def feature_list():
    with ui.column().classes("gap-2.5 mt-2"):
        for icon, text in FEATURES:
            with ui.row().classes("items-center gap-2.5"):
                ui.icon(icon).classes("text-purple-600 text-base")
                ui.label(text).classes("text-xs text-gray-600")


def glow_background(top_left: bool = True):
    """Two soft blurred glows in opposite corners, mirrored per page."""
    corner_a = "-top-32 -left-32" if top_left else "-top-32 -right-32"
    corner_b = "-bottom-32 -right-32" if top_left else "-bottom-32 -left-32"

    ui.element("div").classes(
        f"absolute {corner_a} w-96 h-96 rounded-full "
        "bg-purple-300/30 blur-[120px] animate-pulse"
    ).style("animation-duration: 6s;")

    ui.element("div").classes(
        f"absolute {corner_b} w-96 h-96 rounded-full "
        "bg-sky-300/25 blur-[120px] animate-pulse"
    ).style("animation-duration: 8s;")


def hero_panel(headline: str, subtext: str):
    with ui.column().classes(
        "w-[38%] h-full p-8 "
        "bg-gradient-to-br from-white via-[#F7F7FB] to-[#EEF2F9] "
        "text-gray-900 justify-between box-border border-r border-gray-100"
    ):
        with ui.column().classes("gap-6"):
            brand_logo()

            with ui.column().classes("gap-2.5 mt-4"):
                ui.label(headline).classes(
                    "text-3xl font-semibold leading-tight tracking-tight "
                    "text-gray-900"
                )
                ui.label(subtext).classes(
                    "text-sm text-gray-500 leading-6 max-w-xs"
                )

            feature_list()

        ui.label("Simple. Fast. Connected.").classes("text-xs text-gray-400")


@ui.page("/signup")
def signup_page():
    set_page_background()

    with ui.element("div").classes(
        "h-screen w-full flex items-center justify-center "
        "bg-[#F7F7FA] p-4 relative overflow-hidden"
    ):
        glow_background(top_left=True)

        with ui.card().classes(
            "relative z-10 "
            "bg-white border border-gray-200 "
            "rounded-[24px] shadow-2xl p-0 overflow-hidden"
        ).style(
            f"width: {CARD_WIDTH}; height: {CARD_HEIGHT}; "
            "max-width: 95vw; max-height: 92vh;"
        ):
            with ui.row().classes("w-full h-full gap-0 flex-nowrap"):

                hero_panel(
                    "Stay connected.",
                    "Private conversations. Real-time connection.",
                )

                with ui.column().classes(
                    "w-[62%] h-full bg-white "
                    "p-10 justify-center box-border"
                ):
                    with ui.column().classes("w-full max-w-sm mx-auto gap-0"):

                        ui.label("Create account").classes(
                            "text-2xl font-semibold text-gray-900 tracking-tight"
                        )
                        ui.label("Start your conversation.").classes(
                            "text-gray-500 text-sm mt-1 mb-5"
                        )

                        username = ui.input(label="Username").props(
                            "outlined dense"
                        ).classes(INPUT_CLASSES + " mb-3")

                        email = ui.input(label="Email").props(
                            "outlined dense type=email"
                        ).classes(INPUT_CLASSES + " mb-3")

                        password = ui.input(
                            label="Password",
                            password=True,
                            password_toggle_button=True,
                        ).props("outlined dense").classes(INPUT_CLASSES + " mb-3")

                        confirm_password = ui.input(
                            label="Confirm password",
                            password=True,
                            password_toggle_button=True,
                        ).props("outlined dense").classes(INPUT_CLASSES)

                        error_label = ui.label("").classes(
                            "text-red-500 text-xs mt-1 min-h-4"
                        )

                        async def signup():
                            error_label.text = ""

                            if not username.value:
                                error_label.text = "Username is required."
                                return
                            if not email.value:
                                error_label.text = "Email is required."
                                return
                            if not password.value:
                                error_label.text = "Password is required."
                                return
                            if password.value != confirm_password.value:
                                error_label.text = "Passwords do not match."
                                return

                            payload = {
                                "username": username.value,
                                "email": email.value,
                                "password": password.value,
                            }

                            try:
                                async with httpx.AsyncClient() as client:
                                    response = await client.post(
                                        f"{API_BASE_URL}/auth/signup",
                                        json=payload,
                                    )

                                if response.status_code in (200, 201):
                                    ui.notify(
                                        "Account created successfully",
                                        type="positive",
                                    )
                                    ui.navigate.to("/login")
                                else:
                                    try:
                                        error = response.json()
                                        error_label.text = error.get(
                                            "detail", "Signup failed."
                                        )
                                    except Exception:
                                        error_label.text = "Signup failed."

                            except httpx.RequestError:
                                error_label.text = "Unable to connect to server."

                        ui.button("Create account", on_click=signup).props(
                            "unelevated"
                        ).classes(PRIMARY_BUTTON_CLASSES)

                        with ui.row().classes(
                            "w-full justify-center items-center gap-1 mt-4"
                        ):
                            ui.label("Already have an account?").classes(
                                "text-gray-500 text-sm"
                            )
                            ui.link("Sign in", "/login").classes(
                                "text-purple-600 font-semibold no-underline "
                                "text-sm hover:text-purple-500 transition-colors"
                            )


@ui.page("/login")
def login_page():
    set_page_background()

    with ui.element("div").classes(
        "h-screen w-full flex items-center justify-center "
        "bg-[#F7F7FA] p-4 relative overflow-hidden"
    ):
        glow_background(top_left=False)

        with ui.card().classes(
            "relative z-10 "
            "bg-white border border-gray-200 "
            "rounded-[24px] shadow-2xl p-0 overflow-hidden"
        ).style(
            f"width: {CARD_WIDTH}; height: {CARD_HEIGHT}; "
            "max-width: 95vw; max-height: 92vh;"
        ):
            with ui.row().classes("w-full h-full gap-0 flex-nowrap"):

                hero_panel(
                    "Welcome back.",
                    "Your conversations are waiting.",
                )


                with ui.column().classes(
                    "w-[62%] h-full bg-white "
                    "p-10 justify-center box-border"
                ):
                    with ui.column().classes("w-full max-w-sm mx-auto gap-0"):

                        ui.label("Sign in").classes(
                            "text-2xl font-semibold text-gray-900 tracking-tight"
                        )
                        ui.label("Continue to your account.").classes(
                            "text-gray-500 text-sm mt-1 mb-5"
                        )

                        username = ui.input(label="Username").props(
                            "outlined dense"
                        ).classes(INPUT_CLASSES + " mb-3")

                        password = ui.input(
                            label="Password",
                            password=True,
                            password_toggle_button=True,
                        ).props("outlined dense").classes(INPUT_CLASSES)

                        error_label = ui.label("").classes(
                            "text-red-500 text-xs mt-1 min-h-4"
                        )

                        async def login():
                            error_label.text = ""

                            if not username.value:
                                error_label.text = "Username is required."
                                return
                            if not password.value:
                                error_label.text = "Password is required."
                                return

                            payload = {
                                "username": username.value,
                                "password": password.value,
                            }

                            try:
                                async with httpx.AsyncClient() as client:
                                    response = await client.post(
                                        f"{API_BASE_URL}/auth/login",
                                        json=payload,
                                    )

                                if response.status_code == 200:
                                    response_data = response.json()
                                    token_data = response_data["data"]
                                    access_token = token_data["access_token"]

                                    ui.run_javascript(
                                        f"""
                                        localStorage.setItem(
                                            'access_token',
                                            '{access_token}'
                                        );
                                        """
                                    )

                                    ui.notify("Welcome back!", type="positive")
                                    ui.navigate.to("/messenger")
                                else:
                                    try:
                                        error = response.json()
                                        error_label.text = error.get(
                                            "detail",
                                            "Invalid username or password.",
                                        )
                                    except Exception:
                                        error_label.text = "Login failed."

                            except httpx.RequestError:
                                error_label.text = "Unable to connect to server."

                        ui.button("Sign in", on_click=login).props(
                            "unelevated"
                        ).classes(PRIMARY_BUTTON_CLASSES)

                        with ui.row().classes(
                            "w-full justify-center items-center gap-1 mt-4"
                        ):
                            ui.label("Don't have an account?").classes(
                                "text-gray-500 text-sm"
                            )
                            ui.link("Create account", "/signup").classes(
                                "text-purple-600 font-semibold no-underline "
                                "text-sm hover:text-purple-500 transition-colors"
                            )