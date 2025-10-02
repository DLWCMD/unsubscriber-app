import flet as ft
import time

def main(page: ft.Page):
    page.title = "Threaded Update Test"

    def update_ui():
        # This function will be run on the main UI thread
        progress_bar.visible = False
        results_text.value = "Task complete! UI has been updated."
        page.update()

    def real_background_task():
        # This function runs in the background.
        # It simulates a long network call.
        time.sleep(2)
        # After the task is done, we schedule the UI update.
        # CORRECT SYNTAX: The target function is the first argument.
        page.run_thread(update_ui)

    def start_task_button_clicked(e):
        # This happens instantly when the button is clicked.
        progress_bar.visible = True
        results_text.value = "Running background task..."
        page.update()
        # We start the long task in a separate thread.
        # CORRECT SYNTAX: The target function is the first argument.
        page.run_thread(real_background_task)

    progress_bar = ft.ProgressBar(visible=False)
    results_text = ft.Text("")
    
    page.add(
        ft.Text("Test 2: Background Task with UI Update", size=20),
        ft.ElevatedButton("Run Long Task (2 seconds)", on_click=start_task_button_clicked),
        progress_bar,
        results_text
    )

ft.app(target=main)