# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

import PIL.Image


class _g:
    current_client: Client


class Client(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        ...

    def setup(self) -> None:
        pass

    @abstractmethod
    def screenshot(self) -> PIL.Image.Image:
        ...

    @abstractmethod
    def tap(self, point: Tuple[int, int]) -> None:
        ...

    @abstractmethod
    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        ...