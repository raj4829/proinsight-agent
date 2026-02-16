"""
Simplified Portfolio Dataset Generator
Generates CSV files directly without pandas dependency
"""

import csv
from datetime import datetime, timedelta
import random
import math

# Set seed
random.seed(42)

def generate_ecommerce_csv():
    """Generate e-commerce data CSV"""
    filename = "portfolio_ecommerce_techgear_2024.csv"
    
    products = [
        ("Wireless Earbuds Pro", "Audio", 79.99, 35, 15),
        ("Smart Watch Ultra", "Wearables", 299.99, 150, 8),
        ("Laptop Stand Premium", "Accessories", 49.99, 18, 12),
        ("USB-C Hub 7-in-1", "Accessories", 39.99, 15, 20),
        ("Mechanical Keyboard RGB", "Peripherals", 129.99, 55, 10),
        ("Gaming Mouse Pro", "Peripherals", 69.99, 28, 14),
        ("Webcam 4K", "Peripherals", 89.99, 40, 9),
        ("Portable SSD 1TB", "Storage", 119.99, 60, 11),
        ("Phone Case Premium", "Accessories", 24.99, 8, 25),
        ("Screen Protector 3-Pack", "Accessories", 14.99, 4, 30),
        ("Wireless Charger Fast", "Accessories", 34.99, 12, 18),
        ("Bluetooth Speaker", "Audio", 59.99, 25, 13),
        ("Noise Cancelling Headphones", "Audio", 199.99, 90, 7),
        ("Tablet Stand Adjustable", "Accessories", 29.99, 10, 16),
        ("Cable Organizer Set", "Accessories", 19.99, 6, 22),
    ]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Product", "Category", "Units Sold", "Revenue", "Cost", "Returns", "Customer Acquisition Cost", "Average Order Value"])
        
        start_date = datetime(2024, 1, 1)
        
        for day in range(365):
            date = start_date + timedelta(days=day)
            month = date.month
            day_of_week = date.weekday()
            
            # Seasonal factors
            is_black_friday = (month == 11 and 24 <= date.day <= 27)
            is_cyber_monday = (month == 11 and date.day == 28)
            is_holiday = month == 12
            is_back_to_school = month in [8, 9]
            
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0
            
            seasonal_factor = 1.0
            if is_black_friday:
                seasonal_factor = 3.5
            elif is_cyber_monday:
                seasonal_factor = 3.2
            elif is_holiday:
                seasonal_factor = 1.8
            elif is_back_to_school:
                seasonal_factor = 1.4
            
            daily_noise = random.uniform(0.85, 1.15)
            
            for name, category, price, cost, base_units in products:
                units = int(base_units * seasonal_factor * weekend_factor * daily_noise)
                
                if units < 5 and random.random() < 0.3:
                    units = 0
                
                if units > 0:
                    actual_price = price
                    if is_black_friday or is_cyber_monday:
                        actual_price *= 0.75
                    elif random.random() < 0.1:
                        actual_price *= 0.9
                    
                    revenue = round(actual_price * units, 2)
                    total_cost = round(cost * units, 2)
                    returns = int(units * random.uniform(0.02, 0.15))
                    cac = round(random.uniform(8, 25) * units, 2)
                    aov = round(revenue / units, 2)
                    
                    writer.writerow([
                        date.strftime("%Y-%m-%d"),
                        name,
                        category,
                        units,
                        revenue,
                        total_cost,
                        returns,
                        cac,
                        aov
                    ])
    
    print(f"✓ Created {filename}")
    return filename


