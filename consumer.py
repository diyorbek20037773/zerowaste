def tables():
    import streamlit as st
    import pandas as pd

    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv('store_product_data.csv')
            return df
        except FileNotFoundError:
            try:
                df = pd.read_csv("D:/Dasturlash/VS code/Hakhathon/Navruz/ZeroWaste/store_product_data.csv")
                return df
            except Exception as e:
                st.error(f"Error loading CSV file: {e}")
                return pd.DataFrame(columns=['product_group', 'product_brand', 'product_name'])


    def main():
    
        
        df = load_data()
        
        if df.empty:
            st.warning("No data available. Please check the CSV file path.")
            return
        
        df.columns = [col.lower() for col in df.columns]
     
        required_columns = ['product_group', 'product_brand', 'product_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"Missing columns in CSV: {', '.join(missing_columns)}")
            st.write("Available columns:", ", ".join(df.columns))
            
            column_mapping = {}
            for req_col in missing_columns:
                possible_matches = [col for col in df.columns if req_col.replace('_', '') in col.replace('_', '').lower()]
                if possible_matches:
                    column_mapping[possible_matches[0]] = req_col
                    st.info(f"Mapped '{possible_matches[0]}' to '{req_col}'")
     
            if column_mapping:
                df = df.rename(columns=column_mapping)
        
        st.sidebar.header("Filters")
        
        if 'product_group' in df.columns:
            product_groups = ['All'] + sorted(df['product_group'].unique().tolist())
            selected_group = st.sidebar.selectbox("Select Product Group:", product_groups)
        else:
            selected_group = 'All'
            st.sidebar.warning("Product Group filter not available")
        
        if 'product_brand' in df.columns:
          
            if selected_group != 'All':
                brand_options = df[df['product_group'] == selected_group]['product_brand'].unique()
            else:
                brand_options = df['product_brand'].unique()
            
            product_brands = ['All'] + sorted(brand_options.tolist())
            selected_brand = st.sidebar.selectbox("Select Product Brand:", product_brands)
        else:
            selected_brand = 'All'
            st.sidebar.warning("Product Brand filter not available")
        
       
        if 'product_name' in df.columns:
         
            filtered_df = df.copy()
            if selected_group != 'All':
                filtered_df = filtered_df[filtered_df['product_group'] == selected_group]
            if selected_brand != 'All':
                filtered_df = filtered_df[filtered_df['product_brand'] == selected_brand]
            
            product_names = ['All'] + sorted(filtered_df['product_name'].unique().tolist())
            selected_name = st.sidebar.selectbox("Select Product Name:", product_names)
        else:
            selected_name = 'All'
            st.sidebar.warning("Product Name filter not available")
        
    
        filtered_df = df.copy()
        
        if selected_group != 'All' and 'product_group' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['product_group'] == selected_group]
        
        if selected_brand != 'All' and 'product_brand' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['product_brand'] == selected_brand]
        
        if selected_name != 'All' and 'product_name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['product_name'] == selected_name]
        
     
        st.write("### Current Filters:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Product Group:** {selected_group}")
        with col2:
            st.write(f"**Product Brand:** {selected_brand}")
        with col3:
            st.write(f"**Product Name:** {selected_name}")
        

        st.write(f"### Results: {len(filtered_df)} products found")
        
      
        search_term = st.text_input("Search in results:", "")
        if search_term:
         
            text_columns = filtered_df.select_dtypes(include=['object']).columns
            mask = False
            for col in text_columns:
                mask = mask | filtered_df[col].str.contains(search_term, case=False, na=False)
            filtered_df = filtered_df[mask]
            st.write(f"Found {len(filtered_df)} results containing '{search_term}'")
        
  
        columns_to_show = ['store_name', 'product_group', 'product_brand', 'product_name',"product_price", "status",  "date_of_manufacture", "date_of_expiry","sales_volume"]
        st.dataframe(filtered_df[columns_to_show], use_container_width=True)
        
     
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Filtered Data",
                csv,
                "filtered_products.csv",
                "text/csv",
                key="download-csv"
            )
  
    main()















