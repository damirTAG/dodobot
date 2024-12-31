import json

with open('src/misc/ui/ui_text.json', 'r', encoding='utf-8') as file:
    ui_text = json.load(file)

start_text = (
    ui_text["commands"]["start"]["text"]["greeting"] +
    ui_text["commands"]["start"]["text"]["instructions"] +
    ui_text["commands"]["start"]["text"]["inline_mode"] +
    ui_text["commands"]["start"]["text"]["select_country"]
)