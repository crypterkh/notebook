import flet as ft
import os
from datetime import datetime

# --- 1. ROBUST PATHING ---
# Saving to your User Documents folder is the safest way to avoid permission errors
DOCS_PATH = os.path.join(os.path.expanduser("~"), "MyFletNotes")
if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)

DRAFT_PATH = os.path.join(DOCS_PATH, "emergency_draft.txt")

def main(page: ft.Page):
    page.title = "Data-Safe Notebook"
    page.theme_mode = "light"
    page.padding = 0

    state = {"current_note": None}

    # --- 2. THE SAVE FUNCTION (REWRITTEN) ---
    def save_now(e=None):
        content = editor.value
        
        # If a note is selected, save to that file
        if state["current_note"]:
            filename = f"{state['current_note']}.md"
            path = os.path.join(DOCS_PATH, filename)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                save_btn.icon_color = "green"
                status_text.value = f"Success: Saved to {filename} at {datetime.now().strftime('%H:%M:%S')}"
            except Exception as err:
                save_btn.icon_color = "red"
                status_text.value = f"Error: {str(err)}"
        else:
            # EMERGENCY BACKUP: If no note is selected, save to draft
            with open(DRAFT_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            status_text.value = "Draft Saved (No note selected. Click 'New Note' to name it!)"
        
        page.update()

    # --- 3. UI COMPONENTS ---
    editor = ft.TextField(
        multiline=True, expand=True, border="none",
        hint_text="Type here... even if you haven't created a note yet, I will save a draft.",
        on_change=save_now # Auto-save on every character
    )

    status_text = ft.Text("Ready", size=12, color="grey700")
    current_title = ft.Text("Unnamed Draft", size=20, weight="bold")
    save_btn = ft.IconButton(icon="save", on_click=save_now, tooltip="Manual Save")
    sidebar_list = ft.ListView(expand=True)

    def refresh_sidebar():
        sidebar_list.controls.clear()
        files = [f[:-3] for f in os.listdir(DOCS_PATH) if f.endswith('.md')]
        for f in sorted(files):
            sidebar_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f),
                    on_click=lambda e, name=f: load_note(name),
                    leading=ft.Icon("description")
                )
            )
        page.update()

    def load_note(name):
        state["current_note"] = name
        path = os.path.join(DOCS_PATH, f"{name}.md")
        with open(path, "r", encoding="utf-8") as file:
            editor.value = file.read()
        current_title.value = name
        refresh_sidebar()

    def create_note(e):
        def confirm(e):
            if name_input.value:
                state["current_note"] = name_input.value
                save_now() # Immediately save the current editor text to the new file
                dlg.open = False
                current_title.value = name_input.value
                refresh_sidebar()
        
        name_input = ft.TextField(label="New Note Name")
        dlg = ft.AlertDialog(
            title=ft.Text("Save As..."),
            content=name_input,
            actions=[ft.TextButton("Save", on_click=confirm)]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- 4. LAYOUT ---
    page.add(
        ft.Row([
            # Sidebar
            ft.Container(
                content=ft.Column([
                    ft.Text("MY FILES", weight="bold"),
                    ft.ElevatedButton("New Note", icon="add", on_click=create_note),
                    sidebar_list,
                ]),
                width=250, bgcolor="#f0f0f0", padding=20
            ),
            # Editor
            ft.Container(
                content=ft.Column([
                    ft.Row([current_title, save_btn], alignment="spaceBetween"),
                    ft.Divider(),
                    editor,
                    status_text
                ]),
                expand=True, padding=20
            )
        ], expand=True)
    )

    # Recovery: Load the last draft if it exists on startup
    if os.path.exists(DRAFT_PATH):
        with open(DRAFT_PATH, "r", encoding="utf-8") as f:
            editor.value = f.read()
        status_text.value = "Recovered unsaved draft from last session."

    refresh_sidebar()

ft.app(target=main)