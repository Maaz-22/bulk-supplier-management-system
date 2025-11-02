# Bulk Supplier Management System

A **command-line inventory & supplier management system** built in Python using `pandas`, `reportlab`, `tabulate`, and `plotext`.  
Perfect for small-to-medium businesses that need to track suppliers, products, purchase orders, sales, and generate PDF reports & charts  using CSV.

---

## Features

- **Suppliers** – Add, update, delete, search  
- **Products** – SKU-based catalog with MOQ, cost, stock levels  
- **Purchase Orders** – Place orders (MOQ & stock validation)  
- **Sales** – Record sales & automatically reduce inventory  
- **Low-Stock Alerts** – Configurable threshold  
- **PDF Reports**  
  - *Inventory Report* – low stock + order/sales summary  
  - *Product Sales Report* – per-product transaction list  
- **Bar Chart** – Total order costs by supplier (terminal)  
- **Search** – suppliers, products, orders  
- **CSV Persistence** – all data stored in `suppliers.csv`, `products.csv`, `orders.csv`, `sales.csv`

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `pandas` | Data handling & CSV I/O |
| `tabulate` | Pretty CLI tables |
| `reportlab` | PDF report generation |
| `plotext` | Terminal bar charts |

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/bulk-supplier-management-system.git
cd bulk-supplier-management-system

# 2. Install dependencies
pip install pandas tabulate reportlab plotext
```

---

## Running the App

```bash
python main.py
```

(If your script has a different name, replace `main.py` accordingly.)

Follow the interactive menu to manage your inventory.

---

## File Overview

| File | Description |
|------|-------------|
| `suppliers.csv` | Supplier records |
| `products.csv` | Product catalog |
| `orders.csv` | Purchase orders |
| `sales.csv` | Sales transactions |
| `inventory_report_*.pdf` | Generated inventory reports |
| `product_sales_report_*.pdf` | Per-product sales reports |

---

## Sample Menu

```
====== Bulk Supplier Management System ======
1. Add New Supplier
2. View All Suppliers
...
18. Generate Inventory Report (PDF)
19. View Order Summary Chart
20. Record Product Sale
22. Generate Product Sales Report (PDF)
0. Exit
```

---

## Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/xyz`)  
3. Commit your changes (`git commit -am 'Add xyz'`)  
4. Push to the branch (`git push origin feature/xyz`)  
5. Open a Pull Request  

---

## License

[MIT License](LICENSE) – feel free to use, modify, and distribute.

---

**Made with ❤️ for efficient bulk supply chain management.**
```


