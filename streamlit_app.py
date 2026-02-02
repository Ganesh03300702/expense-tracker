import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database
import analytics

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS (Teal/Mint Theme) ---
# Primary: #00BFA6, Dark BG: #0D1B1E, Card: #1B2B30
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0D1B1E;
        color: #FFFFFF;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1B2B30;
    }
    
    /* Inputs */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #2B3B40; 
        color: white;
        border-radius: 10px;
    }
    
    /* Buttons (Primary Teal) */
    div.stButton > button {
        background-color: #00BFA6;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #26A69A;
        border: none;
        color: white;
    }
    
    /* Metrics/Cards */
    div[data-testid="metric-container"] {
        background-color: #1B2B30;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00BFA6 !important;
        font-family: 'Roboto', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Expense Tracker")
    st.markdown("---")
    menu = st.radio("Navigation", ["Dashboard", "Add Expense", "History"], label_visibility="collapsed")
    st.markdown("---")
    st.info("💡 **Tip**: Switch between Light/Dark mode in Streamlit Settings (top right) to see how the custom CSS adapts (it is optimized for Dark Mode).")

# --- FUNCTIONS ---
def refresh_data():
    # Helper to clear cache if needed, though direct DB calls here don't cache by default
    pass

# --- PAGES ---

if menu == "Dashboard":
    st.title("📊 Financial Dashboard")
    
    # KPIs
    total_spending = analytics.get_total_spending()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Spending", value=f"${total_spending:,.2f}", delta=None)
    
    st.markdown("### Spending Analysis")
    
    cat_summary = analytics.get_category_summary()
    monthly_summary = analytics.get_monthly_summary()
    
    if not cat_summary:
        st.info("No data available yet. Go to **Add Expense** to get started!")
    else:
        col_charts1, col_charts2 = st.columns(2)
        
        # Pie Chart (Plotly)
        with col_charts1:
            st.subheader("By Category")
            df_cat = pd.DataFrame(list(cat_summary.items()), columns=['Category', 'Amount'])
            fig_pie = px.pie(df_cat, values='Amount', names='Category', 
                             color_discrete_sequence=['#00BFA6', '#26A69A', '#4DB6AC', '#80CBC4', '#B2DFDB'])
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Bar Chart (Plotly)
        with col_charts2:
            st.subheader("Monthly Trends")
            df_month = pd.DataFrame(list(monthly_summary.items()), columns=['Month', 'Amount'])
            fig_bar = px.bar(df_month, x='Month', y='Amount', 
                             color_discrete_sequence=['#00BFA6'])
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white",
                                  xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333'))
            st.plotly_chart(fig_bar, use_container_width=True)

elif menu == "Add Expense":
    st.title("➕ Add New Expense")
    
    with st.container():
        st.write("Fill out the details below:")
        
        c1, c2 = st.columns(2)
        date_input = c1.date_input("Date", datetime.now())
        category_input = c2.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"])
        
        amount_input = st.number_input("Amount ($)", min_value=0.0, step=0.01, format="%.2f")
        desc_input = st.text_input("Description", placeholder="e.g. Groceries at Walmart")
        
        if st.button("Save Expense", type="primary"):
            if amount_input > 0:
                database.add_expense(date_input.strftime("%Y-%m-%d"), category_input, amount_input, desc_input)
                st.success("✅ Expense Added Successfully!")
                st.balloons()
            else:
                st.error("⚠️ Amount must be greater than 0.")

elif menu == "History":
    st.title("📜 Transaction History")
    
    # Fetch Data
    expenses = database.fetch_expenses()
    if not expenses:
        st.info("No transaction history found.")
    else:
        # Convert to DataFrame for better display
        df = pd.DataFrame(expenses, columns=["ID", "Date", "Category", "Amount", "Description"])
        
        # Format Amount
        df['Amount'] = df['Amount'].apply(lambda x: f"${x:.2f}")
        
        # Display Table
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
        
        # Export Actions
        csv = df.drop(columns=["ID"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name='expenses.csv',
            mime='text/csv',
        )
        
        st.markdown("---")
        st.markdown("**Note:** To delete transactions, please use the Desktop App version.")
