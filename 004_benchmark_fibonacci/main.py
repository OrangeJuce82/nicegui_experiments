import base64
import time
from functools import lru_cache
from io import BytesIO
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from nicegui import ui, run
from numba import jit
from sympy import fibonacci


# --- Fibonacci ---
def fib_binet(n):
    phi = (1 + sqrt(5)) / 2
    return round((phi**n - (-phi) ** -n) / sqrt(5))


def fib_sympy(n):
    return int(fibonacci(n))


@jit(nopython=True, cache=True)
def fib_numba_cache(n):
    if n <= 1:
        return n
    return fib_numba_cache(n - 1) + fib_numba_cache(n - 2)


@jit(nopython=True)
def fib_numba(n):
    if n <= 1:
        return n
    return fib_numba(n - 1) + fib_numba(n - 2)


@jit(nopython=True)
def fib_numba_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_numpy(n):
    F = np.array([[1, 1], [1, 0]], dtype=object)
    if n == 0:
        return 0
    result = np.linalg.matrix_power(F, n - 1)
    return result[0, 0]


@lru_cache(maxsize=None)
def fib_lru(n):
    if n <= 1:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)


# --- Benchmark ---
def benchmark_fibonacci(n):
    results = {}
    functions = {
        # "Numba": fib_numba,
        # "Numba cache": fib_numba_cache,
        "Numba iter": fib_numba_iter,
        "Sympy": fib_sympy,
        "Binet": fib_binet,
        "NumPy": fib_numpy,
        "LRU Cache": fib_lru,
    }

    for name, func in functions.items():
        start_time = time.time()
        result = func(n)
        elapsed = time.time() - start_time
        results[name] = {"result": result, "time": elapsed}

    return results


# --- UI with NiceGUI ---
def create_plot(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    names = list(data.keys())
    times = [data[name]["time"] for name in names]

    colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#D5BAFF"]
    ax.bar(names, times, color=colors)
    ax.set_ylabel("Time (seconds)")
    ax.set_title(f"Execution time for Fibonacci(n)")

    # Improve x-axis labels spacing
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")  # Rotate and align labels

    # Adjust the x-ticks for more uniform spacing
    ax.set_xticks(np.arange(len(names)))

    # Set y-axis to logarithmic scale
    ax.set_yscale("log")

    # Add padding at the bottom for the x-axis labels
    plt.subplots_adjust(bottom=0.3)  # Adjust the bottom padding

    # Save the fig
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return encoded_image


async def on_run():
    # Display the spinner during the calculation
    spinner.visible = True

    n = int(number_input.value)

    # Use cpu_bound to run the benchmark without blocking the UI
    results = await run.cpu_bound(benchmark_fibonacci, n)

    # Cache the results and the plot
    table.rows.clear()
    for name, data in results.items():
        table.add_row(
            row={
                "name": name,
                "result": data["result"],
                "time": f"{data['time']:.6f} s",
            }
        )

    # Generate and display the plot
    plot_image = create_plot(results)
    plot.set_content(
        f'<img src="data:image/png;base64,{plot_image}" style="width:100%;">'
    )

    # Hide the spinner after the calculation
    spinner.visible = False


with ui.column().classes("text-center w-[600px] m-auto"):
    ui.label("Benchmark of different Fibonacci functions").classes("text-xl font-bold")

    with ui.row():
        number_input = ui.number(label="Value of n", value=10, min=1, step=1)
        ui.button("Run the benchmark", on_click=on_run)
        spinner = ui.spinner("audio", size="lg")
        spinner.visible = False

    # Create the table for displaying results
    columns = [
        {"name": "name", "label": "Name", "field": "name"},
        {"name": "result", "label": "Result", "field": "result"},
        {"name": "time", "label": "Time", "field": "time", "sortable": True},
    ]
    table = ui.table(columns=columns, rows=[]).classes("w-full mt-4")

    # Plot
    plot = ui.html().classes("mt-4")

ui.run(title="Fibonacci Benchmark")
