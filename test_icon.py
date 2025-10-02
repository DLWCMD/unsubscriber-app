import flet as ft
import time

def main(page: ft.Page):
    page.title = "Icon Test"

    def button_clicked(e):
        # This handler runs in the background
        e.control.text = "Working..."
        page.update()
        
        time.sleep(1) # Simulate work
        
        # CORRECTED: ft.Icons (Capital I)
        e.control.icon = ft.Icons.CHECK 
        e.control.text = "Success!"
        e.control.disabled = True
        page.update()

    test_button = ft.ElevatedButton("Click Me", on_click=button_clicked)
    
    page.add(
        ft.Text("Icon Test", size=20),
        test_button
    )

ft.app(target=main)