# -*- coding=UTF-8 -*-
# pyright: strict

import ctypes
from ctypes import byref
from ctypes.wintypes import HWND, LONG, LPARAM, RECT, UINT
from typing import Text, List

_EnumWindows = ctypes.windll.user32.EnumWindows
_EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
_GetWindowText = ctypes.windll.user32.GetWindowTextW
_GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
_IsWindowVisible = ctypes.windll.user32.IsWindowVisible
_GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
_GetWindowRect = ctypes.windll.user32.GetWindowRect
_GetClientRect = ctypes.windll.user32.GetClientRect
_SetWindowPos = ctypes.windll.user32.SetWindowPos
_GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics

class WinWindow:
    hwnd: HWND
    Title: Text
    PID: UINT


def GetAllWindows() -> List[WinWindow]:
    windows:List[WinWindow] = []
    def foreach_window(hwnd: HWND, lParam: LPARAM):
        if _IsWindowVisible(hwnd):
            length = _GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            _GetWindowText(hwnd, buff, length + 1)
            window = WinWindow()
            window.hwnd = hwnd
            window.Title = buff.value
            pid = ctypes.c_uint()
            window.PID = _GetWindowThreadProcessId(hwnd, byref(pid))
            windows.append(window)
        return True
    _EnumWindows(_EnumWindowsProc(foreach_window), 0)
    return windows

def GetWindowRect(hwnd: HWND) -> RECT:
    win_rect = RECT()
    _GetWindowRect(hwnd, byref(win_rect))

    #print("%d, %d, %d, %d"%(win_rect.left, win_rect.right, win_rect.top, win_rect.bottom))
    #print("%d, %d, %d, %d"%(c_rect.left, c_rect.right, c_rect.top, c_rect.bottom))
    return win_rect

def GetClientRect(hwnd: HWND) -> RECT:
    c_rect = RECT()
    _GetClientRect(hwnd, byref(c_rect))
    return c_rect

def GetWindowTitleBarHeight():
    return _GetSystemMetrics(33) + _GetSystemMetrics(4) + _GetSystemMetrics(92)

def SetWindowPos(hwnd: HWND, hWndInsertAfter: HWND, x: int, y: int, cx: int, cy: int, uFlags: UINT):
    _SetWindowPos(hwnd, hWndInsertAfter, x, y, cx, cy, uFlags)