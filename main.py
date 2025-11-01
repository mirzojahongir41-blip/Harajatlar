# -*- coding: utf-8 -*-
import os
import pickle
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

KV = """
ScreenManager:
    DashboardScreen:
    ExpenseScreen:
    StatsScreen:
    BudgetScreen:

<CommonButton@Button>:
    size_hint_y: None
    height: 56
    background_normal: ''
    background_color: 0.12,0.56,0.86,1
    color: 1,1,1,1
    font_size: 16
    radius: [12,]

<DashboardScreen>:
    name: "dashboard"
    BoxLayout:
        orientation: 'vertical'
        padding: 14
        spacing: 12
        canvas.before:
            Color:
                rgba: 0.96,0.98,1,1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Harajatlar"
            size_hint_y: None
            height: 56
            font_size: 26
            color: 0,0,0,1
        BoxLayout:
            size_hint_y: None
            height: 120
            spacing: 10
            BoxLayout:
                orientation: 'vertical'
                padding: 10
                canvas.before:
                    Color: 0.18,0.55,0.9,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10,]
                Label:
                    id: total_label
                    text: "Jami: 0 so'm"
                    color: 1,1,1,1
                    font_size: 20
                Label:
                    id: monthly_label
                    text: "Bu oy: 0 so'm"
                    color: 1,1,1,1
            BoxLayout:
                orientation: 'vertical'
                padding: 10
                canvas.before:
                    Color: 0.2,0.8,0.6,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10,]
                Label:
                    id: daily_label
                    text: "Bugun: 0 so'm"
                    color: 1,1,1,1
                Label:
                    text: ""
        CommonButton:
            text: "💰 Xarajat qo'shish"
            on_press: app.root.current = "expenses"
        CommonButton:
            text: "📈 Statistika"
            on_press: app.show_stats()
        CommonButton:
            text: "🎯 Byudjet"
            on_press: app.root.current = "budget"

<ExpenseRow@BoxLayout>:
    size_hint_y: None
    height: 50
    spacing: 8
    Label:
        id: dlabel
        text: root.date_str
        size_hint_x: 0.25
        color: 0,0,0,1
    Label:
        id: clabel
        text: root.category
        size_hint_x: 0.45
        color: 0,0,0,1
    Label:
        id: alabel
        text: root.amount_str
        size_hint_x: 0.3
        color: 0,0,0,1

<ExpenseScreen>:
    name: "expenses"
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 10
        canvas.before:
            Color: 1,1,1,1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: 48
            spacing: 8
            TextInput:
                id: amount
                hint_text: "Summa (so'm)"
                input_filter: 'float'
                multiline: False
            Spinner:
                id: category
                text: "Kategoriya"
                values: ["Oziq-ovqat","Transport","Kommunal","Salomatlik","Kiyim","O'yin","Ta'lim","Boshqa"]
                size_hint_x: 0.5
        TextInput:
            id: description
            hint_text: "Tavsif (ixtiyoriy)"
            size_hint_y: None
            height: 48
            multiline: False
        CommonButton:
            text: "Saqlash"
            on_press: app.add_expense()
        Label:
            text: "So'nggi xarajatlar"
            size_hint_y: None
            height: 30
            color: 0,0,0,1
        ScrollView:
            GridLayout:
                id: expense_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        CommonButton:
            text: "🏠 Dashboard"
            on_press: app.root.current = "dashboard"

<StatsScreen>:
    name: "stats"
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 10
        canvas.before:
            Color: 0.98,0.98,1,1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Statistika"
            size_hint_y: None
            height: 48
        BoxLayout:
            id: chart_box
        CommonButton:
            text: "🏠 Dashboardga qaytish"
            on_press: app.root.current = "dashboard"

<BudgetScreen>:
    name: "budget"
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 10
        Label:
            text: "Byudjet (kategoriya bo'yicha oylik limit)"
            size_hint_y: None
            height: 48
        GridLayout:
            id: budget_grid
            cols: 2
            size_hint_y: None
            height: self.minimum_height
        CommonButton:
            text: "Saqlash"
            on_press: app.save_budget()
        CommonButton:
            text: "🏠 Dashboardga qaytish"
            on_press: app.root.current = "dashboard"
"""

Builder.load_string(KV)

class DashboardScreen(Screen): pass
class ExpenseScreen(Screen): pass
class StatsScreen(Screen): pass
class BudgetScreen(Screen): pass

class ExpenseApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file = "expenses.pkl"
        self.expenses = []
        self.budget = {}
        self.load_data()

    def build(self):
        return Builder.load_string(KV)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "rb") as f:
                    data = pickle.load(f)
                    self.expenses = data.get("expenses", [])
                    self.budget = data.get("budget", {})
            except Exception:
                self.expenses = []
                self.budget = {}

    def save_data(self):
        data = {"expenses": self.expenses, "budget": self.budget}
        with open(self.data_file, "wb") as f:
            pickle.dump(data, f)

    def on_start(self):
        self.update_dashboard()
        self.update_expense_list()
        self.load_budget_inputs()

    def show_popup(self, title, message):
        Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4)).open()

    def update_dashboard(self):
        total = sum(e['amount'] for e in self.expenses)
        now = datetime.now()
        monthly = sum(e['amount'] for e in self.expenses if e['date'].month == now.month)
        daily = sum(e['amount'] for e in self.expenses if e['date'].date() == now.date())
        try:
            scr = self.root.get_screen("dashboard")
            scr.ids.total_label.text = f"Jami: {total:,.0f} so'm"
            scr.ids.monthly_label.text = f"Bu oy: {monthly:,.0f} so'm"
            scr.ids.daily_label.text = f"Bugun: {daily:,.0f} so'm"
        except Exception:
            pass

    def add_expense(self):
        try:
            scr = self.root.get_screen("expenses")
            amount = scr.ids.amount.text
            cat = scr.ids.category.text
            desc = scr.ids.description.text
            if not amount or cat == "Kategoriya":
                self.show_popup("Xato", "Summa va kategoriya kiriting")
                return
            amount = float(amount)
            exp = {"amount": amount, "category": cat, "description": desc, "date": datetime.now()}
            self.expenses.append(exp)
            self.save_data()
            scr.ids.amount.text = ""
            scr.ids.description.text = ""
            self.update_expense_list()
            self.update_dashboard()
            self.show_popup("✅", "Xarajat qo'shildi")
        except Exception as ex:
            self.show_popup("Xato", str(ex))

    def update_expense_list(self):
        try:
            scr = self.root.get_screen("expenses")
            grid = scr.ids.expense_list
            grid.clear_widgets()
            for e in reversed(self.expenses[-50:]):
                from kivy.uix.boxlayout import BoxLayout
                w = BoxLayout(size_hint_y=None, height=40)
                w.add_widget(Label(text=e['date'].strftime('%d/%m'), size_hint_x=0.25, color=(0,0,0,1)))
                w.add_widget(Label(text=e['category'], size_hint_x=0.45, color=(0,0,0,1)))
                w.add_widget(Label(text=f"{e['amount']:,.0f} so'm", size_hint_x=0.3, color=(0,0,0,1)))
                grid.add_widget(w)
        except Exception:
            pass

    def show_stats(self):
        scr = self.root.get_screen("stats")
        scr.ids.chart_box.clear_widgets()
        categories = {}
        for e in self.expenses:
            categories[e['category']] = categories.get(e['category'], 0) + e['amount']
        if not categories:
            self.show_popup("Ma'lumot yo'q", "Hozircha xarajatlar kiritilmagan")
            return
        fig, ax = plt.subplots(figsize=(4,3))
        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
        ax.axis('equal')
        scr.ids.chart_box.add_widget(FigureCanvasKivyAgg(fig))
        self.root.current = "stats"

    def load_budget_inputs(self):
        try:
            scr = self.root.get_screen("budget")
            grid = scr.ids.budget_grid
            grid.clear_widgets()
            from kivy.uix.textinput import TextInput
            self.budget_inputs = {}
            cats = ["Oziq-ovqat","Transport","Kommunal","Salomatlik","Kiyim","O'yin","Ta'lim","Boshqa"]
            for cat in cats:
                grid.add_widget(Label(text=cat, size_hint_y=None, height=40, color=(0,0,0,1)))
                inp = TextInput(text=str(self.budget.get(cat, 0)), multiline=False, size_hint_y=None, height=40)
                grid.add_widget(inp)
                self.budget_inputs[cat] = inp
        except Exception:
            pass

    def save_budget(self):
        try:
            for cat, inp in self.budget_inputs.items():
                try:
                    self.budget[cat] = float(inp.text)
                except:
                    self.budget[cat] = 0
            self.save_data()
            self.show_popup("✅", "Byudjet saqlandi")
        except Exception as ex:
            self.show_popup("Xato", str(ex))

if __name__ == "__main__":
    ExpenseApp().run()
