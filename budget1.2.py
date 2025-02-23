import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Set the page configuration
st.set_page_config(layout="wide", page_title="Budget Management", initial_sidebar_state="expanded")

# Initialize session state to persist the data between interactions
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'Category': ['Business Registration', 'Website Development', 'Office Furnishing', 'Staff Hiring', 'Sales Hiring', 'Licenses'],
        'Fixed Costs': [40000, 150000, 200000, 60000, 50000, 10000],
        'Variable Costs': [10000, 30000, 20000, 60000, 50000, 1000],
        'Actual Costs': [0, 0, 0, 0, 0, 0]
    })

if 'df_dept' not in st.session_state:
    st.session_state.df_dept = pd.DataFrame({
        'Department': ['Marketing', 'Operations', 'HR', 'Sales'],
        'Fixed Budget': [10000, 150000, 50000, 30000],
        'Variable Budget': [2000, 3000, 1000, 4000],
        'Actual Spend': [0, 0, 0, 0]
    })

if 'forecast_df' not in st.session_state:
    current_month = datetime.now().month
    months = [datetime(2025, month, 1).strftime('%B') for month in range(current_month, current_month + 6)]
    inflows = [12000] * 6
    outflows = [12530] * 6
    net_cash_flow = np.array(inflows) - np.array(outflows)

    st.session_state.forecast_df = pd.DataFrame({
        'Month': months,
        'Inflows': inflows,
        'Outflows': outflows,
        'Net Cash Flow': net_cash_flow
    })

# Set default role (for testing purposes, set to 'admin', 'staff', or 'guest')
if 'role' not in st.session_state:
    st.session_state.role = 'admin'  # Change this to 'staff' or 'guest' as needed

# Function to calculate total costs
def calculate_totals(df):
    total_fixed_cost = df['Fixed Costs'].sum()
    total_variable_cost = df['Variable Costs'].sum()
    total_actual_cost = df['Actual Costs'].sum()
    return total_fixed_cost, total_variable_cost, total_actual_cost

# Add Category function
def add_category(category_name, fixed_cost, variable_cost, actual_cost):
    new_entry = pd.DataFrame({
        'Category': [category_name],
        'Fixed Costs': [fixed_cost],
        'Variable Costs': [variable_cost],
        'Actual Costs': [actual_cost]
    })
    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)

# Function to delete a category
def delete_category(index):
    df = st.session_state.df.drop(index).reset_index(drop=True)
    st.session_state.df = df

# Function to update a category
def update_category(index, fixed_cost, variable_cost, actual_cost):
    st.session_state.df.at[index, 'Fixed Costs'] = fixed_cost
    st.session_state.df.at[index, 'Variable Costs'] = variable_cost
    st.session_state.df.at[index, 'Actual Costs'] = actual_cost

# Add department function
def add_department(department_name, fixed_budget, variable_budget, actual_spend):
    new_department = pd.DataFrame({
        'Department': [department_name],
        'Fixed Budget': [fixed_budget],
        'Variable Budget': [variable_budget],
        'Actual Spend': [actual_spend]
    })
    st.session_state.df_dept = pd.concat([st.session_state.df_dept, new_department], ignore_index=True)

# Update department function
def update_department(index, fixed_budget, variable_budget, actual_spend):
    st.session_state.df_dept.at[index, 'Fixed Budget'] = fixed_budget
    st.session_state.df_dept.at[index, 'Variable Budget'] = variable_budget
    st.session_state.df_dept.at[index, 'Actual Spend'] = actual_spend

# Delete department function
def delete_department(index):
    st.session_state.df_dept = st.session_state.df_dept.drop(index).reset_index(drop=True)

# Update forecast function
def update_forecast(df, month, inflow, outflow):
    df.at[month, 'Inflows'] = inflow
    df.at[month, 'Outflows'] = outflow
    df.at[month, 'Net Cash Flow'] = inflow - outflow
    return df

# Header
st.title('💼 Budget Management System XYZ Group')

# Sidebar for navigation
st.sidebar.title("📊 Navigation")
section = st.sidebar.radio("Select Section", ['Overview', 'Departmental Budgets', 'Cash Flow Forecast', 'Reports', 'Settings'])

# SECTION 1: Overview
if section == 'Overview':
    st.subheader('📊 Overview of Financial Data')

    # Display the cost data table first
    with st.expander("Cost Breakdown"):
        st.dataframe(st.session_state.df)

        # Recalculate totals based on updated data
        total_fixed_cost, total_variable_cost, total_actual_cost = calculate_totals(st.session_state.df)

        # Display updated totals
        col1, col2 = st.columns([2, 1])  # Two columns for cleaner display
        with col1:
            st.markdown(f"#### **Total Fixed Costs (Budget)**: ${total_fixed_cost:,}")
            st.markdown(f"#### **Total Variable Costs (Budget)**: ${total_variable_cost:,}")
            st.markdown(f"#### **Total Actual Costs**: ${total_actual_cost:,}")
        
        # Pie chart of cost distribution
        with col2:
            st.write("### **Cost Distribution (Fixed vs Variable)**")
            fig = px.pie(names=['Fixed Costs', 'Variable Costs'], values=[total_fixed_cost, total_variable_cost],
                         title='Cost Distribution', color=['#FF5733', '#33C1FF'])
            st.plotly_chart(fig)

    # Add, update, delete for cost categories (conditional based on role)
    if st.session_state.role == 'admin':
        with st.expander("Add, Update, or Delete Category"):
            category_list = st.session_state.df['Category'].tolist()
            
            # Add new category
            st.write("### Add New Category")
            category_name = st.text_input("Category Name")
            fixed_cost = st.number_input("Fixed Cost", min_value=0)
            variable_cost = st.number_input("Variable Cost", min_value=0)
            actual_cost = st.number_input("Actual Cost", min_value=0)

            if st.button("Add Category"):
                add_category(category_name, fixed_cost, variable_cost, actual_cost)
                st.success(f"Category '{category_name}' added!")

            # Update existing category
            st.write("### Update Existing Category")
            category_to_update = st.selectbox("Select Category to Update", category_list)
            index_to_update = st.session_state.df[st.session_state.df['Category'] == category_to_update].index[0]

            # Display current values
            current_fixed_cost = st.session_state.df.at[index_to_update, 'Fixed Costs']
            current_variable_cost = st.session_state.df.at[index_to_update, 'Variable Costs']
            current_actual_cost = st.session_state.df.at[index_to_update, 'Actual Costs']

            # Input fields for update
            new_fixed_cost = st.number_input("Fixed Cost", min_value=0, value=current_fixed_cost)
            new_variable_cost = st.number_input("Variable Cost", min_value=0, value=current_variable_cost)
            new_actual_cost = st.number_input("Actual Cost", min_value=0, value=current_actual_cost)

            if st.button("Update Category"):
                update_category(index_to_update, new_fixed_cost, new_variable_cost, new_actual_cost)
                st.success(f"Category '{category_to_update}' updated!")

            # Delete category
            if st.button("Delete Category"):
                delete_category(index_to_update)
                st.success(f"Category '{category_to_update}' deleted!")

