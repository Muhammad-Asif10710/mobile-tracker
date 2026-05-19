import os
import sqlite3
import shutil
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

KV = """
<InventoryScreen>:
    orientation: 'vertical'
    padding: dp(14)
    spacing: dp(12)

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)

        TextInput:
            id: object_name_input
            hint_text: 'Object Name'
            multiline: False
            write_tab: False

        Button:
            text: 'Choose Image'
            size_hint_x: None
            width: dp(140)
            on_release: root.open_file_chooser_popup()

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)

        Button:
            text: 'Save Object'
            on_release: root.save_object()

        TextInput:
            id: search_input
            hint_text: 'Search exact name'
            multiline: False
            write_tab: False
            on_text_validate: root.search_object(self.text)

        Button:
            text: 'Search'
            size_hint_x: None
            width: dp(100)
            on_release: root.search_object(search_input.text)

    Image:
        id: result_image
        source: ''
        allow_stretch: True
        keep_ratio: True
        size_hint_y: 0.6
        canvas.before:
            Color:
                rgba: .15, .15, .15, 1
            Rectangle:
                pos: self.pos
                size: self.size

    Label:
        id: status_bar
        size_hint_y: None
        height: dp(32)
        text: root.status_message
        text_size: self.width - dp(16), None
        halign: 'left'
        valign: 'middle'
        shorten: True
"""


class InventoryScreen(BoxLayout):
    status_message = StringProperty('Ready to store items.')
    selected_image_path = StringProperty('')

    def open_file_chooser_popup(self):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        filechooser = FileChooserListView(path='/', filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'], size_hint=(1, 1))
        content.add_widget(filechooser)

        button_bar = BoxLayout(size_hint_y=None, height='48dp', spacing=8)
        select_button = App.get_running_app().build_button('Select', lambda *_: self.select_image(filechooser.selection, popup))
        cancel_button = App.get_running_app().build_button('Cancel', lambda *_: popup.dismiss())
        button_bar.add_widget(select_button)
        button_bar.add_widget(cancel_button)
        content.add_widget(button_bar)

        popup = Popup(title='Select image file', content=content, size_hint=(0.95, 0.95), auto_dismiss=False)
        popup.open()

    def select_image(self, selection, popup):
        if not selection:
            self.status_message = 'No image selected. Choose a file first.'
            return
        selected_path = selection[0]
        if not os.path.isfile(selected_path):
            self.status_message = 'Invalid image file selected.'
            return
        self.selected_image_path = selected_path
        self.status_message = f'Image selected: {os.path.basename(selected_path)}'
        popup.dismiss()

    def save_object(self):
        app = App.get_running_app()
        object_name = self.ids.object_name_input.text.strip()
        image_path = self.selected_image_path
        if not object_name:
            self.status_message = 'Please enter an object name.'
            return
        if not image_path:
            self.status_message = 'Please choose an image before saving.'
            return
        if not os.path.isfile(image_path):
            self.status_message = 'Selected image file does not exist.'
            return

        target_dir = app.image_storage_dir
        os.makedirs(target_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        extension = os.path.splitext(image_path)[1].lower()
        safe_name = ''.join(ch if ch.isalnum() else '_' for ch in object_name).rstrip('_')
        target_filename = f'{safe_name}_{timestamp}{extension}'
        target_path = os.path.join(target_dir, target_filename)

        try:
            with open(image_path, 'rb') as src_file, open(target_path, 'wb') as dst_file:
                shutil.copyfileobj(src_file, dst_file)
        except Exception as exc:
            self.status_message = f'Failed to copy image: {exc}'
            return

        try:
            app.save_item_to_db(object_name, os.path.abspath(target_path))
        except Exception as exc:
            self.status_message = f'Database save failed: {exc}'
            return

        self.status_message = f'Object "{object_name}" saved successfully.'
        self.ids.object_name_input.text = ''
        self.selected_image_path = ''

    def search_object(self, query_text: str):
        query = query_text.strip()
        if not query:
            self.status_message = 'Enter an object name to search.'
            return

        app = App.get_running_app()
        result = app.search_item_by_name(query)
        if not result:
            self.ids.result_image.source = ''
            self.status_message = f'No object found with name "{query}".'
            return

        image_path = result
        if not os.path.isfile(image_path):
            self.ids.result_image.source = ''
            self.status_message = 'Image file is missing for the stored object.'
            return

        self.ids.result_image.source = image_path
        self.status_message = f'Loaded object "{query}" from storage.'


class InventoryApp(App):
    db_path = None
    image_storage_dir = None

    def build(self):
        self.title = 'Mobile Inventory Tracker'
        self.create_storage_paths()
        self.initialize_database()
        return Builder.load_string(KV)

    def create_storage_paths(self):
        user_dir = App.get_running_app().user_data_dir if App.get_running_app() else self.user_data_dir
        os.makedirs(user_dir, exist_ok=True)
        self.db_path = os.path.join(user_dir, 'inventory.db')
        self.image_storage_dir = os.path.join(user_dir, 'stored_images')
        os.makedirs(self.image_storage_dir, exist_ok=True)

    def initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                'CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, image_path TEXT NOT NULL)'
            )
            conn.commit()
        finally:
            conn.close()

    def save_item_to_db(self, name: str, image_path: str):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                'INSERT INTO items (name, image_path) VALUES (?, ?)',
                (name, image_path),
            )
            conn.commit()
        finally:
            conn.close()

    def search_item_by_name(self, name: str):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                'SELECT image_path FROM items WHERE LOWER(name) = LOWER(?) LIMIT 1',
                (name,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    @staticmethod
    def build_button(text, callback):
        from kivy.uix.button import Button
        return Button(text=text, size_hint=(1, 1), on_release=callback)


if __name__ == '__main__':
    InventoryApp().run()
