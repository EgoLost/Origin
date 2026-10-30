from pathlib import Path
from uib_inf100_graphics.helpers import (
    load_image,
    image_in_box
)

# -- Images
image_folder = Path(__file__).resolve().parents[2] / "data" / "img"

fon = load_image(str(image_folder / "fon_main.jpg"))
home_icon = load_image(str(image_folder / "home.png"))
settings_icon = load_image(str(image_folder / "setting.png"))


# -- Main navigation buttons
def get_menu_buttons(app):
    scale_x = app.width / 1920
    scale_y = app.height / 1080
    scale = min(scale_x, scale_y)

    button_width = app.width * 0.21
    button_height = 42 * scale
    gap = 15 * scale

    center_x = app.width / 2
    total_width = button_width * 3 + gap * 2
    start_x = center_x - total_width / 2

    y1 = 20 * scale
    y2 = y1 + button_height

    names = ["Persona", "Lobby", "Workshop"]

    buttons = []

    for i in range(len(names)):
        x1 = start_x + i * (button_width + gap)

        buttons.append({
            "text": names[i],
            "action": names[i].lower(),
            "x1": x1,
            "y1": y1,
            "x2": x1 + button_width,
            "y2": y2
        })

    icon_size = 52 * scale

    buttons.append({
        "text": "Home",
        "action": "home",
        "x1": app.width * 0.035,
        "y1": y1,
        "x2": app.width * 0.035 + icon_size,
        "y2": y1 + icon_size
    })

    buttons.append({
        "text": "Settings",
        "action": "settings",
        "x1": app.width * 0.965 - icon_size,
        "y1": y1,
        "x2": app.width * 0.965,
        "y2": y1 + icon_size
    })

    return buttons


# -- Side buttons
def get_side_buttons(app):
    scale = min(app.width / 1920, app.height / 1080)

    x1 = app.width * 0.755
    x2 = app.width * 0.97

    button_height = 55 * scale
    gap = 18 * scale

    start_y = app.height * 0.175

    names = [
        "Support on Boosty",
        "News & Updates",
        "Discussion & Feedback"
    ]

    actions = [
        "boosty",
        "news",
        "feedback"
    ]

    buttons = []

    for i in range(len(names)):
        y1 = start_y + i * (button_height + gap)

        buttons.append({
            "text": names[i],
            "action": actions[i],
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y1 + button_height
        })

    return buttons


# -- Check if mouse is inside a button
def is_inside_button(x, y, button):
    return (
        button["x1"] <= x <= button["x2"]
        and button["y1"] <= y <= button["y2"]
    )


# -- Draw the navigation menu
def draw_header(app, canvas):
    scale = min(app.width / 1920, app.height / 1080)

    x1 = app.width * 0.025
    x2 = app.width * 0.975

    y1 = 12 * scale
    y2 = 75 * scale

    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill="#29292b",
        stipple="gray75",
        outline=""
    )

    buttons = get_menu_buttons(app)

    for button in buttons:
        action = button["action"]

        x1 = button["x1"]
        y1 = button["y1"]
        x2 = button["x2"]
        y2 = button["y2"]

        if action == "home":
            image_in_box(
                canvas, x1, y1, x2, y2,
                home_icon
            )

        elif action == "settings":
            image_in_box(
                canvas, x1, y1, x2, y2,
                settings_icon
            )

        else:
            color = "#08090c"
            text_color = "#cbb59f"

            if app.state == action:
                color = "#484345"

            elif app.hovered_button == action:
                color = "#383337"
                text_color = "#f5e2c9"

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=""
            )

            canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=button["text"],
                font=("Georgia", max(12, int(22 * scale)), "bold"),
                fill=text_color
            )


# -- Draw the news panel
def draw_news_panel(app, canvas):
    scale = min(app.width / 1920, app.height / 1080)

    x1 = app.width * 0.025
    y1 = 85 * scale

    x2 = app.width * 0.745
    y2 = app.height * 0.97

    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill="#252427",
        stipple="gray75",
        outline=""
    )

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    canvas.create_text(
        center_x,
        center_y,
        text="No news",
        font=("Georgia", max(15, int(25 * scale)), "bold"),
        fill="#cbb59f"
    )


# -- Draw the side panel
def draw_side_panel(app, canvas):
    scale = min(app.width / 1920, app.height / 1080)

    buttons = get_side_buttons(app)

    for button in buttons:
        x1 = button["x1"]
        y1 = button["y1"]
        x2 = button["x2"]
        y2 = button["y2"]

        action = button["action"]

        color = "#08090c"
        text_color = "#ffffff"

        if action == "boosty":
            color = "#f15a29"

        if app.hovered_button == action:
            if action == "boosty":
                color = "#ff794d"
            else:
                color = "#302b2a"

        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="#b9a99a",
            width=max(1, int(scale))
        )

        canvas.create_text(
            x1 + 15 * scale,
            (y1 + y2) / 2,
            text=button["text"],
            anchor="w",
            font=("Arial", max(9, int(13 * scale)), "bold"),
            fill=text_color
        )


# -- Draw the home menu
def draw_home(app, canvas):
    image_in_box(
        canvas,
        0, 0,
        app.width, app.height,
        fon,
        fit_mode="stretch"
    )

    draw_news_panel(app, canvas)
    draw_side_panel(app, canvas)
    draw_header(app, canvas)


# -- Mouse click
def menu_mouse_pressed(app, event):
    buttons = get_menu_buttons(app)

    if app.state == "home":
        buttons += get_side_buttons(app)

    for button in buttons:
        if is_inside_button(event.x, event.y, button):
            return button["action"]

    return None


# -- Mouse movement
def menu_mouse_moved(app, event):
    buttons = get_menu_buttons(app)

    if app.state == "home":
        buttons += get_side_buttons(app)

    for button in buttons:
        if is_inside_button(event.x, event.y, button):
            app.hovered_button = button["action"]
            return button["action"]

    app.hovered_button = None

    return None
