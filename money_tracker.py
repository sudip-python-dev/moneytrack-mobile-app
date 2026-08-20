import sqlite3
import threading
from datetime import datetime
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.clock import mainthread
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu

class DatabaseManager:
    def __init__(self, db_name="money_track.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    budget REAL DEFAULT 50000.0
                )
            ''')
            cursor.execute('INSERT OR IGNORE INTO settings (id, budget) VALUES (1, 17500.0)')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            conn.commit()

    def get_budget(self):
        with self.get_connection() as conn:
            row = conn.cursor().execute('SELECT budget FROM settings WHERE id = 1').fetchone()
            return float(row[0]) if row else 0.0

    def update_budget(self, new_budget):
        with self.get_connection() as conn:
            conn.cursor().execute('UPDATE settings SET budget = ? WHERE id = 1', (float(new_budget),))
            conn.commit()

    def add_expense(self, category, amount, description):
        date_str = date_str = datetime.now().strftime("%d %b, %Y | %I:%M %p")
        with self.get_connection() as conn:
            conn.cursor().execute('''
                INSERT INTO expenses (category, amount, description, date)
                VALUES (?, ?, ?, ?)
            ''', (category.strip().title(), float(amount), description.strip(), date_str))
            conn.commit()

    def delete_expense(self, expense_id):
        with self.get_connection() as conn:
            conn.cursor().execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()

    def get_dashboard_data(self, default_categories):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) FROM expenses')
            res = cursor.fetchone()[0]
            total_spent = float(res) if res else 0.0
            
            cursor.execute('SELECT budget FROM settings WHERE id = 1')
            b_row = cursor.fetchone()
            budget = float(b_row[0]) if b_row else 0.0

            cursor.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
            db_data = {row[0]: float(row[1]) for row in cursor.fetchall()}
            
            all_cats = list(dict.fromkeys(default_categories + list(db_data.keys())))
            category_totals = [(cat, db_data.get(cat, 0.0)) for cat in all_cats]

            return total_spent, budget, category_totals

    def get_expenses_by_category(self, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, category, amount, description, date 
                FROM expenses 
                WHERE LOWER(category) = LOWER(?) 
                ORDER BY id DESC
            ''', (category.strip(),))
            return cursor.fetchall()


CATEGORY_THEMES = {
    "Water": {"icon": "water", "color": (0.2, 0.6, 1, 1)},
    "Food": {"icon": "food", "color": (1, 0.4, 0.4, 1)},
    "Shopping": {"icon": "cart", "color": (0.4, 0.8, 0.4, 1)},
    "Travel": {"icon": "bus", "color": (0.2, 0.8, 0.7, 1)},
}

DEFAULT_CATEGORIES = ["Water", "Food", "Shopping", "Travel"]

def get_cat_style(cat_name):
    return CATEGORY_THEMES.get(cat_name.title(), {"icon": "tag", "color": (0.35, 0.65, 0.75, 1)})


class CategoryCardItem(MDCard, ButtonBehavior):
    cat_name = StringProperty("")
    cat_spent = StringProperty("₹ 0")
    icon_name = StringProperty("tag")
    icon_bg = ListProperty([0.2, 0.6, 1, 1])

class ExpenseRowItem(MDCard, ButtonBehavior):
    desc_text = StringProperty("")
    date_text = StringProperty("")
    amount_text = StringProperty("")