def maps():
    import streamlit as st
    import pandas as pd
    import folium
    from streamlit_folium import folium_static
    from math import radians, sin, cos, sqrt, asin

    @st.cache_data
    def load_data():
        try:
         
            try:
            
                df = pd.read_csv('./store_product_data.csv')
            except FileNotFoundError:
            
                try:
                    df = pd.read_csv("D:/Dasturlash/VS code/Hakhathon/Navruz/ZeroWaste/store_product_data.csv")
                    st.info("Using absolute path for data file.")
                except:
                    st.error("Could not find the data file. Using sample data instead.")
               
                    sample_data = {
                        'shop_name': ['Sample Shop 1', 'Sample Shop 2', 'Sample Shop 3', 
                                      'Sample Shop 4', 'Sample Shop 5', 'Sample Shop 6'],
                        'latitude': [34.0047, 34.1205, 34.0553, 34.0298, 34.0331, 34.0482],
                        'longitude': [-118.2661, -118.3071, -118.4152, -118.2943, -118.3550, -118.2437]
                    }
                    return pd.DataFrame(sample_data)

            column_mapping = {
                'store name': 'shop_name',
                'location_lat': 'latitude', 
                'location_long': 'longitude'  
            }
            
          
            for original, new_name in column_mapping.items():
                if original in df.columns:
                    df = df.rename(columns={original: new_name})
            
          
            required_columns = ['shop_name', 'latitude', 'longitude']
            missing_columns = set(required_columns) - set(df.columns)
            
         
            if missing_columns:
        
                position_mapping = {}
                
          
                if 'shop_name' in missing_columns and len(df.columns) >= 1:
                    position_mapping[df.columns[0]] = 'shop_name'
                    
            
                if 'longitude' in missing_columns and len(df.columns) >= 2:
                    position_mapping[df.columns[1]] = 'longitude'
                    
            
                if 'latitude' in missing_columns and len(df.columns) >= 3:
                    position_mapping[df.columns[2]] = 'latitude'
                
        
                if position_mapping:
                    df = df.rename(columns=position_mapping)
            
       
            still_missing = set(required_columns) - set(df.columns)
            if still_missing:
                raise ValueError(f"Could not map the following required columns: {still_missing}")
            
            return df
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
            sample_data = {
                'shop_name': ['Sample Shop 1', 'Sample Shop 2', 'Sample Shop 3',
                              'Sample Shop 4', 'Sample Shop 5', 'Sample Shop 6'],
                'latitude': [34.0047, 34.1205, 34.0553, 34.0298, 34.0331, 34.0482],
                'longitude': [-118.2661, -118.3071, -118.4152, -118.2943, -118.3550, -118.2437]
            }
            return pd.DataFrame(sample_data)


    def haversine_distance(lat1, lon1, lat2, lon2):
   
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 
        
        return c * r

  
    df = load_data()

    
  
    unique_shops = sorted(df['shop_name'].unique())
    
   
    shop_to_show = st.selectbox("Select a shop:", unique_shops)
    
  
    if shop_to_show:
       
        selected_shop = df[df['shop_name'] == shop_to_show].iloc[0]
        
    
        base_lat = selected_shop['latitude']
        base_lon = selected_shop['longitude']
        
  
        distances = []
        for idx, row in df.iterrows():
            
            if row['shop_name'] == shop_to_show and row['latitude'] == base_lat and row['longitude'] == base_lon:
                continue
                
            distance = haversine_distance(base_lat, base_lon, row['latitude'], row['longitude'])
            distances.append((row['shop_name'], row['latitude'], row['longitude'], distance))

        nearest_shops = sorted(distances, key=lambda x: x[3])[:4]
   
        m = folium.Map(location=[base_lat, base_lon], zoom_start=14)
        

        folium.Marker(
            [base_lat, base_lon],
            popup=shop_to_show,
            tooltip=shop_to_show,
            icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
        ).add_to(m)
        
   
        for shop_name, lat, lon, distance in nearest_shops:
            folium.Marker(
                [lat, lon],
                popup=f"{shop_name} - {distance:.2f} km away",
                tooltip=shop_name,
                icon=folium.Icon(color='blue', icon='store', prefix='fa')
            ).add_to(m)
            
        
            folium.PolyLine(
                locations=[[base_lat, base_lon], [lat, lon]],
                color='gray',
                weight=2,
                opacity=0.7,
                dash_array='5'
            ).add_to(m)
        
   
        st.subheader(f"Selected Shop: {shop_to_show}")
        st.write(f"Location: {base_lat:.6f}, {base_lon:.6f}")
        
        st.subheader("Nearest 4 Shops:")
        for i, (shop_name, lat, lon, distance) in enumerate(nearest_shops, 1):
            st.write(f"{i}. {shop_name} - {distance:.2f} km away")
        
     
        st.subheader("Map:")
        folium_static(m)