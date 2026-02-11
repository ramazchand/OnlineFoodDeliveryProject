import pandas as pd
from sqlalchemy import create_engine, text

csv_file = r"C:\Users\ADMIN\OneDrive\Desktop\OnlineFoodDeliveryProject\data\cleaned_food_delivery.csv"
df = pd.read_csv(csv_file)
print("CSV Loaded Successfully!")
print(df.head()) 

engine = create_engine('mysql+mysqlconnector://root:Welcome%404533@localhost:3306/food_delivery')

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

df.to_sql('orders', con=engine, if_exists='replace', index=False)
print("CSV data successfully imported into MySQL!")