kv = '''
ScreenManager:
    MainScreen:
        name: 'main_screen'
    BalanceScreen:
        name: 'balance_screen'
    AddExpenseScreen:
        name: 'add_expense_screen'
    CategoryScreen:
        name: 'category_screen'
    DetailScreen:
        name: 'detail_screen'

<CategoryCardItem>:
    elevation: 2
    radius: [20, 20, 20, 20]
    md_bg_color: 1, 1, 1, 1
    size_hint: None, None
    size: "140dp", "165dp"
    ripple_behavior: True

    MDFloatLayout:
        MDCard:
            elevation: 0
            radius: [15, 15, 15, 15]
            md_bg_color: root.icon_bg
            size_hint: None, None
            size: "110dp", "85dp"
            pos_hint: {'center_x': 0.5, 'center_y': 0.65}
            
            MDIcon:
                icon: root.icon_name
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                font_size: "38sp"
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                halign: 'center'
                
        MDLabel:
            text: root.cat_name
            font_size: "15sp"
            bold: True
            halign: 'center'
            pos_hint: {'center_x': 0.5, 'center_y': 0.25}
            
        MDLabel:
            text: root.cat_spent
            font_size: "13sp"
            halign: 'center'
            theme_text_color: "Secondary"
            pos_hint: {'center_x': 0.5, 'center_y': 0.10}

<ExpenseRowItem>:
    size_hint: 1, None
    height: "75dp"
    radius: [15, 15, 15, 15]
    elevation: 1
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True

    MDFloatLayout:
        MDLabel:
            text: root.desc_text
            font_size: "16sp"
            bold: True
            pos_hint: {'x': 0.05, 'center_y': 0.65}
            
        MDLabel:
            text: root.date_text
            font_size: "13sp"
            theme_text_color: "Secondary"
            pos_hint: {'x': 0.05, 'center_y': 0.28}
            
        MDLabel:
            text: root.amount_text
            font_size: "18sp"
            bold: True
            halign: "right"
            pos_hint: {'right': 0.95, 'center_y': 0.5}
            theme_text_color: "Custom"
            text_color: 0.9, 0.2, 0.2, 1

<MainScreen>:
    MDFloatLayout:
        MDCard:
            md_bg_color: 1, 0.663, 0.3, 1
            elevation: 2
            radius: [80, 5, 80, 5] 
            size_hint: 0.95, 0.65
            pos_hint: {'center_x': 0.5, 'center_y': 0.35}
        
        MDCard:
            orientation: 'vertical'
            padding: "15dp"
            spacing: "5dp"
            pos_hint: {'center_x': 0.5, 'center_y': 0.75}
            md_bg_color: 0, 0.937, 1, 1 
            elevation: 3
            radius: [40, 40, 40, 40]
            size_hint: 0.88, 0.22
            
            MDFloatLayout:
                MDLabel:
                    text: 'Spent / Budget'
                    font_size: '18sp'
                    bold: True
                    halign: 'center'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.75}
                
                MDIconButton:
                    icon: 'pencil-circle'
                    font_size: '28sp'
                    theme_text_color: 'Custom'
                    text_color: 0, 0.4, 0.8, 1
                    pos_hint: {'right': 0.98, 'center_y': 0.75}
                    on_release: app.change_screen('balance_screen', 'left')
                
                MDLabel:
                    id: total_balance_label
                    text: 'Loading...'
                    font_size: '22sp'
                    italic: True
                    bold: True
                    halign: 'center'
                    pos_hint: {'center_x': 0.5, 'center_y': 0.28}
        
        ScrollView:
            do_scroll_x: True
            do_scroll_y: False 
            pos_hint: {'center_x': 0.5, 'center_y': 0.22} 
            size_hint: 0.95, None
            height: "190dp"
            bar_color: 0, 0, 0, 0
            bar_inactive_color: 0, 0, 0, 0
            
            GridLayout:
                id: scroll
                rows: 1 
                padding: "10dp"
                spacing: "15dp"
                size_hint_x: None
                size_hint_y: None
                height: self.parent.height
                width: self.minimum_width
        
        MDFloatingActionButton:
            icon: 'plus'
            md_bg_color: 0.2, 0.6, 1, 1
            text_color: 1, 1, 1, 1
            elevation: 4
            pos_hint: {'center_x': 0.5, 'center_y': 0.07}
            on_release: app.change_screen('add_expense_screen', 'left')

<BalanceScreen>:
    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.96, 1
        
        MDFloatLayout:
            size_hint: 1, 0.12
            pos_hint: {'top': 1}
            md_bg_color: 0, 0.8, 0.9, 1
            
            MDIconButton:
                icon: 'arrow-left'
                pos_hint: {'center_y': 0.5, 'x': 0.03}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.change_screen('main_screen', 'right')
                
            MDLabel:
                text: 'Set Budget'
                font_size: '22sp'
                bold: True
                halign: 'center'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
        
        MDCard:
            orientation: 'vertical'
            padding: "25dp"
            spacing: "20dp"
            size_hint: 0.88, 0.35
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
            radius: [20, 20, 20, 20]
            elevation: 3
            md_bg_color: 1, 1, 1, 1
            
            MDTextField:
                id: budget_input
                hint_text: "Total Budget Amount (₹)"
                input_filter: "float"
                mode: "rectangle"
                icon_left: "cash-multiple"
            
            MDFillRoundFlatButton:
                text: "SAVE BUDGET"
                font_size: "16sp"
                size_hint_x: 1
                md_bg_color: 0, 0.8, 0.9, 1
                on_release: app.save_budget()

<AddExpenseScreen>:
    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.96, 1
        
        MDFloatLayout:
            size_hint: 1, 0.12
            pos_hint: {'top': 1}
            md_bg_color: 0.2, 0.6, 1, 1
            
            MDIconButton:
                icon: 'arrow-left'
                pos_hint: {'center_y': 0.5, 'x': 0.03}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.change_screen('main_screen', 'right')
                
            MDLabel:
                text: 'Add Expense'
                font_size: '22sp'
                bold: True
                halign: 'center'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
        
        MDCard:
            orientation: 'vertical'
            padding: "25dp"
            spacing: "18dp"
            size_hint: 0.9, 0.62
            pos_hint: {'center_x': 0.5, 'center_y': 0.50}
            radius: [20, 20, 20, 20]
            elevation: 3
            md_bg_color: 1, 1, 1, 1
            
            MDFloatLayout:
                size_hint_y: None
                height: "60dp"
                
                MDTextField:
                    id: cat_field
                    hint_text: "Category / Type"
                    mode: "rectangle"
                    size_hint_x: 1
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                
                MDIconButton:
                    id: drop_button
                    icon: "chevron-down"
                    pos_hint: {'right': 0.98, 'center_y': 0.5}
                    on_release: app.open_category_dropdown(self)
            
            MDTextField:
                id: amount_field
                hint_text: "Amount (₹)"
                input_filter: "float"
                mode: "rectangle"
                icon_left: "currency-inr"
            
            MDTextField:
                id: desc_field
                hint_text: "Description (e.g. Filter Water Jar)"
                mode: "rectangle"
                icon_left: "text-box-outline"
            
            MDFillRoundFlatButton:
                text: "ADD EXPENSE"
                font_size: "16sp"
                size_hint_x: 1
                md_bg_color: 0.2, 0.6, 1, 1
                on_release: app.save_new_expense()

<CategoryScreen>:
    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.96, 1
        
        MDFloatLayout:
            size_hint: 1, 0.12
            pos_hint: {'top': 1}
            md_bg_color: 0.2, 0.6, 1, 1
            
            MDIconButton:
                icon: 'arrow-left'
                pos_hint: {'center_y': 0.5, 'x': 0.03}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.change_screen('main_screen', 'right')
                
            MDLabel:
                id: category_title
                text: 'Category Items'
                font_size: '22sp'
                bold: True
                halign: 'center'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
        
        ScrollView:
            pos_hint: {'top': 0.88}
            size_hint: 1, 0.88
            
            GridLayout:
                id: item_list
                cols: 1
                padding: "15dp"
                spacing: "12dp"
                size_hint_y: None
                height: self.minimum_height

<DetailScreen>:
    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.96, 1
        
        MDFloatLayout:
            size_hint: 1, 0.12
            pos_hint: {'top': 1}
            md_bg_color: 0.15, 0.15, 0.2, 1
            
            MDIconButton:
                icon: 'arrow-left'
                pos_hint: {'center_y': 0.5, 'x': 0.03}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                on_release: app.change_screen('category_screen', 'right')
                
            MDLabel:
                text: 'Transaction Details'
                font_size: '20sp'
                bold: True
                halign: 'center'
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
        
        MDCard:
            orientation: 'vertical'
            padding: "25dp"
            spacing: "15dp"
            size_hint: 0.88, 0.60
            pos_hint: {'center_x': 0.5, 'center_y': 0.48}
            radius: [25, 25, 25, 25]
            elevation: 3
            md_bg_color: 1, 1, 1, 1
            
            MDIcon:
                id: detail_icon
                icon: 'receipt'
                font_size: '55sp'
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: 0.2, 0.6, 1, 1
                
            MDLabel:
                id: detail_category
                text: 'Category'
                font_size: '18sp'
                halign: 'center'
                theme_text_color: 'Secondary'
                
            MDLabel:
                id: detail_amount
                text: '₹0.00'
                font_size: '28sp'
                bold: True
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: 0.9, 0.2, 0.2, 1
                
            MDLabel:
                id: detail_desc
                text: 'Description note'
                font_size: '16sp'
                halign: 'center'
                bold: True
                
            MDLabel:
                id: detail_date
                text: 'Date: 01 Jan, 2026'
                font_size: '14sp'
                halign: 'center'
                italic: True
            
            MDFillRoundFlatButton:
                text: "DELETE ENTRY"
                size_hint_x: 1
                md_bg_color: 0.9, 0.2, 0.2, 1
                on_release: app.delete_current_expense()
'''

