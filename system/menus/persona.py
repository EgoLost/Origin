import json
import re
import tkinter as tk
from pathlib import Path

from uib_inf100_graphics.helpers import load_image, image_in_box
from menus.home import draw_header, is_inside_button

# -- Images
image_folder = Path(__file__).resolve().parents[2] / "data" / "img"
fon_persona = load_image(str(image_folder / "fon_persona.jpg"))


# -- Settings
CHARACTERS_FOLDER = Path(__file__).resolve().parents[2] / 'content' / 'characters'
PERSONA_COLUMNS = 3
PERSONA_MAX_ROWS = 6

# -- Systems available during character creation
CHARACTER_SYSTEMS = [
    ("dnd", "DnD"),
    ("fate", "Fate"),
    ("world_creators", "Создатели миров")
]


# -- Read characters
def read_character(path):
    character = {
        'file_name': path.name,
        'name': path.stem,
        'subtitle': 'New character',
        'hp_text': '-- / --',
        'system': ''
    }

    try:
        text = path.read_text(encoding='utf-8')
        data = json.loads(text)

        if isinstance(data, dict):
            character['name'] = str(data.get('name', path.stem))
            character['subtitle'] = str(data.get('subtitle', 'New character'))
            character['hp_text'] = str(data.get('hp_text', '-- / --'))
            character['system'] = str(data.get('system', ''))
    except (OSError, ValueError):
        pass

    return character


def character_sort_key(path):
    parts = re.split(r'(\d+)', path.stem.lower())
    key = []

    for part in parts:
        if part.isdigit():
            key.append((1, int(part)))
        else:
            key.append((0, part))

    return key


def load_characters():
    CHARACTERS_FOLDER.mkdir(parents=True, exist_ok=True)
    files = []

    for path in CHARACTERS_FOLDER.iterdir():
        if path.is_file() and path.suffix.lower() == '.json':
            files.append(path)

    files.sort(key=character_sort_key)
    characters = []

    for path in files:
        characters.append(read_character(path))

    return characters


def create_new_character(system):
    CHARACTERS_FOLDER.mkdir(parents=True, exist_ok=True)
    number = 1

    while True:
        name = f'Character {number}'
        path = CHARACTERS_FOLDER / f'{name}.json'

        if not path.exists():
            character = {
                'name': name,
                'subtitle': 'Empty sheet',
                'hp_text': '0 / 0',
                'system': system
            }

            text = json.dumps(character, ensure_ascii=False, indent=4)
            path.write_text(text, encoding='utf-8')
            return path

        number += 1


# -- Model
def persona_started(app):
    app.persona_page = 0
    app.persona_characters = load_characters()
    app.selected_character = None
    app.hovered_character = None
    app.persona_system_window = False
    app.persona_hovered_system = None
    app.persona_search_text = ''
    app.persona_search_query = ''
    app.persona_search_active = False
    app.persona_search_entry = None


def get_persona_layout(app):
    scale = min(app.width / 1920, app.height / 1080)
    panel_x1 = app.width * 0.025
    panel_y1 = 85 * scale
    panel_x2 = app.width * 0.975
    panel_y2 = app.height * 0.97

    padding = 24 * scale
    gap_x = 28 * scale
    gap_y = 18 * scale
    card_height = 105 * scale
    search_height = 45 * scale
    search_y1 = panel_y1 + padding
    cards_y1 = search_y1 + search_height + 24 * scale

    content_width = panel_x2 - panel_x1 - 2 * padding
    card_width = (content_width - (PERSONA_COLUMNS - 1) * gap_x) / PERSONA_COLUMNS

    available_height = panel_y2 - cards_y1 - padding - 78 * scale
    row_height = card_height + gap_y
    rows = int((available_height + gap_y) / row_height)
    rows = max(1, min(PERSONA_MAX_ROWS, rows))

    return {
        'panel_x1': panel_x1,
        'panel_y1': panel_y1,
        'panel_x2': panel_x2,
        'panel_y2': panel_y2,
        'x1': panel_x1 + padding,
        'y1': cards_y1,
        'search_x1': panel_x1 + padding,
        'search_y1': search_y1,
        'search_x2': panel_x2 - padding,
        'search_y2': search_y1 + search_height,
        'card_width': card_width,
        'card_height': card_height,
        'gap_x': gap_x,
        'gap_y': gap_y,
        'rows': rows,
        'page_size': rows * PERSONA_COLUMNS,
        'scale': scale
    }


