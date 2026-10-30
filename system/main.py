
from uib_inf100_graphics.event_app import run_app

from menus.home import (
    draw_home,
    draw_header,
    menu_mouse_pressed,
    menu_mouse_moved
)


# -- App starter
def app_started(app):
    app.state = "home"
    app.hovered_button = None

    app._root.state("zoomed")


# -- Shortcuts
def go_to_home(app):
    app.state = "home"


def go_to_persona(app):
    app.state = "persona"


def go_to_lobby(app):
    app.state = "lobby"


def go_to_workshop(app):
    app.state = "workshop"


def go_to_settings(app):
    app.state = "settings"


# -- Mouse click
def mouse_pressed(app, event):
    action = menu_mouse_pressed(app, event)

    if action == "home":
        go_to_home(app)

    elif action == "persona":
        go_to_persona(app)

    elif action == "lobby":
        go_to_lobby(app)

    elif action == "workshop":
        go_to_workshop(app)

    elif action == "settings":
        go_to_settings(app)


# -- Mouse movement
def mouse_moved(app, event):
    menu_mouse_moved(app, event)


# -- Keyboard
def key_pressed(app, event):
    if event.key == "Escape":
        go_to_home(app)


# -- Drawing
def redraw_all(app, canvas):
    if app.state == "home":
        draw_home(app, canvas)

    else:
        canvas.create_rectangle(
            0, 0,
            app.width, app.height,
            fill="#29292b",
            outline=""
        )

        canvas.create_text(
            app.width / 2,
            app.height / 2,
            text=app.state.upper(),
            font=("Georgia", 40, "bold"),
            fill="#cbb59f"
        )

        draw_header(app, canvas)


# -- Start application
if __name__ == "__main__":
    run_app(
        width=1920,
        height=1080,
        title="Origin"
    )
