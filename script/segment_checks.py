"""
Customer segmentation: checks behind the README figures.
Reads data/retail_sales_dataset.csv and prints segment tables and the
statistical tests quoted in the README.

Run:  python script/segment_checks.py
Needs: pandas, scipy
"""
from pathlib import Path
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

DATA = Path(__file__).resolve().parent.parent / "data" / "retail_sales_dataset.csv"
c = pd.read_csv(DATA, encoding="utf-8-sig")  # file has a byte-order mark
c["Date"] = pd.to_datetime(c["Date"], format="%d-%m-%Y")  # dates are day-month-year

print("Rows:", len(c), "| customers:", c["Customer ID"].nunique(), "| transactions:", c["Transaction ID"].nunique())
print("Date range:", c.Date.min().date(), "to", c.Date.max().date())
print("Total sales:", c["Total Amount"].sum(), "| AOV:", round(c["Total Amount"].mean(), 2))

c["Age Group"] = pd.cut(c.Age, [17, 25, 35, 45, 55, 64], labels=["18-25", "26-35", "36-45", "46-55", "56-64"])
c["Spend Tier"] = pd.cut(c["Total Amount"], [0, 100, 500, 1000, 10000], labels=["Under 100", "100-499", "500-999", "1000+"], right=False)

print("\nRevenue and transactions by age group:")
print(c.groupby("Age Group", observed=True)["Total Amount"].agg(["sum", "count", "mean"]).round(0).to_string())
print("\nRevenue by gender:")
print(c.groupby("Gender")["Total Amount"].agg(["sum", "count", "mean"]).round(0).to_string())
print("\nRevenue by category:")
print(c.groupby("Product Category")["Total Amount"].agg(["sum", "count", "mean"]).round(0).to_string())
print("\nSpend tiers (share of transactions vs share of revenue):")
t = c.groupby("Spend Tier", observed=True)["Total Amount"].agg(["count", "sum"])
t["share_transactions_%"] = (t["count"] / len(c) * 100).round(1)
t["share_revenue_%"] = (t["sum"] / c["Total Amount"].sum() * 100).round(1)
print(t.to_string())
print("\nAge group x category revenue:")
print(c.pivot_table(index="Age Group", columns="Product Category", values="Total Amount", aggfunc="sum", observed=True).round(0).to_string())

print("\nTests:")
print("  chi-square, age group x category: p =", round(chi2_contingency(pd.crosstab(c["Age Group"], c["Product Category"]))[1], 3))
print("  chi-square, gender x category: p =", round(chi2_contingency(pd.crosstab(c.Gender, c["Product Category"]))[1], 3))
print("  Kruskal-Wallis, transaction amount by age group: p =",
      round(kruskal(*[g["Total Amount"] for _, g in c.groupby("Age Group", observed=True)]).pvalue, 3))
print("  Kruskal-Wallis, transaction amount by gender: p =",
      round(kruskal(*[g["Total Amount"] for _, g in c.groupby("Gender")]).pvalue, 3))
