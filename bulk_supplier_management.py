import pandas as pd
import os
import re
from datetime import datetime
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import plotext as plt

# ------------------- Input Validation Functions -------------------
def is_valid_contact(contact):
    """Validate email or phone number format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^\+?1?\d{10,15}$'
    return bool(re.match(email_pattern, contact) or re.match(phone_pattern, contact))

def is_non_empty_string(value):
    """Check if a string is non-empty after stripping whitespace."""
    return bool(value.strip())

def is_positive_number(value):
    """Check if a value is a positive number."""
    return isinstance(value, (int, float)) and value > 0

# ------------------- Supplier Class -------------------
class Supplier:
    def __init__(self, supplier_id, name, location, contact_info):
        self.supplier_id = supplier_id
        self.name = name
        self.location = location
        self.contact_info = contact_info

    def to_dict(self):
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "location": self.location,
            "contact_info": self.contact_info
        }

    @staticmethod
    def from_dict(data):
        return Supplier(
            data["supplier_id"],
            data["name"],
            data["location"],
            data["contact_info"]
        )

# ------------------- Supplier Manager Class -------------------
class SupplierManager:
    FILE_PATH = "suppliers.csv"

    @staticmethod
    def load_suppliers():
        try:
            if not os.path.exists(SupplierManager.FILE_PATH):
                return []
            df = pd.read_csv(SupplierManager.FILE_PATH)
            return [Supplier.from_dict(row) for _, row in df.iterrows()]
        except Exception as e:
            print(f"❌ Error reading suppliers file: {e}")
            return []

    @staticmethod
    def get_next_supplier_id():
        suppliers = SupplierManager.load_suppliers()
        if not suppliers:
            return "SUP001"
        last_id = suppliers[-1].supplier_id
        num = int(last_id.replace("SUP", ""))
        return f"SUP{num + 1:03d}"

    @staticmethod
    def save_supplier(supplier):
        try:
            df = pd.DataFrame([supplier.to_dict()])
            if not os.path.exists(SupplierManager.FILE_PATH):
                df.to_csv(SupplierManager.FILE_PATH, index=False)
            else:
                existing_df = pd.read_csv(SupplierManager.FILE_PATH)
                new_df = pd.concat([existing_df, df], ignore_index=True)
                new_df.to_csv(SupplierManager.FILE_PATH, index=False)
        except Exception as e:
            print(f"❌ Error saving supplier: {e}")

    @staticmethod
    def update_supplier(supplier_id, updated_supplier):
        try:
            df = pd.read_csv(SupplierManager.FILE_PATH)
            if supplier_id not in df["supplier_id"].values:
                return False
            df.loc[df["supplier_id"] == supplier_id, ["name", "location", "contact_info"]] = [
                updated_supplier.name, updated_supplier.location, updated_supplier.contact_info
            ]
            df.to_csv(SupplierManager.FILE_PATH, index=False)
            return True
        except Exception as e:
            print(f"❌ Error updating supplier: {e}")
            return False

    @staticmethod
    def delete_supplier(supplier_id):
        try:
            # Check for dependencies
            products_df = pd.read_csv(ProductManager.FILE_PATH) if os.path.exists(ProductManager.FILE_PATH) else pd.DataFrame()
            orders_df = pd.read_csv(OrderManager.FILE_PATH) if os.path.exists(OrderManager.FILE_PATH) else pd.DataFrame()
            if not products_df.empty and supplier_id in products_df["supplier_id"].values:
                return False, "Cannot delete supplier with associated products."
            if not orders_df.empty and supplier_id in orders_df["supplier_id"].values:
                return False, "Cannot delete supplier with associated orders."
            
            df = pd.read_csv(SupplierManager.FILE_PATH)
            if supplier_id not in df["supplier_id"].values:
                return False, "Supplier ID not found."
            df = df[df["supplier_id"] != supplier_id]
            df.to_csv(SupplierManager.FILE_PATH, index=False)
            return True, "Supplier deleted successfully."
        except Exception as e:
            return False, f"Error deleting supplier: {e}"

    @staticmethod
    def is_valid_supplier_id(supplier_id):
        suppliers = SupplierManager.load_suppliers()
        return any(s.supplier_id == supplier_id for s in suppliers)

    @staticmethod
    def search_suppliers(search_term):
        suppliers = SupplierManager.load_suppliers()
        return [
            s for s in suppliers
            if search_term.lower() in s.name.lower() or search_term.lower() in s.location.lower()
        ]

# ------------------- Product Class -------------------
class Product:
    def __init__(self, product_id, name, sku, cost_per_unit, moq, available_qty, supplier_id):
        self.product_id = product_id
        self.name = name
        self.sku = sku
        self.cost_per_unit = cost_per_unit
        self.moq = moq
        self.available_qty = available_qty
        self.supplier_id = supplier_id

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "sku": self.sku,
            "cost_per_unit": self.cost_per_unit,
            "moq": self.moq,
            "available_qty": self.available_qty,
            "supplier_id": self.supplier_id
        }

    @staticmethod
    def from_dict(data):
        return Product(
            data["product_id"],
            data["name"],
            data["sku"],
            data["cost_per_unit"],
            data["moq"],
            data["available_qty"],
            data["supplier_id"]
        )

# ------------------- Product Manager Class -------------------
class ProductManager:
    FILE_PATH = "products.csv"

    @staticmethod
    def load_products():
        try:
            if not os.path.exists(ProductManager.FILE_PATH):
                return []
            df = pd.read_csv(ProductManager.FILE_PATH)
            return [Product.from_dict(row) for _, row in df.iterrows()]
        except Exception as e:
            print(f"❌ Error reading products file: {e}")
            return []

    @staticmethod
    def get_next_product_id():
        products = ProductManager.load_products()
        if not products:
            return "PROD001"
        last_id = products[-1].product_id
        num = int(last_id.replace("PROD", ""))
        return f"PROD{num + 1:03d}"

    @staticmethod
    def save_product(product):
        try:
            df = pd.DataFrame([product.to_dict()])
            if not os.path.exists(ProductManager.FILE_PATH):
                df.to_csv(ProductManager.FILE_PATH, index=False)
            else:
                existing_df = pd.read_csv(ProductManager.FILE_PATH)
                new_df = pd.concat([existing_df, df], ignore_index=True)
                new_df.to_csv(ProductManager.FILE_PATH, index=False)
        except Exception as e:
            print(f"❌ Error saving product: {e}")

    @staticmethod
    def update_product(product_id, updated_product):
        try:
            df = pd.read_csv(ProductManager.FILE_PATH)
            if product_id not in df["product_id"].values:
                return False
            # Check SKU uniqueness, excluding current product
            if updated_product.sku != df.loc[df["product_id"] == product_id, "sku"].iloc[0]:
                if not ProductManager.is_unique_sku(updated_product.sku):
                    return False, "SKU already exists."
            df.loc[df["product_id"] == product_id, ["name", "sku", "cost_per_unit", "moq", "available_qty", "supplier_id"]] = [
                updated_product.name, updated_product.sku, updated_product.cost_per_unit,
                updated_product.moq, updated_product.available_qty, updated_product.supplier_id
            ]
            df.to_csv(ProductManager.FILE_PATH, index=False)
            return True, "Product updated successfully."
        except Exception as e:
            return False, f"Error updating product: {e}"

    @staticmethod
    def delete_product(product_id):
        try:
            # Check for dependencies
            orders_df = pd.read_csv(OrderManager.FILE_PATH) if os.path.exists(OrderManager.FILE_PATH) else pd.DataFrame()
            sales_df = pd.read_csv(SalesManager.FILE_PATH) if os.path.exists(SalesManager.FILE_PATH) else pd.DataFrame()
            if not orders_df.empty and product_id in orders_df["product_id"].values:
                return False, "Cannot delete product with associated orders."
            if not sales_df.empty and product_id in sales_df["product_id"].values:
                return False, "Cannot delete product with associated sales."
            
            df = pd.read_csv(ProductManager.FILE_PATH)
            if product_id not in df["product_id"].values:
                return False, "Product ID not found."
            df = df[df["product_id"] != product_id]
            df.to_csv(ProductManager.FILE_PATH, index=False)
            return True, "Product deleted successfully."
        except Exception as e:
            return False, f"Error deleting product: {e}"

    @staticmethod
    def is_valid_product_id(product_id):
        products = ProductManager.load_products()
        return any(p.product_id == product_id for p in products)

    @staticmethod
    def is_unique_sku(sku):
        products = ProductManager.load_products()
        return not any(p.sku == sku for p in products)

    @staticmethod
    def validate_order_quantity(product_id, quantity):
        products = ProductManager.load_products()
        product = next((p for p in products if p.product_id == product_id), None)
        if not product:
            return False, "Product not found."
        if not is_positive_number(quantity):
            return False, "Quantity must be a positive number."
        if quantity < product.moq:
            return False, f"Quantity must be at least {product.moq} (MOQ)."
        if quantity > product.available_qty:
            return False, f"Only {product.available_qty} units available."
        return True, ""

    @staticmethod
    def search_products(search_term):
        products = ProductManager.load_products()
        return [
            p for p in products
            if search_term.lower() in p.name.lower() or search_term.lower() in p.sku.lower()
        ]

    @staticmethod
    def get_low_stock_products(threshold=10):
        products = ProductManager.load_products()
        return [p for p in products if p.available_qty <= threshold]

    @staticmethod
    def update_product_quantity(product_id, quantity_change):
        try:
            df = pd.read_csv(ProductManager.FILE_PATH)
            if product_id not in df["product_id"].values:
                return False, "Product not found."
            current_qty = df.loc[df["product_id"] == product_id, "available_qty"].iloc[0]
            new_qty = current_qty + quantity_change
            if new_qty < 0:
                return False, f"Cannot reduce quantity below 0. Current quantity: {current_qty}."
            df.loc[df["product_id"] == product_id, "available_qty"] = new_qty
            df.to_csv(ProductManager.FILE_PATH, index=False)
            return True, f"Updated quantity to {new_qty}."
        except Exception as e:
            return False, f"Error updating product quantity: {e}"

# ------------------- Order Class -------------------
class Order:
    def __init__(self, order_id, product_id, supplier_id, quantity, total_cost, order_date, delivery_status):
        self.order_id = order_id
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.quantity = quantity
        self.total_cost = total_cost
        self.order_date = order_date
        self.delivery_status = delivery_status

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "product_id": self.product_id,
            "supplier_id": self.supplier_id,
            "quantity": self.quantity,
            "total_cost": self.total_cost,
            "order_date": self.order_date,
            "delivery_status": self.delivery_status
        }

    @staticmethod
    def from_dict(data):
        return Order(
            data["order_id"],
            data["product_id"],
            data["supplier_id"],
            data["quantity"],
            data["total_cost"],
            data["order_date"],
            data["delivery_status"]
        )

# ------------------- Order Manager Class -------------------
class OrderManager:
    FILE_PATH = "orders.csv"

    @staticmethod
    def load_orders():
        try:
            if not os.path.exists(OrderManager.FILE_PATH):
                return []
            df = pd.read_csv(OrderManager.FILE_PATH)
            return [Order.from_dict(row) for _, row in df.iterrows()]
        except Exception as e:
            print(f"❌ Error reading orders file: {e}")
            return []

    @staticmethod
    def get_next_order_id():
        orders = OrderManager.load_orders()
        if not orders:
            return "ORD001"
        last_id = orders[-1].order_id
        num = int(last_id.replace("ORD", ""))
        return f"ORD{num + 1:03d}"

    @staticmethod
    def save_order(order):
        try:
            df = pd.DataFrame([order.to_dict()])
            if not os.path.exists(OrderManager.FILE_PATH):
                df.to_csv(OrderManager.FILE_PATH, index=False)
            else:
                existing_df = pd.read_csv(OrderManager.FILE_PATH)
                new_df = pd.concat([existing_df, df], ignore_index=True)
                new_df.to_csv(OrderManager.FILE_PATH, index=False)
        except Exception as e:
            print(f"❌ Error saving order: {e}")

    @staticmethod
    def update_order_status(order_id, new_status):
        try:
            df = pd.read_csv(OrderManager.FILE_PATH)
            if order_id not in df["order_id"].values:
                return False, "Order ID not found."
            # If status changes to Delivered, update product quantity
            if new_status.lower() == "delivered":
                order = df[df["order_id"] == order_id]
                product_id = order["product_id"].iloc[0]
                quantity = order["quantity"].iloc[0]
                success, message = ProductManager.update_product_quantity(product_id, quantity)
                if not success:
                    return False, message
            df.loc[df["order_id"] == order_id, "delivery_status"] = new_status
            df.to_csv(OrderManager.FILE_PATH, index=False)
            return True, f"Order {order_id} status updated to {new_status}."
        except Exception as e:
            return False, f"Error updating order status: {e}"

    @staticmethod
    def delete_order(order_id):
        try:
            df = pd.read_csv(OrderManager.FILE_PATH)
            if order_id not in df["order_id"].values:
                return False, "Order ID not found."
            df = df[df["order_id"] != order_id]
            df.to_csv(OrderManager.FILE_PATH, index=False)
            return True, "Order deleted successfully."
        except Exception as e:
            return False, f"Error deleting order: {e}"

    @staticmethod
    def search_orders(search_term):
        orders = OrderManager.load_orders()
        return [
            o for o in orders
            if search_term.lower() in o.delivery_status.lower() or
               search_term.lower() in str(o.order_date)
        ]

    @staticmethod
    def get_order_summary_by_supplier():
        try:
            df = pd.read_csv(OrderManager.FILE_PATH)
            if df.empty:
                return []
            summary = df.groupby("supplier_id")["total_cost"].sum().reset_index()
            return summary.to_dict(orient="records")
        except Exception as e:
            print(f"❌ Error generating order summary: {e}")
            return []

# ------------------- Sale Class -------------------
class Sale:
    def __init__(self, sale_id, product_id, quantity_sold, sale_date):
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity_sold = quantity_sold
        self.sale_date = sale_date

    def to_dict(self):
        return {
            "sale_id": self.sale_id,
            "product_id": self.product_id,
            "quantity_sold": self.quantity_sold,
            "sale_date": self.sale_date
        }

    @staticmethod
    def from_dict(data):
        return Sale(
            data["sale_id"],
            data["product_id"],
            data["quantity_sold"],
            data["sale_date"]
        )

# ------------------- Sales Manager Class -------------------
class SalesManager:
    FILE_PATH = "sales.csv"

    @staticmethod
    def load_sales():
        try:
            if not os.path.exists(SalesManager.FILE_PATH):
                return []
            df = pd.read_csv(SalesManager.FILE_PATH)
            return [Sale.from_dict(row) for _, row in df.iterrows()]
        except Exception as e:
            print(f"❌ Error reading sales file: {e}")
            return []

    @staticmethod
    def get_next_sale_id():
        sales = SalesManager.load_sales()
        if not sales:
            return "SALE001"
        last_id = sales[-1].sale_id
        num = int(last_id.replace("SALE", ""))
        return f"SALE{num + 1:03d}"

    @staticmethod
    def save_sale(sale):
        try:
            df = pd.DataFrame([sale.to_dict()])
            if not os.path.exists(SalesManager.FILE_PATH):
                df.to_csv(SalesManager.FILE_PATH, index=False)
            else:
                existing_df = pd.read_csv(SalesManager.FILE_PATH)
                new_df = pd.concat([existing_df, df], ignore_index=True)
                new_df.to_csv(SalesManager.FILE_PATH, index=False)
        except Exception as e:
            print(f"❌ Error saving sale: {e}")

    @staticmethod
    def get_sales_summary():
        try:
            sales_df = pd.read_csv(SalesManager.FILE_PATH) if os.path.exists(SalesManager.FILE_PATH) else pd.DataFrame()
            products_df = pd.read_csv(ProductManager.FILE_PATH) if os.path.exists(ProductManager.FILE_PATH) else pd.DataFrame()
            if sales_df.empty or products_df.empty:
                return []
            summary = sales_df.groupby("product_id")["quantity_sold"].sum().reset_index()
            summary = summary.merge(products_df[["product_id", "name", "cost_per_unit"]], on="product_id", how="left")
            summary["total_revenue"] = summary["quantity_sold"] * summary["cost_per_unit"]
            return summary.to_dict(orient="records")
        except Exception as e:
            print(f"❌ Error generating sales summary: {e}")
            return []

    @staticmethod
    def get_product_sales(product_id):
        try:
            sales_df = pd.read_csv(SalesManager.FILE_PATH) if os.path.exists(SalesManager.FILE_PATH) else pd.DataFrame()
            if sales_df.empty or product_id not in sales_df["product_id"].values:
                return []
            product_sales = sales_df[sales_df["product_id"] == product_id]
            return [Sale.from_dict(row) for _, row in product_sales.iterrows()]
        except Exception as e:
            print(f"❌ Error retrieving product sales: {e}")
            return []

# ------------------- Report Generators -------------------
def generate_inventory_report():
    print("\n--- Generate Inventory Report ---")
    threshold = input("Enter low stock threshold (default 10): ")
    try:
        threshold = int(threshold) if threshold.strip() else 10
    except ValueError:
        print("❌ Invalid threshold. Using default (10).")
        threshold = 10

    # Get data
    low_stock_products = ProductManager.get_low_stock_products(threshold)
    order_summary = OrderManager.get_order_summary_by_supplier()
    sales_summary = SalesManager.get_sales_summary()
    
    # Create PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"inventory_report_{timestamp}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Inventory Report", styles['Title']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Low Stock Products
    elements.append(Paragraph(f"Low Stock Products (Threshold: {threshold})", styles['Heading2']))
    if not low_stock_products:
        elements.append(Paragraph("No low stock products.", styles['Normal']))
    else:
        data = [["ID", "Name", "SKU", "Available Qty", "Supplier ID"]]
        data += [[p.product_id, p.name, p.sku, p.available_qty, p.supplier_id] for p in low_stock_products]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Order Summary
    elements.append(Paragraph("Order Summary by Supplier", styles['Heading2']))
    if not order_summary:
        elements.append(Paragraph("No orders found.", styles['Normal']))
    else:
        data = [["Supplier ID", "Total Cost"]]
        data += [[s["supplier_id"], f"${s['total_cost']:.2f}"] for s in order_summary]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Sales Summary
    elements.append(Paragraph("Sales Summary by Product", styles['Heading2']))
    if not sales_summary:
        elements.append(Paragraph("No sales found.", styles['Normal']))
    else:
        data = [["Product ID", "Name", "Total Units Sold", "Total Revenue"]]
        data += [[s["product_id"], s["name"], s["quantity_sold"], f"${s['total_revenue']:.2f}"] for s in sales_summary]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

    try:
        doc.build(elements)
        print(f"✅ Report generated: {filename}\n")
    except Exception as e:
        print(f"❌ Error generating report: {e}\n")

def generate_product_sales_report():
    print("\n--- Generate Product Sales Report ---")
    product_id = input("Enter Product ID (e.g., PROD001): ")
    if not ProductManager.is_valid_product_id(product_id):
        print("❌ Product ID not found.")
        return

    # Get product name and cost per unit
    products_df = pd.read_csv(ProductManager.FILE_PATH) if os.path.exists(ProductManager.FILE_PATH) else pd.DataFrame()
    if products_df.empty or product_id not in products_df["product_id"].values:
        print("❌ Product data not found.")
        return
    product_name = products_df.loc[products_df["product_id"] == product_id, "name"].iloc[0]
    cost_per_unit = products_df.loc[products_df["product_id"] == product_id, "cost_per_unit"].iloc[0]
    
    # Get sales data
    product_sales = SalesManager.get_product_sales(product_id)
    
    # Create PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_sales_report_{product_id}_{timestamp}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"Product Sales Report: {product_name} ({product_id})", styles['Title']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Cost per Unit: ${cost_per_unit:.2f}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Sales Transactions
    if not product_sales:
        elements.append(Paragraph("No sales found for this product.", styles['Normal']))
    else:
        data = [["Sale ID", "Quantity Sold", "Sale Date", "Cost/Unit", "Total Revenue"]]
        total_revenue = 0
        for sale in product_sales:
            sale_revenue = sale.quantity_sold * cost_per_unit
            total_revenue += sale_revenue
            data.append([
                sale.sale_id,
                sale.quantity_sold,
                sale.sale_date,
                f"${cost_per_unit:.2f}",
                f"${sale_revenue:.2f}"
            ])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph(f"Total Revenue for {product_name}: ${total_revenue:.2f}", styles['Heading2']))

    try:
        doc.build(elements)
        print(f"✅ Report generated: {filename}\n")
    except Exception as e:
        print(f"❌ Error generating report: {e}\n")

# ------------------- Chart Generator -------------------
def plot_order_summary():
    print("\n--- Order Summary Chart ---")
    summary = OrderManager.get_order_summary_by_supplier()
    if not summary:
        print("No orders found for chart.\n")
        return

    supplier_ids = [s["supplier_id"] for s in summary]
    total_costs = [s["total_cost"] for s in summary]

    plt.bar(supplier_ids, total_costs, orientation='vertical')
    plt.title("Total Order Costs by Supplier")
    plt.xlabel("Supplier ID")
    plt.ylabel("Total Cost ($)")
    plt.show()
    print()

# ------------------- CLI Functions -------------------
def add_new_supplier():
    print("\n--- Add New Supplier ---")
    name = input("Enter supplier name: ")
    if not is_non_empty_string(name):
        print("❌ Supplier name cannot be empty.")
        return
    location = input("Enter supplier location: ")
    if not is_non_empty_string(location):
        print("❌ Location cannot be empty.")
        return
    contact = input("Enter contact info (email or phone): ")
    if not is_valid_contact(contact):
        print("❌ Invalid contact info. Please enter a valid email or phone number.")
        return

    confirm = input("Confirm adding supplier [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    supplier_id = SupplierManager.get_next_supplier_id()
    supplier = Supplier(supplier_id, name, location, contact)
    SupplierManager.save_supplier(supplier)
    print(f"✅ Supplier {supplier_id} added successfully!\n")

def update_supplier():
    print("\n--- Update Supplier ---")
    supplier_id = input("Enter Supplier ID (e.g., SUP001): ")
    if not SupplierManager.is_valid_supplier_id(supplier_id):
        print("❌ Supplier ID not found.")
        return

    name = input("Enter new supplier name: ")
    if not is_non_empty_string(name):
        print("❌ Supplier name cannot be empty.")
        return
    location = input("Enter new supplier location: ")
    if not is_non_empty_string(location):
        print("❌ Location cannot be empty.")
        return
    contact = input("Enter new contact info (email or phone): ")
    if not is_valid_contact(contact):
        print("❌ Invalid contact info. Please enter a valid email or phone number.")
        return

    confirm = input("Confirm updating supplier [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    updated_supplier = Supplier(supplier_id, name, location, contact)
    if SupplierManager.update_supplier(supplier_id, updated_supplier):
        print(f"✅ Supplier {supplier_id} updated successfully!\n")
    else:
        print("❌ Failed to update supplier.")

def delete_supplier():
    print("\n--- Delete Supplier ---")
    supplier_id = input("Enter Supplier ID (e.g., SUP001): ")
    if not SupplierManager.is_valid_supplier_id(supplier_id):
        print("❌ Supplier ID not found.")
        return

    confirm = input("Confirm deleting supplier [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    success, message = SupplierManager.delete_supplier(supplier_id)
    if success:
        print(f"✅ {message}\n")
    else:
        print(f"❌ {message}")

def view_all_suppliers():
    print("\n--- All Suppliers ---")
    suppliers = SupplierManager.load_suppliers()
    if not suppliers:
        print("No suppliers found.\n")
        return

    table = [[s.supplier_id, s.name, s.location, s.contact_info] for s in suppliers]
    print(tabulate(table, headers=["ID", "Name", "Location", "Contact"], tablefmt="grid"))
    print()

def search_suppliers():
    print("\n--- Search Suppliers ---")
    search_term = input("Enter name or location to search: ")
    if not is_non_empty_string(search_term):
        print("❌ Search term cannot be empty.")
        return
    suppliers = SupplierManager.search_suppliers(search_term)
    if not suppliers:
        print("No suppliers found matching the search term.\n")
        return

    table = [[s.supplier_id, s.name, s.location, s.contact_info] for s in suppliers]
    print(tabulate(table, headers=["ID", "Name", "Location", "Contact"], tablefmt="grid"))
    print()

def add_new_product():
    print("\n--- Add New Product ---")
    name = input("Enter product name: ")
    if not is_non_empty_string(name):
        print("❌ Product name cannot be empty.")
        return
    sku = input("Enter SKU: ")
    if not is_non_empty_string(sku):
        print("❌ SKU cannot be empty.")
        return
    if not ProductManager.is_unique_sku(sku):
        print("❌ SKU already exists. Please use a unique SKU.")
        return

    try:
        cost = float(input("Enter cost per unit: "))
        if not is_positive_number(cost):
            print("❌ Cost per unit must be a positive number.")
            return
        moq = int(input("Enter minimum order quantity (MOQ): "))
        if not is_positive_number(moq):
            print("❌ MOQ must be a positive integer.")
            return
        qty = int(input("Enter available quantity: "))
        if not is_positive_number(qty):
            print("❌ Available quantity must be a positive integer.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter numeric values for cost and quantities.")
        return

    supplier_id = input("Enter supplier ID (e.g., SUP001): ")
    if not SupplierManager.is_valid_supplier_id(supplier_id):
        print("❌ Invalid Supplier ID.")
        return

    confirm = input("Confirm adding product [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    product_id = ProductManager.get_next_product_id()
    product = Product(product_id, name, sku, cost, moq, qty, supplier_id)
    ProductManager.save_product(product)
    print(f"✅ Product {product_id} added successfully!\n")

def update_product():
    print("\n--- Update Product ---")
    product_id = input("Enter Product ID (e.g., PROD001): ")
    if not ProductManager.is_valid_product_id(product_id):
        print("❌ Product ID not found.")
        return

    name = input("Enter new product name: ")
    if not is_non_empty_string(name):
        print("❌ Product name cannot be empty.")
        return
    sku = input("Enter new SKU: ")
    if not is_non_empty_string(sku):
        print("❌ SKU cannot be empty.")
        return

    try:
        cost = float(input("Enter new cost per unit: "))
        if not is_positive_number(cost):
            print("❌ Cost per unit must be a positive number.")
            return
        moq = int(input("Enter new minimum order quantity (MOQ): "))
        if not is_positive_number(moq):
            print("❌ MOQ must be a positive integer.")
            return
        qty = int(input("Enter new available quantity: "))
        if not is_positive_number(qty):
            print("❌ Available quantity must be a positive integer.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter numeric values for cost and quantities.")
        return

    supplier_id = input("Enter new supplier ID (e.g., SUP001): ")
    if not SupplierManager.is_valid_supplier_id(supplier_id):
        print("❌ Invalid Supplier ID.")
        return

    confirm = input("Confirm updating product [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    updated_product = Product(product_id, name, sku, cost, moq, qty, supplier_id)
    success, message = ProductManager.update_product(product_id, updated_product)
    if success:
        print(f"✅ {message}\n")
    else:
        print(f"❌ {message}")

def delete_product():
    print("\n--- Delete Product ---")
    product_id = input("Enter Product ID (e.g., PROD001): ")
    if not ProductManager.is_valid_product_id(product_id):
        print("❌ Product ID not found.")
        return

    confirm = input("Confirm deleting product [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    success, message = ProductManager.delete_product(product_id)
    if success:
        print(f"✅ {message}\n")
    else:
        print(f"❌ {message}")

def view_all_products():
    print("\n--- All Products ---")
    products = ProductManager.load_products()
    if not products:
        print("No products found.\n")
        return

    table = [[p.product_id, p.name, p.sku, p.cost_per_unit, p.moq, p.available_qty, p.supplier_id]
             for p in products]
    print(tabulate(table, headers=["ID", "Name", "SKU", "Cost/Unit", "MOQ", "Available Qty", "Supplier ID"], tablefmt="grid"))
    print()

def search_products():
    print("\n--- Search Products ---")
    search_term = input("Enter name or SKU to search: ")
    if not is_non_empty_string(search_term):
        print("❌ Search term cannot be empty.")
        return
    products = ProductManager.search_products(search_term)
    if not products:
        print("No products found matching the search term.\n")
        return

    table = [[p.product_id, p.name, p.sku, p.cost_per_unit, p.moq, p.available_qty, p.supplier_id]
             for p in products]
    print(tabulate(table, headers=["ID", "Name", "SKU", "Cost/Unit", "MOQ", "Available Qty", "Supplier ID"], tablefmt="grid"))
    print()

def view_low_stock_products():
    print("\n--- Low Stock Products ---")
    threshold = input("Enter low stock threshold (default 10): ")
    try:
        threshold = int(threshold) if threshold.strip() else 10
        if not is_positive_number(threshold):
            print("❌ Threshold must be a positive integer.")
            return
    except ValueError:
        print("❌ Invalid threshold. Using default (10).")
        threshold = 10

    products = ProductManager.get_low_stock_products(threshold)
    if not products:
        print(f"No products with stock below {threshold}.\n")
        return

    table = [[p.product_id, p.name, p.sku, p.available_qty, p.supplier_id]
             for p in products]
    print(tabulate(table, headers=["ID", "Name", "SKU", "Available Qty", "Supplier ID"], tablefmt="grid"))
    print()

def add_new_order():
    print("\n--- Add New Order ---")
    product_id = input("Enter Product ID (e.g., PROD001): ")
    if not ProductManager.is_valid_product_id(product_id):
        print("❌ Invalid Product ID.")
        return

    supplier_id = input("Enter Supplier ID (e.g., SUP001): ")
    if not SupplierManager.is_valid_supplier_id(supplier_id):
        print("❌ Invalid Supplier ID.")
        return

    try:
        quantity = int(input("Enter quantity: "))
        if not is_positive_number(quantity):
            print("❌ Quantity must be a positive integer.")
            return
        cost_per_unit = float(input("Enter cost per unit: "))
        if not is_positive_number(cost_per_unit):
            print("❌ Cost per unit must be a positive number.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter numeric values for quantity and cost.")
        return

    is_valid, message = ProductManager.validate_order_quantity(product_id, quantity)
    if not is_valid:
        print(f"❌ {message}")
        return

    total_cost = quantity * cost_per_unit
    order_date = datetime.today().strftime("%Y-%m-%d")
    delivery_status = "Pending"

    confirm = input("Confirm adding order [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    order_id = OrderManager.get_next_order_id()
    order = Order(order_id, product_id, supplier_id, quantity, total_cost, order_date, delivery_status)
    OrderManager.save_order(order)
    print(f"✅ Order {order_id} added successfully!\n")

def update_order_status():
    print("\n--- Update Order Status ---")
    order_id = input("Enter Order ID (e.g., ORD001): ")
    orders = OrderManager.load_orders()
    if not any(o.order_id == order_id for o in orders):
        print("❌ Order ID not found.")
        return

    new_status = input("Enter new delivery status (e.g., Pending, Shipped, Delivered): ")
    if not is_non_empty_string(new_status):
        print("❌ Status cannot be empty.")
        return
    confirm = input("Confirm updating order status [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    success, message = OrderManager.update_order_status(order_id, new_status)
    if success:
        print(f"✅ {message}\n")
    else:
        print(f"❌ {message}")

def delete_order():
    print("\n--- Delete Order ---")
    order_id = input("Enter Order ID (e.g., ORD001): ")
    if not any(o.order_id == order_id for o in OrderManager.load_orders()):
        print("❌ Order ID not found.")
        return

    confirm = input("Confirm deleting order [Y/N]? ").lower()
    if confirm != "y":
        print("❌ Operation canceled.")
        return

    success, message = OrderManager.delete_order(order_id)
    if success:
        print(f"✅ {message}\n")
    else:
        print(f"❌ {message}")

def view_all_orders():
    print("\n--- All Orders ---")
    orders = OrderManager.load_orders()
    if not orders:
        print("No orders found.\n")
        return

    table = [[o.order_id, o.product_id, o.supplier_id, o.quantity, o.total_cost, o.order_date, o.delivery_status]
             for o in orders]
    print(tabulate(table, headers=["ID", "Product ID", "Supplier ID", "Quantity", "Total Cost", "Order Date", "Status"], tablefmt="grid"))
    print()

def search_orders():
    print("\n--- Search Orders ---")
    search_term = input("Enter status or date to search: ")
    if not is_non_empty_string(search_term):
        print("❌ Search term cannot be empty.")
        return
    orders = OrderManager.search_orders(search_term)
    if not orders:
        print("No orders found matching the search term.\n")
        return

    table = [[o.order_id, o.product_id, o.supplier_id, o.quantity, o.total_cost, o.order_date, o.delivery_status]
             for o in orders]
    print(tabulate(table, headers=["ID", "Product ID", "Supplier ID", "Quantity", "Total Cost", "Order Date", "Status"], tablefmt="grid"))
    print()

def view_order_summary():
    print("\n--- Order Summary by Supplier ---")
    summary = OrderManager.get_order_summary_by_supplier()
    if not summary:
        print("No orders found for summary.\n")
        return

    table = [[s["supplier_id"], s["total_cost"]] for s in summary]
    print(tabulate(table, headers=["Supplier ID", "Total Cost"], tablefmt="grid"))
    print()

def record_product_sale():
    print("\n--- Record Product Sale ---")
    product_id = input("Enter Product ID (e.g., PROD001): ")
    if not ProductManager.is_valid_product_id(product_id):
        print("❌ Product ID not found.")
        return

    try:
        quantity_sold = int(input("Enter quantity sold: "))
        if not is_positive_number(quantity_sold):
            print("❌ Quantity sold must be a positive integer.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a numeric quantity.")
        return

    # Update product quantity
    success, message = ProductManager.update_product_quantity(product_id, -quantity_sold)
    if not success:
        print(f"❌ {message}")
        return

    # Record sale
    sale_id = SalesManager.get_next_sale_id()
    sale_date = datetime.today().strftime("%Y-%m-%d")
    sale = Sale(sale_id, product_id, quantity_sold, sale_date)
    SalesManager.save_sale(sale)
    print(f"✅ Sale {sale_id} recorded successfully! {message}\n")

# ------------------- Main Menu -------------------
def main():
    while True:
        print("\n====== Bulk Supplier Management System ======")
        print("1. Add New Supplier")
        print("2. View All Suppliers")
        print("3. Update Supplier")
        print("4. Delete Supplier")
        print("5. Search Suppliers")
        print("6. Add New Product")
        print("7. View All Products")
        print("8. Update Product")
        print("9. Delete Product")
        print("10. Search Products")
        print("11. View Low Stock Products")
        print("12. Add New Order")
        print("13. View All Orders")
        print("14. Update Order Status")
        print("15. Delete Order")
        print("16. Search Orders")
        print("17. View Order Summary by Supplier")
        print("18. Generate Inventory Report (PDF)")
        print("19. View Order Summary Chart")
        print("20. Record Product Sale")
        print("21. Generate Sales Summary Report (PDF)")
        print("22. Generate Product Sales Report (PDF)")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_new_supplier()
        elif choice == "2":
            view_all_suppliers()
        elif choice == "3":
            update_supplier()
        elif choice == "4":
            delete_supplier()
        elif choice == "5":
            search_suppliers()
        elif choice == "6":
            add_new_product()
        elif choice == "7":
            view_all_products()
        elif choice == "8":
            update_product()
        elif choice == "9":
            delete_product()
        elif choice == "10":
            search_products()
        elif choice == "11":
            view_low_stock_products()
        elif choice == "12":
            add_new_order()
        elif choice == "13":
            view_all_orders()
        elif choice == "14":
            update_order_status()
        elif choice == "15":
            delete_order()
        elif choice == "16":
            search_orders()
        elif choice == "17":
            view_order_summary()
        elif choice == "18":
            generate_inventory_report()
        elif choice == "19":
            plot_order_summary()
        elif choice == "20":
            record_product_sale()
        elif choice == "21":
            generate_inventory_report()  # Reusing for sales summary
        elif choice == "22":
            generate_product_sales_report()
        elif choice == "0":
            print("👋 Exiting... Goodbye bro!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

# ------------------- Run App -------------------
if __name__ == "__main__":
    main()