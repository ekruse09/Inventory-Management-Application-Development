# ui.py

'''
# TODO
1. Headers dissapear when entries are made (pushed upwards)
2. Input validation for create order
3. Text display for too long names, etc -> expand ability
3. Button dispaly for create order, edit/delete order, mark delivered, restore item
4. Functionality for edit/delete order, mark delivered, restore item

5. Account Functionality
5. Loading on Phone

6. Import Excel File 
7. BOM Import
8. Reciept Import
9. Barcode Scanner
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from database import SessionLocal, Order, OnHand, Expended, OrderHistory
from kivy.uix.checkbox import CheckBox
from sqlalchemy.sql import func


# Connect to the SQLite database
session = SessionLocal()

class InventoryApp(App):

    # For App Creation
    def build(self):
        
        # ROOT
        root = BoxLayout(orientation='vertical', 
                         height=Window.height, 
                         width=Window.width)
        root.bind(height=lambda instance, value: setattr(instance, 'height', value))
        root.bind(width=lambda instance, value: setattr(instance, 'width', value))

        Window.clearcolor = (0.74, 0.83, 0.9, 1)  # Light blue background
        padding_percentage = 0.02


        # TOP SECTION
        logo_section = BoxLayout(orientation='horizontal', 
                                size_hint=(1, 2/10), 
                                padding=dp(Window.width * padding_percentage))
        logo_section.bind(padding=lambda instance, value: setattr(instance, 'padding', dp(Window.width * padding_percentage)))
        
        # Outer Rectangle
        with logo_section.canvas.before:
            Color(0.3, 0.4, 0.6, 1)  # Darker blue background
            self.rect = Rectangle(size=logo_section.size, 
                                  pos=logo_section.pos)
            logo_section.bind(size=lambda instance, _: setattr(self.rect, 'size', instance.size))
            logo_section.bind(pos=lambda instance, _: setattr(self.rect, 'pos', instance.pos))

        # Inner Rectangle
        with logo_section.canvas.before:
            Color(1, 1, 1, 1)  # White color
            self.rect2 = Rectangle(size=(logo_section.width - 2 * logo_section.padding[0], logo_section.height - 2 * logo_section.padding[0]),
                                pos=(logo_section.x + logo_section.padding[0], logo_section.y + logo_section.padding[0]))
            logo_section.bind(size=lambda instance, _: setattr(self.rect2, 'size', (instance.width - 2 * logo_section.padding[0], instance.height - 2 * logo_section.padding[0])))
            logo_section.bind(pos=lambda instance, _: setattr(self.rect2, 'pos', (instance.x + logo_section.padding[0], instance.y + logo_section.padding[0])))
        
        logo = Image(source='fliteway_logo.gif',
                     keep_ratio=True,
                     pos_hint={'center_y': 0.5},
                     size_hint=(1, 1),
                     anim_delay=0.04,
                     anim_loop=1)
        logo_section.add_widget(logo)

        root.add_widget(logo_section)


        # MIDDLE SECTION
        action_section = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 1/10), 
                                   padding=dp(Window.width * padding_percentage))

        place_order_button = Button(text='Place Order', on_press=self.create_order_popup)
        mark_delivered_button = Button(text='Mark Delivered', on_press=self.mark_delivered)
        expend_item_button = Button(text='Expend Item', on_press=self.use_item)

        action_section.add_widget(place_order_button)
        action_section.add_widget(mark_delivered_button)
        action_section.add_widget(expend_item_button)

        root.add_widget(action_section)


        # BOTTOM SECTION
        data_section = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 7/10), 
                                   padding=dp(Window.width * padding_percentage))

        self.tabbed_panel = TabbedPanel(do_default_tab=False, size_hint=(1, 1))

        for sheet_name in ['Order History', 'Orders', 'On Hand', 'Expended']:
            tab = TabbedPanelItem(text=sheet_name)
            
            scroll_view = ScrollView(size_hint=(1, 1))
            content_layout = BoxLayout(orientation='horizontal', size_hint=(1,1))

            scroll_view.add_widget(content_layout)

            tab.content = scroll_view
            self.tabbed_panel.add_widget(tab)
        
        data_section.add_widget(self.tabbed_panel)
        root.add_widget(data_section)

        self.tabbed_panel.bind(current_tab=self.on_tab_switch)

        return root



    # UI Helper Methods
    # Populate the initial grid for the first tab
    def on_start(self):
        self.switch_sheet(self.tabbed_panel.tab_list[3].text)

    def on_tab_switch(self, instance, value):
        self.switch_sheet(value.text)

    def populate_grid(self, sheet_name):
            
            if sheet_name == 'Order History':
                headers = ['Part Number', 'Description', 'Manufacturer', 'Quantity', 'Total Price', 'Order Notes', 'Repurchase Link', 'Order Date', 'Ordered By']
                order_history_items = session.query(OrderHistory).all()
                session.close()
            elif sheet_name == 'Orders':
                headers = ['Part Number', 'Description', 'Manufacturer', 'Quantity', 'Total Price', 'Order Notes', 'Order Location', 'Order Date', 'Ordered By']
                order_items = session.query(Order).all()
                session.close()
            elif sheet_name == 'On Hand':
                headers = ['Part Number', 'Description', 'Manufacturer', 'Quantity', 'Price Per Unit', 'Location', 'Inventory Notes', 'Updated On', 'Updated By']
                on_hand_items = session.query(OnHand).all()
                session.close()
            elif sheet_name == 'Expended':
                headers = ['Part Number', 'Description', 'Manufacturer', 'Quantity', 'Total Price', 'Project', 'Usage Notes', 'Usage Date', 'Updated By']
                expended_items = session.query(Expended).all()
                session.close()

            cols = len(headers)
            grid = GridLayout(cols=cols, spacing=10, size_hint_y=1/10)
            grid.bind(minimum_height=grid.setter('height'))

            for header_text in headers:
                header = Label(text=header_text, bold=True, size_hint_y=1/10, valign='middle', halign='center')
                header.bind(size=header.setter('text_size'))  # Ensure text is centered

                grid.add_widget(header)
            
            if sheet_name == 'Orders History':
                for item in order_history_items:
                    grid.add_widget(Label(text=item.part_number))
                    grid.add_widget(Label(text=item.description))
                    grid.add_widget(Label(text=item.manufacturer))
                    grid.add_widget(Label(text=str(item.quantity)))
                    grid.add_widget(Label(text=str(item.total_price)))
                    grid.add_widget(Label(text=item.order_notes))
                    grid.add_widget(Label(text=item.purchase_link))
                    grid.add_widget(Label(text=item.order_location))
                    grid.add_widget(Label(text=str(item.order_date)))
                    grid.add_widget(Label(text=str(item.ordered_by)))

            elif sheet_name == 'Orders':
                for item in order_items:
                    grid.add_widget(Label(text=item.part_number))
                    grid.add_widget(Label(text=item.description))
                    grid.add_widget(Label(text=item.manufacturer))
                    grid.add_widget(Label(text=str(item.quantity)))
                    grid.add_widget(Label(text=str(item.total_price)))
                    grid.add_widget(Label(text=item.order_notes))
                    grid.add_widget(Label(text=item.order_location))
                    grid.add_widget(Label(text=str(item.order_date)))
                    grid.add_widget(Label(text=item.ordered_by))

            elif sheet_name == 'On Hand':
                for item in on_hand_items:
                    grid.add_widget(Label(text=item.part_number))
                    grid.add_widget(Label(text=item.description))
                    grid.add_widget(Label(text=item.manufacturer))
                    grid.add_widget(Label(text=str(item.quantity)))
                    grid.add_widget(Label(text=str(item.price_per_unit)))
                    grid.add_widget(Label(text=item.location))
                    grid.add_widget(Label(text=item.inventory_notes))
                    grid.add_widget(Label(text=str(item.updated_on)))
                    grid.add_widget(Label(text=item.updated_by))
            
            elif sheet_name == 'Expended':
                for item in expended_items:
                    grid.add_widget(Label(text=item.part_number))
                    grid.add_widget(Label(text=item.description))
                    grid.add_widget(Label(text=item.manufacturer))
                    grid.add_widget(Label(text=str(item.quantity)))
                    grid.add_widget(Label(text=str(item.total_price)))
                    grid.add_widget(Label(text=item.project))
                    grid.add_widget(Label(text=item.usage_notes))
                    grid.add_widget(Label(text=str(item.usage_date)))
                    grid.add_widget(Label(text=item.updated_by))

            return grid

    # Update the currently displayed tab text
    def switch_sheet(self, sheet_name):
        self.tabbed_panel.current_tab.text = sheet_name
        
        grid = self.populate_grid(sheet_name)

        # Check if the current_tab's content exists and is a layout where we can add widgets
        if self.tabbed_panel.current_tab.content:
            # Clear existing content of the tab
            self.tabbed_panel.current_tab.content.clear_widgets()
            # Add the new grid to the tab's content
            self.tabbed_panel.current_tab.content.add_widget(grid)
        else:
            # If content does not exist or is not set properly, create a new BoxLayout for content
            content_layout = BoxLayout(orientation='vertical')
            content_layout.add_widget(grid)
            self.tabbed_panel.current_tab.content = content_layout
            self.tabbed_panel.current_tab.add_widget(content_layout)


    # Database Access Methods (Read/Write)
    def create_order_popup(self, instance):
        session = SessionLocal()

        popup_layout = BoxLayout(orientation='vertical', padding=10)
        part_number_input = TextInput(hint_text='Part Number')
        description_input = TextInput(hint_text='Part Description')
        manufacturer_input = TextInput(hint_text='Part Manufacturer')
        quantity_input = TextInput(hint_text='Quantity', input_filter='int')
        total_price_input = TextInput(hint_text='Total Price', input_filter='float')
        order_location_input = TextInput(hint_text='Order Location')
        order_notes_input = TextInput(hint_text='Order Notes')
        link_input = TextInput(hint_text='Link')

        submit_button = Button(text='Submit', on_press=lambda x: self.submit_order(part_number=part_number_input.text, description=description_input.text, manufacturer=manufacturer_input.text, quantity=quantity_input.text, total_price=total_price_input.text, order_date=func.date(func.now()), order_location=order_location_input.text, order_notes=order_notes_input.text, link=link_input.text, ordered_by="")) 
        close_button = Button(text='Close', on_press=lambda x: self.order_popup.dismiss())
        
        popup_layout.add_widget(part_number_input)
        popup_layout.add_widget(description_input)
        popup_layout.add_widget(manufacturer_input)
        popup_layout.add_widget(quantity_input)
        popup_layout.add_widget(total_price_input)
        popup_layout.add_widget(order_location_input)
        popup_layout.add_widget(order_notes_input)
        popup_layout.add_widget(link_input)

        popup_layout.add_widget(submit_button)
        popup_layout.add_widget(close_button)
        
        self.order_popup = Popup(title='Create Order', content=popup_layout, size_hint=(0.8, 0.8))
        self.order_popup.open()

    def submit_order(self, part_number, description, manufacturer, quantity, total_price, order_date, order_location, order_notes, link, ordered_by):
        # Start a new database session
        session = SessionLocal()

        try:
            Order.create_order(cls=Order, session=session, part_number=part_number, description=description, manufacturer=manufacturer, quantity=quantity, total_price=total_price, ordered_by=ordered_by, order_date=order_date, order_location=order_location, order_notes=order_notes, purchase_link=link)

        except Exception as e:
            # Rollback the session in case of error
            session.rollback()
            print(f"Error: {e}")

        finally:
            # Close the session
            session.close()

        # Dismiss the order popup and switch to the 'Orders' sheet
        self.order_popup.dismiss()
        self.switch_sheet('Orders')



    def mark_delivered(self, instance):
        pass
        '''
        orders = session.query(Order).all()

        popup_layout = BoxLayout(orientation='vertical', padding=10)
        orders_layout = BoxLayout(orientation='vertical', spacing=10)
        submit_button = Button(text='Mark Delivered', on_press=lambda x: self.submit_mark_delivered(orders_layout))
        close_button = Button(text='Close', on_press=lambda x: self.delivered_popup.dismiss())

        for order in orders:
            checkbox = CheckBox(group='orders', size_hint_y=None, height=dp(30))
            checkbox.order_id = order.id  # Attach order id to checkbox for reference
            checkbox_label = Label(text=f'Order ID: {order.id}, Location: {order.order_location}')
            orders_layout.add_widget(BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), children=[checkbox, checkbox_label]))

        scroll_view = ScrollView()
        scroll_view.add_widget(orders_layout)

        popup_layout.add_widget(scroll_view)
        popup_layout.add_widget(submit_button)
        popup_layout.add_widget(close_button)

        self.delivered_popup = Popup(title='Mark Delivered', content=popup_layout, size_hint=(0.8, 0.8))
        self.delivered_popup.open()

    def submit_mark_delivered(self, orders_layout):
        for child in orders_layout.children:
            if isinstance(child, BoxLayout):
                checkbox = child.children[0]  # Assuming the checkbox is the first widget in the BoxLayout
                if checkbox.active:
                    order_id = checkbox.order_id
                    order = session.query(Order).filter(Order.id == order_id).first()
                    if order:
                        # Update order status to delivered in the database
                        order.status = 'delivered'
                        session.commit()

        self.delivered_popup.dismiss()
        self.switch_sheet('Orders')
        '''
    def use_item(self, instance):
        pass
        '''
        on_hand_items = session.query(OnHand).all()

        popup_layout = BoxLayout(orientation='vertical', padding=10)
        items_layout = BoxLayout(orientation='vertical', spacing=10)
        submit_button = Button(text='Use Item', on_press=lambda x: self.submit_use_item(items_layout))
        close_button = Button(text='Close', on_press=lambda x: self.use_item_popup.dismiss())

        for item in on_hand_items:
            checkbox = CheckBox(group='items', size_hint_y=None, height=dp(30))
            checkbox.item_id = item.id  # Attach item id to checkbox for reference
            checkbox_label = Label(text=f'Part Number: {item.item.part_number}, Description: {item.item.description}')
            items_layout.add_widget(BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), children=[checkbox, checkbox_label]))

        scroll_view = ScrollView()
        scroll_view.add_widget(items_layout)

        popup_layout.add_widget(scroll_view)
        popup_layout.add_widget(submit_button)
        popup_layout.add_widget(close_button)

        self.use_item_popup = Popup(title='Use Item', content=popup_layout, size_hint=(0.8, 0.8))
        self.use_item_popup.open()

    def submit_use_item(self, items_layout):
        for child in items_layout.children:
            if isinstance(child, BoxLayout):
                checkbox = child.children[0]  # Assuming the checkbox is the first widget in the BoxLayout
                if checkbox.active:
                    item_id = checkbox.item_id
                    on_hand_item = session.query(OnHand).filter(OnHand.id == item_id).first()
                    if on_hand_item:
                        # Implement logic to use the item and mark as expended in the database
                        try:
                            on_hand_item.decrement_quantity(session, quantity=1, updated_by='user', usage_notes='Used in production')
                        except ValueError as e:
                            print(f"Error: {str(e)}")
                            # Handle error or display message if necessary

        self.use_item_popup.dismiss()
        self.switch_sheet('On Hand')
        '''
# Entry point to run the application
if __name__ == '__main__':
    InventoryApp().run()
