from uib_inf100_graphics.event_app import run_app

from menus.home import (
    draw_home,
    draw_header,
    menu_mouse_pressed,
    menu_mouse_moved
)

from menus.persona import (
    persona_started,
    draw_persona,
    persona_mouse_pressed,
    persona_mouse_moved,
    load_characters,
    get_persona_page_count,
    close_system_window,
    show_persona_search,
    hide_persona_search
)


# -- App starter
def app_started(app):
    app.state = "home"
    app.hovered_button = None
    persona_started(app)


# -- Shortcuts
def go_to_home(app):
    hide_persona_search(app)
    app.state = "home"


def go_to_persona(app):
    app.state = "persona"
    app.persona_characters = load_characters()
    app.persona_page = min(app.persona_page, get_persona_page_count(app) - 1)
    show_persona_search(app)


def go_to_lobby(app):
    hide_persona_search(app)
    app.state = "lobby"


def go_to_workshop(app):
    hide_persona_search(app)
    app.state = "workshop"


def go_to_settings(app):
    hide_persona_search(app)
    app.state = "settings"


# -- Mouse click
def mouse_pressed(app, event):
    if app.state == "persona" and app.persona_system_window:
        persona_mouse_pressed(app, event)
        return

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
    elif app.state == "persona":
        persona_mouse_pressed(app, event)


# -- Mouse movement
def mouse_moved(app, event):
    if app.state == "persona" and app.persona_system_window:
        app.hovered_button = None
        persona_mouse_moved(app, event)
        return
    menu_mouse_moved(app, event)
    if app.state == "persona":
        persona_mouse_moved(app, event)


# -- Keyboard
def key_pressed(app, event):
    if event.key == "Escape":
        if app.state == "persona" and app.persona_system_window:
            close_system_window(app)
        else:
            go_to_home(app)
    elif app.state == "persona":
        if app.persona_system_window:
            return
        if event.key == "Right":
            app.persona_page = min(get_persona_page_count(app) - 1, app.persona_page + 1)
        elif event.key == "Left":
            app.persona_page = max(0, app.persona_page - 1)


# -- Drawing
def redraw_all(app, canvas):
    if app.state == "home":
        draw_home(app, canvas)
    elif app.state == "persona":
        draw_persona(app, canvas)
    else:
        canvas.create_rectangle(
            0, 0, app.width, app.height,
            fill="#29292b", outline=""
        )
        canvas.create_text(
            app.width / 2, app.height / 2,
            text=app.state.upper(),
            font=("Georgia", 40, "bold"), fill="#cbb59f"
        )
        draw_header(app, canvas)


# -- Start application
if __name__ == "__main__":
    run_app(width=1920, height=1080, title="Origin")
