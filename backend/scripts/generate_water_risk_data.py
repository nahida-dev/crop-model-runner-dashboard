import pandas as pd
import numpy as np
from pathlib import Path

# Path setup
data_dir = Path(__file__).resolve().parents[1] / "data"
yield_path = data_dir / "yield_data.csv"
water_path = data_dir / "water_risk_data.csv"

# Load yield dataset (from USDA)
df = pd.read_csv(yield_path)

# Generate synthetic water-related data
np.random.seed(42)
df["rainfall_mm"] = np.random.normal(850, 100, len(df)).round(1)
df["irrigation_cost_usd_per_acre"] = np.random.normal(25, 75, len(df)).round(1)
df["drought_index"] = np.random.normal(0.1, 0.9, len(df)).round(3)

'''
# Derived columns
df["soil_moisture_index"] = (
    (df["rainfall_mm"] - df["evapotranspiration_mm"]) / 1000
).round(2)

df["risk_level"] = pd.cut(
    df["soil_moisture_index"],
    bins=[-1, 0.3, 0.6, 1],
    labels=["High", "Medium", "Low"],
)
'''

# Save new file
data_dir.mkdir(exist_ok=True)
df.to_csv(water_path, index=False)
print(f"Water risk dataset created: {water_path}")
