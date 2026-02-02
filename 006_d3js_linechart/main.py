from datetime import date, timedelta
import random

from nicegui import ui

from components import D3LineChart


# Generate initial data
def generate_data(start_date: date = None, days: int = 7) -> list:
    if start_date is None:
        start_date = date(2024, 1, 1)
    
    data = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "value": int(random.random() * 100) + 1,
        })
    return data


# Initial data
data = generate_data()


@ui.page("/")
def main_page():
    ui.label("D3.js Line Chart with NiceGUI").classes("text-h4 q-pb-md")
    
    # Add custom styles
    ui.add_head_html('''
        <style>
            .d3-linechart-container {
                background: #1a1a2e;
                border-radius: 8px;
                padding: 16px;
                position: relative;
            }
            .d3-linechart-container .line {
                fill: none;
                stroke: #4fc3f7;
                stroke-width: 2px;
            }
            .d3-linechart-container .axis text {
                fill: #ffffff;
            }
            .d3-linechart-container .axis line,
            .d3-linechart-container .axis path {
                stroke: #666;
            }
            .d3-linechart-container .grid line {
                stroke: #333;
                stroke-opacity: 0.7;
            }
            .d3-linechart-container .tooltip {
                position: absolute;
                background: #333;
                color: #fff;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
            }
        </style>
    ''')
    
    # Create the chart component
    chart = D3LineChart(data=data).classes("w-full")

    # Add randomize button
    def randomize_data():
        new_data = generate_data()
        chart.set_data(new_data)
    
    ui.button("Randomize Data", on_click=randomize_data).classes("q-mt-md")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
