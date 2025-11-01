import streamlit as st
import requests
import json

API_BASE_URL = "http://localhost:8000"

# Page config - no icon, no sidebar
st.set_page_config(
    page_title="Stock Market Sentiment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    /* Hide deploy button */
    .stDeployButton {
        display: none;
    }
    /* Hide streamlit menu */
    #MainMenu {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="main-header">Stock Market Sentiment Analyzer</div>', unsafe_allow_html=True)
st.markdown("---")

# Fetch companies from API
@st.cache_data
def get_companies():
    try:
        response = requests.get(f"{API_BASE_URL}/companies")
        if response.status_code == 200:
            return response.json()["companies"]
        else:
            return []
    except Exception as e:
        return []

# Main content
companies = get_companies()

if companies:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Select Company")
        selected_company = st.selectbox(
            "Choose a company to analyze",
            options=companies,
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Go button
        if st.button("🚀 Analyze", type="primary", use_container_width=True):
            with st.spinner(f"🔍 Analyzing {selected_company}..."):
                try:
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-company",
                        json={"company_name": selected_company},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Success message
                        st.success(f"✓ Analysis complete for **{data['company_name']}**")
                        st.markdown("---")
                        
                        # Display results
                        result_data = data.get("result", {})
                        
                        if isinstance(result_data, list) and len(result_data) > 0:
                            st.markdown(f"### 📰 Top {min(len(result_data), 5)} Articles")
                            
                            # Simple list display - just headline and summary
                            for i, item in enumerate(result_data[:5], 1):
                                if isinstance(item, dict):
                                    # Get headline
                                    headline = item.get('headline', item.get('title', 'No headline available'))
                                    
                                    # Get summary
                                    summary = item.get('summary', item.get('description', 'No summary available'))
                                    
                                    # Display
                                    st.markdown(f"#### {i}. {headline}")
                                    st.write(summary)
                                    st.markdown("---")
                                else:
                                    st.write(f"{i}. {item}")
                                    st.markdown("---")
                            
                            # Show full data in expander
                            with st.expander("🔍 View Full Data"):
                                st.json(data)
                        
                        elif isinstance(result_data, dict):
                            # If result is a dict, show as sections
                            st.markdown("### 📊 Results")
                            for key, value in result_data.items():
                                st.markdown(f"#### {key.replace('_', ' ').title()}")
                                if isinstance(value, (dict, list)):
                                    st.json(value)
                                else:
                                    st.info(str(value))
                                st.markdown("---")
                            
                            with st.expander("🔍 View Full Data"):
                                st.json(data)
                        
                        else:
                            # Fallback
                            st.markdown("### Results")
                            st.write(result_data)
                            with st.expander("🔍 View Full Data"):
                                st.json(data)
                        
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.code(response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
else:
    st.warning("⚠️ Unable to fetch companies. Make sure the API server is running.")
    st.code("python3 server.py", language="bash")
    st.info("💡 The API should be running at http://localhost:8000")
