# ===========================================
# Online Food Delivery - Data Cleaning Script
# ===========================================

import pandas as pd

# -------------------------------
# Step 1: Load raw dataset
# -------------------------------
raw_csv_path = r"C:\Users\ADMIN\Downloads\online_food_delivery.csv"  # <-- Update path if needed
df = pd.read_csv(raw_csv_path)

# -------------------------------
# Step 2: Inspect and clean column names
# -------------------------------
print("Original Columns:", df.columns.tolist())

# Standardize: lowercase, remove spaces, replace with underscores
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
print("Cleaned Columns:", df.columns.tolist())

# -------------------------------
# Step 3: Handle missing values
# -------------------------------

# Numeric columns
numeric_cols = ['rating', 'profit', 'order_value', 'delivery_time_min', 'distance_km', 'final_amount', 'restaurant_rating', 'delivery_rating']
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# Categorical columns
categorical_cols = ['city', 'cuisine_type', 'payment_mode', 'order_status', 'cancellation_reason', 'customer_gender', 'area', 'restaurant_name']
for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')

# -------------------------------
# Step 4: Feature Engineering
# -------------------------------

# Convert order_date to datetime
if 'order_date' in df.columns:
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

# Create order_day_type: Weekday or Weekend
if 'order_date' in df.columns:
    df['order_day_type'] = df['order_date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')

# Peak hour indicator (1 = 18:00-21:00, else 0)
if 'order_time' in df.columns:
    def peak_hour(x):
        try:
            hour = int(str(x).split(":")[0])
            return 1 if 18 <= hour <= 21 else 0
        except:
            return 0
    df['peak_hour'] = df['order_time'].apply(peak_hour)

# Profit margin % (create if not exists)
if 'profit_margin' not in df.columns:
    if 'final_amount' in df.columns and 'order_value' in df.columns:
        df['profit_margin'] = ((df['final_amount'] - df['order_value']) / df['order_value']) * 100

# Delivery performance based on delivery_time_min
if 'delivery_time_min' in df.columns:
    df['delivery_performance'] = pd.cut(df['delivery_time_min'],
                                        bins=[0, 30, 60, 90, 150, 1000],
                                        labels=['Excellent', 'Good', 'Average', 'Poor', 'Very Poor'])

# -------------------------------
# Step 5: Save cleaned dataset
# -------------------------------
cleaned_csv_path = r"C:\Users\ADMIN\OneDrive\Desktop\OnlineFoodDeliveryProject\data\cleaned_food_delivery.csv"
df.to_csv(cleaned_csv_path, index=False)
print(f"✅ Data cleaning complete! Cleaned file saved at:\n{cleaned_csv_path}")
