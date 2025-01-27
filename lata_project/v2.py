import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from datetime import datetime
import io
import base64
from PIL import Image


st.set_page_config(
    page_title="Web Scraper",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Main page gradient background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 25%, #c3cfe2 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 25%, #3498db 100%);
    }
    
    /* Headers */
    h1 {
        background: -webkit-linear-gradient(45deg, #ffffff, #964b00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    h2 {
        color: #ffffff;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(to right, #4CAF50, #45a049);
        color: white;
        padding: 10px 24px;
        border-radius: 5px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(to right, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* DataFrames */
    .dataframe {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Metrics */
    .css-1r6slb0 {
        background: linear-gradient(135deg, #fff 0%, #f7f9fc 100%);
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Custom container */
    .custom-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# def add_bg_from_local(image_path):
#     with open(image_path, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode()
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-image: url("data:image/png;base64,{encoded_string}");
#             background-attachment: fixed;
#             background-size: cover;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# add_bg_from_local("E:\web scrapping\Basics\project\lata_project\wallpapersden.com_cybersecurity-core_1927x1080.jpg")

st.markdown(
    """
    <div class="footer">
        <p>Web Scraper © 2025 | Made with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Utility Functions
def setup_session():
    """Initialize session state variables"""
    if 'scrape_count' not in st.session_state:
        st.session_state.scrape_count = 0
    if 'last_scrape' not in st.session_state:
        st.session_state.last_scrape = None

def scrape_with_retry(url, proxies=None, max_retries=3):
    """Enhanced scraping with retry mechanism"""
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(url, proxies=proxies)
        response.raise_for_status()
        return response
    except Exception as e:
        st.error(f"Error during scraping: {str(e)}")
        return None

def scrape_content(url, settings):
    """Main scraping function with progress tracking"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize scraping
        progress_bar.progress(10)
        status_text.text("Initializing scraper...")
        
        # Setup proxy if enabled
        proxies = None
        if settings.get('use_proxy'):
            proxies = {
                'http': settings['proxy_url'],
                'https': settings['proxy_url']
            }
        
        # Fetch page content
        response = scrape_with_retry(url, proxies)
        if not response:
            return None
        
        progress_bar.progress(30)
        status_text.text("Parsing content...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data based on settings
        data = {
            'tables': [],
            'headlines': [],
            'links': [],
            'images': [],
            'media': [],
            'custom_tags': []
        }
        
        # Scrape tables
        if settings.get('scrape_tables'):
            progress_bar.progress(50)
            status_text.text("Scraping tables...")
            tables = soup.find_all('table')
            for table in tables:
                df = pd.read_html(str(table))[0]
                data['tables'].append(df)
        
        # Scrape headlines
        if settings.get('scrape_headlines'):
            progress_bar.progress(60)
            status_text.text("Scraping headlines...")
            for tag in settings.get('headline_tags', []):
                headlines = soup.find_all(tag)
                data['headlines'].extend([h.text.strip() for h in headlines])
        
        # Scrape links
        if settings.get('scrape_links'):
            progress_bar.progress(70)
            status_text.text("Scraping links...")
            links = soup.find_all('a', href=True)
            data['links'].extend([l['href'] for l in links if l['href'].startswith('http')])
        
        # Scrape images
        if settings.get('scrape_images'):
            progress_bar.progress(80)
            status_text.text("Scraping images...")
            images = soup.find_all('img', src=True)
            data['images'].extend([i['src'] for i in images])
        
        # Scrape custom tags
        if settings.get('custom_tag'):
            progress_bar.progress(90)
            status_text.text("Scraping custom tags...")
            custom_elements = soup.find_all(settings['custom_tag'])
            data['custom_tags'].extend([e.text.strip() for e in custom_elements])
        
        progress_bar.progress(100)
        status_text.text("Scraping completed!")
        
        return data
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def export_data(data, format_type):
    """Export scraped data in selected format"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == "JSON":
        json_str = json.dumps(data, default=str, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"scraped_data_{timestamp}.json",
            mime="application/json"
        )
    
    elif format_type == "Excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write tables
            for i, df in enumerate(data['tables']):
                df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
            
            # Write other data
            pd.DataFrame(data['headlines'], columns=['Headlines']).to_excel(
                writer, sheet_name='Headlines', index=False)
            pd.DataFrame(data['links'], columns=['Links']).to_excel(
                writer, sheet_name='Links', index=False)
            pd.DataFrame(data['images'], columns=['Images']).to_excel(
                writer, sheet_name='Images', index=False)
        
        excel_data = output.getvalue()
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"scraped_data_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Scraper", "Results", "Settings"],
        icons=['cloud-download', 'table', 'gear'],
        menu_icon="cast",
        default_index=0,
    )

# Initialize session
setup_session()

# Main UI
if selected == "Scraper":
    st.title("🌐 Web Scraper")
    
    # Input URL
    url = st.text_input("Enter URL to scrape:")
    
    # Scraping options
    with st.expander("Scraping Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            scrape_tables = st.checkbox("Scrape Tables", True)
            scrape_headlines = st.checkbox("Scrape Headlines")
            headline_tags = st.multiselect(
                "Select headline tags:",
                ["h1", "h2", "h3", "h4", "h5", "h6"]
            )
        
        with col2:
            scrape_links = st.checkbox("Scrape Links")
            scrape_images = st.checkbox("Scrape Images")
            custom_tag = st.text_input("Custom tag to scrape:")
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        use_proxy = st.checkbox("Use Proxy")
        proxy_url = st.text_input("Proxy URL:") if use_proxy else None
        export_format = st.selectbox(
            "Export Format:",
            ["JSON", "Excel"]
        )
    
    # Start scraping
    if st.button("Start Scraping"):
        if url:
            settings = {
                'scrape_tables': scrape_tables,
                'scrape_headlines': scrape_headlines,
                'headline_tags': headline_tags,
                'scrape_links': scrape_links,
                'scrape_images': scrape_images,
                'custom_tag': custom_tag,
                'use_proxy': use_proxy,
                'proxy_url': proxy_url
            }
            
            data = scrape_content(url, settings)
            if data:
                st.session_state.last_scrape = data
                st.session_state.scrape_count += 1
                export_data(data, export_format)
        else:
            st.warning("Please enter a URL to scrape.")

elif selected == "Results":
    st.title("📊 Scraping Results")
    
    if st.session_state.last_scrape:
        data = st.session_state.last_scrape
        
        # Display tables
        if data['tables']:
            st.subheader("Tables")
            for i, df in enumerate(data['tables']):
                st.write(f"Table {i+1}")
                st.dataframe(df)
        
        # Display other data
        for key in ['headlines', 'links', 'images', 'custom_tags']:
            if data[key]:
                st.subheader(key.title())
                st.write(data[key])
    else:
        st.info("No scraping results available. Run the scraper first.")

elif selected == "Settings":
    st.title("⚙️ Settings")
    st.write("Total scrapes:", st.session_state.scrape_count)
    if st.session_state.last_scrape:
        st.write("Last scrape data available")
    
    if st.button("Clear Session Data"):
        st.session_state.clear()
        st.success("Session data cleared!")