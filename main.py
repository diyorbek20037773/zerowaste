import numpy as np
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from consumer import maps, tables
from zero_waste_stats import StoreDataAnalysisDashboard
from dataa import dat
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os


image = Image.open("21.png")

st.set_page_config(page_title="ZeroWaste", layout="wide")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    load_css("style.css")
    
    page_by_image = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05)), 
                        url("https://images.unsplash.com/photo-1486895756674-b48b9b2eacf3?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: 78% 100%; /* or 100% 100% for stretch */
        background-repeat: no-repeat;
        background-position: right;
    }
    </style>
    """
    st.markdown(page_by_image, unsafe_allow_html=True)
    
    # Initialize session state for page navigation
    if "page" not in st.session_state:
        st.session_state.page = "1"  # Default page
    
    
    col1, col2 = st.sidebar.columns([1, 2])

    # Display the logo in the first column with custom styling to move it higher
    with col1:
        st.image(image, width=100)
        # Add CSS to shift the image upward
        st.markdown(
            """
            <style>
            img {
                margin-top: -10px;  /* Adjust this value to move the image higher (negative moves up) */
                border-radius: 50%;
                width: 80px;
                height: 80px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Display the title in the second column
    with col2:
        st.markdown('<div class="unistream-title">ZeroWaste</div>', unsafe_allow_html=True)
        
    st.markdown(
    """
    <style>
    div[data-testid="stSidebar"] .stButton > button {
        color: #FFFFFF; /* Default text color (white) */
        font-family: Georgia, 'Times New Roman', Times, serif !important;
        font-size: 25px !important;
        transition: color 0.3s ease; /* Smooth transition for color change */
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        color: #FF4500; /* OrangeRed on hover */
    }
    div[data-testid="stSidebar"] .stButton > button:active {
        color: #FFD700; /* Gold when clicked */
    }
    </style>
    """,
    unsafe_allow_html=True
)    
        
    # Sidebar buttons
    with st.sidebar:
        st.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)
        if st.button("📑 Data"):
            st.session_state.page = "1"
        if st.button("🔢 Statistics"):
            st.session_state.page = "2"
        if st.button("💯 Consumer"):
            st.session_state.page = "3"
        if st.button("❗Non-edible products"):
            st.session_state.page = "4"

    
    # Page content based on session state
    if st.session_state.page == "1":
        st.markdown(f"""
                    <div style="background-color: #f0f2f6; margin-top:-55px; margin-bottom:30px;  padding: 0px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); ">
                        <h1 style="color: green; margin: 0;">DATA ENTRANCE</h1>
                    </div>
                """, unsafe_allow_html=True)


        dat()
       
       
        
    elif st.session_state.page == "2":
        dashboard = StoreDataAnalysisDashboard(set_page_config=False)
        dashboard.run()
        
    elif st.session_state.page == "3":
            st.markdown(f"""
                    <div style="background-color: #f0f2f6; margin-top:-25px; margin-bottom:30px;  padding: 0px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); ">
                        <h1 style="color: #333; margin: 0;">Product search</h1>
                    </div>
                """, unsafe_allow_html=True)
            
            tables()
        
            st.markdown(f"""
                    <div style="background-color: #f0f2f6; margin-top:60px; margin-bottom:30px;  padding: 0px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); ">
                        <h1 style="color: #333; margin: 0;">Shop Location Finder</h1>
                    </div>
                """, unsafe_allow_html=True)
            # st.title("Shop Location Finder")
            maps()
    elif st.session_state.page == "4":
        pass



if __name__ == "__main__":
    main()