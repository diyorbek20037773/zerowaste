import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import folium
from streamlit_folium import folium_static
import calendar
import os

class StoreDataAnalysisDashboard:
    """
    A comprehensive Streamlit dashboard for analyzing store data with 
    advanced visualizations and machine learning insights.
    """
    
    def __init__(self, set_page_config=True):
        """Initialize the dashboard with configuration settings"""
        # Set page configuration only if requested
        if set_page_config:
            st.set_page_config(
                layout="wide",
                initial_sidebar_state="expanded"
            )
        

        
        # Apply custom CSS
        self.apply_custom_css()
        
        # Initialize state variables
        self.df = None
        self.df_filtered = None
        self.model = None
        self.discount_threshold = 15.0
        self.ultra_discount_threshold = 20.0
        
        # Load data and model
        self.load_data()
        self.load_model()
    
    def apply_custom_css(self):
        """Apply custom CSS styling to the dashboard"""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1E88E5;
                text-align: center;
                margin-bottom: 1rem;
            }
            .sub-header {
                font-size: 1.8rem;
                color: #0D47A1;
                margin-top: 2rem;
            }
            .section-header {
                font-size: 1.3rem;
                color: #1565C0;
                margin-top: 1rem;
            }
            .highlight {
                background-color: grey;
                padding: 1rem;
                border-radius: 0.5rem;
            }
            .metric-card {
                background-color: #F5F5F5;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #1E88E5;
            }
            .metric-label {
                font-size: 1rem;
                color: #616161;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # @st.cache_data
    def load_data(self):
        """Load and preprocess the dataset"""
        try:
            # Try to load the enhanced data first
            self.df = pd.read_csv("enhanced_store_data.csv")
        except FileNotFoundError:
            try:
                # If enhanced data not found, try to load the original data
                self.df = pd.read_csv("store_product_data.csv")
              
            except FileNotFoundError:
                st.error("❌ No data files found! Please generate data first.")
                st.stop()
        
        # Convert date columns to datetime
        date_columns = [col for col in self.df.columns if 'date' in col.lower()]
        for col in date_columns:
            self.df[col] = pd.to_datetime(self.df[col])
        
        # Set the filtered dataframe initially to the full dataframe
        self.df_filtered = self.df.copy()
    
    # @st.cache_resource
    def load_model(self):
        """Load the ML model if available"""
        try:
            self.model = joblib.load('discount_percentage_model.joblib')
        except FileNotFoundError:
            pass
    
    def build_sidebar_filters(self):
        """Create sidebar filters for interactive data exploration"""
        st.sidebar.markdown("## Filters")
        
        # Date range filter
        if 'date_of_manufacture' in self.df.columns:
            min_date = self.df['date_of_manufacture'].min().date()
            max_date = self.df['date_of_manufacture'].max().date()
            
            date_range = st.sidebar.date_input(
                "Date Range (Manufacture Date)",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (self.df['date_of_manufacture'].dt.date >= start_date) & (self.df['date_of_manufacture'].dt.date <= end_date)
                self.df_filtered = self.df[mask]
            else:
                self.df_filtered = self.df
        else:
            self.df_filtered = self.df
        
        # Store filter
        if 'store_name' in self.df.columns:
            all_stores = ['All Stores'] + sorted(self.df['store_name'].unique().tolist())
            selected_store = st.sidebar.selectbox("Select Store", all_stores)
            
            if selected_store != 'All Stores':
                self.df_filtered = self.df_filtered[self.df_filtered['store_name'] == selected_store]
        
        # Product group filter
        if 'product_group' in self.df.columns:
            all_groups = ['All Groups'] + sorted(self.df['product_group'].unique().tolist())
            selected_group = st.sidebar.selectbox("Select Product Group", all_groups)
            
            if selected_group != 'All Groups':
                self.df_filtered = self.df_filtered[self.df_filtered['product_group'] == selected_group]
        
        # Brand filter
        if 'product_brand' in self.df.columns:
            all_brands = ['All Brands'] + sorted(self.df_filtered['product_brand'].unique().tolist())
            selected_brand = st.sidebar.selectbox("Select Brand", all_brands)
            
            if selected_brand != 'All Brands':
                self.df_filtered = self.df_filtered[self.df_filtered['product_brand'] == selected_brand]
        
        # Status filter
        if 'status' in self.df.columns:
            status_options = ['All'] + sorted(self.df['status'].unique().tolist())
            selected_status = st.sidebar.selectbox("Select Status", status_options)
            
            if selected_status != 'All':
                self.df_filtered = self.df_filtered[self.df_filtered['status'] == selected_status]
        
        # Discount filter
        if 'discount' in self.df.columns:
            discount_options = ['All', 'yes', 'no']
            selected_discount = st.sidebar.selectbox("Discount Applied", discount_options)
            
            if selected_discount != 'All':
                self.df_filtered = self.df_filtered[self.df_filtered['discount'] == selected_discount]
        
        # Sales volume range filter
        if 'sales_volume' in self.df.columns:
            min_sales = int(self.df['sales_volume'].min())
            max_sales = int(self.df['sales_volume'].max())
            
            sales_range = st.sidebar.slider(
                "Sales Volume Range",
                min_sales, max_sales,
                (min_sales, max_sales)
            )
            
            self.df_filtered = self.df_filtered[(self.df_filtered['sales_volume'] >= sales_range[0]) & 
                                         (self.df_filtered['sales_volume'] <= sales_range[1])]
        
        # Price range filter
        if 'product_price' in self.df.columns:
            min_price = float(self.df['product_price'].min())
            max_price = float(self.df['product_price'].max())
            
            price_range = st.sidebar.slider(
                "Product Price Range ($)",
                min_price, max_price,
                (min_price, max_price)
            )
            
            self.df_filtered = self.df_filtered[(self.df_filtered['product_price'] >= price_range[0]) & 
                                         (self.df_filtered['product_price'] <= price_range[1])]
        
        # Display filtered data count
        #st.sidebar.markdown(f"### Showing {len(self.df_filtered)} of {len(self.df)} records")
    
    def build_ml_thresholds(self):
        """Add ML threshold controls to the sidebar"""
        #st.sidebar.markdown("## ML Thresholds")
        
        if 'discount_percentage' in self.df.columns:
            self.discount_threshold = st.sidebar.slider(
                "Discount Percentage Threshold (%)",
                0.0, 50.0, 15.0, 0.5
            )
        
        if 'ultra_discount_percentage' in self.df.columns:
            self.ultra_discount_threshold = st.sidebar.slider(
                "Ultra Discount Threshold (%)",
                0.0, 50.0, 20.0, 0.5
            )
    
    def add_download_button(self):
        """Add download button for filtered data"""
        st.sidebar.markdown("## Export Data")
        
        if st.sidebar.button("Download Filtered Data"):
            csv = self.df_filtered.to_csv(index=False)
            st.sidebar.download_button(
                label="Click to Download CSV",
                data=csv,
                file_name="filtered_store_data.csv",
                mime="text/csv"
            )
    
    def build_overall_stats_tab(self):
        """Build the Overall Statistics tab content"""
        #st.markdown("<h2 class='sub-header'>Overall Statistics</h2>", unsafe_allow_html=True)
        
        # Key metrics in a row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-value'>{len(self.df_filtered)}</div>
                    <div class='metric-label'>Products</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            if 'product_price' in self.df_filtered.columns:
                total_value = self.df_filtered['product_price'].sum()
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-value'>${total_value:,.2f}</div>
                        <div class='metric-label'>Total Value</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        with col3:
            if 'sales_volume' in self.df_filtered.columns:
                total_sales = self.df_filtered['sales_volume'].sum()
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-value'>{total_sales:,}</div>
                        <div class='metric-label'>Total Sales Volume</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        with col4:
            if 'discount' in self.df_filtered.columns:
                discount_count = (self.df_filtered['discount'] == 'yes').sum()
                discount_pct = (discount_count / len(self.df_filtered)) * 100 if len(self.df_filtered) > 0 else 0
                st.markdown(
                    f"""
                    <div class='metric-card'>
                        <div class='metric-value'>{discount_pct:.1f}%</div>
                        <div class='metric-label'>Products Discounted</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        self.build_product_distribution()
        self.build_sales_pricing_analysis()
        self.build_geographic_distribution()
    
    def build_product_distribution(self):
        """Build product distribution charts"""
        st.markdown("<h3 class='section-header'>Product Distribution</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if 'product_group' in self.df_filtered.columns:
                group_counts = self.df_filtered['product_group'].value_counts().reset_index()
                group_counts.columns = ['Product Group', 'Count']
                
                fig = px.pie(
                    group_counts, 
                    values='Count', 
                    names='Product Group', 
                    title='Distribution by Product Group',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'store_name' in self.df_filtered.columns:
                store_counts = self.df_filtered['store_name'].value_counts().reset_index()
                store_counts.columns = ['Store', 'Count']
                
                fig = px.bar(
                    store_counts, 
                    x='Store', 
                    y='Count',
                    title='Distribution by Store',
                    color='Count',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def build_sales_pricing_analysis(self):
        """Build sales and pricing analysis charts"""
        st.markdown("<h3 class='section-header'>Sales & Pricing Analysis</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if 'product_group' in self.df_filtered.columns and 'sales_volume' in self.df_filtered.columns:
                group_sales = self.df_filtered.groupby('product_group')['sales_volume'].sum().reset_index()
                group_sales.columns = ['Product Group', 'Total Sales']
                
                fig = px.bar(
                    group_sales, 
                    x='Product Group', 
                    y='Total Sales',
                    title='Total Sales by Product Group',
                    color='Total Sales',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'product_group' in self.df_filtered.columns and 'product_price' in self.df_filtered.columns:
                group_price = self.df_filtered.groupby('product_group')['product_price'].mean().reset_index()
                group_price.columns = ['Product Group', 'Average Price']
                
                fig = px.bar(
                    group_price, 
                    x='Product Group', 
                    y='Average Price',
                    title='Average Price by Product Group',
                    color='Average Price',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(yaxis_title="Average Price ($)")
                st.plotly_chart(fig, use_container_width=True)
    
    # def build_geographic_distribution(self):
    #     """Build geographic distribution map"""
    #     if 'location_lat' in self.df_filtered.columns and 'location_long' in self.df_filtered.columns and 'store_name' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>Geographic Distribution</h3>", unsafe_allow_html=True)
            
    #         # Create a map centered at the mean of coordinates
    #         map_center = [self.df_filtered['location_lat'].mean(), self.df_filtered['location_long'].mean()]
    #         m = folium.Map(location=map_center, zoom_start=2)
            
    #         # Group by store and get mean coordinates and counts
    #         store_data = self.df_filtered.groupby('store_name').agg({
    #             'location_lat': 'mean',
    #             'location_long': 'mean',
    #             'product_name': 'count'
    #         }).reset_index()
            
    #         store_data.columns = ['store_name', 'lat', 'lon', 'count']
            
    #         # Add markers for each store
    #         for idx, row in store_data.iterrows():
    #             popup_text = f"""
    #             <b>{row['store_name']}</b><br>
    #             Products: {row['count']}<br>
    #             """
                
    #             folium.CircleMarker(
    #                 location=[row['lat'], row['lon']],
    #                 radius=5 + (row['count'] / store_data['count'].max() * 15),
    #                 popup=popup_text,
    #                 color='blue',
    #                 fill=True,
    #                 fill_color='blue'
    #             ).add_to(m)
            
    #         # Display the map
    #         folium_static(m)
    
    
    
    
    def build_geographic_distribution(self):
        """Build a beautiful and enhanced geographic distribution map"""
        # Import required plugins
        from folium.plugins import MarkerCluster, MiniMap
        import folium.plugins as plugins
        
        if 'location_lat' in self.df_filtered.columns and 'location_long' in self.df_filtered.columns and 'store_name' in self.df_filtered.columns:
            st.markdown("<h3 class='section-header' style='color:white; padding:10px; border-bottom:2px solid #4DA1A9;'>Geographic Distribution of Stores</h3>", unsafe_allow_html=True)
            
            # Calculate center and zoom level
            map_center = [self.df_filtered['location_lat'].mean(), self.df_filtered['location_long'].mean()]
            
            # Determine zoom level based on data spread
            lat_range = self.df_filtered['location_lat'].max() - self.df_filtered['location_lat'].min()
            lon_range = self.df_filtered['location_long'].max() - self.df_filtered['location_long'].min()
            
            # Calculate appropriate zoom level
            max_range = max(lat_range, lon_range)
            if max_range > 50:
                zoom_level = 2
            elif max_range > 20:
                zoom_level = 4
            elif max_range > 10:
                zoom_level = 5
            elif max_range > 5:
                zoom_level = 6
            else:
                zoom_level = 8
            
            # Create map with a more attractive tile layer
            m = folium.Map(
                location=map_center,
                zoom_start=zoom_level,
                tiles='CartoDB positron',  # Clean, modern look
                width='100%',
                attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
            )
            
            # Add alternative tile layers for user to choose from
            folium.TileLayer(
                'CartoDB dark_matter', 
                name='Dark Mode',
                attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
            ).add_to(m)
            
            folium.TileLayer(
                'OpenStreetMap', 
                name='Street View',
                attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            ).add_to(m)
            
            # Group by store and get mean coordinates and counts
            store_data = self.df_filtered.groupby('store_name').agg({
                'location_lat': 'mean',
                'location_long': 'mean',
                'product_name': 'count'
            }).reset_index()
            
            store_data.columns = ['store_name', 'lat', 'lon', 'count']
            
            # Create a MarkerCluster for better performance with many points
            marker_cluster = MarkerCluster(name='Store Clusters').add_to(m)
            
            # Color scheme based on count
            def get_color(count, max_count):
                # Create a gradient from light blue to dark blue
                ratio = count / max_count
                if ratio < 0.2:
                    return '#8FB9E5'  # Light blue
                elif ratio < 0.4:
                    return '#5B9BD5'  # Medium blue
                elif ratio < 0.6:
                    return '#2A75C0'  # Blue
                elif ratio < 0.8:
                    return '#1E4E79'  # Dark blue
                else:
                    return '#0F2B43'  # Very dark blue
            
            # Create a feature group for the regular markers
            store_markers = folium.FeatureGroup(name='Individual Stores')
            
            # Add markers for each store with custom styling
            for idx, row in store_data.iterrows():
                # Calculate size based on count (min 8, max 25)
                size = 8 + (row['count'] / store_data['count'].max() * 17)
                color = get_color(row['count'], store_data['count'].max())
                
                # Create a custom HTML icon
                icon_size = int(size * 2)  # Double the marker size for the icon
                
                # Enhanced popup with more styled information
                popup_html = f"""
                <div style="width:200px; font-family:Arial,sans-serif;">
                    <h4 style="color:#2E4057; margin:2px 0; border-bottom:1px solid #ccc; padding-bottom:5px;">
                        {row['store_name']}
                    </h4>
                    <div style="margin:8px 0;">
                        <strong>Products:</strong> <span style="color:#2A75C0; font-weight:bold;">{row['count']}</span>
                    </div>
                    <div style="margin:5px 0; font-size:11px; color:#777;">
                        Coordinates: [{row['lat']:.4f}, {row['lon']:.4f}]
                    </div>
                </div>
                """
                
                # Create a better looking popup
                popup = folium.Popup(folium.Html(popup_html, script=True), max_width=250)
                
                # Create a circle marker with a pulse effect
                circle = folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=size,
                    popup=popup,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    weight=1.5,
                    opacity=0.9
                )
                
                # Add to store markers group
                circle.add_to(store_markers)
                
                # Create a smaller marker for the cluster view
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=5,
                    popup=popup,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8
                ).add_to(marker_cluster)
            
            # Add the feature group to the map
            store_markers.add_to(m)
            
            # Add a minimap for context
            minimap = MiniMap(toggle_display=True, position='bottomright')
            m.add_child(minimap)
            
            # Add fullscreen button
            plugins.Fullscreen(position='topleft', title='Expand map', title_cancel='Exit fullscreen', force_separate_button=True).add_to(m)
            
            # Add a measure tool
            plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
            
            # Add a search function to locate stores
            store_dict = {}
            for idx, row in store_data.iterrows():
                store_dict[row['store_name']] = [row['lat'], row['lon']]
            
            search = plugins.Search(
                layer=store_markers,
                geom_type='Point',
                placeholder='Search for a store',
                collapsed=True,
                search_label='store_name'
            )
            m.add_child(search)
            
            # Add layer control
            folium.LayerControl(position='topright', collapsed=False).add_to(m)
            
            # Add a title and legend
            title_html = '''
            <div style="position: fixed; 
                        top: 10px; left: 50px; width: 250px; height: 30px; 
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color:white; padding: 5px;
                        border-radius:5px; box-shadow: 3px 3px 6px rgba(0,0,0,0.2);">
                <b>Store Distribution Map</b>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Create a custom legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; 
                        border:2px solid grey; z-index:9999; font-size:12px;
                        background-color:white; padding: 10px;
                        border-radius:5px; box-shadow: 3px 3px 6px rgba(0,0,0,0.2);">
                <p style="margin:0 0 5px 0; font-weight:bold;">Number of Products</p>
                <div style="display:flex; align-items:center; margin:2px 0;">
                    <div style="width:15px; height:15px; border-radius:50%; background-color:#8FB9E5; margin-right:5px;"></div>
                    <span>Small (< 20%)</span>
                </div>
                <div style="display:flex; align-items:center; margin:2px 0;">
                    <div style="width:15px; height:15px; border-radius:50%; background-color:#5B9BD5; margin-right:5px;"></div>
                    <span>Medium (20-40%)</span>
                </div>
                <div style="display:flex; align-items:center; margin:2px 0;">
                    <div style="width:15px; height:15px; border-radius:50%; background-color:#2A75C0; margin-right:5px;"></div>
                    <span>Large (40-60%)</span>
                </div>
                <div style="display:flex; align-items:center; margin:2px 0;">
                    <div style="width:15px; height:15px; border-radius:50%; background-color:#1E4E79; margin-right:5px;"></div>
                    <span>Very Large (60-80%)</span>
                </div>
                <div style="display:flex; align-items:center; margin:2px 0;">
                    <div style="width:15px; height:15px; border-radius:50%; background-color:#0F2B43; margin-right:5px;"></div>
                    <span>Massive (> 80%)</span>
                </div>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            
            # Display the map
            folium_static(m)
            
            # Add additional context below the map
            st.markdown("""
            <div style="margin-top:15px; font-size:0.9em; color:#666;">
               
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Geographic data (location_lat, location_long, store_name) is required for the map display.")




    
    
    
    
    
    
    
    
    def build_detailed_analysis_tab(self):
        """Build the Detailed Analysis tab content"""
        #st.markdown("<h2 class='sub-header'>Detailed Analysis</h2>", unsafe_allow_html=True)
        
        self.build_time_series_analysis()
        self.build_product_performance()
        self.build_expiry_analysis()
    
    def build_time_series_analysis(self):
        """Build time series analysis charts"""
        if 'date_of_manufacture' in self.df_filtered.columns and 'sales_volume' in self.df_filtered.columns:
            st.markdown("<h3 class='section-header'>Time Series Analysis</h3>", unsafe_allow_html=True)
            
            # Group by month and calculate metrics
            self.df_filtered['month_year'] = self.df_filtered['date_of_manufacture'].dt.strftime('%Y-%m')
            monthly_data = self.df_filtered.groupby('month_year').agg({
                'sales_volume': 'sum',
                'product_price': 'mean',
                'product_name': 'count'
            }).reset_index()
            
            monthly_data.columns = ['Month', 'Sales Volume', 'Average Price', 'Product Count']
            
            # Sort by month
            monthly_data['Month_dt'] = pd.to_datetime(monthly_data['Month'] + '-01')
            monthly_data = monthly_data.sort_values('Month_dt')
            monthly_data['Month'] = monthly_data['Month_dt'].dt.strftime('%b %Y')
            
            # Create time series chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_data['Month'],
                y=monthly_data['Sales Volume'],
                mode='lines+markers',
                name='Sales Volume',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_data['Month'],
                y=monthly_data['Product Count'],
                mode='lines+markers',
                name='Product Count',
                line=dict(color='green', width=2),
                yaxis='y2'
            ))
            
            # Create secondary y-axis
            fig.update_layout(
                title='Monthly Sales Volume and Product Count',
                xaxis_title='Month',
                yaxis_title='Sales Volume',
                yaxis2=dict(
                    title='Product Count',
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def build_product_performance(self):
        """Build product performance analysis charts"""
        st.markdown("<h3 class='section-header'>Product Performance Analysis</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
                if 'product_name' in self.df_filtered.columns and 'sales_volume' in self.df_filtered.columns:
                    # Get top 10 products
                    top_products = self.df_filtered.groupby('product_name')['sales_volume'].sum().reset_index()
                    top_products = top_products.sort_values('sales_volume', ascending=False).head(10)
                    
                    # Create horizontal bar chart for better readability
                    fig = px.bar(
                        top_products,
                        y='product_name',  # Swapped x and y for horizontal bars
                        x='sales_volume',
                        title='Top 10 Products by Sales Volume',
                        color='sales_volume',
                        color_continuous_scale='Viridis',
                        orientation='h'    # Horizontal orientation
                    )
                    
                    # Enhance the styling
                    fig.update_layout(
                        xaxis_title='Sales Volume',
                        yaxis_title='Product',
                        yaxis={'categoryorder': 'total ascending'},  # Sort bars
                        
                        font=dict(family="Arial, sans-serif", size=12),
                    )
              
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'product_brand' in self.df_filtered.columns and 'sales_volume' in self.df_filtered.columns:
                brand_performance = self.df_filtered.groupby('product_brand').agg({
                    'sales_volume': 'sum',
                    'product_name': 'count'
                }).reset_index()
                
                brand_performance.columns = ['Brand', 'Sales Volume', 'Product Count']
                brand_performance = brand_performance.sort_values('Sales Volume', ascending=False)
                
                fig = px.scatter(
                    brand_performance,
                    x='Product Count',
                    y='Sales Volume',
                    size='Sales Volume',
                    color='Brand',
                    hover_name='Brand',
                    title='Brand Performance by Product Count and Sales'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def build_expiry_analysis(self):
        """Build expiry analysis charts"""
        if 'date_of_expiry' in self.df_filtered.columns:
            st.markdown("<h3 class='section-header'>Expiry Analysis</h3>", unsafe_allow_html=True)
            
            # Calculate days until expiry
            current_date = datetime.now()
            self.df_filtered['days_until_expiry'] = (self.df_filtered['date_of_expiry'] - current_date).dt.days
            
            # Create expiry bins
            bins = [-1000, 0, 30, 90, 180, 365, 1000]
            labels = ['Expired', '< 30 days', '30-90 days', '90-180 days', '6mo-1yr', '> 1 year']
            self.df_filtered['expiry_status'] = pd.cut(self.df_filtered['days_until_expiry'], bins=bins, labels=labels)
            
            expiry_counts = self.df_filtered['expiry_status'].value_counts().reset_index()
            expiry_counts.columns = ['Expiry Status', 'Count']
            
            # Reorder categories
            expiry_counts['Expiry Status'] = pd.Categorical(
                expiry_counts['Expiry Status'],
                categories=labels,
                ordered=True
            )
            expiry_counts = expiry_counts.sort_values('Expiry Status')
            
            fig = px.bar(
                expiry_counts,
                x='Expiry Status',
                y='Count',
                title='Products by Expiry Timeframe',
                color='Expiry Status',
                color_discrete_map={
                    'Expired': 'red',
                    '< 30 days': 'orange',
                    '30-90 days': 'yellow',
                    '90-180 days': 'yellowgreen',
                    '6mo-1yr': 'green',
                    '> 1 year': 'darkgreen'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Products expiring soon
            if self.df_filtered[self.df_filtered['expiry_status'] == '< 30 days'].shape[0] > 0:
                #st.markdown("<div class='highlight'>", unsafe_allow_html=True)
                st.markdown("<b>⚠️ Products Expiring in Next 30 Days:</b>", unsafe_allow_html=True)
                
                expiring_soon = self.df_filtered[self.df_filtered['expiry_status'] == '< 30 days'].sort_values('days_until_expiry')
                expiring_display = expiring_soon[['product_name', 'product_brand', 'store_name', 'days_until_expiry', 'product_price']].head(10)
                st.dataframe(expiring_display)
                st.markdown("</div>", unsafe_allow_html=True)
    


















    def build_ml_insights_tab(self):
            """Build the ML Insights tab content"""
            st.markdown("<h2 class='sub-header'>Machine Learning Insights</h2>", unsafe_allow_html=True)
            
            self.build_discount_analysis()
            self.build_sales_discount_correlation()
            self.build_ultra_discount_analysis()
            self.build_model_insights()
            self.build_customer_segmentation()
            self.build_ml_recommendations()
        
    def build_discount_analysis(self):
        """Build discount analysis charts"""
        if 'discount' not in self.df_filtered.columns or 'discount_percentage' not in self.df_filtered.columns:
            # st.warning("Discount analysis requires 'discount' and 'discount_percentage' columns.")
            # return
            pass
            
        st.markdown("<h3 class='section-header'>Discount Analysis</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution of discount percentages
            discount_data = self.df_filtered[self.df_filtered['discount'] == 'yes']
            
            if len(discount_data) == 0:
                st.info("No products with discounts in the current filtered dataset.")
                return
                
            fig = px.histogram(
                discount_data,
                x='discount_percentage',
                nbins=20,
                title='Distribution of Discount Percentages',
                color_discrete_sequence=['blue']
            )
            fig.update_layout(xaxis_title='Discount Percentage (%)', yaxis_title='Count')
            
            # Add threshold line
            fig.add_vline(
                x=self.discount_threshold,
                line_dash='dash',
                line_color='red',
                annotation_text=f'Threshold: {self.discount_threshold}%',
                annotation_position="top right"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Discount percentage by product group
            if 'product_group' in self.df_filtered.columns:
                group_discount = discount_data.groupby('product_group')['discount_percentage'].mean().reset_index()
                
                if len(group_discount) == 0:
                    st.info("No product groups with discounts in the current filtered dataset.")
                    return
                    
                group_discount.columns = ['Product Group', 'Average Discount (%)']
                
                fig = px.bar(
                    group_discount,
                    x='Product Group',
                    y='Average Discount (%)',
                    title='Average Discount by Product Group',
                    color='Average Discount (%)',
                    color_continuous_scale='Viridis'
                )
                
                # Add threshold line
                fig.add_hline(
                    y=self.discount_threshold,
                    line_dash='dash',
                    line_color='red',
                    annotation_text=f'Threshold: {self.discount_threshold}%',
                    annotation_position="top right"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Product group information not available for discount analysis by group.")
    
    def build_sales_discount_correlation(self):
        """Build sales vs discount correlation charts"""
        if 'sales_volume' not in self.df_filtered.columns or 'discount_percentage' not in self.df_filtered.columns:
            st.warning("Sales-discount correlation requires 'sales_volume' and 'discount_percentage' columns.")
            return
            
        st.markdown("<h3 class='section-header'>Sales vs Discount Correlation</h3>", unsafe_allow_html=True)
        
        # Scatter plot
        discount_sales_data = self.df_filtered[self.df_filtered['discount'] == 'yes']
        
        if len(discount_sales_data) == 0:
            st.info("No products with discounts in the current filtered dataset.")
            return
            
        hover_data = ['product_name']
        if 'product_price' in discount_sales_data.columns:
            hover_data.append('product_price')
            
        fig = px.scatter(
            discount_sales_data,
            x='sales_volume',
            y='discount_percentage',
            color='product_group' if 'product_group' in discount_sales_data.columns else None,
            title='Sales Volume vs Discount Percentage',
            trendline='ols',
            hover_data=hover_data
        )
        fig.update_layout(xaxis_title='Sales Volume', yaxis_title='Discount Percentage (%)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate correlation coefficient
        corr = discount_sales_data['sales_volume'].corr(discount_sales_data['discount_percentage'])
        
        correlation_text = "This indicates "
        if corr > 0.3:
            correlation_text += "a positive relationship, suggesting higher discounts for higher-selling products."
        elif corr < -0.3:
            correlation_text += "a negative relationship, suggesting higher discounts for lower-selling products."
        else:
            correlation_text += "no clear relationship between sales volume and discount percentage."
        
        st.markdown(f"""
        <div class='highlight'>
        <b>Correlation Analysis:</b><br>
        The correlation coefficient between sales volume and discount percentage is <b>{corr:.2f}</b>.
        {correlation_text}
        </div>
        """, unsafe_allow_html=True)
    
    def build_ultra_discount_analysis(self):
        """Build ultra discount analysis charts"""
        if 'ultra_discount_percentage' not in self.df_filtered.columns:
            st.warning("Ultra discount analysis requires the 'ultra_discount_percentage' column.")
            return
            
        st.markdown("<h3 class='section-header'>Ultra Discount Analysis</h3>", unsafe_allow_html=True)
        
        # Count products with ultra discount
        ultra_discount_count = (self.df_filtered['ultra_discount_percentage'] > 0).sum()
        
        if len(self.df_filtered) == 0:
            st.info("No data available for ultra discount analysis.")
            return
            
        ultra_discount_pct = (ultra_discount_count / len(self.df_filtered)) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ultra discount gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ultra_discount_pct,
                title={'text': "Products with Ultra Discount (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 50], 'color': "gray"},
                        {'range': [50, 100], 'color': "darkgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': getattr(self, 'ultra_discount_threshold', 30) * 2  # Default to 30 if not set
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            ultra_discount_products = self.df_filtered[self.df_filtered['ultra_discount_percentage'] > 0]
            
            if len(ultra_discount_products) == 0:
                st.info("No products with ultra discounts in the current filtered dataset.")
            elif 'product_group' in self.df_filtered.columns:
                # Ultra discount by product group
                ultra_group = ultra_discount_products.groupby('product_group').agg({
                    'product_name': 'count',
                    'ultra_discount_percentage': 'mean'
                }).reset_index()
                
                ultra_group.columns = ['Product Group', 'Product Count', 'Average Ultra Discount (%)']
                
                if len(ultra_group) > 0:
                    fig = px.scatter(
                        ultra_group,
                        x='Product Count',
                        y='Average Ultra Discount (%)',
                        size='Product Count',
                        color='Product Group',
                        title='Ultra Discount Overview by Product Group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No product groups with ultra discounts available.")
            else:
                st.info("Product group information not available for ultra discount analysis by group.")
    
    def build_model_insights(self):
        """Build ML model insights charts"""
        if not hasattr(self, 'model') or self.model is None:
            pass
            return
            
        st.markdown("<h3 class='section-header'>Machine Learning Model Insights</h3>", unsafe_allow_html=True)
        
        # Display feature importance
        if hasattr(self.model, 'feature_importances_'):
            try:
                # Define features used by the model (based on how it was trained)
                # Get the feature names from model if available, otherwise use defaults
                if hasattr(self.model, 'feature_names_in_'):
                    features = self.model.feature_names_in_
                else:
                    features = ['sales_volume', 'product_price', 'duration_of_expiry', 'days_to_expiry', 'is_discount']
                
                # Ensure feature importances match feature count
                if len(features) != len(self.model.feature_importances_):
                    st.warning(f"Feature count mismatch: {len(features)} names vs {len(self.model.feature_importances_)} importances")
                    return
                    
                # Create feature importance DataFrame
                feature_importance = pd.DataFrame({
                    'Feature': features,
                    'Importance': self.model.feature_importances_
                }).sort_values('Importance', ascending=False)
                
                # Plot feature importance
                fig = px.bar(
                    feature_importance,
                    x='Feature',
                    y='Importance',
                    title='Feature Importance for Discount Prediction',
                    color='Importance',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Explain the model
                model_type = type(self.model).__name__
                st.markdown(f"""
                <div class='highlight'>
                <b>ML Model Explanation:</b><br>
                This machine learning model uses a {model_type} algorithm to predict discount percentages based on multiple factors. 
                The chart above shows which features have the most influence on determining discount percentages.
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying model insights: {str(e)}")
        else:
            st.info("The current model does not provide feature importance information.")
    
    def build_customer_segmentation(self):
        """Build customer segmentation analysis"""
        required_columns = ['sales_volume', 'product_price']
        missing_columns = [col for col in required_columns if col not in self.df_filtered.columns]
        
        if missing_columns:
            st.warning(f"Customer segmentation requires columns: {', '.join(missing_columns)}")
            return
            
        if len(self.df_filtered) < 3:
            st.warning("Not enough data points for meaningful segmentation analysis.")
            return
            
        st.markdown("<h3 class='section-header'>Customer Segmentation Analysis</h3>", unsafe_allow_html=True)
        
        try:
            # Prepare data for clustering
            cluster_data = self.df_filtered[['sales_volume', 'product_price']].copy()
            
            if 'discount_percentage' in self.df_filtered.columns:
                cluster_data['discount_percentage'] = self.df_filtered['discount_percentage']
            
            # Check for and handle NaN values
            if cluster_data.isna().any().any():
                st.warning("Data contains missing values. Filling with appropriate defaults for segmentation.")
                cluster_data = cluster_data.fillna({
                    'sales_volume': cluster_data['sales_volume'].median(),
                    'product_price': cluster_data['product_price'].median(),
                    'discount_percentage': 0 if 'discount_percentage' in cluster_data.columns else None
                })
            
            # Standardize the data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(cluster_data)
            
            # Determine optimal number of clusters (3-5 typically works well)
            n_clusters = st.slider("Number of Segments", 2, 6, 3)
            
            # Perform KMeans clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            self.df_filtered['cluster'] = kmeans.fit_predict(scaled_data)
            
            # Create segment labels
            cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
            segment_labels = []
            
            for i in range(n_clusters):
                center = cluster_centers[i]
                if len(center) >= 3:  # If discount_percentage is included
                    sales, price, discount = center
                    if sales > cluster_centers[:, 0].mean() and price > cluster_centers[:, 1].mean():
                        label = "High Value Premium"
                    elif sales > cluster_centers[:, 0].mean() and discount > cluster_centers[:, 2].mean():
                        label = "High Volume Promotional"
                    elif price > cluster_centers[:, 1].mean():
                        label = "Premium Niche"
                    elif sales > cluster_centers[:, 0].mean():
                        label = "Popular Mainstream"
                    else:
                        label = "Budget Basics"
                else:  # Just sales and price
                    sales, price = center
                    if sales > cluster_centers[:, 0].mean() and price > cluster_centers[:, 1].mean():
                        label = "Premium Bestsellers"
                    elif sales > cluster_centers[:, 0].mean():
                        label = "Popular Value"
                    elif price > cluster_centers[:, 1].mean():
                        label = "Luxury Niche"
                    else:
                        label = "Economy Essentials"
                
                segment_labels.append(f"Segment {i+1}: {label}")
            
            # Map cluster numbers to segment labels
            segment_map = {i: segment_labels[i] for i in range(n_clusters)}
            self.df_filtered['segment'] = self.df_filtered['cluster'].map(segment_map)
            
            # Visualize the clusters
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot of clusters
                hover_data = ['product_name']
                if 'product_group' in self.df_filtered.columns:
                    hover_data.append('product_group')
                    
                fig = px.scatter(
                    self.df_filtered, 
                    x='sales_volume', 
                    y='product_price',
                    color='segment',
                    hover_data=hover_data,
                    title='Product Segmentation Analysis',
                    labels={'sales_volume': 'Sales Volume', 'product_price': 'Product Price ($)'}
                )
                
                # Move the legend below the chart
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        title=None
                    ),
                    margin=dict(b=100)  # Add bottom margin to make room for the legend
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Segment composition
                segment_counts = self.df_filtered['segment'].value_counts().reset_index()
                segment_counts.columns = ['Segment', 'Count']
                
                fig = px.pie(
                    segment_counts,
                    values='Count',
                    names='Segment',
                    title='Segment Distribution',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                # Move the legend below the chart
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        title=None
                    ),
                    margin=dict(b=100)  # Add bottom margin to make room for the legend
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Segment insights table
            st.markdown("<b>Segment Insights:</b>", unsafe_allow_html=True)
            
            agg_dict = {
                'product_name': 'count',
                'sales_volume': 'mean',
                'product_price': 'mean'
            }
            
            if 'discount_percentage' in self.df_filtered.columns:
                agg_dict['discount_percentage'] = 'mean'
            
            segment_insights = self.df_filtered.groupby('segment').agg(agg_dict).reset_index()
            
            columns = ['Segment', 'Product Count', 'Avg Sales Volume', 'Avg Price ($)']
            if 'discount_percentage' in agg_dict:
                columns.append('Avg Discount (%)')
                
            segment_insights.columns = columns
            
            st.dataframe(segment_insights)
        except Exception as e:
            st.error(f"Error in customer segmentation: {str(e)}")
    
    def build_ml_recommendations(self):
        """Build ML-driven recommendations"""
        if 'discount' not in self.df_filtered.columns or 'sales_volume' not in self.df_filtered.columns:
            st.warning("ML recommendations require 'discount' and 'sales_volume' columns.")
            return
            
        if len(self.df_filtered) == 0:
            st.info("No data available for generating recommendations.")
            return
            
        st.markdown("<h3 class='section-header'>ML-Driven Recommendations</h3>", unsafe_allow_html=True)
        
        try:
            # Identify products for potential discount
            sales_threshold = self.df_filtered['sales_volume'].quantile(0.7)
            potential_discount = self.df_filtered[
                (self.df_filtered['discount'] == 'no') & 
                (self.df_filtered['sales_volume'] > sales_threshold)
            ]
            
            if len(potential_discount) > 0:
                st.markdown("""
                <div class='highlight'>
                <b>🔍 High-Volume Products Without Discounts:</b><br>
                These high-selling products currently have no discounts but may be good candidates for promotional pricing:
                </div>
                """, unsafe_allow_html=True)
                
                # Prepare columns for display
                display_columns = ['product_name']
                if 'product_brand' in potential_discount.columns:
                    display_columns.append('product_brand')
                if 'product_group' in potential_discount.columns:
                    display_columns.append('product_group')
                if 'sales_volume' in potential_discount.columns:
                    display_columns.append('sales_volume')
                if 'product_price' in potential_discount.columns:
                    display_columns.append('product_price')
                
                potential_table = potential_discount.sort_values('sales_volume', ascending=False)[
                    display_columns
                ].head(10)
                
                st.dataframe(potential_table)
            else:
                st.info("No high-volume products without discounts identified.")
            
            # Identify products for potential ultra discounts
            if 'discount_percentage' in self.df_filtered.columns and 'ultra_discount_percentage' in self.df_filtered.columns:
                discount_threshold = getattr(self, 'discount_threshold', 20)  # Default to 20 if not set
                potential_ultra = self.df_filtered[
                    (self.df_filtered['discount'] == 'yes') & 
                    (self.df_filtered['discount_percentage'] >= discount_threshold) &
                    (self.df_filtered['ultra_discount_percentage'] == 0)
                ]
                
                if len(potential_ultra) > 0:
                    st.markdown("""
                    <div class='highlight'>
                    <b>🔍 Products for Potential Ultra Discounts:</b><br>
                    These products have high regular discounts but no ultra discounts applied:
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Prepare columns for display
                    display_columns = ['product_name']
                    if 'product_brand' in potential_ultra.columns:
                        display_columns.append('product_brand')
                    if 'discount_percentage' in potential_ultra.columns:
                        display_columns.append('discount_percentage')
                    if 'product_price' in potential_ultra.columns:
                        display_columns.append('product_price')
                    
                    ultra_table = potential_ultra.sort_values('discount_percentage', ascending=False)[
                        display_columns
                    ].head(10)
                    
                    st.dataframe(ultra_table)
                else:
                    st.info("No products identified for potential ultra discounts.")
            
            # Identify underperforming products
            if 'product_price' in self.df_filtered.columns:
                sales_lower_threshold = self.df_filtered['sales_volume'].quantile(0.3)
                price_upper_threshold = self.df_filtered['product_price'].quantile(0.7)
                
                underperforming = self.df_filtered[
                    (self.df_filtered['sales_volume'] < sales_lower_threshold) & 
                    (self.df_filtered['product_price'] > price_upper_threshold)
                ]
                
                if len(underperforming) > 0:
                    st.markdown("""
                    <div class='highlight'>
                    <b>🔍 Underperforming Premium Products:</b><br>
                    These high-priced products have low sales volume and might benefit from price adjustments:
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Prepare columns for display
                    display_columns = ['product_name']
                    if 'product_brand' in underperforming.columns:
                        display_columns.append('product_brand')
                    if 'product_group' in underperforming.columns:
                        display_columns.append('product_group')
                    if 'sales_volume' in underperforming.columns:
                        display_columns.append('sales_volume')
                    if 'product_price' in underperforming.columns:
                        display_columns.append('product_price')
                    
                    underperforming_table = underperforming.sort_values('product_price', ascending=False)[
                        display_columns
                    ].head(10)
                    
                    st.dataframe(underperforming_table)
                else:
                    st.info("No underperforming premium products identified.")
            else:
                st.warning("Product price information not available for underperforming product analysis.")
        except Exception as e:
            st.error(f"Error generating ML recommendations: {str(e)}")
    
    def add_footer(self):
        """Add footer to the dashboard"""
        st.markdown("""
        <div style="text-align: center; color: #666;">
      
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main method to run the dashboard"""
        # Display title
        st.markdown("<h1 class='main-header'>Advanced Store Data Analysis Dashboard</h1>", unsafe_allow_html=True)
        
        # Build sidebar filters and controls
        self.build_sidebar_filters()
        self.build_ml_thresholds()
        self.add_download_button()
        
        # Main content tabs
        tab1, tab2, tab3 = st.tabs(["📊 Overall Statistics", "🔍 Detailed Analysis", "🧠 ML Insights"])
        
        # Tab 1: Overall Statistics
        with tab1:
            self.build_overall_stats_tab()
        
        # Tab 2: Detailed Analysis
        with tab2:
            self.build_detailed_analysis_tab()
        
        # Tab 3: ML Insights
        with tab3:
            self.build_ml_insights_tab()
        
        # Add footer
        self.add_footer()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def build_ml_insights_tab(self):
    #     """Build the ML Insights tab content"""
    #     #st.markdown("<h2 class='sub-header'>Machine Learning Insights</h2>", unsafe_allow_html=True)
        
    #     self.build_discount_analysis()
    #     self.build_sales_discount_correlation()
    #     self.build_ultra_discount_analysis()
    #     self.build_model_insights()
    #     self.build_customer_segmentation()
    #     self.build_ml_recommendations()
    
    # def build_discount_analysis(self):
    #     """Build discount analysis charts"""
    #     if 'discount' in self.df_filtered.columns and 'discount_percentage' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>Discount Analysis</h3>", unsafe_allow_html=True)
            
    #         col1, col2 = st.columns(2)
            
    #         with col1:
    #             # Distribution of discount percentages
    #             discount_data = self.df_filtered[self.df_filtered['discount'] == 'yes']['discount_percentage']
                
    #             fig = px.histogram(
    #                 discount_data,
    #                 x='discount_percentage',
    #                 nbins=20,
    #                 title='Distribution of Discount Percentages',
    #                 color_discrete_sequence=['blue']
    #             )
    #             fig.update_layout(xaxis_title='Discount Percentage (%)', yaxis_title='Count')
                
    #             # Add threshold line
    #             fig.add_vline(
    #                 x=self.discount_threshold,
    #                 line_dash='dash',
    #                 line_color='red',
    #                 annotation_text=f'Threshold: {self.discount_threshold}%',
    #                 annotation_position="top right"
    #             )
                
    #             st.plotly_chart(fig, use_container_width=True)
            
    #         with col2:
    #             # Discount percentage by product group
    #             if 'product_group' in self.df_filtered.columns:
    #                 group_discount = self.df_filtered[self.df_filtered['discount'] == 'yes'].groupby('product_group')['discount_percentage'].mean().reset_index()
    #                 group_discount.columns = ['Product Group', 'Average Discount (%)']
                    
    #                 fig = px.bar(
    #                     group_discount,
    #                     x='Product Group',
    #                     y='Average Discount (%)',
    #                     title='Average Discount by Product Group',
    #                     color='Average Discount (%)',
    #                     color_continuous_scale='Viridis'
    #                 )
                    
    #                 # Add threshold line
    #                 fig.add_hline(
    #                     y=self.discount_threshold,
    #                     line_dash='dash',
    #                     line_color='red',
    #                     annotation_text=f'Threshold: {self.discount_threshold}%',
    #                     annotation_position="top right"
    #                 )
                    
    #                 st.plotly_chart(fig, use_container_width=True)
    
    # def build_sales_discount_correlation(self):
    #     """Build sales vs discount correlation charts"""
    #     if 'sales_volume' in self.df_filtered.columns and 'discount_percentage' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>Sales vs Discount Correlation</h3>", unsafe_allow_html=True)
            
    #         # Scatter plot
    #         discount_sales_data = self.df_filtered[self.df_filtered['discount'] == 'yes']
            
    #         if len(discount_sales_data) > 0:
    #             fig = px.scatter(
    #                 discount_sales_data,
    #                 x='sales_volume',
    #                 y='discount_percentage',
    #                 color='product_group' if 'product_group' in discount_sales_data.columns else None,
    #                 title='Sales Volume vs Discount Percentage',
    #                 trendline='ols',
    #                 hover_data=['product_name', 'product_price']
    #             )
    #             fig.update_layout(xaxis_title='Sales Volume', yaxis_title='Discount Percentage (%)')
    #             st.plotly_chart(fig, use_container_width=True)
                
    #             # Calculate correlation coefficient
    #             corr = discount_sales_data['sales_volume'].corr(discount_sales_data['discount_percentage'])
                
    #             st.markdown(f"""
    #             <div class='highlight'>
    #             <b>Correlation Analysis:</b><br>
    #             The correlation coefficient between sales volume and discount percentage is <b>{corr:.2f}</b>.
    #             {"This indicates a positive relationship, suggesting higher discounts for higher-selling products." if corr > 0 else 
    #              "This indicates a negative relationship, suggesting higher discounts for lower-selling products." if corr < 0 else
    #              "This indicates no clear relationship between sales volume and discount percentage."}
    #             </div>
    #             """, unsafe_allow_html=True)
    
    # def build_ultra_discount_analysis(self):
    #     """Build ultra discount analysis charts"""
    #     if 'ultra_discount_percentage' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>Ultra Discount Analysis</h3>", unsafe_allow_html=True)
            
    #         # Count products with ultra discount
    #         ultra_discount_count = (self.df_filtered['ultra_discount_percentage'] > 0).sum()
    #         ultra_discount_pct = (ultra_discount_count / len(self.df_filtered)) * 100 if len(self.df_filtered) > 0 else 0
            
    #         col1, col2 = st.columns(2)
            
    #         with col1:
    #             # Ultra discount gauge chart
    #             fig = go.Figure(go.Indicator(
    #                 mode="gauge+number",
    #                 value=ultra_discount_pct,
    #                 title={'text': "Products with Ultra Discount (%)"},
    #                 gauge={
    #                     'axis': {'range': [None, 100]},
    #                     'bar': {'color': "darkblue"},
    #                     'steps': [
    #                         {'range': [0, 20], 'color': "lightgray"},
    #                         {'range': [20, 50], 'color': "gray"},
    #                         {'range': [50, 100], 'color': "darkgray"}
    #                     ],
    #                     'threshold': {
    #                         'line': {'color': "red", 'width': 4},
    #                         'thickness': 0.75,
    #                         'value': self.ultra_discount_threshold * 2
    #                     }
    #                 }
    #             ))
    #             st.plotly_chart(fig, use_container_width=True)
            
    #         with col2:
    #             if 'product_group' in self.df_filtered.columns:
    #                 # Ultra discount by product group
    #                 ultra_group = self.df_filtered[self.df_filtered['ultra_discount_percentage'] > 0].groupby('product_group').agg({
    #                     'product_name': 'count',
    #                     'ultra_discount_percentage': 'mean'
    #                 }).reset_index()
                    
    #                 ultra_group.columns = ['Product Group', 'Product Count', 'Average Ultra Discount (%)']
                    
    #                 fig = px.scatter(
    #                     ultra_group,
    #                     x='Product Count',
    #                     y='Average Ultra Discount (%)',
    #                     size='Product Count',
    #                     color='Product Group',
    #                     title='Ultra Discount Overview by Product Group'
    #                 )
    #                 st.plotly_chart(fig, use_container_width=True)
    
    # def build_model_insights(self):
    #     """Build ML model insights charts"""
    #     if self.model is not None:
    #         st.markdown("<h3 class='section-header'>Machine Learning Model Insights</h3>", unsafe_allow_html=True)
            
    #         # Display feature importance
    #         if hasattr(self.model, 'feature_importances_'):
    #             # Define features used by the model (based on how it was trained)
    #             features = ['sales_volume', 'product_price', 'duration_of_expiry', 'days_to_expiry', 'is_discount']
                
    #             # Create feature importance DataFrame
    #             feature_importance = pd.DataFrame({
    #                 'Feature': features,
    #                 'Importance': self.model.feature_importances_
    #             }).sort_values('Importance', ascending=False)
                
    #             # Plot feature importance
    #             fig = px.bar(
    #                 feature_importance,
    #                 x='Feature',
    #                 y='Importance',
    #                 title='Feature Importance for Discount Prediction',
    #                 color='Importance',
    #                 color_continuous_scale='Viridis'
    #             )
    #             st.plotly_chart(fig, use_container_width=True)
                
    #             # Explain the model
    #             st.markdown("""
    #             <div class='highlight'>
    #             <b>ML Model Explanation:</b><br>
    #             This machine learning model uses a Random Forest algorithm to predict discount percentages based on multiple factors. 
    #             The chart above shows which features have the most influence on determining discount percentages.
    #             </div>
    #             """, unsafe_allow_html=True)
    
    # def build_customer_segmentation(self):
    #     """Build customer segmentation analysis"""
    #     if 'sales_volume' in self.df_filtered.columns and 'product_price' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>Customer Segmentation Analysis</h3>", unsafe_allow_html=True)
            
    #         # Prepare data for clustering
    #         cluster_data = self.df_filtered[['sales_volume', 'product_price']].copy()
            
    #         if 'discount_percentage' in self.df_filtered.columns:
    #             cluster_data['discount_percentage'] = self.df_filtered['discount_percentage']
            
    #         # Standardize the data
    #         scaler = StandardScaler()
    #         scaled_data = scaler.fit_transform(cluster_data)
            
    #         # Determine optimal number of clusters (3-5 typically works well)
    #         n_clusters = st.slider("Number of Segments", 2, 6, 3)
            
    #         # Perform KMeans clustering
    #         kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    #         self.df_filtered['cluster'] = kmeans.fit_predict(scaled_data)
            
    #         # Create segment labels
    #         cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    #         segment_labels = []
            
    #         for i in range(n_clusters):
    #             center = cluster_centers[i]
    #             if len(center) >= 3:  # If discount_percentage is included
    #                 sales, price, discount = center
    #                 if sales > cluster_centers[:, 0].mean() and price > cluster_centers[:, 1].mean():
    #                     label = "High Value Premium"
    #                 elif sales > cluster_centers[:, 0].mean() and discount > cluster_centers[:, 2].mean():
    #                     label = "High Volume Promotional"
    #                 elif price > cluster_centers[:, 1].mean():
    #                     label = "Premium Niche"
    #                 elif sales > cluster_centers[:, 0].mean():
    #                     label = "Popular Mainstream"
    #                 else:
    #                     label = "Budget Basics"
    #             else:  # Just sales and price
    #                 sales, price = center
    #                 if sales > cluster_centers[:, 0].mean() and price > cluster_centers[:, 1].mean():
    #                     label = "Premium Bestsellers"
    #                 elif sales > cluster_centers[:, 0].mean():
    #                     label = "Popular Value"
    #                 elif price > cluster_centers[:, 1].mean():
    #                     label = "Luxury Niche"
    #                 else:
    #                     label = "Economy Essentials"
                
    #             segment_labels.append(f"Segment {i+1}: {label}")
            
    #         # Map cluster numbers to segment labels
    #         segment_map = {i: segment_labels[i] for i in range(n_clusters)}
    #         self.df_filtered['segment'] = self.df_filtered['cluster'].map(segment_map)
            
    #         # Visualize the clusters
    #         col1, col2 = st.columns(2)
            
    #         with col1:
    #             # Scatter plot of clusters
    #             fig = px.scatter(
    #                 self.df_filtered, 
    #                 x='sales_volume', 
    #                 y='product_price',
    #                 color='segment',
    #                 hover_data=['product_name', 'product_group'],
    #                 title='Product Segmentation Analysis',
    #                 labels={'sales_volume': 'Sales Volume', 'product_price': 'Product Price ($)'}
    #             )
    #             st.plotly_chart(fig, use_container_width=True)
            
    #         with col2:
    #             # Segment composition
    #             segment_counts = self.df_filtered['segment'].value_counts().reset_index()
    #             segment_counts.columns = ['Segment', 'Count']
                
    #             fig = px.pie(
    #                 segment_counts,
    #                 values='Count',
    #                 names='Segment',
    #                 title='Segment Distribution',
    #                 color_discrete_sequence=px.colors.qualitative.Pastel
    #             )
    #             fig.update_traces(textposition='inside', textinfo='percent+label')
    #             st.plotly_chart(fig, use_container_width=True)
            
    #         # Segment insights table
    #         st.markdown("<b>Segment Insights:</b>", unsafe_allow_html=True)
            
    #         segment_insights = self.df_filtered.groupby('segment').agg({
    #             'product_name': 'count',
    #             'sales_volume': 'mean',
    #             'product_price': 'mean',
    #             'discount_percentage': 'mean' if 'discount_percentage' in self.df_filtered.columns else 'size'
    #         }).reset_index()
            
    #         segment_insights.columns = ['Segment', 'Product Count', 'Avg Sales Volume', 'Avg Price ($)', 
    #                                     'Avg Discount (%)' if 'discount_percentage' in self.df_filtered.columns else 'Size']
            
    #         st.dataframe(segment_insights)
    
    # def build_ml_recommendations(self):
    #     """Build ML-driven recommendations"""
    #     if 'discount' in self.df_filtered.columns and 'discount_percentage' in self.df_filtered.columns:
    #         st.markdown("<h3 class='section-header'>ML-Driven Recommendations</h3>", unsafe_allow_html=True)
            
    #         # Identify products for potential discount
    #         potential_discount = self.df_filtered[
    #             (self.df_filtered['discount'] == 'no') & 
    #             (self.df_filtered['sales_volume'] > self.df_filtered['sales_volume'].quantile(0.7))
    #         ]
            
    #         if len(potential_discount) > 0:
    #             st.markdown("""
    #             <div class='highlight'>
    #             <b>🔍 High-Volume Products Without Discounts:</b><br>
    #             These high-selling products currently have no discounts but may be good candidates for promotional pricing:
    #             </div>
    #             """, unsafe_allow_html=True)
                
    #             potential_table = potential_discount.sort_values('sales_volume', ascending=False)[
    #                 ['product_name', 'product_brand', 'product_group', 'sales_volume', 'product_price']
    #             ].head(10)
                
    #             st.dataframe(potential_table)
            
    #         # Identify products for potential ultra discounts
    #         if 'ultra_discount_percentage' in self.df_filtered.columns:
    #             potential_ultra = self.df_filtered[
    #                 (self.df_filtered['discount'] == 'yes') & 
    #                 (self.df_filtered['discount_percentage'] >= self.discount_threshold) &
    #                 (self.df_filtered['ultra_discount_percentage'] == 0)
    #             ]
                
    #             if len(potential_ultra) > 0:
    #                 st.markdown("""
    #                 <div class='highlight'>
    #                 <b>🔍 Products for Potential Ultra Discounts:</b><br>
    #                 These products have high regular discounts but no ultra discounts applied:
    #                 </div>
    #                 """, unsafe_allow_html=True)
                    
    #                 ultra_table = potential_ultra.sort_values('discount_percentage', ascending=False)[
    #                     ['product_name', 'product_brand', 'discount_percentage', 'product_price']
    #                 ].head(10)
                    
    #                 st.dataframe(ultra_table)
            
    #         # Identify underperforming products
    #         underperforming = self.df_filtered[
    #             (self.df_filtered['sales_volume'] < self.df_filtered['sales_volume'].quantile(0.3)) & 
    #             (self.df_filtered['product_price'] > self.df_filtered['product_price'].quantile(0.7))
    #         ]
            
    #         if len(underperforming) > 0:
    #             st.markdown("""
    #             <div class='highlight'>
    #             <b>🔍 Underperforming Premium Products:</b><br>
    #             These high-priced products have low sales volume and might benefit from price adjustments:
    #             </div>
    #             """, unsafe_allow_html=True)
                
    #             underperforming_table = underperforming.sort_values('product_price', ascending=False)[
    #                 ['product_name', 'product_brand', 'product_group', 'sales_volume', 'product_price']
    #             ].head(10)
                
    #             st.dataframe(underperforming_table)
    
    # def add_footer(self):
    #     """Add footer to the dashboard"""
    #     st.markdown("---")
    #     st.markdown("""
    #     <div style="text-align: center; color: #666;">
    #     <small>Advanced Store Data Analysis Dashboard • Powered by Machine Learning</small>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # def run(self):
    #     """Main method to run the dashboard"""
    #     # Display title
    #     st.markdown("<h1 class='main-header'>Advanced Store Data Analysis Dashboard</h1>", unsafe_allow_html=True)
        
    #     # Build sidebar filters and controls
    #     self.build_sidebar_filters()
    #     self.build_ml_thresholds()
    #     self.add_download_button()
        
    #     # Main content tabs
    #     tab1, tab2, tab3 = st.tabs(["📊 Overall Statistics", "🔍 Detailed Analysis", "🧠 ML Insights"])
        
    #     # Tab 1: Overall Statistics
    #     with tab1:
    #         self.build_overall_stats_tab()
        
    #     # Tab 2: Detailed Analysis
    #     with tab2:
    #         self.build_detailed_analysis_tab()
        
    #     # Tab 3: ML Insights
    #     with tab3:
    #         self.build_ml_insights_tab()
        
    #     # Add footer
    #     self.add_footer()


# Run the dashboard when script is executed directly
if __name__ == "__main__":
    dashboard = StoreDataAnalysisDashboard()
    dashboard.run()