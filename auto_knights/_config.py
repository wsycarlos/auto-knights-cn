# -*- coding=UTF-8 -*-
# pyright: strict

import os
from typing import Text

from . import plugin, template, terminal
from .clients import ADBClient, Client

def _getenv_int(key: Text, d: int) -> int:
    try:
        return int(os.getenv(key, ""))
    except:
        return d


def _default_client() -> Client:
    raise NotImplementedError()


class config:
    LOG_PATH = os.getenv("AUTO_KNIGHTS_LOG_PATH", "auto_knights.log")
    PLUGINS = tuple(i for i in os.getenv("AUTO_KNIGHTS_PLUGINS", "").split(",") if i)
    ADB_ADDRESS = os.getenv("AUTO_KNIGHTS_ADB_ADDRESS", "")
    CHECK_UPDATE = os.getenv("AUTO_KNIGHTS_CHECK_UPDATE", "").lower() == "true"

    client = _default_client
    last_screenshot_save_path = os.getenv("AUTO_KNIGHTS_LAST_SCREENSHOT_SAVE_PATH", "")
    
    plugin_path = os.getenv("AUTO_KNIGHTS_PLUGIN_PATH", "plugins")
    
    adb_key_path = os.getenv("AUTO_KNIGHTS_ADB_KEY_PATH", ADBClient.key_path)
    adb_action_wait = _getenv_int("AUTO_KNIGHTS_ADB_ACTION_WAIT", ADBClient.action_wait)

    terminal_pause_sound_path = os.path.expandvars(
        "${WinDir}/Media/Windows Background.wav"
    )
    terminal_prompt_sound_path = terminal_pause_sound_path

    @classmethod
    def apply(cls) -> None:
        ADBClient.key_path = cls.adb_key_path
        ADBClient.action_wait = cls.adb_action_wait
        
        plugin.g.path = cls.plugin_path
        
        template.g.last_screenshot_save_path = cls.last_screenshot_save_path
        terminal.g.pause_sound_path = cls.terminal_pause_sound_path
        terminal.g.prompt_sound_path = cls.terminal_prompt_sound_path


config.apply()