def get_system_name(system):
    if system == 'dnd':
        return 'Dungeons & Dragons'
    if system == 'fate':
        return 'Fate'
    if system == 'world_creators':
        return 'Создатели миров'
    return 'Unknown system'


def get_persona_items(app):
    # -- Filter ALL characters before splitting them into pages
    query = app.persona_search_query.strip().casefold()
    items = []

    for character in app.persona_characters:
        name = character['name'].casefold()
        system = character.get('system', '').casefold()
        system_name = get_system_name(system).casefold()

        # -- Also accept common names for DnD and World Creators
        if system == 'dnd':
            system_name += ' dnd d&d днд'
        elif system == 'fate':
            system_name += ' fate фейт'
        elif system == 'world_creators':
            system_name += ' world creators создатели миров'

        if query == '' or query in name or query in system or query in system_name:
            items.append(character)

    # -- New-character card is not part of search results
    if query == '':
        items.append({
            'name': '+',
            'subtitle': 'Create new character',
            'hp_text': '',
            'action': 'new_character'
        })

    return items


# -- Tkinter search input
# -- The native Entry handles cursor, selection and Ctrl shortcuts.
def create_persona_search(app):
    if app.persona_search_entry is not None:
        return

    entry = tk.Entry(
        app._root,
        font=('Arial', 16),
        bg='#10141f',
        fg='#e8d5c3',
        insertbackground='#e8d5c3',
        selectbackground='#655a6d',
        selectforeground='#ffffff',
        relief='flat',
        borderwidth=0,
        highlightthickness=0
    )
    entry.insert(0, app.persona_search_text)
    entry.bind('<Return>', lambda event: submit_persona_search(app))
    entry.bind('<KP_Enter>', lambda event: submit_persona_search(app))
    entry.bind('<Control-KeyPress>', select_all_text)
    app.persona_search_entry = entry

# -- Select all text
def select_all_text(event):
    if event.keycode == 65:
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return 'break'

def show_persona_search(app):
    create_persona_search(app)
    search = get_persona_search_buttons(app)
    scale = get_persona_layout(app)['scale']

    x = int(search['x1'] + 16 * scale)
    y = int(search['y1'] + 5 * scale)
    width = int(search['search_x1'] - search['x1'] - 26 * scale)
    height = int(search['y2'] - search['y1'] - 10 * scale)

    app.persona_search_entry.place(
        x=x, y=y, width=max(30, width), height=max(20, height)
    )
    app.persona_search_entry.lift()


def hide_persona_search(app):
    if app.persona_search_entry is not None:
        app.persona_search_text = app.persona_search_entry.get()
        app.persona_search_entry.place_forget()


def submit_persona_search(app):
    if app.persona_search_entry is not None:
        app.persona_search_text = app.persona_search_entry.get()
    app.persona_search_query = app.persona_search_text.strip()
    app.persona_page = 0
    app.hovered_character = None
    return 'break'


def clear_persona_search(app):
    if app.persona_search_entry is not None:
        app.persona_search_entry.delete(0, tk.END)
    app.persona_search_text = ''
    app.persona_search_query = ''
    app.persona_page = 0
    if app.persona_search_entry is not None:
        app.persona_search_entry.focus_set()


def get_persona_search_buttons(app):
    layout = get_persona_layout(app)
    scale = layout['scale']
    return {
        'x1': layout['search_x1'],
        'y1': layout['search_y1'],
        'x2': layout['search_x2'],
        'y2': layout['search_y2'],
        'clear_x1': layout['search_x2'] - 55 * scale,
        'search_x1': layout['search_x2'] - 140 * scale
    }


