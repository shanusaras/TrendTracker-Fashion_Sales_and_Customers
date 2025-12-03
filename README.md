# 👗 TrendTracker – Fashion Sales & Customer Behavior Dashboard

**TrendTracker** is an end-to-end data analytics project that helps fashion retailers understand customer behavior, monitor product performance, and track sales trends using a clean, interactive dashboard and Python-based data pipeline.

---

## 1. Business Problem

Fashion retailers often struggle with:
- Identifying which products, categories, and collections are underperforming
- Understanding customer demographics, repeat behavior, and retention gaps
- Tracking monthly sales, revenue trends, and campaign effectiveness
- No segmentation framework to prioritize high-value customers  
- Lack of a centralized, interactive dashboard for stakeholders  


**TrendTracker** solves these challenges by combining cleaned sales and customer data with visual analytics to enable business decision-making across product, marketing, and merchandising teams.

---

## 2. Project Objectives

- Build a **clean, reliable dataset** from raw sales, product & customer files
- Perform **exploratory data analysis (EDA)** to identify trends & patterns
- Create **RFM-based customer segmentation** for retention and marketing campaigns
- Build a streamlined **Streamlit dashboard** with KPIs, filters, and charts
- Generate **business insights** for product, marketing, and growth teams

---

## 3. Tech Stack

| Layer             | Tools Used                       |
|------------------|----------------------------------|
| **Data Cleaning** | Python (Pandas, NumPy)    |
| **Exploratory Analysis** | Pandas, Matplotlib, Seaborn |
| **Segmentation**  | RFM (Recency, Frequency, Monetary) modeling |
| **Dashboarding**  | Streamlit, Plotly                |
| **Documentation** | Jupyter Notebook, Markdown |

---

## 4. Data Pipeline Flow

```text
                 ┌──────────────────────────┐
                 │        Raw Data           │
                 │  (customers, orders,      │
                 │   products CSV files)     │
                 └─────────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │  Data Cleaning &  │
                    │    Preprocessing  │
                    │ (Pandas, NumPy)   │
                    └─────────┬─────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │ Exploratory Analysis │
                  │ (Plots, Trends, EDA) │
                  └────────────┬─────────┘
                               │
                               ▼
                  ┌──────────────────────┐
                  │   RFM Segmentation   │
                  │  (Recency, Frequency,│
                  │      Monetary)       │
                  └────────────┬─────────┘
                               │
                               ▼
                  ┌──────────────────────┐
                  │   Streamlit App      │
                  │  KPIs, Filters, UI   │
                  └────────────┬─────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Interactive Dashboard     │
                 │  (Insights & Decisions)   │
                 └──────────────────────────┘
```

## 5. Project Architecture

```text
trendtracker-fashion-sales/
├── dashboard/               # Streamlit dashboard application
│   ├── dashboard.py        # Main application file
│   └── all_data.csv        # Preprocessed dataset
├── dataset/                # Raw data files
│   ├── customers.csv       # Customer information
│   ├── orders.csv         # Order details
│   ├── products.csv       # Product catalog
│   ├── sales.csv          # Sales transactions
│   └── Legend.txt         # Data dictionary
├── assets/                # Static resources
│   └── logo.png          # Application logo
├── Online_Fashion_Data_Analysis.ipynb  # Jupyter notebook for EDA
├── online_fashion_data_analysis.py     # Script version of the analysis
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 6. Data Dictionary

### Customers (`dataset/customers.csv`)
| Column | Type | Description |
|--------|------|-------------|
| customer_id | String | Unique identifier for each customer |
| customer_name | String | Full name of the customer |
| gender | String | Customer's gender (M/F/Other) |
| age | Integer | Customer's age |
| home_address | String | Complete address |
| zip_code | String | Postal/ZIP code |
| city | String | City of residence |
| state | String | State/Province |
| country | String | Country of residence |

### Orders (`dataset/orders.csv`)
| Column | Type | Description |
|--------|------|-------------|
| order_id | String | Unique order identifier |
| customer_id | String | Reference to customer |
| order_date | Date | Date of order placement |
| delivery_date | Date | Date of order delivery |

### Products (`dataset/products.csv`)
| Column | Type | Description |
|--------|------|-------------|
| product_id | String | Unique product identifier |
| product_type | String | Main category of product |
| product_name | String | Name of the product |
| size | String | Available sizes (S/M/L/XL) |
| color | String | Product color |
| price | Float | Unit price in AUD |
| quantity | Integer | Available stock quantity |
| description | String | Product description |

### Sales (`dataset/sales.csv`)
| Column | Type | Description |
|--------|------|-------------|
| sales_id | String | Unique sales record identifier |
| order_id | String | Reference to order |
| product_id | String | Reference to product |
| price_per_unit | Float | Price per unit at time of sale |
| quantity | Integer | Number of units sold |
| total_price | Float | Total transaction amount (price_per_unit * quantity) |


## 7. Feature Highlights

### Data Analysis
- **Sales & Revenue Trends** with monthly AOV (Average Order Value) tracking
- **Customer Demographics** analysis by age group, gender, and state
- **Product Performance** tracking with top-selling items and categories
- **Cohort Analysis** to understand customer retention patterns

### 🔍 Advanced Analytics
- **RFM (Recency, Frequency, Monetary) Analysis**
  - Customer segmentation using quintile scoring (1-5) for each RFM dimension
  - Visual representation of customer distribution across segments
  - Identification of high-value customer segments
  - Revenue analysis by customer segment

### 📈 Interactive Dashboard (Streamlit)
- **Dynamic Filtering**
  - Date range selection
  - State, gender, and age group filters
  - Product search functionality
  - Minimum order value filter

- **Key Metrics**
  - Total Orders and Revenue
  - Average Order Value (AOV)
  - Repeat Purchase Rate
  - Median Delivery Time

- **Visualizations**
  - Cohort retention heatmaps
  - Monthly AOV trends
  - CLTV (Customer Lifetime Value) distribution
  - Delivery time analysis

### 📤 Data Export
- Download filtered data in CSV or Excel format
- Export charts as PNG images
- Auto-generated insights and recommendations

📌 **Live Dashboard:** *Add your Streamlit URL here*  
📌 **Screenshots:** Add images in `/docs/screenshots/` and embed them here.

---

## 💡 8. Business Insights (Examples)

> *(Replace with your real insights from your analysis)*

- **Top 10% of customers generate ~40% of revenue**  
- Women’s fashion leads revenue while Accessories show **high repeat behavior**  
- “Champions” segment has the **highest CLV**  
- Underperforming SKUs mostly fall in **low-price categories**  
- Evenings (5–10 PM) show the highest order volume  
- AOV is improving month-on-month  
- At-risk customers show high past spending → major retention opportunity  

---


## 🧪 9. How to Run This Project

### Step 1 — Clone the repo
```bash
git clone https://github.com/yourusername/trendtracker-fashion-sales.git
cd trendtracker-fashion-sales
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the Streamlit app
```bash
streamlit run dashboard/dashboard.py
```

### Step 4 — Open the dashboard in your browser
The dashboard should open automatically in your default web browser. If it doesn’t, you can open it manually by navigating to `http://localhost:8501` in your browser.

--- 

## 10. Future Enhancements

- Customer churn prediction
- Product recommendation model
- LTV prediction
- Automated sales forecasting
- Power BI business dashboard
- Docker-based deployment

---


## 10. 📌 Contact

Made with ❤️ by [@shanusaras](https://github.com/shanusaras)  
Connect with me to collaborate or discuss analytics use cases in retail and fashion tech.

