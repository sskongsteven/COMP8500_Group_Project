from inventory import add_product, change_stock, list_products

# add_product("Notebook", "12.50", 20)
# change_stock("P001", -3)
# print(list_products())

sample_products = [
    ("Ballpoint Pen", "6.00", 100),
    ("Pencil", "4.00", 120),
    ("Eraser", "5.00", 75),
    ("Highlighter", "12.00", 45),
    ("Sticky Notes", "18.00", 60),
    ("A4 Paper Pack", "45.00", 30),
    ("File Folder", "12.00", 50),
    ("Stapler", "38.00", 25),
    ("Paper Clips Box", "12.00", 40),
]

for name, price, starting_stock in sample_products:
    product = add_product(name, price, starting_stock)
    print(f"Added {product['product_id']}: {product['product_name']}")

print(list_products())