def draw_persona_search(app, canvas):
    search = get_persona_search_buttons(app)
    scale = get_persona_layout(app)['scale']

    canvas.create_rectangle(
        search['x1'], search['y1'], search['x2'], search['y2'],
        fill='#10141f', outline='#5d5660', width=2
    )
    canvas.create_rectangle(
        search['search_x1'], search['y1'],
        search['clear_x1'], search['y2'],
        fill='#302b37', outline='#5d5660'
    )
    canvas.create_text(
        (search['search_x1'] + search['clear_x1']) / 2,
        (search['y1'] + search['y2']) / 2,
        text='🔍', fill='#e8d5c3',
        font=('Arial', max(18, int(22 * scale)), 'bold')
    )
    canvas.create_text(
        (search['clear_x1'] + search['x2']) / 2,
        (search['y1'] + search['y2']) / 2,
        text='X', fill='#e8d5c3',
        font=('Arial', max(11, int(17 * scale)))
    )
    if app.persona_search_query != '':
        count = len(get_persona_items(app))
        canvas.create_text(
            search['x1'], search['y2'] + 13 * scale,
            text=f'Found: {count}', anchor='w',
            fill='#b9a99a', font=('Arial', max(9, int(11 * scale)))
        )


def persona_search_mouse_pressed(app, event):
    search = get_persona_search_buttons(app)

    if not is_inside_button(event.x, event.y, search):
        return False

    if event.x >= search['clear_x1']:
        clear_persona_search(app)

    elif event.x >= search['search_x1']:
        submit_persona_search(app)

    else:
        if app.persona_search_entry is None:
            show_persona_search(app)

        app.persona_search_entry.focus_set()

    return True


def get_persona_page_count(app):
    items = get_persona_items(app)
    page_size = get_persona_layout(app)['page_size']
    number_of_pages = (len(items) + page_size - 1) // page_size
    return max(1, number_of_pages)


def get_persona_cards(app):
    layout = get_persona_layout(app)
    items = get_persona_items(app)
    start = app.persona_page * layout['page_size']
    end = start + layout['page_size']
    visible_items = items[start:end]
    cards = []

    for i in range(len(visible_items)):
        character = visible_items[i]
        column = i % PERSONA_COLUMNS
        row = i // PERSONA_COLUMNS
        x1 = layout['x1'] + column * (layout['card_width'] + layout['gap_x'])
        y1 = layout['y1'] + row * (layout['card_height'] + layout['gap_y'])

        if 'action' in character:
            action = character['action']
        else:
            action = 'character::' + character['file_name']

        cards.append({
            'x1': x1,
            'y1': y1,
            'x2': x1 + layout['card_width'],
            'y2': y1 + layout['card_height'],
            'action': action,
            'data': character
        })

    return cards


def get_persona_page_buttons(app):
    layout = get_persona_layout(app)
    scale = layout['scale']
    page_count = get_persona_page_count(app)

    first_page = max(0, app.persona_page - 2)
    last_page = min(page_count, first_page + 5)
    first_page = max(0, last_page - 5)

    labels = [('previous', '<')]
    for page in range(first_page, last_page):
        labels.append((f'page::{page}', str(page + 1)))
    labels.append(('next', '>'))

    width = 45 * scale
    height = 35 * scale
    gap = 8 * scale
    total_width = len(labels) * width + (len(labels) - 1) * gap
    center_x = (layout['panel_x1'] + layout['panel_x2']) / 2
    center_y = layout['panel_y2'] - 50 * scale
    x1 = center_x - total_width / 2
    buttons = []

    for action, label in labels:
        buttons.append({
            'action': action,
            'text': label,
            'x1': x1,
            'y1': center_y - height / 2,
            'x2': x1 + width,
            'y2': center_y + height / 2
        })
        x1 += width + gap

    return buttons


