#bakery odering program
#members: Long, Josh, Huyhuy, Kelvin, Steven
#date: 2024/03/20

import tkinter as tk
from tkinter import ttk, messagebox
from array import array
from datetime import datetime


# domain classes

class Product:
    def __init__(self, pid: str, name: str, price: float, category: str):
        self.id = pid
        self.name = name
        self.price = float(price)
        self.category = category

    def __str__(self):
        return f"{self.name} (${self.price:.2f})"

class OrderItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = int(quantity)

    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = ${self.line_total():.2f}"

class Order:
    def __init__(self):
        self.items = []  # list of OrderItem

    def add_item(self, item: OrderItem):
        # if same product exists, increase quantity
        for it in self.items:
            if it.product.id == item.product.id:
                it.quantity += item.quantity
                return
        self.items.append(item)

    def total(self):
        return sum(it.line_total() for it in self.items)

    def clear(self):
        self.items = []

    def receipt_text(self):
        lines = []
        lines.append("Local Bakery Receipt")
        lines.append("------------------------------")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        for it in self.items:
            lines.append(f"{it.product.name:<20} {it.quantity:>2}  ${it.line_total():.2f}")
        lines.append("")
        lines.append(f"TOTAL: ${self.total():.2f}")
        return "\n".join(lines)


# inventory (kho luu tru hang hoa)

class InventoryManager:
    def __init__(self):
        # categories as tuple
        self.categories = ("Bread", "Pastry", "Drink")
        # initial product list (list of Product)
        self.product_list = [
            Product("P001", "Sourdough Loaf", 5.00, "Bread"),
            Product("P002", "Whole Wheat", 4.50, "Bread"),
            Product("P003", "Croissant", 2.50, "Pastry"),
            Product("P004", "Chocolate Muffin", 2.75, "Pastry"),
            Product("P005", "Coffee (12oz)", 1.75, "Drink"),
            Product("P006", "Tea (12oz)", 1.50, "Drink"),
        ]
        # dict mapping id->Product
        self.products = {p.id: p for p in self.product_list}
        # stock quantities stored in an array ('i' for signed int)
        # parallel to product_list order
        initial_stocks = [10, 8, 20, 12, 30, 30]
        self.stock = array('i', initial_stocks)

    def get_product_by_id(self, pid):
        return self.products.get(pid)

    def list_products(self):
        return self.product_list  # returns list

    def get_stock_for_index(self, idx):
        return self.stock[idx]

    def decrement_stock(self, product_idx, qty):
        if self.stock[product_idx] >= qty:
            self.stock[product_idx] -= qty
            return True
        return False

    def find_index_by_product_id(self, pid):
        for idx, p in enumerate(self.product_list):
            if p.id == pid:
                return idx
        return None


# GUI (giao dien nguoi dung)

class BakeryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Local Bakery Ordering System")
        self.geometry("750x420")
        self.resizable(False, False)

        self.inventory = InventoryManager()
        self.order = Order()

        self.create_widgets()
        self.refresh_product_list()

    def create_widgets(self):
        # Left frame: products
        left = ttk.Frame(self, padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        ttk.Label(left, text="Products").pack(anchor=tk.W)
        self.product_tree = ttk.Treeview(left, columns=("Price", "Category", "Stock"), show='headings', height=12)
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.heading("Stock", text="Stock")
        self.product_tree.column("Price", width=80, anchor=tk.CENTER)
        self.product_tree.column("Category", width=100, anchor=tk.W)
        self.product_tree.column("Stock", width=60, anchor=tk.CENTER)
        self.product_tree.pack()

        # quantity and add button
        bottom_left = ttk.Frame(left, padding=(0,10,0,0))
        bottom_left.pack(fill=tk.X)
        ttk.Label(bottom_left, text="Quantity:").pack(side=tk.LEFT)
        self.qty_spin = tk.Spinbox(bottom_left, from_=1, to=20, width=5)
        self.qty_spin.pack(side=tk.LEFT, padx=(5,10))
        ttk.Button(bottom_left, text="Add to Cart", command=self.add_to_cart).pack(side=tk.LEFT)

        # Right frame: cart & actions
        right = ttk.Frame(self, padding=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Cart").pack(anchor=tk.W)
        self.cart_listbox = tk.Listbox(right, height=12, width=40)
        self.cart_listbox.pack()

        # action buttons
        actions = ttk.Frame(right, padding=(0,10,0,0))
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT)
        ttk.Button(actions, text="Checkout", command=self.checkout).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Print Receipt", command=self.print_receipt).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=5)

        # receipt area
        ttk.Label(right, text="Receipt / Messages").pack(anchor=tk.W, pady=(10,0))
        self.text = tk.Text(right, height=10, width=50)
        self.text.pack()

    def refresh_product_list(self):
        # clear tree
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        # insert products with current stock
        for idx, p in enumerate(self.inventory.list_products()):
            stock = self.inventory.get_stock_for_index(idx)
            self.product_tree.insert("", "end", iid=p.id, values=(f"${p.price:.2f}", p.category, stock), text=p.name)

    def add_to_cart(self):
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a product to add.")
            return
        pid = sel[0]
        product = self.inventory.get_product_by_id(pid)
        qty = int(self.qty_spin.get())
        idx = self.inventory.find_index_by_product_id(pid)
        if idx is None:
            messagebox.showerror("Error", "Product not found.")
            return
        if self.inventory.get_stock_for_index(idx) < qty:
            messagebox.showerror("Out of stock", f"Only {self.inventory.get_stock_for_index(idx)} available.")
            return
        self.order.add_item(OrderItem(product, qty))
        self.refresh_cart_display()
        self.text.insert(tk.END, f"Added {qty} x {product.name}\n")
        self.text.see(tk.END)

    def refresh_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        for it in self.order.items:
            self.cart_listbox.insert(tk.END, str(it))
        if not self.order.items:
            self.cart_listbox.insert(tk.END, "(cart is empty)")

    def remove_selected(self):
        sel = self.cart_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select item", "Select an item in the cart to remove.")
            return
        idx = sel[0]
        if idx >= len(self.order.items):
            return
        del self.order.items[idx]
        self.refresh_cart_display()
        self.text.insert(tk.END, "Removed item from cart.\n")
        self.text.see(tk.END)

    def clear_cart(self):
        self.order.clear()
        self.refresh_cart_display()
        self.text.insert(tk.END, "Cart cleared.\n")
        self.text.see(tk.END)

    def checkout(self):
        if not self.order.items:
            messagebox.showinfo("Empty Cart", "Cart is empty — add items before checkout.")
            return
        # attempt to decrement stock for each order item
        # ensure all quantities are available before committing   #Josh suggested change
        # we'll use indexes from inventory
        needed = []
        for it in self.order.items:
            idx = self.inventory.find_index_by_product_id(it.product.id)
            if idx is None or self.inventory.get_stock_for_index(idx) < it.quantity:
                messagebox.showerror("Stock Error", f"Not enough stock for {it.product.name}.")
                return
            needed.append((idx, it.quantity))
        # commit
        for idx, q in needed:
            self.inventory.decrement_stock(idx, q)
        total = self.order.total()
        self.text.insert(tk.END, f"Checkout successful. Total = ${total:.2f}\n")
        self.text.insert(tk.END, "Inventory updated.\n")
        # show receipt automatically in text area
        self.text.insert(tk.END, "\n" + self.order.receipt_text() + "\n\n")
        self.order.clear()
        self.refresh_cart_display()
        self.refresh_product_list()

    def print_receipt(self):
        if not self.order.items:
            messagebox.showinfo("No items", "No items in cart to print receipt for.")
            return
        receipt = self.order.receipt_text()
        messagebox.showinfo("Receipt", receipt)

if __name__ == "__main__":
    app = BakeryApp()
    app.mainloop()
