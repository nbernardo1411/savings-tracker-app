# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
import os

# Create persistent storage
store = JsonStore("savings_log.json")

class SavingsEntry(BoxLayout):
    def __init__(self, entry_id, entry_data, refresh_callback, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5, **kwargs)
        self.entry_id = entry_id
        self.refresh_callback = refresh_callback

        summary = f"{entry_data['date']} | Saved: ₱{entry_data['saveable_amount']:.2f}"
        self.add_widget(Label(text=summary, halign="left", valign="middle", size_hint_x=0.8))
        
        delete_btn = Button(text="❌", size_hint_x=0.2)
        delete_btn.bind(on_press=self.delete_entry)
        self.add_widget(delete_btn)

    def delete_entry(self, instance):
        if store.exists(self.entry_id):
            store.delete(self.entry_id)
        self.refresh_callback()

class SavingsApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.inputs = {}
        fields = [
            ("Monthly Salary", "salary"),
            ("Parent Support", "parent_support"),
            ("Rent", "rent"),
            ("1st Cutoff Expenses", "first_cutoff"),
            ("2nd Cutoff Expenses", "second_cutoff"),
            ("Other Expenses", "other_expenses"),
        ]

        for label, key in fields:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
            box.add_widget(Label(text=label, size_hint_x=0.4))
            inp = TextInput(multiline=False, input_filter='float', hint_text="₱0.00")
            self.inputs[key] = inp
            box.add_widget(inp)
            self.add_widget(box)

        self.save_btn = Button(text="Save Entry", size_hint_y=None, height='50dp')
        self.save_btn.bind(on_press=self.calculate)
        self.add_widget(self.save_btn)

        self.log_panel = ScrollView(size_hint_y=0.5)
        self.log_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        self.log_panel.add_widget(self.log_box)
        self.add_widget(self.log_panel)

        self.load_logs()

    def calculate(self, instance):
        try:
            salary = float(self.inputs["salary"].text or 0)
            total_expenses = sum(float(self.inputs[k].text or 0) for k in self.inputs if k != "salary")
            saveable_amount = salary - total_expenses
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                "date": now,
                "salary": salary,
                "parent_support": float(self.inputs["parent_support"].text or 0),
                "rent": float(self.inputs["rent"].text or 0),
                "first_cutoff": float(self.inputs["first_cutoff"].text or 0),
                "second_cutoff": float(self.inputs["second_cutoff"].text or 0),
                "other_expenses": float(self.inputs["other_expenses"].text or 0),
                "total_expenses": total_expenses,
                "saveable_amount": saveable_amount
            }
            entry_id = f"log_{now.replace(' ', '_').replace(':', '-')}"
            store.put(entry_id, **entry)
            self.load_logs()
            Popup(title="Success", content=Label(text=f"Saved ₱{saveable_amount:.2f}"), size_hint=(0.7, 0.3)).open()
        except Exception as e:
            Popup(title="Error", content=Label(text=str(e)), size_hint=(0.7, 0.3)).open()

    def load_logs(self):
        self.log_box.clear_widgets()
        for key in sorted(store.keys(), reverse=True):
            entry_data = store.get(key)
            self.log_box.add_widget(SavingsEntry(key, entry_data, self.load_logs))

class MySavingsApp(App):
    def build(self):
        self.title = "My Savings Tracker"
        return SavingsApp()

if __name__ == '__main__':
    MySavingsApp().run()
