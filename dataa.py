import numpy as np
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from consumer import maps, tables
from zero_waste_stats import StoreDataAnalysisDashboard
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os




def dat():

    food_products = {
        "Dairy Products": {
            "brands": ["Nestlé", "Danone", "Parmalat", "President", "Amul", "Campina"],
            "products": ["Milk", "Yogurt", "Kefir", "Cheese", "Cottage Cheese", "Cream", "Butter"]
        },
        "Bakery Products": {
            "brands": ["Barilla", "Makfa", "Ozon", "Pioner", "Yashkino"],
            "products": ["Wheat Flour", "Pasta", "Bread", "Biscuits", "Noodles", "Buns"]
        },
        "Meat Products": {
            "brands": ["Tyson", "Oscar Mayer", "Hormel", "Perdue", "Cherkizovo"],
            "products": ["Beef", "Lamb", "Poultry", "Sausage", "Hot Dogs", "Smoked Meat"]
        },
        "Beverages": {
            "brands": ["Coca-Cola", "Pepsi", "Nestlé Pure Life", "Lipton", "Nescafé"],
            "products": ["Mineral Water", "Carbonated Drinks", "Juices", "Tea", "Coffee"]
        },
        "Sweets": {
            "brands": ["Mars", "Ferrero", "Milka", "Nestlé", "Roshen"],
            "products": ["Chocolate", "Candies", "Cakes", "Ice Cream", "Halva", "Jam"]
        }
    }

    csv_file = "products_data.csv"

    # Initialize session state variables
    if 'uploaded_df' not in st.session_state:
        st.session_state.uploaded_df = None
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False
    if 'show_manual' not in st.session_state:
        st.session_state.show_manual = False
        
    # For button-based selection state variables
    if 'selected_direction' not in st.session_state:
        st.session_state.selected_direction = None
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None
    if 'selected_brand' not in st.session_state:
        st.session_state.selected_brand = None
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = None
    if 'date_input_method' not in st.session_state:
        st.session_state.date_input_method = None
    if 'expire_date_method' not in st.session_state:
        st.session_state.expire_date_method = None
    if 'production_year' not in st.session_state:
        st.session_state.production_year = None
    if 'production_month' not in st.session_state:
        st.session_state.production_month = None
    if 'production_day' not in st.session_state:
        st.session_state.production_day = None
    if 'expire_year' not in st.session_state:
        st.session_state.expire_year = None
    if 'expire_month' not in st.session_state:
        st.session_state.expire_month = None
    if 'expire_day' not in st.session_state:
        st.session_state.expire_day = None
    if 'brand_availability' not in st.session_state:
        st.session_state.brand_availability = None

    # Main interface
    st.title("Product Management System")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Upload"):
            st.session_state.show_upload = True
            st.session_state.show_manual = False  # Hide manual when showing upload
    with col2:
        if st.button("Manual"):
            st.session_state.show_manual = True
            st.session_state.show_upload = False  # Hide upload when showing manual
            # Reset selection state when switching to manual mode
            st.session_state.selected_direction = None
            st.session_state.selected_category = None
            st.session_state.selected_brand = None
            st.session_state.selected_product = None
            st.session_state.date_input_method = None
            st.session_state.expire_date_method = None

    # File Upload Section (shown only when "Upload" is clicked)
    if st.session_state.show_upload:
        st.subheader("File Upload")
        try:
            uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file, encoding='iso-8859-1', sep=',', on_bad_lines='skip')
                    elif uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file)
                    
                    st.success(f"File '{uploaded_file.name}' successfully loaded!")
                    # Display single editable table
                    edited_df = st.data_editor(df, num_rows="dynamic", key="upload_editor")
                    st.session_state.uploaded_df = edited_df
                    
                    # Save edited data to CSV
                    if st.button("Save Uploaded Data"):
                        if not os.path.exists(csv_file):
                            edited_df.to_csv(csv_file, index=False)
                        else:
                            df_old = pd.read_csv(csv_file)
                            df_all = pd.concat([df_old, edited_df], ignore_index=True)
                            df_all.to_csv(csv_file, index=False)
                        st.success("Uploaded data saved successfully!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    st.info("Try opening and resaving your CSV file in Excel with comma delimiter and ISO-8859-1 encoding.")
        except Exception as e:
            st.error(f"Error with file uploader: {str(e)}")

    # Manual Data Entry Section (shown when "Manual" is clicked)
    if st.session_state.show_manual:
        st.subheader("Manual Product Entry")
        
        # Direction selection with buttons
        st.write("Select product direction:")
        dir_col1, dir_col2 = st.columns(2)
        with dir_col1:
            if st.button("Food Products", key="btn_food"):
                st.session_state.selected_direction = "food_products"
                # Reset downstream selections
                st.session_state.selected_category = None
        with dir_col2:
            if st.button("Non-Food Products", key="btn_nonfood"):
                st.session_state.selected_direction = "non_food_products"
                # Reset downstream selections
                st.session_state.selected_category = None
                
        # Show the selected direction
        if st.session_state.selected_direction:
            st.write(f"Selected direction: **{st.session_state.selected_direction}**")
                
        # Category Selection (only shown after direction is selected)
        if st.session_state.selected_direction:
            st.write("Select product category:")
            
            if st.session_state.selected_direction == "food_products":
                # Create columns for food product categories
                categories = list(food_products.keys())
                category_cols = st.columns(len(categories))
                
                for i, category in enumerate(categories):
                    with category_cols[i]:
                        if st.button(category, key=f"btn_cat_{category}"):
                            st.session_state.selected_category = category
                            # Reset downstream selections
                            st.session_state.selected_brand = None
                            st.session_state.selected_product = None
            else:
                # For non-food products, use limited categories
                non_food_categories = ["Electronics", "Clothing", "Home Goods"]
                nf_category_cols = st.columns(len(non_food_categories))
                
                for i, category in enumerate(non_food_categories):
                    with nf_category_cols[i]:
                        if st.button(category, key=f"btn_cat_{category}"):
                            st.session_state.selected_category = category
                            # Reset downstream selections
                            st.session_state.selected_brand = None
                            st.session_state.selected_product = None
        
        # Show the selected category
        if st.session_state.selected_category:
            st.write(f"Selected category: **{st.session_state.selected_category}**")
            
        # Brand Selection (only shown after category is selected)
        if st.session_state.selected_category and st.session_state.selected_direction == "food_products":
            st.write("Select product brand:")
            
            # Get the brands for the selected category
            brands = food_products[st.session_state.selected_category]["brands"]
            # Create a dynamic number of columns based on how many brands
            brand_cols = st.columns(min(len(brands), 3))
            
            # Place brands in columns and create buttons
            for i, brand in enumerate(brands):
                col_index = i % len(brand_cols)
                with brand_cols[col_index]:
                    if st.button(brand, key=f"btn_brand_{brand}"):
                        st.session_state.selected_brand = brand
                        # Reset product selection
                        st.session_state.selected_product = None
        elif st.session_state.selected_category and st.session_state.selected_direction == "non_food_products":
            # For non-food products, use a text input for brand
            st.session_state.selected_brand = st.text_input("Enter product brand", "Brand Name")
            
        # Show the selected brand
        if st.session_state.selected_brand:
            st.write(f"Selected brand: **{st.session_state.selected_brand}**")
            
        # Product Selection (only shown after brand is selected)
        if st.session_state.selected_brand and st.session_state.selected_direction == "food_products":
            st.write("Select product:")
            
            # Get the products for the selected category
            products = food_products[st.session_state.selected_category]["products"]
            # Create columns for products
            product_cols = st.columns(min(len(products), 3))
            
            # Place products in columns and create buttons
            for i, product in enumerate(products):
                col_index = i % len(product_cols)
                with product_cols[col_index]:
                    if st.button(product, key=f"btn_product_{product}"):
                        st.session_state.selected_product = product
        elif st.session_state.selected_brand and st.session_state.selected_direction == "non_food_products":
            # For non-food products, use a text input for product name
            st.session_state.selected_product = st.text_input("Enter product name", "Product Name")
            
        # Show the selected product
        if st.session_state.selected_product:
            st.write(f"Selected product: **{st.session_state.selected_product}**")
            
        # Price input (only shown after product is selected)
        if st.session_state.selected_product:
            price = st.number_input("product_price", min_value=0, step=1000, value=0)
            st.write(f"{price} sum")
            
            # Production Date Selection
            st.subheader("Production Date")
            
            # Date input method buttons
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                if st.button("Direct input", key="btn_direct_date"):
                    st.session_state.date_input_method = "Direct input"
            with date_col2:
                if st.button("Step by step", key="btn_step_date"):
                    st.session_state.date_input_method = "Step by step"
                    
            # Show the selected date input method
            if st.session_state.date_input_method:
                st.write(f"Selected method: **{st.session_state.date_input_method}**")
            
            production_date = ""
            if st.session_state.date_input_method == "Direct input":
                # Get current date for the default and validation
                current_date = datetime.now()
                default_date = f"{current_date.day:02d}.{current_date.month:02d}.{current_date.year}"
                
                production_date = st.text_input("production_date (dd.mm.yyyy)", value=default_date)
                
                # Validate the direct input date is not in the future
                try:
                    input_date = datetime.strptime(production_date, "%d.%m.%Y")
                    if input_date > current_date:
                        st.error("Production date cannot be in the future!")
                        production_date = default_date
                except:
                    st.error("Invalid date format. Please use dd.mm.yyyy format.")
                    production_date = default_date
            elif st.session_state.date_input_method == "Step by step":
                # Year selection
                st.write("Select production year:")
                year_cols = st.columns(6)
                
                # Get current date
                current_date = datetime.now()
                current_year = current_date.year
                
                # Limit years to range from 2020 up to current year
                years = list(range(2020, current_year + 1))
                for i, year in enumerate(years):
                    with year_cols[i % 6]:  # Ensure we don't exceed number of columns
                        if st.button(str(year), key=f"btn_year_{year}"):
                            st.session_state.production_year = year
                
                # Month selection (only shown after year is selected)
                if st.session_state.production_year:
                    st.write(f"Selected production year: **{st.session_state.production_year}**")
                    st.write("Select production month:")
                    month_cols = st.columns(6)
                    
                    # Get current date
                    current_date = datetime.now()
                    
                    # If selected year is current year, only show months up to current month
                    if st.session_state.production_year == current_date.year:
                        months = list(range(1, current_date.month + 1))
                    else:
                        months = list(range(1, 13))
                        
                    for i, month in enumerate(months):
                        with month_cols[i % 6]:
                            if st.button(f"{month:02d}", key=f"btn_month_{month}"):
                                st.session_state.production_month = month
                
                # Day selection (only shown after month is selected)
                if st.session_state.production_month:
                    st.write(f"Selected production month: **{st.session_state.production_month:02d}**")
                    st.write("Select production day:")
                    
                    # Get current date
                    current_date = datetime.now()
                    
                    # Calculate max days for the month
                    max_day = 31
                    if st.session_state.production_month in [4, 6, 9, 11]:
                        max_day = 30
                    elif st.session_state.production_month == 2:
                        if st.session_state.production_year % 4 == 0 and (st.session_state.production_year % 100 != 0 or st.session_state.production_year % 400 == 0):
                            max_day = 29
                        else:
                            max_day = 28
                    
                    # If selected year and month are current year and month, limit days to current day
                    if (st.session_state.production_year == current_date.year and 
                        st.session_state.production_month == current_date.month):
                        max_day = min(max_day, current_date.day)
                    
                    # Create day buttons
                    day_cols = st.columns(7)
                    days = list(range(1, max_day + 1))
                    for i, day in enumerate(days):
                        with day_cols[i % 7]:
                            if st.button(f"{day:02d}", key=f"btn_day_{day}"):
                                st.session_state.production_day = day
                
                # Construct the production date
                if st.session_state.production_year and st.session_state.production_month and st.session_state.production_day:
                    production_date = f"{st.session_state.production_day:02d}.{st.session_state.production_month:02d}.{st.session_state.production_year}"
                    st.write(f"Production date: **{production_date}**")
            
            min_expire_date = None
            try:
                if production_date:
                    prod_date = datetime.strptime(production_date, "%d.%m.%Y")
                    min_expire_date = prod_date
            except:
                st.warning("Invalid production date format")
            
            # Expire Date Selection
            if production_date:
                st.subheader("Expire Date")
                
                # Expire date method buttons
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    if st.button("Direct input", key="btn_direct_exp"):
                        st.session_state.expire_date_method = "Direct input"
                with exp_col2:
                    if st.button("Step by step", key="btn_step_exp"):
                        st.session_state.expire_date_method = "Step by step"
                        
                # Show the selected expire date method
                if st.session_state.expire_date_method:
                    st.write(f"Selected method: **{st.session_state.expire_date_method}**")
                
                expire_date = ""
                if st.session_state.expire_date_method == "Direct input":
                    expire_date = st.text_input("expire_date (dd.mm.yyyy)", value="01.03.2025")
                elif st.session_state.expire_date_method == "Step by step":
                    # Set default values
                    default_year = datetime.now().year
                    default_month = datetime.now().month
                    default_day = 1
                    if min_expire_date:
                        default_expire = min_expire_date + timedelta(days=60)
                        default_year = default_expire.year
                        default_month = default_expire.month
                        default_day = default_expire.day
                    
                    # Year selection
                    st.write("Select expire year:")
                    exp_year_cols = st.columns(5)
                    # Ensure expire year cannot be earlier than production year
                    min_year = st.session_state.production_year
                    exp_years = list(range(min_year, 2030))
                    for i, year in enumerate(exp_years):
                        with exp_year_cols[i % 5]:
                            if st.button(str(year), key=f"btn_exp_year_{year}"):
                                st.session_state.expire_year = year
                    
                    # Month selection (only shown after year is selected)
                    if st.session_state.expire_year:
                        st.write(f"Selected expire year: **{st.session_state.expire_year}**")
                        st.write("Select expire month:")
                        exp_month_cols = st.columns(6)
                        
                        # If same year as production date, start months from production month
                        min_month = 1
                        if st.session_state.expire_year == st.session_state.production_year:
                            min_month = st.session_state.production_month
                            
                        exp_months = list(range(min_month, 13))
                        for i, month in enumerate(exp_months):
                            with exp_month_cols[i % 6]:
                                if st.button(f"{month:02d}", key=f"btn_exp_month_{month}"):
                                    st.session_state.expire_month = month
                    
                    # Day selection (only shown after month is selected)
                    if st.session_state.expire_month:
                        st.write(f"Selected expire month: **{st.session_state.expire_month:02d}**")
                        st.write("Select expire day:")
                        
                        # Calculate max days for the month
                        max_day = 31
                        if st.session_state.expire_month in [4, 6, 9, 11]:
                            max_day = 30
                        elif st.session_state.expire_month == 2:
                            if st.session_state.expire_year % 4 == 0 and (st.session_state.expire_year % 100 != 0 or st.session_state.expire_year % 400 == 0):
                                max_day = 29
                            else:
                                max_day = 28
                                
                        # Check if expire date would be earlier than production date
                        min_day = 1
                        if (st.session_state.expire_year == st.session_state.production_year and 
                            st.session_state.expire_month == st.session_state.production_month):
                            # If same year and month, expiry day must be >= production day
                            min_day = st.session_state.production_day
                        
                        # Create day buttons
                        exp_day_cols = st.columns(7)
                        exp_days = list(range(min_day, max_day + 1))
                        for i, day in enumerate(exp_days):
                            with exp_day_cols[i % 7]:
                                if st.button(f"{day:02d}", key=f"btn_exp_day_{day}"):
                                    st.session_state.expire_day = day
                    
                    # Construct the expire date
                    if st.session_state.expire_year and st.session_state.expire_month and st.session_state.expire_day:
                        expire_date = f"{st.session_state.expire_day:02d}.{st.session_state.expire_month:02d}.{st.session_state.expire_year}"
                        st.write(f"Expiration date: **{expire_date}**")
                
                duration = 0
                if production_date and expire_date:
                    try:
                        production_date_dt = datetime.strptime(production_date, "%d.%m.%Y")
                        expire_date_dt = datetime.strptime(expire_date, "%d.%m.%Y")
                        
                        # Validate that expire date is not before production date
                        if expire_date_dt < production_date_dt:
                            st.error("Error: Expiration date cannot be earlier than production date!")
                            duration = 0
                        else:
                            duration = (expire_date_dt - production_date_dt).days
                    except Exception as e:
                        st.error(f"Error calculating duration: {str(e)}")
                        duration = 0
                    
                    st.subheader("Product Duration Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Production Date:**")
                        st.markdown("**Expiration Date:**")
                        st.markdown("**Period of Duration:**")
                    with col2:
                        st.markdown(f"**{production_date}**")
                        st.markdown(f"**{expire_date}**")
                        st.markdown(f"**{duration} days**" if duration >= 0 else "**<span style='color:red'>non-eatable product</span>**", unsafe_allow_html=True)
                    
                    today = datetime.now()
                    expire_datetime = datetime.strptime(expire_date, "%d.%m.%Y")
                    if expire_datetime < today:
                        st.error("Warning: Product has already expired!")
                    
                    # Brand availability with buttons
                    st.write("Brand availability:")
                    avail_col1, avail_col2 = st.columns(2)
                    with avail_col1:
                        if st.button("Yes", key="btn_avail_yes"):
                            st.session_state.brand_availability = "yes"
                    with avail_col2:
                        if st.button("No", key="btn_avail_no"):
                            st.session_state.brand_availability = "no"
                    
                    # Show selected brand availability
                    if st.session_state.brand_availability:
                        st.write(f"Brand availability: **{st.session_state.brand_availability}**")
                    
                    # Discount input
                    discount = st.number_input("discount", min_value=0, max_value=100, step=1)
                    
                    discount_amount = price * discount / 100
                    discounted_price = int(price - discount_amount)
                    
                    st.subheader("Discount Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Real price of product:**")
                        st.markdown("**Discount percentage:**")
                        st.markdown("**Price after discount:**")
                    with col2:
                        st.markdown(f"**{price} sum**")
                        st.markdown(f"**{discount}%**")
                        st.markdown(f"**{discounted_price} sum**")
                    
                    # Only show submit button when all required fields are filled
                    if st.session_state.brand_availability:
                        st.markdown("---")
                        st.markdown("### Ready to submit your product data")
                        
                        # Create a prominent SUBMIT button with custom styling
                        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                        with submit_col2:
                            if st.button("SUBMIT", key="final_submit", use_container_width=True):
                                data = {
                                    "product_direction": st.session_state.selected_direction,
                                    "product_category": st.session_state.selected_category,
                                    "product_brand": st.session_state.selected_brand,
                                    "product_name": st.session_state.selected_product,
                                    "product_price": f"{price} sum",
                                    "production_date": production_date,
                                    "expire_date": expire_date,
                                    "period_of_duration": f"{duration} days" if duration >= 0 else "non-eatable product",
                                    "brand_availability": st.session_state.brand_availability,
                                    "discount_percentage": f"{discount}%",
                                    "price_after_discount": f"{discounted_price} sum"
                                }
                                df_new = pd.DataFrame([data])
                                if not os.path.exists(csv_file):
                                    df_new.to_csv(csv_file, index=False)
                                else:
                                    df_old = pd.read_csv(csv_file)
                                    df_all = pd.concat([df_old, df_new], ignore_index=True)
                                    df_all.to_csv(csv_file, index=False)
                                
                                st.success("Data submitted successfully")
                                st.table(data)
                                
                                
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
              
# def dat():

#     food_products = {
#         "Dairy Products": {
#             "brands": ["Nestlé", "Danone", "Parmalat", "President", "Amul", "Campina"],
#             "products": ["Milk", "Yogurt", "Kefir", "Cheese", "Cottage Cheese", "Cream", "Butter"]
#         },
#         "Bakery Products": {
#             "brands": ["Barilla", "Makfa", "Ozon", "Pioner", "Yashkino"],
#             "products": ["Wheat Flour", "Pasta", "Bread", "Biscuits", "Noodles", "Buns"]
#         },
#         "Meat Products": {
#             "brands": ["Tyson", "Oscar Mayer", "Hormel", "Perdue", "Cherkizovo"],
#             "products": ["Beef", "Lamb", "Poultry", "Sausage", "Hot Dogs", "Smoked Meat"]
#         },
#         "Beverages": {
#             "brands": ["Coca-Cola", "Pepsi", "Nestlé Pure Life", "Lipton", "Nescafé"],
#             "products": ["Mineral Water", "Carbonated Drinks", "Juices", "Tea", "Coffee"]
#         },
#         "Sweets": {
#             "brands": ["Mars", "Ferrero", "Milka", "Nestlé", "Roshen"],
#             "products": ["Chocolate", "Candies", "Cakes", "Ice Cream", "Halva", "Jam"]
#         }
#     }

#     csv_file = "products_data.csv"

#     if 'uploaded_df' not in st.session_state:
#         st.session_state.uploaded_df = None
#     if 'show_upload' not in st.session_state:
#         st.session_state.show_upload = False
#     if 'show_manual' not in st.session_state:
#         st.session_state.show_manual = False

#     # Main interface
#     st.title("Product Management System")

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Upload"):
#             st.session_state.show_upload = True
#             st.session_state.show_manual = False  # Hide manual when showing upload
#     with col2:
#         if st.button("Manual"):
#             st.session_state.show_manual = True
#             st.session_state.show_upload = False  # Hide upload when showing manual

#     # File Upload Section (shown only when "Upload" is clicked)
#     if st.session_state.show_upload:
#         st.subheader("File Upload")
#         try:
#             uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
            
#             if uploaded_file is not None:
#                 try:
#                     if uploaded_file.name.endswith('.csv'):
#                         df = pd.read_csv(uploaded_file, encoding='iso-8859-1', sep=',', on_bad_lines='skip')
#                     elif uploaded_file.name.endswith('.xlsx'):
#                         df = pd.read_excel(uploaded_file)
                    
#                     st.success(f"File '{uploaded_file.name}' successfully loaded!")
#                     # Display single editable table
#                     edited_df = st.data_editor(df, num_rows="dynamic", key="upload_editor")
#                     st.session_state.uploaded_df = edited_df
                    
#                     # Save edited data to CSV
#                     if st.button("Save Uploaded Data"):
#                         if not os.path.exists(csv_file):
#                             edited_df.to_csv(csv_file, index=False)
#                         else:
#                             df_old = pd.read_csv(csv_file)
#                             df_all = pd.concat([df_old, edited_df], ignore_index=True)
#                             df_all.to_csv(csv_file, index=False)
#                         st.success("Uploaded data saved successfully!")
#                 except Exception as e:
#                     st.error(f"Error reading file: {str(e)}")
#                     st.info("Try opening and resaving your CSV file in Excel with comma delimiter and ISO-8859-1 encoding.")
#         except Exception as e:
#             st.error(f"Error with file uploader: {str(e)}")

#     # Manual Data Entry Section (shown when "Manual" is clicked)
#     if st.session_state.show_manual:
#         st.subheader("Manual Product Entry")
        
#         direction = st.selectbox("product_direction", ["food_products", "non_food_products"])
#         selected_category = ""
#         selected_brand = ""
#         selected_product = ""
        
#         if direction == "food_products":
#             selected_category = st.selectbox("product_category", list(food_products.keys()))
#             brands = food_products[selected_category]["brands"] if selected_category else []
#             products = food_products[selected_category]["products"] if selected_category else []
#             selected_brand = st.selectbox("product_brand", brands)
#             selected_product = st.selectbox("product_name", products)
#         else:
#             selected_category = st.selectbox("product_category", ["Dairy Products", "Bakery"])
#             selected_brand = st.text_input("product_brand", "Nestle")
#             selected_product = st.text_input("product_name", "Milk")
        
#         price = st.number_input("product_price", min_value=0, step=1000, value=0)
#         st.write(f"{price} sum")
#         st.subheader("Production Date")
#         date_input_method = st.radio("Choose date input method:", ["Direct input", "Step by step"])
        
#         production_date = ""
#         if date_input_method == "Direct input":
#             production_date = st.text_input("production_date (dd.mm.yyyy)", value="01.01.2025")
#         else:
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 year = st.selectbox("Production Year", list(range(2020, 2026)))
#             with col2:
#                 month = st.selectbox("Production Month", list(range(1, 13)))
#             with col3:
#                 max_day = 31
#                 if month in [4, 6, 9, 11]:
#                     max_day = 30
#                 elif month == 2:
#                     if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
#                         max_day = 29
#                     else:
#                         max_day = 28
#                 day = st.selectbox("Production Day", list(range(1, max_day + 1)))
#             production_date = f"{day:02d}.{month:02d}.{year}"
#             st.write(f"Production date: {production_date}")
        
#         min_expire_date = None
#         try:
#             prod_date = datetime.strptime(production_date, "%d.%m.%Y")
#             min_expire_date = prod_date
#         except:
#             st.warning("Invalid production date format")
        
#         st.subheader("Expire Date")
#         expire_date_method = st.radio("Choose expire date input method:", ["Direct input", "Step by step"], key="expire_method")
        
#         expire_date = ""
#         if expire_date_method == "Direct input":
#             expire_date = st.text_input("expire_date (dd.mm.yyyy)", value="01.03.2025")
#         else:
#             col1, col2, col3 = st.columns(3)
#             default_year = datetime.now().year
#             default_month = datetime.now().month
#             default_day = 1
#             if min_expire_date:
#                 default_expire = min_expire_date + timedelta(days=60)
#                 default_year = default_expire.year
#                 default_month = default_expire.month
#                 default_day = default_expire.day
#             with col1:
#                 year = st.selectbox("Expire Year", list(range(2020, 2030)), index=list(range(2020, 2030)).index(default_year) if default_year in range(2020, 2030) else 5)
#             with col2:
#                 month = st.selectbox("Expire Month", list(range(1, 13)), index=default_month-1)
#             with col3:
#                 max_day = 31
#                 if month in [4, 6, 9, 11]:
#                     max_day = 30
#                 elif month == 2:
#                     if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
#                         max_day = 29
#                     else:
#                         max_day = 28
#                 day = st.selectbox("Expire Day", list(range(1, max_day + 1)), index=min(default_day-1, max_day-1))
#             expire_date = f"{day:02d}.{month:02d}.{year}"
#             st.write(f"Expiration date: {expire_date}")
        
#         duration = 0
#         if production_date and expire_date:
#             try:
#                 production_date_dt = datetime.strptime(production_date, "%d.%m.%Y")
#                 expire_date_dt = datetime.strptime(expire_date, "%d.%m.%Y")
#                 duration = (expire_date_dt - production_date_dt).days
#             except Exception as e:
#                 st.error(f"Error calculating duration: {str(e)}")
#                 duration = 0
            
#             st.subheader("Product Duration Information")
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.markdown("**Production Date:**")
#                 st.markdown("**Expiration Date:**")
#                 st.markdown("**Period of Duration:**")
#             with col2:
#                 st.markdown(f"**{production_date}**")
#                 st.markdown(f"**{expire_date}**")
#                 st.markdown(f"**{duration} days**" if duration >= 0 else "**<span style='color:red'>non-eatable product</span>**", unsafe_allow_html=True)
            
#             today = datetime.now()
#             expire_datetime = datetime.strptime(expire_date, "%d.%m.%Y")
#             if expire_datetime < today:
#                 st.error("Warning: Product has already expired!")
        
#         brand_availability = st.radio("brand_availability", ["yes", "no"])
#         discount = st.number_input("discount", min_value=0, max_value=100, step=1)
        
#         discount_amount = price * discount / 100
#         discounted_price = int(price - discount_amount)
        
#         st.subheader("Discount Information")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.markdown("**Real price of product:**")
#             st.markdown("**Discount percentage:**")
#             st.markdown("**Price after discount:**")
#         with col2:
#             st.markdown(f"**{price} sum**")
#             st.markdown(f"**{discount}%**")
#             st.markdown(f"**{discounted_price} sum**")
        
#         if st.button("Submit"):
#             data = {
#                 "product_direction": direction,
#                 "product_category": selected_category,
#                 "product_brand": selected_brand,
#                 "product_name": selected_product,
#                 "product_price": f"{price} sum",
#                 "production_date": production_date,
#                 "expire_date": expire_date,
#                 "period_of_duration": f"{duration} days" if duration >= 0 else "non-eatable product",
#                 "brand_availability": brand_availability,
#                 "discount_percentage": f"{discount}%",
#                 "price_after_discount": f"{discounted_price} sum"
#             }
#             df_new = pd.DataFrame([data])
#             if not os.path.exists(csv_file):
#                 df_new.to_csv(csv_file, index=False)
#             else:
#                 df_old = pd.read_csv(csv_file)
#                 df_all = pd.concat([df_old, df_new], ignore_index=True)
#                 df_all.to_csv(csv_file, index=False)
            
#             st.success("Data submitted successfully")
#             st.json(data)
































































# def dat():

#     food_products = {
#         "Dairy Products": {
#             "brands": ["Nestlé", "Danone", "Parmalat", "President", "Amul", "Campina"],
#             "products": ["Milk", "Yogurt", "Kefir", "Cheese", "Cottage Cheese", "Cream", "Butter"]
#         },
#         "Bakery Products": {
#             "brands": ["Barilla", "Makfa", "Ozon", "Pioner", "Yashkino"],
#             "products": ["Wheat Flour", "Pasta", "Bread", "Biscuits", "Noodles", "Buns"]
#         },
#         "Meat Products": {
#             "brands": ["Tyson", "Oscar Mayer", "Hormel", "Perdue", "Cherkizovo"],
#             "products": ["Beef", "Lamb", "Poultry", "Sausage", "Hot Dogs", "Smoked Meat"]
#         },
#         "Beverages": {
#             "brands": ["Coca-Cola", "Pepsi", "Nestlé Pure Life", "Lipton", "Nescafé"],
#             "products": ["Mineral Water", "Carbonated Drinks", "Juices", "Tea", "Coffee"]
#         },
#         "Sweets": {
#             "brands": ["Mars", "Ferrero", "Milka", "Nestlé", "Roshen"],
#             "products": ["Chocolate", "Candies", "Cakes", "Ice Cream", "Halva", "Jam"]
#         }
#     }

#     csv_file = "products_data.csv"

#     # Initialize session state variables
#     if 'uploaded_df' not in st.session_state:
#         st.session_state.uploaded_df = None
#     if 'show_upload' not in st.session_state:
#         st.session_state.show_upload = False
#     if 'show_manual' not in st.session_state:
#         st.session_state.show_manual = False
        
#     # For button-based selection state variables
#     if 'selected_direction' not in st.session_state:
#         st.session_state.selected_direction = None
#     if 'selected_category' not in st.session_state:
#         st.session_state.selected_category = None
#     if 'selected_brand' not in st.session_state:
#         st.session_state.selected_brand = None
#     if 'selected_product' not in st.session_state:
#         st.session_state.selected_product = None
#     if 'date_input_method' not in st.session_state:
#         st.session_state.date_input_method = None
#     if 'expire_date_method' not in st.session_state:
#         st.session_state.expire_date_method = None
#     if 'production_year' not in st.session_state:
#         st.session_state.production_year = None
#     if 'production_month' not in st.session_state:
#         st.session_state.production_month = None
#     if 'production_day' not in st.session_state:
#         st.session_state.production_day = None
#     if 'expire_year' not in st.session_state:
#         st.session_state.expire_year = None
#     if 'expire_month' not in st.session_state:
#         st.session_state.expire_month = None
#     if 'expire_day' not in st.session_state:
#         st.session_state.expire_day = None
#     if 'brand_availability' not in st.session_state:
#         st.session_state.brand_availability = None

#     # Main interface
#     st.title("Product Management System")

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Upload"):
#             st.session_state.show_upload = True
#             st.session_state.show_manual = False  # Hide manual when showing upload
#     with col2:
#         if st.button("Manual"):
#             st.session_state.show_manual = True
#             st.session_state.show_upload = False  # Hide upload when showing manual
#             # Reset selection state when switching to manual mode
#             st.session_state.selected_direction = None
#             st.session_state.selected_category = None
#             st.session_state.selected_brand = None
#             st.session_state.selected_product = None
#             st.session_state.date_input_method = None
#             st.session_state.expire_date_method = None

#     # File Upload Section (shown only when "Upload" is clicked)
#     if st.session_state.show_upload:
#         st.subheader("File Upload")
#         try:
#             uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
            
#             if uploaded_file is not None:
#                 try:
#                     if uploaded_file.name.endswith('.csv'):
#                         df = pd.read_csv(uploaded_file, encoding='iso-8859-1', sep=',', on_bad_lines='skip')
#                     elif uploaded_file.name.endswith('.xlsx'):
#                         df = pd.read_excel(uploaded_file)
                    
#                     st.success(f"File '{uploaded_file.name}' successfully loaded!")
#                     # Display single editable table
#                     edited_df = st.data_editor(df, num_rows="dynamic", key="upload_editor")
#                     st.session_state.uploaded_df = edited_df
                    
#                     # Save edited data to CSV
#                     if st.button("Save Uploaded Data"):
#                         if not os.path.exists(csv_file):
#                             edited_df.to_csv(csv_file, index=False)
#                         else:
#                             df_old = pd.read_csv(csv_file)
#                             df_all = pd.concat([df_old, edited_df], ignore_index=True)
#                             df_all.to_csv(csv_file, index=False)
#                         st.success("Uploaded data saved successfully!")
#                 except Exception as e:
#                     st.error(f"Error reading file: {str(e)}")
#                     st.info("Try opening and resaving your CSV file in Excel with comma delimiter and ISO-8859-1 encoding.")
#         except Exception as e:
#             st.error(f"Error with file uploader: {str(e)}")

#     # Manual Data Entry Section (shown when "Manual" is clicked)
#     if st.session_state.show_manual:
#         st.subheader("Manual Product Entry")
        
#         # Direction selection with buttons
#         st.write("Select product direction:")
#         dir_col1, dir_col2 = st.columns(2)
#         with dir_col1:
#             if st.button("Food Products", key="btn_food"):
#                 st.session_state.selected_direction = "food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
#         with dir_col2:
#             if st.button("Non-Food Products", key="btn_nonfood"):
#                 st.session_state.selected_direction = "non_food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
                
#         # Show the selected direction
#         if st.session_state.selected_direction:
#             st.write(f"Selected direction: **{st.session_state.selected_direction}**")
                
#         # Category Selection (only shown after direction is selected)
#         if st.session_state.selected_direction:
#             st.write("Select product category:")
            
#             if st.session_state.selected_direction == "food_products":
#                 # Create columns for food product categories
#                 categories = list(food_products.keys())
#                 category_cols = st.columns(len(categories))
                
#                 for i, category in enumerate(categories):
#                     with category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
#             else:
#                 # For non-food products, use limited categories
#                 non_food_categories = ["Electronics", "Clothing", "Home Goods"]
#                 nf_category_cols = st.columns(len(non_food_categories))
                
#                 for i, category in enumerate(non_food_categories):
#                     with nf_category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
        
#         # Show the selected category
#         if st.session_state.selected_category:
#             st.write(f"Selected category: **{st.session_state.selected_category}**")
            
#         # Brand Selection (only shown after category is selected)
#         if st.session_state.selected_category and st.session_state.selected_direction == "food_products":
#             st.write("Select product brand:")
            
#             # Get the brands for the selected category
#             brands = food_products[st.session_state.selected_category]["brands"]
#             # Create a dynamic number of columns based on how many brands
#             brand_cols = st.columns(min(len(brands), 3))
            
#             # Place brands in columns and create buttons
#             for i, brand in enumerate(brands):
#                 col_index = i % len(brand_cols)
#                 with brand_cols[col_index]:
#                     if st.button(brand, key=f"btn_brand_{brand}"):
#                         st.session_state.selected_brand = brand
#                         # Reset product selection
#                         st.session_state.selected_product = None
#         elif st.session_state.selected_category and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for brand
#             st.session_state.selected_brand = st.text_input("Enter product brand", "Brand Name")
            
#         # Show the selected brand
#         if st.session_state.selected_brand:
#             st.write(f"Selected brand: **{st.session_state.selected_brand}**")
            
#         # Product Selection (only shown after brand is selected)
#         if st.session_state.selected_brand and st.session_state.selected_direction == "food_products":
#             st.write("Select product:")
            
#             # Get the products for the selected category
#             products = food_products[st.session_state.selected_category]["products"]
#             # Create columns for products
#             product_cols = st.columns(min(len(products), 3))
            
#             # Place products in columns and create buttons
#             for i, product in enumerate(products):
#                 col_index = i % len(product_cols)
#                 with product_cols[col_index]:
#                     if st.button(product, key=f"btn_product_{product}"):
#                         st.session_state.selected_product = product
#         elif st.session_state.selected_brand and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for product name
#             st.session_state.selected_product = st.text_input("Enter product name", "Product Name")
            
#         # Show the selected product
#         if st.session_state.selected_product:
#             st.write(f"Selected product: **{st.session_state.selected_product}**")
            
#         # Price input (only shown after product is selected)
#         if st.session_state.selected_product:
#             price = st.number_input("product_price", min_value=0, step=1000, value=0)
#             st.write(f"{price} sum")
            
#             # Production Date Selection
#             st.subheader("Production Date")
            
#             # Date input method buttons
#             date_col1, date_col2 = st.columns(2)
#             with date_col1:
#                 if st.button("Direct input", key="btn_direct_date"):
#                     st.session_state.date_input_method = "Direct input"
#             with date_col2:
#                 if st.button("Step by step", key="btn_step_date"):
#                     st.session_state.date_input_method = "Step by step"
                    
#             # Show the selected date input method
#             if st.session_state.date_input_method:
#                 st.write(f"Selected method: **{st.session_state.date_input_method}**")
            
#             production_date = ""
#             if st.session_state.date_input_method == "Direct input":
#                 production_date = st.text_input("production_date (dd.mm.yyyy)", value="01.01.2025")
#             elif st.session_state.date_input_method == "Step by step":
#                 # Year selection
#                 st.write("Select production year:")
#                 year_cols = st.columns(6)
#                 years = list(range(2020, 2026))
#                 for i, year in enumerate(years):
#                     with year_cols[i]:
#                         if st.button(str(year), key=f"btn_year_{year}"):
#                             st.session_state.production_year = year
                
#                 # Month selection (only shown after year is selected)
#                 if st.session_state.production_year:
#                     st.write(f"Selected production year: **{st.session_state.production_year}**")
#                     st.write("Select production month:")
#                     month_cols = st.columns(6)
#                     months = list(range(1, 13))
#                     for i, month in enumerate(months):
#                         with month_cols[i % 6]:
#                             if st.button(f"{month:02d}", key=f"btn_month_{month}"):
#                                 st.session_state.production_month = month
                
#                 # Day selection (only shown after month is selected)
#                 if st.session_state.production_month:
#                     st.write(f"Selected production month: **{st.session_state.production_month:02d}**")
#                     st.write("Select production day:")
                    
#                     # Calculate max days for the month
#                     max_day = 31
#                     if st.session_state.production_month in [4, 6, 9, 11]:
#                         max_day = 30
#                     elif st.session_state.production_month == 2:
#                         if st.session_state.production_year % 4 == 0 and (st.session_state.production_year % 100 != 0 or st.session_state.production_year % 400 == 0):
#                             max_day = 29
#                         else:
#                             max_day = 28
                    
#                     # Create day buttons
#                     day_cols = st.columns(7)
#                     days = list(range(1, max_day + 1))
#                     for i, day in enumerate(days):
#                         with day_cols[i % 7]:
#                             if st.button(f"{day:02d}", key=f"btn_day_{day}"):
#                                 st.session_state.production_day = day
                
#                 # Construct the production date
#                 if st.session_state.production_year and st.session_state.production_month and st.session_state.production_day:
#                     production_date = f"{st.session_state.production_day:02d}.{st.session_state.production_month:02d}.{st.session_state.production_year}"
#                     st.write(f"Production date: **{production_date}**")
            
#             min_expire_date = None
#             try:
#                 if production_date:
#                     prod_date = datetime.strptime(production_date, "%d.%m.%Y")
#                     min_expire_date = prod_date
#             except:
#                 st.warning("Invalid production date format")
            
#             # Expire Date Selection
#             if production_date:
#                 st.subheader("Expire Date")
                
#                 # Expire date method buttons
#                 exp_col1, exp_col2 = st.columns(2)
#                 with exp_col1:
#                     if st.button("Direct input", key="btn_direct_exp"):
#                         st.session_state.expire_date_method = "Direct input"
#                 with exp_col2:
#                     if st.button("Step by step", key="btn_step_exp"):
#                         st.session_state.expire_date_method = "Step by step"
                        
#                 # Show the selected expire date method
#                 if st.session_state.expire_date_method:
#                     st.write(f"Selected method: **{st.session_state.expire_date_method}**")
                
#                 expire_date = ""
#                 if st.session_state.expire_date_method == "Direct input":
#                     expire_date = st.text_input("expire_date (dd.mm.yyyy)", value="01.03.2025")
#                 elif st.session_state.expire_date_method == "Step by step":
#                     # Set default values
#                     default_year = datetime.now().year
#                     default_month = datetime.now().month
#                     default_day = 1
#                     if min_expire_date:
#                         default_expire = min_expire_date + timedelta(days=60)
#                         default_year = default_expire.year
#                         default_month = default_expire.month
#                         default_day = default_expire.day
                    
#                     # Year selection
#                     st.write("Select expire year:")
#                     exp_year_cols = st.columns(5)
#                     exp_years = list(range(2020, 2030))
#                     for i, year in enumerate(exp_years):
#                         with exp_year_cols[i % 5]:
#                             if st.button(str(year), key=f"btn_exp_year_{year}"):
#                                 st.session_state.expire_year = year
                    
#                     # Month selection (only shown after year is selected)
#                     if st.session_state.expire_year:
#                         st.write(f"Selected expire year: **{st.session_state.expire_year}**")
#                         st.write("Select expire month:")
#                         exp_month_cols = st.columns(6)
#                         exp_months = list(range(1, 13))
#                         for i, month in enumerate(exp_months):
#                             with exp_month_cols[i % 6]:
#                                 if st.button(f"{month:02d}", key=f"btn_exp_month_{month}"):
#                                     st.session_state.expire_month = month
                    
#                     # Day selection (only shown after month is selected)
#                     if st.session_state.expire_month:
#                         st.write(f"Selected expire month: **{st.session_state.expire_month:02d}**")
#                         st.write("Select expire day:")
                        
#                         # Calculate max days for the month
#                         max_day = 31
#                         if st.session_state.expire_month in [4, 6, 9, 11]:
#                             max_day = 30
#                         elif st.session_state.expire_month == 2:
#                             if st.session_state.expire_year % 4 == 0 and (st.session_state.expire_year % 100 != 0 or st.session_state.expire_year % 400 == 0):
#                                 max_day = 29
#                             else:
#                                 max_day = 28
                        
#                         # Create day buttons
#                         exp_day_cols = st.columns(7)
#                         exp_days = list(range(1, max_day + 1))
#                         for i, day in enumerate(exp_days):
#                             with exp_day_cols[i % 7]:
#                                 if st.button(f"{day:02d}", key=f"btn_exp_day_{day}"):
#                                     st.session_state.expire_day = day
                    
#                     # Construct the expire date
#                     if st.session_state.expire_year and st.session_state.expire_month and st.session_state.expire_day:
#                         expire_date = f"{st.session_state.expire_day:02d}.{st.session_state.expire_month:02d}.{st.session_state.expire_year}"
#                         st.write(f"Expiration date: **{expire_date}**")
                
#                 duration = 0
#                 if production_date and expire_date:
#                     try:
#                         production_date_dt = datetime.strptime(production_date, "%d.%m.%Y")
#                         expire_date_dt = datetime.strptime(expire_date, "%d.%m.%Y")
#                         duration = (expire_date_dt - production_date_dt).days
#                     except Exception as e:
#                         st.error(f"Error calculating duration: {str(e)}")
#                         duration = 0
                    
#                     st.subheader("Product Duration Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Production Date:**")
#                         st.markdown("**Expiration Date:**")
#                         st.markdown("**Period of Duration:**")
#                     with col2:
#                         st.markdown(f"**{production_date}**")
#                         st.markdown(f"**{expire_date}**")
#                         st.markdown(f"**{duration} days**" if duration >= 0 else "**<span style='color:red'>non-eatable product</span>**", unsafe_allow_html=True)
                    
#                     today = datetime.now()
#                     expire_datetime = datetime.strptime(expire_date, "%d.%m.%Y")
#                     if expire_datetime < today:
#                         st.error("Warning: Product has already expired!")
                    
#                     # Brand availability with buttons
#                     st.write("Brand availability:")
#                     avail_col1, avail_col2 = st.columns(2)
#                     with avail_col1:
#                         if st.button("Yes", key="btn_avail_yes"):
#                             st.session_state.brand_availability = "yes"
#                     with avail_col2:
#                         if st.button("No", key="btn_avail_no"):
#                             st.session_state.brand_availability = "no"
                    
#                     # Show selected brand availability
#                     if st.session_state.brand_availability:
#                         st.write(f"Brand availability: **{st.session_state.brand_availability}**")
                    
#                     # Discount input
#                     discount = st.number_input("discount", min_value=0, max_value=100, step=1)
                    
#                     discount_amount = price * discount / 100
#                     discounted_price = int(price - discount_amount)
                    
#                     st.subheader("Discount Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Real price of product:**")
#                         st.markdown("**Discount percentage:**")
#                         st.markdown("**Price after discount:**")
#                     with col2:
#                         st.markdown(f"**{price} sum**")
#                         st.markdown(f"**{discount}%**")
#                         st.markdown(f"**{discounted_price} sum**")
                    
#                     # Only show submit button when all required fields are filled
#                     if st.session_state.brand_availability:
#                         if st.button("Submit"):
#                             data = {
#                                 "product_direction": st.session_state.selected_direction,
#                                 "product_category": st.session_state.selected_category,
#                                 "product_brand": st.session_state.selected_brand,
#                                 "product_name": st.session_state.selected_product,
#                                 "product_price": f"{price} sum",
#                                 "production_date": production_date,
#                                 "expire_date": expire_date,
#                                 "period_of_duration": f"{duration} days" if duration >= 0 else "non-eatable product",
#                                 "brand_availability": st.session_state.brand_availability,
#                                 "discount_percentage": f"{discount}%",
#                                 "price_after_discount": f"{discounted_price} sum"
#                             }
#                             df_new = pd.DataFrame([data])
#                             if not os.path.exists(csv_file):
#                                 df_new.to_csv(csv_file, index=False)
#                             else:
#                                 df_old = pd.read_csv(csv_file)
#                                 df_all = pd.concat([df_old, df_new], ignore_index=True)
#                                 df_all.to_csv(csv_file, index=False)
                            
#                             st.success("Data submitted successfully")
#                             st.json(data)







































































# def dat():

#     food_products = {
#         "Dairy Products": {
#             "brands": ["Nestlé", "Danone", "Parmalat", "President", "Amul", "Campina"],
#             "products": ["Milk", "Yogurt", "Kefir", "Cheese", "Cottage Cheese", "Cream", "Butter"]
#         },
#         "Bakery Products": {
#             "brands": ["Barilla", "Makfa", "Ozon", "Pioner", "Yashkino"],
#             "products": ["Wheat Flour", "Pasta", "Bread", "Biscuits", "Noodles", "Buns"]
#         },
#         "Meat Products": {
#             "brands": ["Tyson", "Oscar Mayer", "Hormel", "Perdue", "Cherkizovo"],
#             "products": ["Beef", "Lamb", "Poultry", "Sausage", "Hot Dogs", "Smoked Meat"]
#         },
#         "Beverages": {
#             "brands": ["Coca-Cola", "Pepsi", "Nestlé Pure Life", "Lipton", "Nescafé"],
#             "products": ["Mineral Water", "Carbonated Drinks", "Juices", "Tea", "Coffee"]
#         },
#         "Sweets": {
#             "brands": ["Mars", "Ferrero", "Milka", "Nestlé", "Roshen"],
#             "products": ["Chocolate", "Candies", "Cakes", "Ice Cream", "Halva", "Jam"]
#         }
#     }

#     csv_file = "products_data.csv"

#     # Initialize session state variables
#     if 'uploaded_df' not in st.session_state:
#         st.session_state.uploaded_df = None
#     if 'show_upload' not in st.session_state:
#         st.session_state.show_upload = False
#     if 'show_manual' not in st.session_state:
#         st.session_state.show_manual = False
        
#     # For button-based selection state variables
#     if 'selected_direction' not in st.session_state:
#         st.session_state.selected_direction = None
#     if 'selected_category' not in st.session_state:
#         st.session_state.selected_category = None
#     if 'selected_brand' not in st.session_state:
#         st.session_state.selected_brand = None
#     if 'selected_product' not in st.session_state:
#         st.session_state.selected_product = None
#     if 'date_input_method' not in st.session_state:
#         st.session_state.date_input_method = None
#     if 'expire_date_method' not in st.session_state:
#         st.session_state.expire_date_method = None
#     if 'production_year' not in st.session_state:
#         st.session_state.production_year = None
#     if 'production_month' not in st.session_state:
#         st.session_state.production_month = None
#     if 'production_day' not in st.session_state:
#         st.session_state.production_day = None
#     if 'expire_year' not in st.session_state:
#         st.session_state.expire_year = None
#     if 'expire_month' not in st.session_state:
#         st.session_state.expire_month = None
#     if 'expire_day' not in st.session_state:
#         st.session_state.expire_day = None
#     if 'brand_availability' not in st.session_state:
#         st.session_state.brand_availability = None

#     # Main interface
#     st.title("Product Management System")

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Upload"):
#             st.session_state.show_upload = True
#             st.session_state.show_manual = False  # Hide manual when showing upload
#     with col2:
#         if st.button("Manual"):
#             st.session_state.show_manual = True
#             st.session_state.show_upload = False  # Hide upload when showing manual
#             # Reset selection state when switching to manual mode
#             st.session_state.selected_direction = None
#             st.session_state.selected_category = None
#             st.session_state.selected_brand = None
#             st.session_state.selected_product = None
#             st.session_state.date_input_method = None
#             st.session_state.expire_date_method = None

#     # File Upload Section (shown only when "Upload" is clicked)
#     if st.session_state.show_upload:
#         st.subheader("File Upload")
#         try:
#             uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
            
#             if uploaded_file is not None:
#                 try:
#                     if uploaded_file.name.endswith('.csv'):
#                         df = pd.read_csv(uploaded_file, encoding='iso-8859-1', sep=',', on_bad_lines='skip')
#                     elif uploaded_file.name.endswith('.xlsx'):
#                         df = pd.read_excel(uploaded_file)
                    
#                     st.success(f"File '{uploaded_file.name}' successfully loaded!")
#                     # Display single editable table
#                     edited_df = st.data_editor(df, num_rows="dynamic", key="upload_editor")
#                     st.session_state.uploaded_df = edited_df
                    
#                     # Save edited data to CSV
#                     if st.button("Save Uploaded Data"):
#                         if not os.path.exists(csv_file):
#                             edited_df.to_csv(csv_file, index=False)
#                         else:
#                             df_old = pd.read_csv(csv_file)
#                             df_all = pd.concat([df_old, edited_df], ignore_index=True)
#                             df_all.to_csv(csv_file, index=False)
#                         st.success("Uploaded data saved successfully!")
#                 except Exception as e:
#                     st.error(f"Error reading file: {str(e)}")
#                     st.info("Try opening and resaving your CSV file in Excel with comma delimiter and ISO-8859-1 encoding.")
#         except Exception as e:
#             st.error(f"Error with file uploader: {str(e)}")

#     # Manual Data Entry Section (shown when "Manual" is clicked)
#     if st.session_state.show_manual:
#         st.subheader("Manual Product Entry")
        
#         # Direction selection with buttons
#         st.write("Select product direction:")
#         dir_col1, dir_col2 = st.columns(2)
#         with dir_col1:
#             if st.button("Food Products", key="btn_food"):
#                 st.session_state.selected_direction = "food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
#         with dir_col2:
#             if st.button("Non-Food Products", key="btn_nonfood"):
#                 st.session_state.selected_direction = "non_food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
                
#         # Show the selected direction
#         if st.session_state.selected_direction:
#             st.write(f"Selected direction: **{st.session_state.selected_direction}**")
                
#         # Category Selection (only shown after direction is selected)
#         if st.session_state.selected_direction:
#             st.write("Select product category:")
            
#             if st.session_state.selected_direction == "food_products":
#                 # Create columns for food product categories
#                 categories = list(food_products.keys())
#                 category_cols = st.columns(len(categories))
                
#                 for i, category in enumerate(categories):
#                     with category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
#             else:
#                 # For non-food products, use limited categories
#                 non_food_categories = ["Electronics", "Clothing", "Home Goods"]
#                 nf_category_cols = st.columns(len(non_food_categories))
                
#                 for i, category in enumerate(non_food_categories):
#                     with nf_category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
        
#         # Show the selected category
#         if st.session_state.selected_category:
#             st.write(f"Selected category: **{st.session_state.selected_category}**")
            
#         # Brand Selection (only shown after category is selected)
#         if st.session_state.selected_category and st.session_state.selected_direction == "food_products":
#             st.write("Select product brand:")
            
#             # Get the brands for the selected category
#             brands = food_products[st.session_state.selected_category]["brands"]
#             # Create a dynamic number of columns based on how many brands
#             brand_cols = st.columns(min(len(brands), 3))
            
#             # Place brands in columns and create buttons
#             for i, brand in enumerate(brands):
#                 col_index = i % len(brand_cols)
#                 with brand_cols[col_index]:
#                     if st.button(brand, key=f"btn_brand_{brand}"):
#                         st.session_state.selected_brand = brand
#                         # Reset product selection
#                         st.session_state.selected_product = None
#         elif st.session_state.selected_category and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for brand
#             st.session_state.selected_brand = st.text_input("Enter product brand", "Brand Name")
            
#         # Show the selected brand
#         if st.session_state.selected_brand:
#             st.write(f"Selected brand: **{st.session_state.selected_brand}**")
            
#         # Product Selection (only shown after brand is selected)
#         if st.session_state.selected_brand and st.session_state.selected_direction == "food_products":
#             st.write("Select product:")
            
#             # Get the products for the selected category
#             products = food_products[st.session_state.selected_category]["products"]
#             # Create columns for products
#             product_cols = st.columns(min(len(products), 3))
            
#             # Place products in columns and create buttons
#             for i, product in enumerate(products):
#                 col_index = i % len(product_cols)
#                 with product_cols[col_index]:
#                     if st.button(product, key=f"btn_product_{product}"):
#                         st.session_state.selected_product = product
#         elif st.session_state.selected_brand and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for product name
#             st.session_state.selected_product = st.text_input("Enter product name", "Product Name")
            
#         # Show the selected product
#         if st.session_state.selected_product:
#             st.write(f"Selected product: **{st.session_state.selected_product}**")
            
#         # Price input (only shown after product is selected)
#         if st.session_state.selected_product:
#             price = st.number_input("product_price", min_value=0, step=1000, value=0)
#             st.write(f"{price} sum")
            
#             # Production Date Selection
#             st.subheader("Production Date")
            
#             # Date input method buttons
#             date_col1, date_col2 = st.columns(2)
#             with date_col1:
#                 if st.button("Direct input", key="btn_direct_date"):
#                     st.session_state.date_input_method = "Direct input"
#             with date_col2:
#                 if st.button("Step by step", key="btn_step_date"):
#                     st.session_state.date_input_method = "Step by step"
                    
#             # Show the selected date input method
#             if st.session_state.date_input_method:
#                 st.write(f"Selected method: **{st.session_state.date_input_method}**")
            
#             production_date = ""
#             if st.session_state.date_input_method == "Direct input":
#                 production_date = st.text_input("production_date (dd.mm.yyyy)", value="01.01.2025")
#             elif st.session_state.date_input_method == "Step by step":
#                 # Year selection
#                 st.write("Select production year:")
#                 year_cols = st.columns(6)
#                 years = list(range(2020, 2026))
#                 for i, year in enumerate(years):
#                     with year_cols[i]:
#                         if st.button(str(year), key=f"btn_year_{year}"):
#                             st.session_state.production_year = year
                
#                 # Month selection (only shown after year is selected)
#                 if st.session_state.production_year:
#                     st.write(f"Selected production year: **{st.session_state.production_year}**")
#                     st.write("Select production month:")
#                     month_cols = st.columns(6)
#                     months = list(range(1, 13))
#                     for i, month in enumerate(months):
#                         with month_cols[i % 6]:
#                             if st.button(f"{month:02d}", key=f"btn_month_{month}"):
#                                 st.session_state.production_month = month
                
#                 # Day selection (only shown after month is selected)
#                 if st.session_state.production_month:
#                     st.write(f"Selected production month: **{st.session_state.production_month:02d}**")
#                     st.write("Select production day:")
                    
#                     # Calculate max days for the month
#                     max_day = 31
#                     if st.session_state.production_month in [4, 6, 9, 11]:
#                         max_day = 30
#                     elif st.session_state.production_month == 2:
#                         if st.session_state.production_year % 4 == 0 and (st.session_state.production_year % 100 != 0 or st.session_state.production_year % 400 == 0):
#                             max_day = 29
#                         else:
#                             max_day = 28
                    
#                     # Create day buttons
#                     day_cols = st.columns(7)
#                     days = list(range(1, max_day + 1))
#                     for i, day in enumerate(days):
#                         with day_cols[i % 7]:
#                             if st.button(f"{day:02d}", key=f"btn_day_{day}"):
#                                 st.session_state.production_day = day
                
#                 # Construct the production date
#                 if st.session_state.production_year and st.session_state.production_month and st.session_state.production_day:
#                     production_date = f"{st.session_state.production_day:02d}.{st.session_state.production_month:02d}.{st.session_state.production_year}"
#                     st.write(f"Production date: **{production_date}**")
            
#             min_expire_date = None
#             try:
#                 if production_date:
#                     prod_date = datetime.strptime(production_date, "%d.%m.%Y")
#                     min_expire_date = prod_date
#             except:
#                 st.warning("Invalid production date format")
            
#             # Expire Date Selection
#             if production_date:
#                 st.subheader("Expire Date")
                
#                 # Expire date method buttons
#                 exp_col1, exp_col2 = st.columns(2)
#                 with exp_col1:
#                     if st.button("Direct input", key="btn_direct_exp"):
#                         st.session_state.expire_date_method = "Direct input"
#                 with exp_col2:
#                     if st.button("Step by step", key="btn_step_exp"):
#                         st.session_state.expire_date_method = "Step by step"
                        
#                 # Show the selected expire date method
#                 if st.session_state.expire_date_method:
#                     st.write(f"Selected method: **{st.session_state.expire_date_method}**")
                
#                 expire_date = ""
#                 if st.session_state.expire_date_method == "Direct input":
#                     expire_date = st.text_input("expire_date (dd.mm.yyyy)", value="01.03.2025")
#                 elif st.session_state.expire_date_method == "Step by step":
#                     # Set default values
#                     default_year = datetime.now().year
#                     default_month = datetime.now().month
#                     default_day = 1
#                     if min_expire_date:
#                         default_expire = min_expire_date + timedelta(days=60)
#                         default_year = default_expire.year
#                         default_month = default_expire.month
#                         default_day = default_expire.day
                    
#                     # Year selection
#                     st.write("Select expire year:")
#                     exp_year_cols = st.columns(5)
#                     exp_years = list(range(2020, 2030))
#                     for i, year in enumerate(exp_years):
#                         with exp_year_cols[i % 5]:
#                             if st.button(str(year), key=f"btn_exp_year_{year}"):
#                                 st.session_state.expire_year = year
                    
#                     # Month selection (only shown after year is selected)
#                     if st.session_state.expire_year:
#                         st.write(f"Selected expire year: **{st.session_state.expire_year}**")
#                         st.write("Select expire month:")
#                         exp_month_cols = st.columns(6)
#                         exp_months = list(range(1, 13))
#                         for i, month in enumerate(exp_months):
#                             with exp_month_cols[i % 6]:
#                                 if st.button(f"{month:02d}", key=f"btn_exp_month_{month}"):
#                                     st.session_state.expire_month = month
                    
#                     # Day selection (only shown after month is selected)
#                     if st.session_state.expire_month:
#                         st.write(f"Selected expire month: **{st.session_state.expire_month:02d}**")
#                         st.write("Select expire day:")
                        
#                         # Calculate max days for the month
#                         max_day = 31
#                         if st.session_state.expire_month in [4, 6, 9, 11]:
#                             max_day = 30
#                         elif st.session_state.expire_month == 2:
#                             if st.session_state.expire_year % 4 == 0 and (st.session_state.expire_year % 100 != 0 or st.session_state.expire_year % 400 == 0):
#                                 max_day = 29
#                             else:
#                                 max_day = 28
                        
#                         # Create day buttons
#                         exp_day_cols = st.columns(7)
#                         exp_days = list(range(1, max_day + 1))
#                         for i, day in enumerate(exp_days):
#                             with exp_day_cols[i % 7]:
#                                 if st.button(f"{day:02d}", key=f"btn_exp_day_{day}"):
#                                     st.session_state.expire_day = day
                    
#                     # Construct the expire date
#                     if st.session_state.expire_year and st.session_state.expire_month and st.session_state.expire_day:
#                         expire_date = f"{st.session_state.expire_day:02d}.{st.session_state.expire_month:02d}.{st.session_state.expire_year}"
#                         st.write(f"Expiration date: **{expire_date}**")
                
#                 duration = 0
#                 if production_date and expire_date:
#                     try:
#                         production_date_dt = datetime.strptime(production_date, "%d.%m.%Y")
#                         expire_date_dt = datetime.strptime(expire_date, "%d.%m.%Y")
#                         duration = (expire_date_dt - production_date_dt).days
#                     except Exception as e:
#                         st.error(f"Error calculating duration: {str(e)}")
#                         duration = 0
                    
#                     st.subheader("Product Duration Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Production Date:**")
#                         st.markdown("**Expiration Date:**")
#                         st.markdown("**Period of Duration:**")
#                     with col2:
#                         st.markdown(f"**{production_date}**")
#                         st.markdown(f"**{expire_date}**")
#                         st.markdown(f"**{duration} days**" if duration >= 0 else "**<span style='color:red'>non-eatable product</span>**", unsafe_allow_html=True)
                    
#                     today = datetime.now()
#                     expire_datetime = datetime.strptime(expire_date, "%d.%m.%Y")
#                     if expire_datetime < today:
#                         st.error("Warning: Product has already expired!")
                    
#                     # Brand availability with buttons
#                     st.write("Brand availability:")
#                     avail_col1, avail_col2 = st.columns(2)
#                     with avail_col1:
#                         if st.button("Yes", key="btn_avail_yes"):
#                             st.session_state.brand_availability = "yes"
#                     with avail_col2:
#                         if st.button("No", key="btn_avail_no"):
#                             st.session_state.brand_availability = "no"
                    
#                     # Show selected brand availability
#                     if st.session_state.brand_availability:
#                         st.write(f"Brand availability: **{st.session_state.brand_availability}**")
                    
#                     # Discount input
#                     discount = st.number_input("discount", min_value=0, max_value=100, step=1)
                    
#                     discount_amount = price * discount / 100
#                     discounted_price = int(price - discount_amount)
                    
#                     st.subheader("Discount Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Real price of product:**")
#                         st.markdown("**Discount percentage:**")
#                         st.markdown("**Price after discount:**")
#                     with col2:
#                         st.markdown(f"**{price} sum**")
#                         st.markdown(f"**{discount}%**")
#                         st.markdown(f"**{discounted_price} sum**")
                    
#                     # Only show submit button when all required fields are filled
#                     if st.session_state.brand_availability:
#                         st.markdown("---")
#                         st.markdown("### Ready to submit your product data")
                        
#                         # Create a prominent SUBMIT button with custom styling
#                         submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
#                         with submit_col2:
#                             if st.button("SUBMIT", key="final_submit", use_container_width=True):
#                                 data = {
#                                     "product_direction": st.session_state.selected_direction,
#                                     "product_category": st.session_state.selected_category,
#                                     "product_brand": st.session_state.selected_brand,
#                                     "product_name": st.session_state.selected_product,
#                                     "product_price": f"{price} sum",
#                                     "production_date": production_date,
#                                     "expire_date": expire_date,
#                                     "period_of_duration": f"{duration} days" if duration >= 0 else "non-eatable product",
#                                     "brand_availability": st.session_state.brand_availability,
#                                     "discount_percentage": f"{discount}%",
#                                     "price_after_discount": f"{discounted_price} sum"
#                                 }
#                                 df_new = pd.DataFrame([data])
#                                 if not os.path.exists(csv_file):
#                                     df_new.to_csv(csv_file, index=False)
#                                 else:
#                                     df_old = pd.read_csv(csv_file)
#                                     df_all = pd.concat([df_old, df_new], ignore_index=True)
#                                     df_all.to_csv(csv_file, index=False)
                                
#                                 st.success("Data submitted successfully")
#                                 st.json(data)



















































# def dat():

#     food_products = {
#         "Dairy Products": {
#             "brands": ["Nestlé", "Danone", "Parmalat", "President", "Amul", "Campina"],
#             "products": ["Milk", "Yogurt", "Kefir", "Cheese", "Cottage Cheese", "Cream", "Butter"]
#         },
#         "Bakery Products": {
#             "brands": ["Barilla", "Makfa", "Ozon", "Pioner", "Yashkino"],
#             "products": ["Wheat Flour", "Pasta", "Bread", "Biscuits", "Noodles", "Buns"]
#         },
#         "Meat Products": {
#             "brands": ["Tyson", "Oscar Mayer", "Hormel", "Perdue", "Cherkizovo"],
#             "products": ["Beef", "Lamb", "Poultry", "Sausage", "Hot Dogs", "Smoked Meat"]
#         },
#         "Beverages": {
#             "brands": ["Coca-Cola", "Pepsi", "Nestlé Pure Life", "Lipton", "Nescafé"],
#             "products": ["Mineral Water", "Carbonated Drinks", "Juices", "Tea", "Coffee"]
#         },
#         "Sweets": {
#             "brands": ["Mars", "Ferrero", "Milka", "Nestlé", "Roshen"],
#             "products": ["Chocolate", "Candies", "Cakes", "Ice Cream", "Halva", "Jam"]
#         }
#     }

#     csv_file = "products_data.csv"

#     # Initialize session state variables
#     if 'uploaded_df' not in st.session_state:
#         st.session_state.uploaded_df = None
#     if 'show_upload' not in st.session_state:
#         st.session_state.show_upload = False
#     if 'show_manual' not in st.session_state:
#         st.session_state.show_manual = False
        
#     # For button-based selection state variables
#     if 'selected_direction' not in st.session_state:
#         st.session_state.selected_direction = None
#     if 'selected_category' not in st.session_state:
#         st.session_state.selected_category = None
#     if 'selected_brand' not in st.session_state:
#         st.session_state.selected_brand = None
#     if 'selected_product' not in st.session_state:
#         st.session_state.selected_product = None
#     if 'date_input_method' not in st.session_state:
#         st.session_state.date_input_method = None
#     if 'expire_date_method' not in st.session_state:
#         st.session_state.expire_date_method = None
#     if 'production_year' not in st.session_state:
#         st.session_state.production_year = None
#     if 'production_month' not in st.session_state:
#         st.session_state.production_month = None
#     if 'production_day' not in st.session_state:
#         st.session_state.production_day = None
#     if 'expire_year' not in st.session_state:
#         st.session_state.expire_year = None
#     if 'expire_month' not in st.session_state:
#         st.session_state.expire_month = None
#     if 'expire_day' not in st.session_state:
#         st.session_state.expire_day = None
#     if 'brand_availability' not in st.session_state:
#         st.session_state.brand_availability = None

#     # Main interface
#     st.title("Product Management System")

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Upload"):
#             st.session_state.show_upload = True
#             st.session_state.show_manual = False  # Hide manual when showing upload
#     with col2:
#         if st.button("Manual"):
#             st.session_state.show_manual = True
#             st.session_state.show_upload = False  # Hide upload when showing manual
#             # Reset selection state when switching to manual mode
#             st.session_state.selected_direction = None
#             st.session_state.selected_category = None
#             st.session_state.selected_brand = None
#             st.session_state.selected_product = None
#             st.session_state.date_input_method = None
#             st.session_state.expire_date_method = None

#     # File Upload Section (shown only when "Upload" is clicked)
#     if st.session_state.show_upload:
#         st.subheader("File Upload")
#         try:
#             uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
            
#             if uploaded_file is not None:
#                 try:
#                     if uploaded_file.name.endswith('.csv'):
#                         df = pd.read_csv(uploaded_file, encoding='iso-8859-1', sep=',', on_bad_lines='skip')
#                     elif uploaded_file.name.endswith('.xlsx'):
#                         df = pd.read_excel(uploaded_file)
                    
#                     st.success(f"File '{uploaded_file.name}' successfully loaded!")
#                     # Display single editable table
#                     edited_df = st.data_editor(df, num_rows="dynamic", key="upload_editor")
#                     st.session_state.uploaded_df = edited_df
                    
#                     # Save edited data to CSV
#                     if st.button("Save Uploaded Data"):
#                         if not os.path.exists(csv_file):
#                             edited_df.to_csv(csv_file, index=False)
#                         else:
#                             df_old = pd.read_csv(csv_file)
#                             df_all = pd.concat([df_old, edited_df], ignore_index=True)
#                             df_all.to_csv(csv_file, index=False)
#                         st.success("Uploaded data saved successfully!")
#                 except Exception as e:
#                     st.error(f"Error reading file: {str(e)}")
#                     st.info("Try opening and resaving your CSV file in Excel with comma delimiter and ISO-8859-1 encoding.")
#         except Exception as e:
#             st.error(f"Error with file uploader: {str(e)}")

#     # Manual Data Entry Section (shown when "Manual" is clicked)
#     if st.session_state.show_manual:
#         st.subheader("Manual Product Entry")
        
#         # Direction selection with buttons
#         st.write("Select product direction:")
#         dir_col1, dir_col2 = st.columns(2)
#         with dir_col1:
#             if st.button("Food Products", key="btn_food"):
#                 st.session_state.selected_direction = "food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
#         with dir_col2:
#             if st.button("Non-Food Products", key="btn_nonfood"):
#                 st.session_state.selected_direction = "non_food_products"
#                 # Reset downstream selections
#                 st.session_state.selected_category = None
                
#         # Show the selected direction
#         if st.session_state.selected_direction:
#             st.write(f"Selected direction: **{st.session_state.selected_direction}**")
                
#         # Category Selection (only shown after direction is selected)
#         if st.session_state.selected_direction:
#             st.write("Select product category:")
            
#             if st.session_state.selected_direction == "food_products":
#                 # Create columns for food product categories
#                 categories = list(food_products.keys())
#                 category_cols = st.columns(len(categories))
                
#                 for i, category in enumerate(categories):
#                     with category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
#             else:
#                 # For non-food products, use limited categories
#                 non_food_categories = ["Electronics", "Clothing", "Home Goods"]
#                 nf_category_cols = st.columns(len(non_food_categories))
                
#                 for i, category in enumerate(non_food_categories):
#                     with nf_category_cols[i]:
#                         if st.button(category, key=f"btn_cat_{category}"):
#                             st.session_state.selected_category = category
#                             # Reset downstream selections
#                             st.session_state.selected_brand = None
#                             st.session_state.selected_product = None
        
#         # Show the selected category
#         if st.session_state.selected_category:
#             st.write(f"Selected category: **{st.session_state.selected_category}**")
            
#         # Brand Selection (only shown after category is selected)
#         if st.session_state.selected_category and st.session_state.selected_direction == "food_products":
#             st.write("Select product brand:")
            
#             # Get the brands for the selected category
#             brands = food_products[st.session_state.selected_category]["brands"]
#             # Create a dynamic number of columns based on how many brands
#             brand_cols = st.columns(min(len(brands), 3))
            
#             # Place brands in columns and create buttons
#             for i, brand in enumerate(brands):
#                 col_index = i % len(brand_cols)
#                 with brand_cols[col_index]:
#                     if st.button(brand, key=f"btn_brand_{brand}"):
#                         st.session_state.selected_brand = brand
#                         # Reset product selection
#                         st.session_state.selected_product = None
#         elif st.session_state.selected_category and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for brand
#             st.session_state.selected_brand = st.text_input("Enter product brand", "Brand Name")
            
#         # Show the selected brand
#         if st.session_state.selected_brand:
#             st.write(f"Selected brand: **{st.session_state.selected_brand}**")
            
#         # Product Selection (only shown after brand is selected)
#         if st.session_state.selected_brand and st.session_state.selected_direction == "food_products":
#             st.write("Select product:")
            
#             # Get the products for the selected category
#             products = food_products[st.session_state.selected_category]["products"]
#             # Create columns for products
#             product_cols = st.columns(min(len(products), 3))
            
#             # Place products in columns and create buttons
#             for i, product in enumerate(products):
#                 col_index = i % len(product_cols)
#                 with product_cols[col_index]:
#                     if st.button(product, key=f"btn_product_{product}"):
#                         st.session_state.selected_product = product
#         elif st.session_state.selected_brand and st.session_state.selected_direction == "non_food_products":
#             # For non-food products, use a text input for product name
#             st.session_state.selected_product = st.text_input("Enter product name", "Product Name")
            
#         # Show the selected product
#         if st.session_state.selected_product:
#             st.write(f"Selected product: **{st.session_state.selected_product}**")
            
#         # Price input (only shown after product is selected)
#         if st.session_state.selected_product:
#             price = st.number_input("product_price", min_value=0, step=1000, value=0)
#             st.write(f"{price} sum")
            
#             # Production Date Selection
#             st.subheader("Production Date")
            
#             # Date input method buttons
#             date_col1, date_col2 = st.columns(2)
#             with date_col1:
#                 if st.button("Direct input", key="btn_direct_date"):
#                     st.session_state.date_input_method = "Direct input"
#             with date_col2:
#                 if st.button("Step by step", key="btn_step_date"):
#                     st.session_state.date_input_method = "Step by step"
                    
#             # Show the selected date input method
#             if st.session_state.date_input_method:
#                 st.write(f"Selected method: **{st.session_state.date_input_method}**")
            
#             production_date = ""
#             if st.session_state.date_input_method == "Direct input":
#                 production_date = st.text_input("production_date (dd.mm.yyyy)", value="01.01.2025")
#             elif st.session_state.date_input_method == "Step by step":
#                 # Year selection
#                 st.write("Select production year:")
#                 year_cols = st.columns(6)
#                 years = list(range(2020, 2026))
#                 for i, year in enumerate(years):
#                     with year_cols[i]:
#                         if st.button(str(year), key=f"btn_year_{year}"):
#                             st.session_state.production_year = year
                
#                 # Month selection (only shown after year is selected)
#                 if st.session_state.production_year:
#                     st.write(f"Selected production year: **{st.session_state.production_year}**")
#                     st.write("Select production month:")
#                     month_cols = st.columns(6)
#                     months = list(range(1, 13))
#                     for i, month in enumerate(months):
#                         with month_cols[i % 6]:
#                             if st.button(f"{month:02d}", key=f"btn_month_{month}"):
#                                 st.session_state.production_month = month
                
#                 # Day selection (only shown after month is selected)
#                 if st.session_state.production_month:
#                     st.write(f"Selected production month: **{st.session_state.production_month:02d}**")
#                     st.write("Select production day:")
                    
#                     # Calculate max days for the month
#                     max_day = 31
#                     if st.session_state.production_month in [4, 6, 9, 11]:
#                         max_day = 30
#                     elif st.session_state.production_month == 2:
#                         if st.session_state.production_year % 4 == 0 and (st.session_state.production_year % 100 != 0 or st.session_state.production_year % 400 == 0):
#                             max_day = 29
#                         else:
#                             max_day = 28
                    
#                     # Create day buttons
#                     day_cols = st.columns(7)
#                     days = list(range(1, max_day + 1))
#                     for i, day in enumerate(days):
#                         with day_cols[i % 7]:
#                             if st.button(f"{day:02d}", key=f"btn_day_{day}"):
#                                 st.session_state.production_day = day
                
#                 # Construct the production date
#                 if st.session_state.production_year and st.session_state.production_month and st.session_state.production_day:
#                     production_date = f"{st.session_state.production_day:02d}.{st.session_state.production_month:02d}.{st.session_state.production_year}"
#                     st.write(f"Production date: **{production_date}**")
            
#             min_expire_date = None
#             try:
#                 if production_date:
#                     prod_date = datetime.strptime(production_date, "%d.%m.%Y")
#                     min_expire_date = prod_date
#             except:
#                 st.warning("Invalid production date format")
            
#             # Expire Date Selection
#             if production_date:
#                 st.subheader("Expire Date")
                
#                 # Expire date method buttons
#                 exp_col1, exp_col2 = st.columns(2)
#                 with exp_col1:
#                     if st.button("Direct input", key="btn_direct_exp"):
#                         st.session_state.expire_date_method = "Direct input"
#                 with exp_col2:
#                     if st.button("Step by step", key="btn_step_exp"):
#                         st.session_state.expire_date_method = "Step by step"
                        
#                 # Show the selected expire date method
#                 if st.session_state.expire_date_method:
#                     st.write(f"Selected method: **{st.session_state.expire_date_method}**")
                
#                 expire_date = ""
#                 if st.session_state.expire_date_method == "Direct input":
#                     expire_date = st.text_input("expire_date (dd.mm.yyyy)", value="01.03.2025")
#                 elif st.session_state.expire_date_method == "Step by step":
#                     # Set default values
#                     default_year = datetime.now().year
#                     default_month = datetime.now().month
#                     default_day = 1
#                     if min_expire_date:
#                         default_expire = min_expire_date + timedelta(days=60)
#                         default_year = default_expire.year
#                         default_month = default_expire.month
#                         default_day = default_expire.day
                    
#                     # Year selection
#                     st.write("Select expire year:")
#                     exp_year_cols = st.columns(5)
#                     # Ensure expire year cannot be earlier than production year
#                     min_year = st.session_state.production_year
#                     exp_years = list(range(min_year, 2030))
#                     for i, year in enumerate(exp_years):
#                         with exp_year_cols[i % 5]:
#                             if st.button(str(year), key=f"btn_exp_year_{year}"):
#                                 st.session_state.expire_year = year
                    
#                     # Month selection (only shown after year is selected)
#                     if st.session_state.expire_year:
#                         st.write(f"Selected expire year: **{st.session_state.expire_year}**")
#                         st.write("Select expire month:")
#                         exp_month_cols = st.columns(6)
                        
#                         # If same year as production date, start months from production month
#                         min_month = 1
#                         if st.session_state.expire_year == st.session_state.production_year:
#                             min_month = st.session_state.production_month
                            
#                         exp_months = list(range(min_month, 13))
#                         for i, month in enumerate(exp_months):
#                             with exp_month_cols[i % 6]:
#                                 if st.button(f"{month:02d}", key=f"btn_exp_month_{month}"):
#                                     st.session_state.expire_month = month
                    
#                     # Day selection (only shown after month is selected)
#                     if st.session_state.expire_month:
#                         st.write(f"Selected expire month: **{st.session_state.expire_month:02d}**")
#                         st.write("Select expire day:")
                        
#                         # Calculate max days for the month
#                         max_day = 31
#                         if st.session_state.expire_month in [4, 6, 9, 11]:
#                             max_day = 30
#                         elif st.session_state.expire_month == 2:
#                             if st.session_state.expire_year % 4 == 0 and (st.session_state.expire_year % 100 != 0 or st.session_state.expire_year % 400 == 0):
#                                 max_day = 29
#                             else:
#                                 max_day = 28
                                
#                         # Check if expire date would be earlier than production date
#                         min_day = 1
#                         if (st.session_state.expire_year == st.session_state.production_year and 
#                             st.session_state.expire_month == st.session_state.production_month):
#                             # If same year and month, expiry day must be >= production day
#                             min_day = st.session_state.production_day
                        
#                         # Create day buttons
#                         exp_day_cols = st.columns(7)
#                         exp_days = list(range(min_day, max_day + 1))
#                         for i, day in enumerate(exp_days):
#                             with exp_day_cols[i % 7]:
#                                 if st.button(f"{day:02d}", key=f"btn_exp_day_{day}"):
#                                     st.session_state.expire_day = day
                    
#                     # Construct the expire date
#                     if st.session_state.expire_year and st.session_state.expire_month and st.session_state.expire_day:
#                         expire_date = f"{st.session_state.expire_day:02d}.{st.session_state.expire_month:02d}.{st.session_state.expire_year}"
#                         st.write(f"Expiration date: **{expire_date}**")
                
#                 duration = 0
#                 if production_date and expire_date:
#                     try:
#                         production_date_dt = datetime.strptime(production_date, "%d.%m.%Y")
#                         expire_date_dt = datetime.strptime(expire_date, "%d.%m.%Y")
                        
#                         # Validate that expire date is not before production date
#                         if expire_date_dt < production_date_dt:
#                             st.error("Error: Expiration date cannot be earlier than production date!")
#                             duration = 0
#                         else:
#                             duration = (expire_date_dt - production_date_dt).days
#                     except Exception as e:
#                         st.error(f"Error calculating duration: {str(e)}")
#                         duration = 0
                    
#                     st.subheader("Product Duration Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Production Date:**")
#                         st.markdown("**Expiration Date:**")
#                         st.markdown("**Period of Duration:**")
#                     with col2:
#                         st.markdown(f"**{production_date}**")
#                         st.markdown(f"**{expire_date}**")
#                         st.markdown(f"**{duration} days**" if duration >= 0 else "**<span style='color:red'>non-eatable product</span>**", unsafe_allow_html=True)
                    
#                     today = datetime.now()
#                     expire_datetime = datetime.strptime(expire_date, "%d.%m.%Y")
#                     if expire_datetime < today:
#                         st.error("Warning: Product has already expired!")
                    
#                     # Brand availability with buttons
#                     st.write("Brand availability:")
#                     avail_col1, avail_col2 = st.columns(2)
#                     with avail_col1:
#                         if st.button("Yes", key="btn_avail_yes"):
#                             st.session_state.brand_availability = "yes"
#                     with avail_col2:
#                         if st.button("No", key="btn_avail_no"):
#                             st.session_state.brand_availability = "no"
                    
#                     # Show selected brand availability
#                     if st.session_state.brand_availability:
#                         st.write(f"Brand availability: **{st.session_state.brand_availability}**")
                    
#                     # Discount input
#                     discount = st.number_input("discount", min_value=0, max_value=100, step=1)
                    
#                     discount_amount = price * discount / 100
#                     discounted_price = int(price - discount_amount)
                    
#                     st.subheader("Discount Information")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown("**Real price of product:**")
#                         st.markdown("**Discount percentage:**")
#                         st.markdown("**Price after discount:**")
#                     with col2:
#                         st.markdown(f"**{price} sum**")
#                         st.markdown(f"**{discount}%**")
#                         st.markdown(f"**{discounted_price} sum**")
                    
#                     # Only show submit button when all required fields are filled
#                     if st.session_state.brand_availability:
#                         st.markdown("---")
#                         st.markdown("### Ready to submit your product data")
                        
#                         # Create a prominent SUBMIT button with custom styling
#                         submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
#                         with submit_col2:
#                             if st.button("SUBMIT", key="final_submit", use_container_width=True):
#                                 data = {
#                                     "product_direction": st.session_state.selected_direction,
#                                     "product_category": st.session_state.selected_category,
#                                     "product_brand": st.session_state.selected_brand,
#                                     "product_name": st.session_state.selected_product,
#                                     "product_price": f"{price} sum",
#                                     "production_date": production_date,
#                                     "expire_date": expire_date,
#                                     "period_of_duration": f"{duration} days" if duration >= 0 else "non-eatable product",
#                                     "brand_availability": st.session_state.brand_availability,
#                                     "discount_percentage": f"{discount}%",
#                                     "price_after_discount": f"{discounted_price} sum"
#                                 }
#                                 df_new = pd.DataFrame([data])
#                                 if not os.path.exists(csv_file):
#                                     df_new.to_csv(csv_file, index=False)
#                                 else:
#                                     df_old = pd.read_csv(csv_file)
#                                     df_all = pd.concat([df_old, df_new], ignore_index=True)
#                                     df_all.to_csv(csv_file, index=False)
                                
#                                 st.success("Data submitted successfully")
#                                 st.table(data)

                  