# -- View
def draw_character_card(app, canvas, card):
    scale = get_persona_layout(app)['scale']
    x1 = card['x1']
    y1 = card['y1']
    x2 = card['x2']
    y2 = card['y2']
    action = card['action']
    character = card['data']

    background = '#10141f'
    border = '#05070d'

    if app.hovered_character == action:
        background = '#171d2c'
    if app.selected_character == action:
        background = '#1f2940'
        border = '#d8c0a6'

    canvas.create_rectangle(x1, y1, x2, y2, fill=background, outline=border, width=2)

    if action == 'new_character':
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10 * scale,
                           text='+', font=('Georgia', max(22, int(28 * scale))),
                           fill='#e5d1b7')
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 + 18 * scale,
                           text='Create new', font=('Arial', max(10, int(12 * scale))),
                           fill='#9cb0d3')
        return

    avatar_size = 65 * scale
    avatar_x1 = x1 + 16 * scale
    avatar_y1 = y1 + (y2 - y1 - avatar_size) / 2
    avatar_x2 = avatar_x1 + avatar_size
    avatar_y2 = avatar_y1 + avatar_size

    canvas.create_rectangle(avatar_x1, avatar_y1, avatar_x2, avatar_y2,
                            fill='#3a1620', outline='#a74646')
    canvas.create_text((avatar_x1 + avatar_x2) / 2, (avatar_y1 + avatar_y2) / 2,
                       text=character['name'][:1].upper(),
                       font=('Georgia', max(14, int(18 * scale)), 'bold'),
                       fill='#ffffff')

    text_x = avatar_x2 + 20 * scale
    canvas.create_text(text_x, y1 + 28 * scale, anchor='w',
                       text=character['name'],
                       font=('Arial', max(12, int(19 * scale)), 'bold'),
                       fill='#d7e4ff')
    canvas.create_text(text_x, y1 + 55 * scale, anchor='w',
                       text=character['subtitle'],
                       font=('Arial', max(11, int(14 * scale))),
                       fill='#8fa2c9')
    canvas.create_text(text_x, y1 + 80 * scale, anchor='w',
                       text=character['hp_text'],
                       font=('Arial', max(10, int(13 * scale))),
                       fill='#78a6ed')
    canvas.create_text(
        x2 - 16 * scale, y2 - 16 * scale,
        text=get_system_name(character.get('system', '')), anchor='e',
        font=('Arial', max(10, int(12 * scale))), fill='#b9a99a'
    )
    canvas.create_text(x2 - 16 * scale, y1 + 18 * scale,
                       text='⋯', font=('Arial', max(12, int(15 * scale)), 'bold'),
                       fill='#ffffff')


def draw_persona_page_buttons(app, canvas):
    layout = get_persona_layout(app)
    page_count = get_persona_page_count(app)

    for button in get_persona_page_buttons(app):
        action = button['action']
        selected = action == f'page::{app.persona_page}'
        disabled = False

        if action == 'previous' and app.persona_page == 0:
            disabled = True
        if action == 'next' and app.persona_page == page_count - 1:
            disabled = True

        color = '#10141f'
        if selected:
            color = '#484345'
        elif action == app.hovered_character and not disabled:
            color = '#35313c'

        text_color = '#d6c0a8'
        if disabled:
            text_color = '#686873'

        canvas.create_rectangle(button['x1'], button['y1'], button['x2'], button['y2'],
                                fill=color, outline='#08090c')
        canvas.create_text((button['x1'] + button['x2']) / 2,
                           (button['y1'] + button['y2']) / 2,
                           text=button['text'], fill=text_color,
                           font=('Georgia', max(10, int(15 * layout['scale'])), 'bold'))

    canvas.create_text(layout['panel_x2'] - 24 * layout['scale'],
                       layout['panel_y2'] - 40 * layout['scale'],
                       text=f'{app.persona_page + 1} / {page_count}', anchor='e',
                       fill='#cbb59f', font=('Arial', max(10, int(12 * layout['scale']))))


def draw_persona(app, canvas):
    image_in_box(
        canvas,
        0, 0,
        app.width, app.height,
        fon_persona,
        fit_mode="stretch"
    )
    
    layout = get_persona_layout(app)

    canvas.create_rectangle(layout['panel_x1'], layout['panel_y1'],
                            layout['panel_x2'], layout['panel_y2'],
                            fill='#25272f', stipple='gray75', outline='')

    draw_persona_search(app, canvas)

    cards = get_persona_cards(app)
    if len(cards) == 0:
        canvas.create_text(
            app.width / 2, layout['y1'] + 70 * layout['scale'],
            text='No characters found', fill='#d7e4ff',
            font=('Georgia', max(12, int(22 * layout['scale'])))
        )
    for card in cards:
        draw_character_card(app, canvas, card)

    draw_persona_page_buttons(app, canvas)
    draw_header(app, canvas)

    if app.persona_system_window:
        draw_system_window(app, canvas)


# -- Window for choosing a character system
def get_system_window(app):
    scale = min(app.width / 1920, app.height / 1080)
    width = 560 * scale
    height = 435 * scale
    x1 = (app.width - width) / 2
    y1 = (app.height - height) / 2

    return {
        'x1': x1,
        'y1': y1,
        'x2': x1 + width,
        'y2': y1 + height,
        'scale': scale
    }


