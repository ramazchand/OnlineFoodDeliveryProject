import pandas as pd
from sqlalchemy import create_engine, text

# -----------------------------
# 1. Read the CSV
# -----------------------------
csv_file = r"C:\Users\ADMIN\OneDrive\Desktop\OnlineFoodDeliveryProject\data\cleaned_food_delivery.csv"
df = pd.read_csv(csv_file)
print("CSV Loaded Successfully!")
print(df.head())  # Optional: preview first 5 rows

# -----------------------------
# 2. Connect to MySQL
# -----------------------------
# Update username, password, host, port, and database as per your MySQL setup
engine = create_engine('mysql+mysqlconnector://root:Welcome%404533@localhost:3306/food_delivery')

# -----------------------------
# 3. Create table (if not exists)
# -----------------------------
create_table_query = text("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(100),
    cuisine_type VARCHAR(100),
    final_amount DECIMAL(10,2),
    delivery_time_min INT,
    order_time DATETIME,
    is_cancelled BOOLEAN DEFAULT 0,
    delivery_rating INT
);
""")

with engine.connect() as conn:
    conn.execute(create_table_query)
    conn.commit()
print("MySQL table is ready!")

# -----------------------------
# 4. Insert CSV data into MySQL
# -----------------------------
df.to_sql('orders', con=engine, if_exists='replace', index=False)
print("CSV data successfully imported into MySQL!")
