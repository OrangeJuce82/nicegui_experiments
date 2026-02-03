#!/usr/bin/env python3
"""The famous TicTacToe game implemented with nicegui

Deeply inspired by : https://github.com/SaitoTsutomu/nicegui-tic_tac_toe/blob/master/src/nicegui_tic_tac_toe/tic_tac_toe.py
"""

from nicegui import ui
from nicegui.events import ClickEventArguments, Handler

PLAYERS: list[str] = ["X", "O"]
WINNING_COMBOS: list[set[int]] = [
    {0, 1, 2},
    {3, 4, 5},
    {6, 7, 8},  # Horizontal indexes
    {0, 3, 6},
    {1, 4, 7},
    {2, 5, 8},  # Vertical indexes
    {0, 4, 8},
    {2, 4, 6},  # Diagonal indexes
]


class Square(ui.element):
    def __init__(self, index: int, on_click: Handler[ClickEventArguments]):
        super().__init__("div")
        self._index = index
        self._on_click = on_click
        self._value = ""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value or ""
        self.build()

    def build(self):
        # Clear all children
        self.clear()
        with self:
            if self.value in PLAYERS:
                name = "close" if self.value == "X" else "radio_button_unchecked"
                color = "red" if self.value == "X" else "indigo-4"
                ui.icon(name, size="3em", color=color).classes("size-16")
            else:
                ui.button(
                    self.value, on_click=lambda: self._on_click(self._index)
                ).classes("size-16")


class Player(ui.element):
    def __init__(self, index: int):
        super().__init__("div")


class Game:
    def __init__(self):
        self._board: list[Square] = []
        self._player_index = 0
        self._message: str = ""
        self._game_over = False

        with ui.column().classes("text-center w-[400px] m-auto"):
            ui.label("Tic Tac Toe").classes("w-full text-xl font-extrabold")
            with ui.card().classes("p-10 m-auto"):
                for row_index in range(3):
                    with ui.row():
                        for col_index in range(3):
                            self._board.append(
                                Square(
                                    index=row_index * 3 + col_index, on_click=self.play
                                )
                            )

            ui.label().bind_text(self, "_message").classes("w-full text-center text-xl")
            ui.button("reset", icon="refresh", on_click=self.reset).classes("m-auto")
            self.reset()

    def play(self, square_index: int):
        if self._game_over:
            return

        if not (0 <= square_index < len(self._board)):
            ui.notify(f"Wrong index {square_index}", type="negative")
            return

        self._board[square_index].value = self.current_player
        self.judge()
        if not self._game_over:
            self.to_next_player()

    def judge(self) -> None:
        for combo in WINNING_COMBOS:
            values = "".join(self._board[index].value or "." for index in combo)
            if values in {"OOO", "XXX"}:
                self._game_over = True
                self._message = f"🥳 {self.current_player} has won!"
                return
        if all(square.value for square in self._board):
            self._game_over = True
            self._message = f"⚖️ Equality!"

    def reset(self):
        """Reset the game"""
        self._message = ""
        self._game_over = False
        self._player_index = 0
        for square_index in range(len(self._board)):
            self._board[square_index].value = ""

    @property
    def current_player(self):
        return PLAYERS[self._player_index]

    def to_next_player(self):
        self._player_index = (self._player_index + 1) % len(PLAYERS)


@ui.page("/")
def play_game():
    Game()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=46758)
