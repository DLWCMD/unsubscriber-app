import flet as ft

def main(page: ft.Page):
    page.title = "Instant Update Test"

    def remove_item(e):
        # e.control is the button that was clicked.
        # e.control.data contains the Row we want to remove.
        items_column.controls.remove(e.control.data)
        page.update()

    items_column = ft.Column()
    for i in range(1, 4):
        # We create the Row first
        item_row = ft.Row()

        # We add a Text control to the Row
        item_row.controls.append(ft.Text(f"Item {i}"))

        # We create a Button and store a reference to the item_row in its `data` attribute
        remove_button = ft.ElevatedButton("Remove", data=item_row, on_click=remove_item)

        # We add the Button to the Row
        item_row.controls.append(remove_button)

        # Finally, we add the completed Row to our main Column
        items_column.controls.append(item_row)

    page.add(ft.Text("Test 1: Instant Update", size=20), items_column)

ft.app(target=main)