def generate_saas_csv():
    """Generate SaaS metrics CSV"""
    filename = "portfolio_saas_cloudsync_2024.csv"
    
    mrr = 35000
    active_customers = 95
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "MRR", "Active Customers", "New Signups", "Churned Customers", "Churn Rate", "Free Users", "Pro Users", "Enterprise Users", "Active Users", "Expansion Revenue"])
        
        start_date = datetime(2024, 1, 1)
        
        for day in range(365):
            date = start_date + timedelta(days=day)
            day_of_week = date.weekday()
            
            # Growth
            monthly_growth = 0.15
            daily_growth = (1 + monthly_growth) ** (1/30) - 1
            growth_factor = (1 + daily_growth) ** day
            noise = random.uniform(0.98, 1.02)
            
            # Signups
            base_signups = 4 if day_of_week < 5 else 1
            new_signups = int(base_signups * random.uniform(0.7, 1.3))
            
            # Churn
            is_month_end = date.day >= 28
            base_churn_rate = 0.035 / 30
            if is_month_end:
                base_churn_rate *= 1.5
            
            churned = int(active_customers * base_churn_rate * random.uniform(0.8, 1.2))
            
            active_customers += new_signups - churned
            active_customers = max(active_customers, 50)
            
            # Tiers
            free_users = int(active_customers * 0.35)
            pro_users = int(active_customers * 0.50)
            enterprise_users = active_customers - free_users - pro_users
            
            # MRR
            pro_mrr = pro_users * 49
            enterprise_mrr = enterprise_users * 199
            total_mrr = pro_mrr + enterprise_mrr
            
            active_users = int(active_customers * random.uniform(0.65, 0.85))
            expansion = round(random.uniform(500, 2000), 2) if random.random() < 0.1 else 0
            churn_rate = round((churned / active_customers) * 100, 2) if active_customers > 0 else 0
            
            writer.writerow([
                date.strftime("%Y-%m-%d"),
                round(total_mrr, 2),
                active_customers,
                new_signups,
                churned,
                churn_rate,
                free_users,
                pro_users,
                enterprise_users,
                active_users,
                expansion
            ])
    
    print(f"✓ Created {filename}")
    return filename


def generate_marketing_csv():
    """Generate marketing campaign CSV"""
    filename = "portfolio_marketing_advantage_2024.csv"
    
    profiles = {
        "Google Ads": (1500, 50000, 0.024, 0.0375, 320),
        "Facebook Ads": (1800, 120000, 0.020, 0.025, 180),
        "LinkedIn Ads": (1200, 25000, 0.030, 0.051, 580),
        "Email Marketing": (300, 15000, 0.060, 0.058, 210)
    }
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Campaign", "Channel", "Ad Spend", "Impressions", "Clicks", "Conversions", "Revenue", "CPC", "CPA", "ROAS", "CTR", "CVR"])
        
        start_date = datetime(2024, 1, 1)
        
        for week in range(52):
            date = start_date + timedelta(weeks=week)
            month = date.month
            
            seasonal_factor = 1.0
            if month in [11, 12]:
                seasonal_factor = 1.4
            elif month in [1, 2]:
                seasonal_factor = 0.8
            
            learning_factor = 1 + (week * 0.005)
            
            for channel, (base_spend, base_impr, ctr, cvr, rev_per_conv) in profiles.items():
                noise = random.uniform(0.85, 1.15)
                
                spend = round(base_spend * seasonal_factor * noise, 2)
                impressions = int(base_impr * seasonal_factor * noise)
                clicks = int(impressions * ctr * learning_factor * noise)
                conversions = int(clicks * cvr * learning_factor * noise)
                revenue = round(conversions * rev_per_conv * random.uniform(0.9, 1.1), 2)
                
                cpc = round(spend / clicks, 2) if clicks > 0 else 0
                cpa = round(spend / conversions, 2) if conversions > 0 else 0
                roas = round(revenue / spend, 2) if spend > 0 else 0
                ctr_pct = round((clicks / impressions * 100), 2) if impressions > 0 else 0
                cvr_pct = round((conversions / clicks * 100), 2) if clicks > 0 else 0
                
                campaign_name = f"{channel} - Week {week + 1}"
                
                writer.writerow([
                    date.strftime("%Y-%m-%d"),
                    campaign_name,
                    channel,
                    spend,
                    impressions,
                    clicks,
                    conversions,
                    revenue,
                    cpc,
                    cpa,
                    roas,
                    ctr_pct,
                    cvr_pct
                ])
    
    print(f"✓ Created {filename}")
    return filename


if __name__ == "__main__":
    print("Generating Portfolio Datasets...")
    print("=" * 50)
    
    print("\n1. E-commerce (TechGear)...")
    generate_ecommerce_csv()
    
    print("\n2. SaaS (CloudSync)...")
    generate_saas_csv()
    
    print("\n3. Marketing (AdVantage)...")
    generate_marketing_csv()
    
    print("\n" + "=" * 50)
    print("✅ All datasets generated!")
    print("\nFiles created:")
    print("  - portfolio_ecommerce_techgear_2024.csv")
    print("  - portfolio_saas_cloudsync_2024.csv")
    print("  - portfolio_marketing_advantage_2024.csv")
