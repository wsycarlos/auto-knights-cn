import time, itertools, threading, textwrap

from .. import action, app, templates, terminal, mathtools, wintools

from ..character_table import Character, Character_Table

from typing import Any, Dict, List, Text, Tuple

import numpy as np
from PIL.Image import Image
import PySimpleGUI as sg
import easyocr

ocr_reader = easyocr.Reader(['ch_sim'])

def public_recruit_tips():

    while True:
        while action.count_image(templates.PUBLIC_RECRUIT_INFO) > 0:
            event_screen = app.device.screenshot(max_age=0)
            
            rp = mathtools.ResizeProxy(event_screen.width)

            label_1_bbox = rp.vector4((750, 720, 1039, 813), 2560)
            label_2_bbox = rp.vector4((1084, 720, 1373, 813), 2560)
            label_3_bbox = rp.vector4((1418, 720, 1707, 813), 2560)

            label_4_bbox = rp.vector4((750, 864, 1039, 957), 2560)
            label_5_bbox = rp.vector4((1084, 864, 1373, 957), 2560)

            label_1_img = np.asarray(event_screen.crop(label_1_bbox).convert("L"))
            label_2_img = np.asarray(event_screen.crop(label_2_bbox).convert("L"))
            label_3_img = np.asarray(event_screen.crop(label_3_bbox).convert("L"))

            label_4_img = np.asarray(event_screen.crop(label_4_bbox).convert("L"))
            label_5_img = np.asarray(event_screen.crop(label_5_bbox).convert("L"))
            
            label_1_result = ocr_reader.readtext(label_1_img)
            label_2_result = ocr_reader.readtext(label_2_img)
            label_3_result = ocr_reader.readtext(label_3_img)

            label_4_result = ocr_reader.readtext(label_4_img)
            label_5_result = ocr_reader.readtext(label_5_img)
            
            label_1_text = label_1_result[0][1]
            label_2_text = label_2_result[0][1]
            label_3_text = label_3_result[0][1]
            label_4_text = label_4_result[0][1]
            label_5_text = label_5_result[0][1]

            tags = [label_1_text, label_2_text, label_3_text, label_4_text, label_5_text]

            valid_characters = get_characters_valid_for_tags_contain_only_special_characters(tags)

            if len(valid_characters) > 0:
                target_window: wintools.WinWindow = find_game_window()
                process_window(event_screen, target_window, valid_characters)


def only_has_special_character(character_list:List[Character]) -> bool:
    for character in character_list:
        if character.rarity == 2:
            return False
    return True

def compute_tag_combinations(tags:List[Text]) -> List[Tuple[Text, ...]]:
    result: List[Tuple[Text, ...]] = []
    for i in range(1, len(tags)+1):
        iter = itertools.combinations(tags, i)
        for item in list(iter):
            result.append(item)
    return result

def is_character_valid_for_tag_combinations(character: Character, tag_combination: Tuple[Text, ...])-> bool:
    if character.rarity == 5 and "高级资深干员" not in tag_combination:
        return False
    for tag in tag_combination:
        if tag not in character.extendTagList:
            return False
    return True

def get_characters_valid_for_tag_combinations(tag_combination: Tuple[Text, ...])-> List[Character]:
    result:List[Character] = []
    for character in Character_Table.GetPublicRecruitCharacterList():
        if is_character_valid_for_tag_combinations(character, tag_combination):
            result.append(character)
    return result

def get_characters_valid_for_tags(tags:List[Text])-> List[Tuple[Tuple[Text, ...],List[Character]]]:
    result:List[Tuple[Tuple[Text, ...],List[Character]]] = []
    tag_combinations = compute_tag_combinations(tags)
    for tag_combination in tag_combinations:
        characters = get_characters_valid_for_tag_combinations(tag_combination)
        if len(characters) > 0:
            result.append([tag_combination,characters])
    return result

