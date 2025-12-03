
import io
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency # for currency formatting
import matplotlib
matplotlib.rcParams['figure.dpi'] = 100

# Page configuration and styling
st.set_page_config(page_title="TrendTracker — Fashion Dashboard", page_icon="👕", layout="wide")
sns.set_style("darkgrid")

# ------------------------------
# Utility helpers
# ------------------------------

# Formats numbers as AUD currency
def format_aud(value):
    try:
        return format_currency(value, 'AUD', locale='en_US')
    except Exception:
        return f"AUD {value:,.2f}"

# Computes Average Order Value (AOV)
# General calc: Total Revenue/ No of Orders
def compute_aov(df):
    if df.empty:
        return 0.0
    order_vals = df.groupby("order_id", as_index=False).agg({"total_price": "sum"})
    return order_vals["total_price"].mean() if not order_vals.empty else 0.0

# Computes % of customers who made more than one purchase--> customers who made more than one unique order
# general calc: (No of repeat customers / Total customers) * 100
def compute_repeat_purchase_rate(df):
    if df.empty:
        return 0.0
    purchases = df.groupby("customer_id").order_id.nunique()
    repeat = (purchases > 1).sum()
    total_customers = purchases.shape[0]
    return (repeat / total_customers) if total_customers > 0 else 0.0

# Convert matplotlib figure to a downloadable img (PNG)
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

# ------------------------------
# Helper functions (kept)
# ------------------------------
def create_daily_orders_df(df):
    if df.empty:
        return pd.DataFrame(columns=['order_date','order_count','revenue'])
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        'order_id': 'nunique',
        'total_price': 'sum'
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        'order_id': 'order_count',
        'total_price': 'revenue'
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    if 'quantity_x' not in df.columns:
        df['quantity_x'] = 0
    sum_order_items_df = df.groupby('product_name').quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bygender_df(df):
    if df.empty:
        return pd.DataFrame(columns=['gender','customer_count'])
    bygender_df = df.groupby(by='gender').customer_id.nunique().reset_index()
    bygender_df.rename(columns={'customer_id': 'customer_count'}, inplace=True)
    return bygender_df

def create_byage_df(df):
    if df.empty:
        return pd.DataFrame(columns=['age_group','customer_count'])
    byage_df = df.groupby(by='age_group').customer_id.nunique().reset_index()
    byage_df.rename(columns={'customer_id': 'customer_count'}, inplace=True)
    return byage_df

def create_bystate_df(df):
    if df.empty:
        return pd.DataFrame(columns=['state','customer_count'])
    bystate_df = df.groupby(by='state').customer_id.nunique().reset_index()
    bystate_df.rename(columns={'customer_id': 'customer_count'}, inplace=True)
    return bystate_df

def create_rfm_df(df):
    if df.empty:
        return pd.DataFrame(columns=['customer_id','frequency','monetary','recency'])
    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        'order_date': 'max',
        'order_id': 'nunique',
        'total_price': 'sum'
    })
    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
    recent_date = df['order_date'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].dt.date.apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    return rfm_df

# ------------------------------
# Load data (remote source)
# ------------------------------
DATA_URL = 'https://raw.githubusercontent.com/shanusaras/TrendTracker-Fashion_Sales_and_Customers/main/dashboard/all_data.csv'

