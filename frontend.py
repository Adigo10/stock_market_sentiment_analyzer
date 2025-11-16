import streamlit as st
import requests
import json

API_BASE_URL = "http://localhost:8000"

# Page config - no icon, no sidebar
st.set_page_config(
    page_title="Stock Market Sentiment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(
        '<div class="main-header">Stock Market Sentiment Analyzer</div>',
        unsafe_allow_html=True,
    )
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
            label_visibility="collapsed",
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
                        timeout=300,  # Increased to 5 minutes for development
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Success message
                        st.success(
                            f"✓ Analysis complete for **{data['company_name']}**"
                        )
                        st.markdown("---")

                        # Display results
                        result_data = data.get("result", {})

                        if isinstance(result_data, list) and len(result_data) > 0:
                            st.markdown(
                                f"### 📰 Top {min(len(result_data), 15)} Articles"
                            )

                            # Simple list display - just headline and summary
                            for i, item in enumerate(result_data[:15], 1):
                                if isinstance(item, dict):
                                    # Get headline
                                    headline = item.get(
                                        "headline",
                                        item.get("title", "No headline available"),
                                    )

                                    # Get summary
                                    summary = item.get(
                                        "summary",
                                        item.get("description", "No summary available"),
                                    )

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
                        st.warning("No keyphrases extracted from analyzed articles.")

                progress_bar.progress(100)
                status_placeholder.success("All steps completed successfully! 🎉")

                # Final article cards - displayed at the bottom with 2-column grid
                # Prepare payload for download regardless of whether there are articles
                download_payload = json.dumps(
                    result_data,
                    indent=2,
                    ensure_ascii=False,
                )

                if result_data:
                    st.markdown("---")  # Separator
                    st.markdown("### 📰 AI-Enriched Articles")
                    st.markdown(
                        f"<div style='color:#6b7280;font-size:1rem;margin-bottom:1.5rem;'>Showing <strong>{min(len(result_data), 15)}</strong> of <strong>{len(result_data)}</strong> analyzed articles with AI insights</div>",
                        unsafe_allow_html=True
                    )

                    articles_to_show = result_data[:15]
                    card_html_list = [
                        display_article_card(article, idx)
                        for idx, article in enumerate(articles_to_show, 1)
                    ]

                    # Display articles in 2-column grid with better spacing
                    for start in range(0, len(card_html_list), 2):
                        cols = st.columns(2, gap="large")
                        for offset in range(2):
                            card_idx = start + offset
                            if card_idx < len(card_html_list):
                                with cols[offset]:
                                    st_html(card_html_list[card_idx], height=650, width=None, scrolling=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    safe_company = re.sub(r"[^a-z0-9]+", "_", selected_company.lower()).strip("_")
                    st.download_button(
                        "📥 Download All Articles (JSON)",
                        data=download_payload.encode("utf-8"),
                        file_name=f"{safe_company or 'analysis'}_ai_articles.json",
                        mime="application/json",
                    )
                else:
                    st.warning(
                        "No enriched articles available from the AI analysis."
                    )
                    safe_company = re.sub(
                        r"[^a-z0-9]+", "_", selected_company.lower()
                    ).strip("_")
                    st.download_button(
                        "📥 Download All Articles (JSON)",
                        data=download_payload.encode("utf-8"),
                        file_name=f"{safe_company or 'analysis'}_ai_articles.json",
                        mime="application/json",
                    )

                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
else:
    st.warning("⚠️ Unable to fetch companies. Make sure the API server is running.")
    st.code("python3 server.py", language="bash")
    st.info("💡 The API should be running at http://localhost:8000")