def get_system_buttons(app):
    window = get_system_window(app)
    scale = window['scale']
    buttons = []

    for i in range(len(CHARACTER_SYSTEMS)):
        system, title = CHARACTER_SYSTEMS[i]
        x1 = window['x1'] + 45 * scale
        y1 = window['y1'] + (112 + i * 88) * scale
        buttons.append({
            'action': system,
            'text': title,
            'x1': x1,
            'y1': y1,
            'x2': window['x2'] - 45 * scale,
            'y2': y1 + 65 * scale
        })

    buttons.append({
        'action': 'cancel',
        'text': 'Cancel',
        'x1': window['x1'] + 185 * scale,
        'y1': window['y2'] - 61 * scale,
        'x2': window['x2'] - 185 * scale,
        'y2': window['y2'] - 25 * scale
    })
    return buttons


def draw_system_window(app, canvas):
    window = get_system_window(app)
    scale = window['scale']

    # -- Opaque background: clicks behind it are blocked by the controller
    canvas.create_rectangle(
        window['x1'], window['y1'], window['x2'], window['y2'],
        fill='#171820', outline='#cbb59f', width=3
    )
    canvas.create_text(
        app.width / 2, window['y1'] + 42 * scale,
        text='Choose a system',
        fill='#e8d5c3',
        font=('Georgia', max(16, int(30 * scale)), 'bold')
    )
    canvas.create_text(
        app.width / 2, window['y1'] + 78 * scale,
        text='Select a system for your new character',
        fill='#9fa6b8',
        font=('Arial', max(11, int(16 * scale)))
    )

    for button in get_system_buttons(app):
        color = '#10141f'
        if app.persona_hovered_system == button['action']:
            color = '#343341'

        canvas.create_rectangle(
            button['x1'], button['y1'], button['x2'], button['y2'],
            fill=color, outline='#5d5660', width=2
        )
        canvas.create_text(
            (button['x1'] + button['x2']) / 2,
            (button['y1'] + button['y2']) / 2,
            text=button['text'],
            fill='#e8d5c3',
            font=('Georgia', max(12, int(23 * scale)), 'bold')
        )


def finish_character_creation(app, system):
    path = create_new_character(system)
    app.persona_characters = load_characters()
    clear_persona_search(app)
    app.selected_character = 'character::' + path.name
    app.persona_system_window = False
    app.persona_hovered_system = None
    show_persona_search(app)

    for i in range(len(app.persona_characters)):
        character = app.persona_characters[i]
        if character['file_name'] == path.name:
            page_size = get_persona_layout(app)['page_size']
            app.persona_page = i // page_size
            break


def close_system_window(app):
    app.persona_system_window = False
    app.persona_hovered_system = None
    if app.state == 'persona':
        show_persona_search(app)


# -- Controller
def persona_mouse_pressed(app, event):
    if app.persona_system_window:
        for button in get_system_buttons(app):
            if is_inside_button(event.x, event.y, button):
                action = button['action']
                if action == 'cancel':
                    close_system_window(app)
                else:
                    finish_character_creation(app, action)
                return action
        return None

    if persona_search_mouse_pressed(app, event):
        return 'search'

    for button in get_persona_page_buttons(app):
        if is_inside_button(event.x, event.y, button):
            action = button['action']
            last_page = get_persona_page_count(app) - 1

            if action == 'previous':
                app.persona_page = max(0, app.persona_page - 1)
            elif action == 'next':
                app.persona_page = min(last_page, app.persona_page + 1)
            elif action.startswith('page::'):
                app.persona_page = int(action.split('::')[1])

            app.hovered_character = None
            return action

    for card in get_persona_cards(app):
        if is_inside_button(event.x, event.y, card):
            action = card['action']

            if action == 'new_character':
                app.persona_system_window = True
                hide_persona_search(app)
                app.persona_hovered_system = None
            else:
                app.selected_character = action

            return action

    return None


def persona_mouse_moved(app, event):
    if app.persona_system_window:
        for button in get_system_buttons(app):
            if is_inside_button(event.x, event.y, button):
                app.persona_hovered_system = button['action']
                return button['action']
        app.persona_hovered_system = None
        return None

    for button in get_persona_page_buttons(app):
        if is_inside_button(event.x, event.y, button):
            app.hovered_character = button['action']
            return button['action']

    for card in get_persona_cards(app):
        if is_inside_button(event.x, event.y, card):
            app.hovered_character = card['action']
            return card['action']

    app.hovered_character = None
    return None