@st.cache_data(ttl=3600) # Caches the data for 1 hour (3600 seconds) to improve performance.
# Prevents re-fetching and reprocessing the data on every interaction.
def load_data(url):
    df = pd.read_csv(url)
    for col in ['order_date', 'delivery_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # error= 'coerce' --> Coerce invalid parsing (dates) to NaT (Not a Time) instead of crashing
    df.sort_values('order_date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

all_df = load_data(DATA_URL)
# all_df is used throughout the dashboard

# Ensure expected columns present
# If a column is missing, it adds it with NaN values.
# Prevents errors when functions try to access these columns later.
for c in ["quantity_x", "total_price", "order_id", "customer_id", "product_name", "gender", "age_group", "state", "delivery_date"]:
    if c not in all_df.columns:
        all_df[c] = np.nan

# ------------------------------
# Sidebar: remote logo + filters
# ------------------------------
REMOTE_LOGO = "https://github.com/dicodingacademy/assets/raw/main/logo.png"
st.sidebar.image(REMOTE_LOGO, use_container_width=True)
st.sidebar.markdown("### Filters")

min_date = all_df['order_date'].min().date()
max_date = all_df['order_date'].max().date()

start_date, end_date = st.sidebar.date_input(
    label='Select Date Range',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

states = sorted(all_df['state'].dropna().unique())
state_sel = st.sidebar.multiselect("State (multi-select)", options=states, default=[])

genders = sorted(all_df['gender'].dropna().unique())
gender_sel = st.sidebar.multiselect("Gender (multi-select)", options=genders, default=[])

age_groups = sorted(all_df['age_group'].dropna().unique())
age_sel = st.sidebar.multiselect("Age group (multi-select)", options=age_groups, default=[])

product_search = st.sidebar.text_input("Product name contains (case-insensitive)")
min_order_value = st.sidebar.number_input("Min order total (AUD)", value=0, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### Visualization Controls")
top_n = st.sidebar.slider("Top N products to show", min_value=3, max_value=20, value=5)
show_values_on_bars = st.sidebar.checkbox("Show values on bars", value=True)

# ------------------------------
# Apply filters
# ------------------------------
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
#  Ensures the end date includes the full day.

mask = (all_df['order_date'] >= start_ts) & (all_df['order_date'] <= end_ts)
# combines all the filters
# mask is a boolean Series where True means the row matches all filters
# Each condition (state_sel, gender_sel etc.) refines the mask
if state_sel:
    mask &= all_df['state'].isin(state_sel)
if gender_sel:
    mask &= all_df['gender'].isin(gender_sel)
if age_sel:
    mask &= all_df['age_group'].isin(age_sel)
if product_search:
    mask &= all_df['product_name'].str.contains(product_search, case=False, na=False)

# Apply filters to df
main_df = all_df.loc[mask].copy()

# min order total: compute order totals then filter
if min_order_value and min_order_value > 0 and not main_df.empty:
    order_totals = main_df.groupby("order_id", as_index=False).total_price.sum().rename(columns={"total_price": "order_total"})
    qualifying_orders = order_totals[order_totals["order_total"] >= float(min_order_value)]["order_id"]
    main_df = main_df[main_df["order_id"].isin(qualifying_orders)].copy()

# ------------------------------
# Aggregations & KPIs
# ------------------------------
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

total_orders = int(daily_orders_df['order_count'].sum()) if not daily_orders_df.empty else 0
total_revenue = float(daily_orders_df['revenue'].sum()) if not daily_orders_df.empty else 0.0
avg_order_value = compute_aov(main_df)
repeat_rate = compute_repeat_purchase_rate(main_df)

# ------------------------------
# Header + KPI band
# ------------------------------
st.title("TrendTracker — Fashion Dashboard (EN)")
k1, k2, k3, k4 = st.columns([1.6, 1.6, 1.6, 1.6])
k1.metric("Total Orders", f"{total_orders:,}")
k2.metric("Total Revenue", format_aud(total_revenue))
k3.metric("Avg Order Value (AOV)", format_aud(avg_order_value))
k4.metric("Repeat Purchase Rate", f"{repeat_rate*100:.1f}%")

st.markdown("---")

# ------------------------------
# Main layout: left charts & right actions
# ------------------------------
left_col, right_col = st.columns([3, 1.15])

with left_col:
    # Orders over time
    st.subheader("Orders Over Time")
    fig, ax = plt.subplots(figsize=(12, 4))
    if not daily_orders_df.empty:
        ax.plot(daily_orders_df['order_date'], daily_orders_df['order_count'], marker='o', linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Orders")
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    st.pyplot(fig)

    # Top Products
    st.subheader("Top Product Performance")
    top_products = sum_order_items_df.head(top_n)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=top_products, x="quantity_x", y="product_name", palette="Blues_d", ax=ax2)
    ax2.set_xlabel("Units Sold")
    ax2.set_ylabel(None)
    if show_values_on_bars:
        for i, v in enumerate(top_products["quantity_x"]):
            ax2.text(v, i, f" {v:,}", va="center", fontsize=10)
    st.pyplot(fig2)

    # Customer Demographics Snapshot
    st.subheader("Customer Demographics Snapshot")
    d1, d2 = st.columns(2)
    with d1:
        gender_counts = bygender_df.sort_values(by='customer_count', ascending=False)
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.barplot(data=gender_counts, x="gender", y="customer_count", ax=ax3)
        ax3.set_ylabel("Unique Customers")
        st.pyplot(fig3)
    with d2:
        age_counts = byage_df.sort_values(by='customer_count', ascending=False)
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.barplot(data=age_counts, x="age_group", y="customer_count", order=['Youth','Adults','Seniors'], ax=ax4)
        st.pyplot(fig4)

    # RFM plots (kept original charts)
    st.subheader("RFM — Top Customers (sample)")
    fig_rfm, ax_rfm = plt.subplots(nrows=1, ncols=3, figsize=(18, 4))
    try:
        asc_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
        sns.barplot(y='recency', x='customer_id', data=asc_recency, palette=['#90CAF9'], ax=ax_rfm[0])
        ax_rfm[0].set_title('By Recency (days)')

        desc_freq = rfm_df.sort_values(by='frequency', ascending=False).head(5)
        sns.barplot(y='frequency', x='customer_id', data=desc_freq, palette=['#90CAF9'], ax=ax_rfm[1])
        ax_rfm[1].set_title('By Frequency')

        desc_monetary = rfm_df.sort_values(by='monetary', ascending=False).head(5)
        sns.barplot(y='monetary', x='customer_id', data=desc_monetary, palette=['#90CAF9'], ax=ax_rfm[2])
        ax_rfm[2].set_title('By Monetary')
    except Exception:
        pass
    st.pyplot(fig_rfm)

    # ------------------------------
    # Advanced analyses: Cohort, AOV, CLTV, Delivery time, RFM segments
    # ------------------------------
    st.markdown("---")
    st.header("Advanced Analyses")

    # 1) Cohort retention heatmap
    st.subheader("Cohort Retention (Monthly)")
    if not main_df.empty:
        cohort_df = main_df[['customer_id','order_date']].copy()

        # converts the order_date to the first day of the month (eg. "2025-11-29" --> "2025-11-01")
        cohort_df['order_month'] = cohort_df['order_date'].dt.to_period('M').dt.to_timestamp()

        # Finding , per customer_id--> first purchase date and extract the month--> cohort month
        # "cohort month"--> the month they first became a customer
        first_order = cohort_df.groupby('customer_id')['order_date'].min().reset_index()
        first_order['cohort_month'] = first_order['order_date'].dt.to_period('M').dt.to_timestamp()

        # left Joining cohort_df + first_order on--> customer_id
        # so for each customer, we have cohort month, every order month
        cohort_df = cohort_df.merge(first_order[['customer_id','cohort_month']], on='customer_id', how='left')

        # period number: how many months? -->  since cohort month (customer's first purchase)
        # That is, each order month - cohort month
        # Example: If first purchase was in January and current order is in March, period_number = 2.
        cohort_df['period_number'] = (
            cohort_df['order_month'].dt.to_period('M').astype(int) - cohort_df['cohort_month'].dt.to_period('M').astype(int)
        )

        # cohort counts= per cohort , per period number--> how many unique customers
        # shows customer retention over time for each cohort
        cohort_counts = cohort_df.groupby(['cohort_month','period_number'])['customer_id'].nunique().reset_index()
        
        # now pivot table, rows--> cohorts (by month), columns--> period number (no of months since first purchase)
        # values--> customer_id (unique customers)
        cohort_pivot = cohort_counts.pivot(index='cohort_month', columns='period_number', values='customer_id')
        
        # 
        if cohort_pivot is not None and not cohort_pivot.empty:
            # cohort size--> Per cohort month --> no of customers in the first period number column. 
            # This is the starting size of each cohort
            cohort_sizes = cohort_pivot.iloc[:,0] # no of customers in each cohort (# Get first column (period 0))

            
            # Dividing each number in the row by that cohort'starting size, replacing Nan with 0
            # Example: (Before division)
               # cohort_month	0 (month 0)	1 (month 1)	2 (month 2)
               #  Jan-2025	       100	         80	       60
               #  Feb-2025	       150	         90	       NaN
            # After division: (example)
              #  cohort_month	0	 1	    2
              #  Jan-2025	  1.0	 0.8	0.6
              #  Feb-2025     1.0	 0.6	NaN
            # So, Jan-2025 cohort retained 80% of customers in the first month, 60% in the second month.
            retention = cohort_pivot.divide(cohort_sizes, axis=0).fillna(0) # Convert to percentages
            
            # visualizing as heatmap
            fig_cohort, ax_cohort = plt.subplots(figsize=(12, max(4, 0.5*len(retention))))
            sns.heatmap(retention, annot=True, fmt=".0%", cmap="YlGnBu", ax=ax_cohort)
            ax_cohort.set_title("Cohort Retention (by months since first purchase)")
            ax_cohort.set_ylabel("Cohort month")
            ax_cohort.set_xlabel("Months since cohort")
            st.pyplot(fig_cohort)
            st.markdown("**Interpretation idea:** look for steep drop-offs in the first 1–3 months — those are retention opportunities.")
        else:
            st.info("Not enough cohort data for a retention heatmap.")
    else:
        st.info("No data for cohort analysis with current filters.")

    # 2) Monthly AOV trend
    st.subheader("AOV Trend (Monthly)")
    
    # 1. Per order_id, per order_month--> find total price (since per order_id may contain many order items)
    # 2. Extract month --> from order_date
    # 3. now, per month--> find mean of total price
    # Example:- If, 
    #    order_id    order_date       total_price      month
    #        101    2025-01-01          150        2025-01-01
    #        102    2025-01-01          200        2025-01-01
    #        103    2025-02-01          150        2025-02-01
    #    Then, per month (may contain many orders)--> find mean of total price
    #        month          total_price
    #     2025-01-01        175.0       # (150 + 200) / 2 = 175
    #     2025-02-01        150.0       # Only one order in February
    if not main_df.empty:
        orders_tot = main_df.groupby(['order_id', pd.Grouper(key='order_date', freq='M')])['total_price'].sum().reset_index()
        orders_tot['month'] = orders_tot['order_date'].dt.to_period('M').dt.to_timestamp()
        aov_monthly = orders_tot.groupby('month')['total_price'].mean().reset_index()
        fig_aov, ax_aov = plt.subplots(figsize=(10,3))
        ax_aov.plot(aov_monthly['month'], aov_monthly['total_price'], marker='o', linewidth=2)
        ax_aov.set_title("Monthly AOV")
        ax_aov.set_ylabel("AUD (avg order)")
        fig_aov.autofmt_xdate()
        st.pyplot(fig_aov)
        if not aov_monthly.empty:
            latest_aov = aov_monthly['total_price'].iloc[-1]
            st.metric("Latest AOV", format_aud(latest_aov))
    else:
        st.info("No data to compute AOV.")

    # 3) CLTV (simple) distribution
    st.subheader("Customer Value (CLTV proxy)")
    if not rfm_df.empty:
        cltv_df = rfm_df.copy()
        cltv_df['cltv'] = cltv_df['monetary']  # simple proxy
        fig_cltv, ax_cltv = plt.subplots(figsize=(10,3))
        sns.histplot(cltv_df['cltv'].dropna(), bins=50, log_scale=(True, False), ax=ax_cltv)
        ax_cltv.set_xlabel("CLTV (AUD)")
        ax_cltv.set_title("Distribution of Customer Value (monetary)")
        st.pyplot(fig_cltv)
        top_customers = cltv_df.sort_values(by='cltv', ascending=False).head(10)
        st.table(top_customers[['customer_id','cltv','frequency']].assign(cltv=lambda df: df['cltv'].map(lambda x: format_aud(x))))
    else:
        st.info("RFM data not available for CLTV.")

    # 4) Delivery time distribution (ops)
    st.subheader("Delivery Time Distribution")
    if 'delivery_date' in main_df.columns and main_df['delivery_date'].notna().any():
        dt = (main_df['delivery_date'] - main_df['order_date']).dt.days.dropna()
        if not dt.empty:
            fig_dt, ax_dt = plt.subplots(figsize=(8,3))
            sns.histplot(dt, bins=30, kde=True, ax=ax_dt)
            ax_dt.set_xlabel("Delivery time (days)")
            ax_dt.set_title("Distribution of Delivery Time")
            st.pyplot(fig_dt)
            st.metric("Median delivery (days)", f"{int(dt.median())}")
        else:
            st.info("No delivery_date values in filtered data.")
    else:
        st.info("Delivery time chart: delivery_date not available in filtered data.")

    # 5) RFM segmentation simple visualization
    st.subheader("RFM Segments (quintiles)")
    # Quintile==> divides a dataset into 5 equal groups, each representing 20% of the data

    if not rfm_df.empty:
        rfm_score = rfm_df.copy()
        # For recency: lower recency is better so invert scores: smallest recency -> highest rank
        # # We subtract from 5 to make higher scores better
        try:
            rfm_score['r_quintile'] = pd.qcut(rfm_score['recency'], 5, labels=False, duplicates='drop')  # 0..4
            rfm_score['r_quintile'] = 5 - rfm_score['r_quintile']  # invert so 5 is best
        except Exception:
            rfm_score['r_quintile'] = 3
        
        # For frequency: Higher is better
        # # Using .rank(method='first') to handle ties
        try:
            rfm_score['f_quintile'] = pd.qcut(rfm_score['frequency'].rank(method='first'), 5, labels=False, duplicates='drop') + 1
            rfm_score['m_quintile'] = pd.qcut(rfm_score['monetary'], 5, labels=False, duplicates='drop') + 1
        except Exception:
            rfm_score['f_quintile'] = 3
            rfm_score['m_quintile'] = 3
        
        # Combining scores into RFM score.
        rfm_score['rfm_score'] = rfm_score['r_quintile'].astype(int).astype(str) + rfm_score['f_quintile'].astype(int).astype(str) + rfm_score['m_quintile'].astype(int).astype(str)

        # How to interpret RFM score
        # eg 1) If RFM score= 555, then it is the best customer (recent, frequent, high spenders)
        # eg 2) If RFM score= 111, then it is the worst customer- Least valuable customers (inactive, rare, low spenders)
        # eg 3) If RFM score= 351, then They buy often but low spending per order (low monetary)

        # Count customers in each RFM segment and sprt by count
        seg_counts = rfm_score.groupby('rfm_score').size().reset_index(name='count').sort_values(by='count', ascending=False)
        if not seg_counts.empty:
            # barplot of top 10 most common RFM segments
            fig_seg, ax_seg = plt.subplots(figsize=(8,3))
            sns.barplot(data=seg_counts.head(10), x='rfm_score', y='count', ax=ax_seg)
            ax_seg.set_title("Top RFM score counts")
            st.pyplot(fig_seg)

            # revenue share by segment

            # Calculate total revenue per customer
            cust_rev = main_df.groupby('customer_id', as_index=False).total_price.sum().rename(columns={'total_price':'customer_revenue'})
            # Merge wtih RFM scores
            merged = rfm_score.merge(cust_rev, on='customer_id', how='left')
            # Group by RFM score and calculate total revenue
            seg_rev = merged.groupby('rfm_score')['customer_revenue'].sum().reset_index().sort_values(by='customer_revenue', ascending=False)
            
            # Display the top revenue-generating segments
            st.write("Top segments by revenue (sample):")
            if not seg_rev.empty:
                st.dataframe(seg_rev.assign(customer_revenue=lambda df: df['customer_revenue'].map(lambda x: format_aud(x))))
        else:
            st.info("Not enough RFM variation to segment.")
    else:
        st.info("RFM data not available for segmentation.")


# QUICK ACTIONS & EXPORTS section
with right_col:
    st.subheader("Quick Actions & Exports")
    st.write(f"Filtered rows: **{len(main_df):,}**")
    st.write(f"Unique customers: **{main_df['customer_id'].nunique():,}**")
    st.write(f"Unique products: **{main_df['product_name'].nunique():,}**")
    st.markdown("---")

    # CSV & Excel downloads
    csv_bytes = main_df.to_csv(index=False).encode('utf-8')
    excel_buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            main_df.to_excel(writer, index=False, sheet_name='filtered')
        excel_buffer.seek(0)
        st.download_button("Download filtered CSV", data=csv_bytes, file_name="trendtracker_filtered.csv", mime="text/csv")
        st.download_button("Download filtered Excel", data=excel_buffer, file_name="trendtracker_filtered.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        # fallback: provide CSV only if openpyxl missing
        st.download_button("Download filtered CSV", data=csv_bytes, file_name="trendtracker_filtered.csv", mime="text/csv")
        st.warning("Excel export requires openpyxl. Install it (pip install openpyxl) to enable Excel downloads.")

    st.markdown("---")
    st.subheader("Download Charts")
    # `fig_to_bytes()` : Function to convert matplotlib figures to downloadable PNGs.
    st.download_button("Download Orders chart (PNG)", data=fig_to_bytes(fig), file_name="orders_over_time.png", mime="image/png")
    st.download_button("Download Top products (PNG)", data=fig_to_bytes(fig2), file_name="top_products.png", mime="image/png")

    st.markdown("---")
    st.subheader("Auto insights (sample)")
    # Calculate top 3 states by total revenue
    top_states = main_df.groupby("state").total_price.sum().reset_index().sort_values(by="total_price", ascending=False).head(3)
    if not top_states.empty:
        for i, row in top_states.iterrows():
            st.write(f"- {row['state']}: {format_aud(row['total_price'])}")
    else:
        st.write("No state revenue for current filters")

st.markdown("---")
st.caption("Notes: Currency uses en_US formatting (AUD). Replace DATA_URL with a local file path if you want offline use.")
