import json
from pathlib import Path

# -- Config
def load_config():
    content = Path("data/config.json").read_text(encoding="utf-8")

    return json.loads(content)


def save_config(config):
    content = json.dumps(config,indent=4)

    Path("data/config.json").write_text(content,encoding="utf-8")


def load_default_config():
    content = Path("data/default_config.json").read_text(encoding="utf-8")

    return json.loads(content)


def reset_settings(app):
    app.config = load_default_config()

    save_config(app.config)


# -- Levels
def load_levels():
    content = Path("data/levels.json").read_text(encoding="utf-8")

    return json.loads(content)


# -- Upgrades
def load_upgrades():
    content = Path("data/upgrades.json").read_text(encoding="utf-8")

    return json.loads(content)


def save_upgrades(upgrades):
    content = json.dumps(upgrades,indent=4)

    Path("data/upgrades.json").write_text(content,encoding="utf-8")