class MainScreen(MDScreen): pass
class BalanceScreen(MDScreen): pass
class AddExpenseScreen(MDScreen): pass
class CategoryScreen(MDScreen): pass
class DetailScreen(MDScreen): pass


class MoneyTrack(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.dropdown_menu = None
        self.current_category = ""
        self.selected_expense_id = None

    def build(self):
        return Builder.load_string(kv)
    
    def on_start(self):
        self.async_load_dashboard()

    def async_load_dashboard(self):
        threading.Thread(target=self._fetch_dashboard_worker, daemon=True).start()

    def _fetch_dashboard_worker(self):
        total_spent, budget, categories = self.db.get_dashboard_data(DEFAULT_CATEGORIES)
        self._update_dashboard_ui(total_spent, budget, categories)

    @mainthread
    def _update_dashboard_ui(self, total_spent, budget, categories):
        main_screen = self.root.get_screen('main_screen')
        main_screen.ids.total_balance_label.text = f"₹ {total_spent:,.0f} / {budget:,.0f}"

        scroll_grid = main_screen.ids.scroll
        scroll_grid.clear_widgets()

        for cat_name, cat_total in categories:
            style = get_cat_style(cat_name)
            card = CategoryCardItem(
                cat_name=cat_name,
                cat_spent=f"₹ {float(cat_total):,.0f}",
                icon_name=style["icon"],
                icon_bg=style["color"]
            )
            card.bind(on_release=lambda instance, name=cat_name: self.open_category(name))
            scroll_grid.add_widget(card)

    def change_screen(self, screen_name, direction='left'):
        self.root.transition = SlideTransition(direction=direction, duration=0.2)
        self.root.current = screen_name

    def save_budget(self):
        screen = self.root.get_screen('balance_screen')
        amount_text = screen.ids.budget_input.text.strip()
        try:
            val = float(amount_text)
            if val > 0:
                threading.Thread(target=self._save_budget_worker, args=(val,), daemon=True).start()
                screen.ids.budget_input.text = ""
                self.change_screen('main_screen', 'right')
        except ValueError:
            pass

    def _save_budget_worker(self, val):
        self.db.update_budget(val)
        self.async_load_dashboard()

    def open_category_dropdown(self, caller):
        def _fetch_cats():
            _, _, cats = self.db.get_dashboard_data(DEFAULT_CATEGORIES)
            self._show_dropdown(caller, [c[0] for c in cats])
            
        threading.Thread(target=_fetch_cats, daemon=True).start()

    @mainthread
    def _show_dropdown(self, caller, cat_names):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": cat,
                "height": dp(48),
                "on_release": lambda x=cat: self.select_category_from_menu(x),
            } for cat in cat_names
        ]
        self.dropdown_menu = MDDropdownMenu(caller=caller, items=menu_items, width_mult=4, max_height=dp(200))
        self.dropdown_menu.open()

    def select_category_from_menu(self, cat_name):
        self.root.get_screen('add_expense_screen').ids.cat_field.text = cat_name
        if self.dropdown_menu:
            self.dropdown_menu.dismiss()

    def save_new_expense(self):
        screen = self.root.get_screen('add_expense_screen')
        cat = screen.ids.cat_field.text.strip()
        amt = screen.ids.amount_field.text.strip()
        desc = screen.ids.desc_field.text.strip()
        
        if cat and amt and desc:
            try:
                amt_val = float(amt)
                threading.Thread(target=self._save_expense_worker, args=(cat, amt_val, desc), daemon=True).start()
                screen.ids.cat_field.text = ""
                screen.ids.amount_field.text = ""
                screen.ids.desc_field.text = ""
                self.change_screen('main_screen', 'right')
            except ValueError:
                pass

    def _save_expense_worker(self, cat, amt, desc):
        self.db.add_expense(category=cat, amount=amt, description=desc)
        self.async_load_dashboard()

    def open_category(self, cat_name):
        self.current_category = cat_name
        cat_screen = self.root.get_screen('category_screen')
        cat_screen.ids.category_title.text = f"{cat_name.title()} Expenses"
        cat_screen.ids.item_list.clear_widgets()
        
        self.change_screen('category_screen', 'left')
        threading.Thread(target=self._load_category_records_worker, args=(cat_name,), daemon=True).start()

    def _load_category_records_worker(self, cat_name):
        records = self.db.get_expenses_by_category(cat_name)
        style = get_cat_style(cat_name)
        self._render_category_items(records, style, cat_name)

    @mainthread
    def _render_category_items(self, records, style, cat_name):
        cat_screen = self.root.get_screen('category_screen')
        item_grid = cat_screen.ids.item_list
        item_grid.clear_widgets()

        if not records:
            empty_card = MDCard(size_hint=(1, None), height=dp(100), radius=[15], elevation=0, md_bg_color=(1, 1, 1, 0.8))
            empty_card.add_widget(MDLabel(text=f"No transactions found for {cat_name}!", halign="center", font_size="16sp", italic=True))
            item_grid.add_widget(empty_card)
        else:
            for rec in records:
                item_card = ExpenseRowItem(
                    desc_text=str(rec[3]),
                    date_text=str(rec[4]),
                    amount_text=f"₹ {float(rec[2]):,.0f}"
                )
                item_card.bind(on_release=lambda instance, r=rec, s=style: self.open_details(r, s))
                item_grid.add_widget(item_card)

    def open_details(self, record, style):
        try:
            self.selected_expense_id = int(record[0])
            det_screen = self.root.get_screen('detail_screen')
            det_screen.ids.detail_icon.icon = style["icon"]
            det_screen.ids.detail_icon.text_color = style["color"]
            det_screen.ids.detail_category.text = f"Category: {record[1]}"
            det_screen.ids.detail_amount.text = f"₹{float(record[2]):,.2f}"
            det_screen.ids.detail_desc.text = f"Note: {record[3]}"
            det_screen.ids.detail_date.text = f"Date: {record[4]}"
            
            self.change_screen('detail_screen', 'left')
        except Exception as e:
            print(f"Error opening details: {e}")

    def delete_current_expense(self):
        if self.selected_expense_id:
            def _delete_worker():
                self.db.delete_expense(self.selected_expense_id)
                self.async_load_dashboard()
                self._load_category_records_worker(self.current_category)
            
            threading.Thread(target=_delete_worker, daemon=True).start()
            self.change_screen('category_screen', 'right')


if __name__ == '__main__':
    MoneyTrack().run()