# SECTION 2: Departmental Budgets
if section == 'Departmental Budgets':
    st.subheader('🏢 Departmental Budgets')

    # Display the department data table first
    with st.expander("Department Budget Breakdown"):
        st.dataframe(st.session_state.df_dept)

        # Calculate totals
        total_fixed_budget = st.session_state.df_dept['Fixed Budget'].sum()
        total_variable_budget = st.session_state.df_dept['Variable Budget'].sum()
        total_actual_spend = st.session_state.df_dept['Actual Spend'].sum()

        # Display totals
        st.markdown(f"#### **Total Fixed Budget**: ${total_fixed_budget:,}")
        st.markdown(f"#### **Total Variable Budget**: ${total_variable_budget:,}")
        st.markdown(f"#### **Total Actual Spend**: ${total_actual_spend:,}")

    # Add, update, delete for departments (conditional based on role)
    if st.session_state.role == 'admin':
        with st.expander("Add, Update, or Delete Department"):
            dept_list = st.session_state.df_dept['Department'].tolist()

            # Add new department
            st.write("### Add New Department")
            department_name = st.text_input("Department Name")
            fixed_budget = st.number_input("Fixed Budget", min_value=0)
            variable_budget = st.number_input("Variable Budget", min_value=0)
            actual_spend = st.number_input("Actual Spend", min_value=0)

            if st.button("Add Department"):
                add_department(department_name, fixed_budget, variable_budget, actual_spend)
                st.success(f"Department '{department_name}' added!")

            # Update existing department
            st.write("### Update Existing Department")
            department_to_update = st.selectbox("Select Department to Update", dept_list)
            index_to_update = st.session_state.df_dept[st.session_state.df_dept['Department'] == department_to_update].index[0]

            # Display current values
            current_fixed_budget = st.session_state.df_dept.at[index_to_update, 'Fixed Budget']
            current_variable_budget = st.session_state.df_dept.at[index_to_update, 'Variable Budget']
            current_actual_spend = st.session_state.df_dept.at[index_to_update, 'Actual Spend']

            # Input fields for update
            new_fixed_budget = st.number_input("Fixed Budget", min_value=0, value=current_fixed_budget)
            new_variable_budget = st.number_input("Variable Budget", min_value=0, value=current_variable_budget)
            new_actual_spend = st.number_input("Actual Spend", min_value=0, value=current_actual_spend)

            if st.button("Update Department"):
                update_department(index_to_update, new_fixed_budget, new_variable_budget, new_actual_spend)
                st.success(f"Department '{department_to_update}' updated!")

            # Delete department
            if st.button("Delete Department"):
                delete_department(index_to_update)
                st.success(f"Department '{department_to_update}' deleted!")

# SECTION 3: Cash Flow Forecast
if section == 'Cash Flow Forecast':
    st.subheader('💵 Cash Flow Forecast')

    # Display the forecast data table
    with st.expander("Cash Flow Forecast Breakdown"):
        st.dataframe(st.session_state.forecast_df)

    # Add, update, delete for forecast (conditional based on role)
    if st.session_state.role == 'admin':
        with st.expander("Update Cash Flow Forecast"):
            months = st.session_state.forecast_df['Month'].tolist()
            month_to_update = st.selectbox("Select Month", months)

            # Get index of the selected month
            month_index = st.session_state.forecast_df[st.session_state.forecast_df['Month'] == month_to_update].index[0]

            inflow = st.number_input(f"Inflows for {month_to_update}", min_value=0)
            outflow = st.number_input(f"Outflows for {month_to_update}", min_value=0)

            if st.button(f"Update Forecast for {month_to_update}"):
                st.session_state.forecast_df = update_forecast(st.session_state.forecast_df, month_index, inflow, outflow)
                st.success(f"Forecast for {month_to_update} updated!")

# SECTION 4: Reports
if section == 'Reports':
    st.subheader('📑 Financial Reports')

    # Report generation logic (this can be further expanded)

# SECTION 5: Settings
if section == 'Settings':
    st.subheader('⚙️ Settings')

    # Allow changing user role for testing purposes
    new_role = st.selectbox("Select User Role", ['admin', 'staff', 'guest'])
    st.session_state.role = new_role
    st.write(f"Current User Role: {st.session_state.role}")
