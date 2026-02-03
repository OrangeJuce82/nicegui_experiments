#!/usr/bin/env python3
"""The Game of Life implemented with nicegui

Sources :
* https://halimb.github.io/gol/
* https://editor.p5js.org/pattvira/sketches/cGuJD9_Ak
* https://github.com/edwinm/game-of-life
"""

from typing import Optional

from nicegui import ui
from nicegui.events import Handler, ClickEventArguments

from components.game_of_life import GameOfLife


def custom_icon(
    icon: Optional[str] = None,
    on_click: Optional[Handler[ClickEventArguments]] = None,
    color="gray-500",
    size="sm",
    *args,
    **kwargs,
):
    return (
        ui.button(icon=icon, on_click=on_click, color=color, *args, **kwargs)
        .props(f'padding="{size}" size="{size}"')
        .classes("text-white")
    )


@ui.page("/")
def home():
    # Add CSS styles
    ui.add_head_html(
        '<link href="https://cdn.jsdelivr.net/themify-icons/0.1.2/css/themify-icons.css" rel="stylesheet" />'
    )
    ui.add_css("""
    body{ 
        overflow:hidden !important; 
    }
    """)

    # --------------------------------------- #
    # ============ Build UI ================= #
    # --------------------------------------- #

    # Build main theme
    ui.colors(primary="white")

    # Remove padding of the nicegui-content element
    ui.query(".nicegui-content").classes("p-0")
    gol = GameOfLife()

    # ============= Header  ================= #
    with ui.header().classes(
        replace="text-black bg-white flex items-center p-2 shadow-2"
    ):
        ui.space()
        ui.label("Conway’s Game of Life").classes("font-bold text-2xl")
        ui.space()
        with ui.row().classes("items-center"):
            custom_icon(
                "ti-control-shuffle", on_click=lambda e: gol.init_grid(mode="random")
            )
            custom_icon("ti-star")

    # ======== Footer / Controls ============ #
    with ui.footer().classes("bg-white text-black flex items-center px-4 shadow-2"):
        with ui.row().classes("items-center"):
            custom_icon("ti-control-play", on_click=gol.toggle_play).bind_icon_from(
                gol,
                target_name="playing",
                backward=lambda value: "ti-control-pause"
                if value
                else "ti-control-play",
            )
            custom_icon("ti-control-skip-forward", on_click=gol.generate_next_grid)

            ui.label("Generation : 0").bind_text_from(
                gol,
                target_name="generation_num",
                backward=lambda value: f"Generation : {value}",
            )

        ui.space()
        with ui.row().classes("items-center"):
            custom_icon("ti-minus", size="xs", on_click=gol.decrease_speed)
            ui.label("Speed : 1x").bind_text_from(
                gol, target_name="speed", backward=lambda value: f"Speed : {value}x"
            )
            custom_icon("ti-plus", size="xs", on_click=gol.increase_speed)

        ui.space()
        with ui.row().classes("items-center"):
            with custom_icon("ti-paint-bucket").style(
                f"background-color: {gol.hex_color}"
            ) as paint_icon:
                ui.color_picker(
                    on_pick=lambda e: (
                        gol.set_hex_color(e.color),
                        paint_icon.style(f"background-color: {e.color}"),
                    )
                )

            custom_icon("ti-pencil", on_click=gol.use_pencil)

            custom_icon("ti-eraser", on_click=gol.use_eraser)
            custom_icon("ti-trash", on_click=lambda e: gol.init_grid())


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=49373)