def get_characters_valid_for_tags_contain_only_special_characters(tags:List[Text])-> List[Tuple[Tuple[Text, ...],List[Character]]]:
    result:List[Tuple[Tuple[Text, ...],List[Character]]] = []
    tag_combinations = compute_tag_combinations(tags)
    for tag_combination in tag_combinations:
        characters = get_characters_valid_for_tag_combinations(tag_combination)
        if len(characters) > 0 and only_has_special_character(characters):
            result.append([tag_combination,characters])
    return result


def stop_for_watching(target_hwnd, window, offset_y):
    while True:
        time.sleep(0.1)
        new_rect = wintools.GetWindowRect(target_hwnd)
        window.move(new_rect.left, new_rect.top + offset_y)
        count_ = action.count_image(templates.PUBLIC_RECRUIT_INFO)
        if count_ <= 0:
            window.write_event_value('-THREAD-', 0)
            return

def find_game_window():
    target_window: wintools.WinWindow = None
    while True:
        windows = wintools.GetAllWindows()
        found = False
        for window in windows:
            if "明日方舟" in window.Title:
                target_window = window
                found = True
        if found:
            sg.set_options(font=("黑体", 20))
            sg.set_options(background_color='red')
            return target_window
        else:
            return None

def display_window(hwnd, layout, size_x: int, size_y: int, border_size_y):

    win_rect = wintools.GetWindowRect(hwnd)

    bg_last = [sg.Column([], size=(size_x, size_y))]
    layout.append(bg_last)
    
    window = sg.Window('', layout, background_color='red', transparent_color='red', keep_on_top=True, size=(size_x, size_y), location=(win_rect.left, win_rect.top + border_size_y), margins=(0, 0), no_titlebar=True, element_padding=(0,0), element_justification='left', finalize=True)
    threading.Thread(target=stop_for_watching, args=(hwnd, window, border_size_y), daemon=True).start()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == '-THREAD-':
            break
    window.close()

def layout_padding(x: int, y: int):
    return [sg.Column([], size=(x, y))]

def layout_text(text: Text, text_color: Text):
    return [sg.Text(text, background_color='white', text_color=text_color)]

def get_text_color_for_characters(characters:List[Character])->Text:
    max_rarity = 0
    for c in characters:
        max_rarity = max(max_rarity, c.rarity)
    if max_rarity == 5:
        return "gold"
    elif max_rarity == 4:
        return "yellow"
    elif max_rarity == 3:
        return "gray"
    elif max_rarity == 2:
        return "blue"
    elif max_rarity == 1:
        return "green"
    elif max_rarity == 0:
        return "black"

def process_window(event_screen: Image, target_window: wintools.WinWindow, valid_characters: List[Tuple[Tuple[Text, ...],List[Character]]]):

    c_rect = wintools.GetClientRect(target_window.hwnd)

    size_x = c_rect.right - c_rect.left
    #size_y = c_rect.bottom - c_rect.top

    event_screen_width = event_screen.width
    event_screen_height = event_screen.height

    event_screen_aspect_ratio = event_screen_height / event_screen_width
    real_size_y = (int)(size_x * event_screen_aspect_ratio)
    
    border_size_y = 50

    size_height_ratio = real_size_y / event_screen_height

    should_create_window = False
    layout = []

    character_length = len(valid_characters)

    if character_length > 0:

        should_create_window = True
        
        _offset_y = (int)(200 * size_height_ratio)
        
        layout.append(layout_padding(size_x, _offset_y))

        for valid_pair in valid_characters:
            tags = ', '.join(valid_pair[0])
            characters = ', '.join(c.name for c in valid_pair[1])

            text_color = get_text_color_for_characters(valid_pair[1])

            layout.append(layout_text("["+tags+"]:", "black"))
            layout.append(layout_text(textwrap.fill(characters, 25), text_color))
            layout.append(layout_text("", "black"))


    if should_create_window:
        display_window(target_window.hwnd, layout, size_x, real_size_y, border_size_y)