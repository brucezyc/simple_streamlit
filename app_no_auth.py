import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
import os
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION - MUST BE THE FIRST STREAMLIT COMMAND
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pro Sales Dashboard (MVP)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    """The main function that runs the Streamlit dashboard."""
    
    # --- SESSION STATE INITIALIZATION ---
    if "sales_data" not in st.session_state:
        dates = pd.date_range(start="2024-01-01", periods=100)
        products = ["Laptop", "Mouse", "Monitor", "Headset", "Printer"]
        regions = ["North", "South", "East", "West"]
        data = {
            "Date": dates, "Product": np.random.choice(products, 100),
            "Region": np.random.choice(regions, 100), "Units Sold": np.random.randint(1, 50, 100),
            "Unit Price": np.random.uniform(20, 1500, 100).round(2),
            "Status": np.random.choice(["Completed", "Pending", "Cancelled"], 100),
            "Rating": np.random.randint(1, 6, 100)
        }
        st.session_state.sales_data = pd.DataFrame(data)

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.subheader("Global Filters")
        
        # Product Filter
        selected_products = st.multiselect(
            "Select Products",
            options=st.session_state.sales_data["Product"].unique(),
            default=st.session_state.sales_data["Product"].unique()
        )
        
        # Region Filter
        selected_regions = st.multiselect(
            "Select Regions",
            options=st.session_state.sales_data["Region"].unique(),
            default=st.session_state.sales_data["Region"].unique()
        )
        
        # Status Filter
        status_filter = st.radio("Order Status", ["All", "Completed", "Pending"])
        
        st.divider()
        st.subheader("Display Settings")
        show_raw_data = st.toggle("Show Raw Data Tab", True)
        theme_color = st.color_picker("Chart Theme Color", "#2E86C1")
        
        # Inject custom CSS for multiselect tags
        st.markdown(
            f"""
            <style>
            span[data-baseweb="tag"] {{
                background-color: {theme_color} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        # st.info("💡 Tip: Double-click cells in the table to edit data.")

    # --- DATA PROCESSING ---
    df_filtered = st.session_state.sales_data.copy()
    
    # Apply filters
    if selected_products:
        df_filtered = df_filtered[df_filtered["Product"].isin(selected_products)]
    if selected_regions:
        df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]
    if status_filter != "All":
        df_filtered = df_filtered[df_filtered["Status"] == status_filter]
        
    df_filtered["Revenue"] = df_filtered["Units Sold"] * df_filtered["Unit Price"]

    # --- MAIN DASHBOARD LAYOUT ---
    st.title("📈 Executive Sales Overview")
    st.markdown(f"Data snapshot for **{len(df_filtered)}** transactions.")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    total_revenue = df_filtered["Revenue"].sum()
    total_units = df_filtered["Units Sold"].sum()
    avg_rating = df_filtered["Rating"].mean()
    completion_rate = (len(df_filtered[df_filtered['Status'] == 'Completed']) / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
    col1.metric("Total Revenue", f"${total_revenue:,.2f}", "+4.5%")
    col2.metric("Units Sold", f"{total_units:,}", "-1.2%")
    col3.metric("Avg Customer Rating", f"{avg_rating:.1f} ⭐", "0.2")
    col4.metric("Completion Rate", f"{completion_rate:.1f}%", "1.5%")
    st.divider()

    # Tabs
    tab_definitions = ["📊 Visual Analytics", "🧠 Deep Dive", "📄 From HTML"]
    if show_raw_data:
        tab_definitions.insert(1, "📝 Data Editor")
        tab_definitions.insert(2, "New Table")
    tab_map = {title: tab for title, tab in zip(tab_definitions, st.tabs(tab_definitions))}

    with tab_map["📊 Visual Analytics"]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Revenue Trend over Time")
            st.altair_chart(alt.Chart(df_filtered).mark_line(color=theme_color).encode(x='Date', y='Revenue', tooltip=['Date', 'Revenue', 'Product']).interactive(), use_container_width=True)
        with c2:
            st.subheader("Sales by Region")
            st.bar_chart(df_filtered, x="Region", y="Revenue", color="Product")

    if show_raw_data:
        with tab_map["📝 Data Editor"]:
            st.subheader("✏️ Master Data Management")
            edited_df = st.data_editor(
                st.session_state.sales_data, num_rows="dynamic", use_container_width=True, height=500,
                column_config={
                    "Unit Price": st.column_config.NumberColumn("Price ($)", format="$%.2f", min_value=0, step=0.01),
                    "Rating": st.column_config.NumberColumn("Rating", help="Customer rating 1-5", min_value=1, max_value=5, step=1, format="%d ⭐"),
                    "Status": st.column_config.SelectboxColumn("Order Status", options=["Completed", "Pending", "Cancelled"], required=True),
                    "Date": st.column_config.DateColumn("Transaction Date", format="YYYY-MM-DD"),
                    "Product": st.column_config.TextColumn("Product Name", validate="^[a-zA-Z0-9 ]+$")
                }
            )
            if not edited_df.equals(st.session_state.sales_data):
                st.session_state.sales_data = edited_df
                st.rerun()
        with tab_map["New Table"]:
            st.subheader("A New Excel-like Table")
            edited_df_new = st.data_editor(st.session_state.sales_data, num_rows="dynamic", use_container_width=True, key="new_editor", height=400)
            if not edited_df_new.equals(st.session_state.sales_data):
                st.session_state.sales_data = edited_df_new
                st.rerun()

    with tab_map["🧠 Deep Dive"]:
        st.subheader("Top Performers")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Top 5 Products by Revenue")
            st.dataframe(df_filtered.groupby("Product")["Revenue"].sum().sort_values(ascending=False).head(5), use_container_width=True)
        with col_b:
            st.markdown("#### Status Distribution")
            st.altair_chart(alt.Chart(df_filtered).mark_arc(outerRadius=120).encode(theta=alt.Theta("count()", stack=True), color=alt.Color("Status", scale=alt.Scale(scheme='category20')), tooltip=["Status", "count()"]), use_container_width=True)

    with tab_map["📄 From HTML"]:
        st.subheader("Embedded HTML Content")
        # Get the absolute path to the directory of the current script
        _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(_CURRENT_DIR, 'partial.html')
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                components.html(f.read(), height=300, scrolling=True)
        except FileNotFoundError:
            st.error(f"The 'partial.html' file was not found. Please ensure it is in the same directory.")

    # --- EXPORT SECTION ---
    st.divider()
    if st.button("💾 Export Current View to CSV"):
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name='sales_dashboard_export.csv', mime='text/csv')

# -----------------------------------------------------------------------------
# 3. SCRIPT EXECUTION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
