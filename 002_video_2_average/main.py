#!/usr/bin/env python3
"""An app who take a video then generate secondary images."""

import base64
import os
import threading
from datetime import datetime
from typing import Union

import aiofiles
import cv2
import numpy as np
from nicegui import ui, events


def log(message: Union[str, Exception]):
    date_str = datetime.now().strftime("%X.%f")[:-5]
    log_element.push(f"{date_str} | {message}")


class Average:
    def __init__(self):
        self._counter = 0
        self._summ = 0

    def add_frame(self, frame: np.ndarray) -> None:
        if not self._counter:
            self._summ = frame.astype(np.uint32)
        else:
            self._summ += frame
        self._counter += 1

    def compute(self) -> np.ndarray:
        if not self._counter:
            raise ValueError("No frames yet")

        return (self._summ / self._counter).astype("uint8")


def decode_video(filepath, notify, container):
    try:
        stream = cv2.VideoCapture(filepath)
        if not stream.isOpened():
            raise Exception("cv2: Video stream can't be opened")

        frame_index = 1
        avg = Average()
        while True:
            frame_got, frame = stream.read()
            if not frame_got:
                break

            avg.add_frame(frame)

            frame_index += 1
            notify(f"{frame_index} | {frame.shape}")

        _, buffer = cv2.imencode(".jpeg", avg.compute())
        encoded_image = base64.b64encode(buffer).decode("utf-8")

        with container:
            ui.image(f"data:image/jpeg;base64,{encoded_image}")

    except Exception as e:
        notify(e)
    finally:
        if os.path.exists(filepath):
            notify(f"Remove temporary file : {filepath}")
            os.remove(filepath)
        if stream and stream.isOpened():
            notify("cv2: Release video stream")
            stream.release()


async def handle_upload(args: events.UploadEventArguments) -> None:
    try:
        async with aiofiles.tempfile.NamedTemporaryFile(
            "wb", delete=False
        ) as temp_file:
            contents = args.content.read()
            await temp_file.write(contents)

            filepath = temp_file.name
            log(f"Start to decode {filepath}")
            threading.Thread(
                target=decode_video, args=(filepath, log, container)
            ).start()

    except Exception as e:
        log(e)


with ui.column().classes("w-full p-10") as container:
    upload_input = ui.upload(
        label="Upload a video file", auto_upload=True, on_upload=handle_upload
    ).classes("w-full")
    log_element = ui.log(max_lines=10).classes("w-full h-40")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        native=True, port=8093, reload=False, storage_secret="THIS_NEEDS_TO_BE_CHANGED"
    )
