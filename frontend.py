import streamlit as st
import requests
import json
import re
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Stock Market Sentiment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS with enhanced styling
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
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
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
    .sentiment-positive {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .sentiment-negative {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .sentiment-neutral {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .keyphrase-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .keyphrase-positive {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .keyphrase-negative {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .keyphrase-neutral {
        background-color: #e2e3e5;
        color: #383d41;
        border: 1px solid #d6d8db;
    }
    .article-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
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
st.markdown(
    '<div class="main-header">🤖 AI Stock Market Sentiment Analyzer</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Powered by Flan-T5 AI Model • Real-time News Analysis • Keyphrase Extraction</div>',
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


# Helper functions
def parse_sentiment(sentiment_text):
    """Parse sentiment from format: <senti>Good<reason>Explanation"""
    if not sentiment_text:
        return "neutral", ""
    
    sentiment_match = re.search(r'<senti>(\w+)', sentiment_text)
    reason_match = re.search(r'<reason>(.*)', sentiment_text, re.DOTALL)
    
    sentiment_type = sentiment_match.group(1).lower() if sentiment_match else 'neutral'
    reason = reason_match.group(1).strip() if reason_match else sentiment_text
    
    return sentiment_type, reason


def get_sentiment_badge(sentiment_type):
    """Return HTML for sentiment badge"""
    sentiment_map = {
        'good': ('positive', '🟢 Positive'),
        'positive': ('positive', '🟢 Positive'),
        'bad': ('negative', '🔴 Negative'),
        'negative': ('negative', '🔴 Negative'),
        'neutral': ('neutral', '⚪ Neutral')
    }
    
    css_class, label = sentiment_map.get(sentiment_type.lower(), ('neutral', '⚪ Neutral'))
    return f'<span class="sentiment-{css_class}">{label}</span>'


def display_keyphrases(keyphrases, max_display=5):
    """Display keyphrases as colored badges"""
    if not keyphrases:
        return ""
    
    html = ""
    for phrase_type in ['positive', 'negative', 'neutral']:
        phrases = keyphrases.get(phrase_type, [])[:max_display]
        if phrases:
            for phrase_data in phrases:
                phrase = phrase_data.get('phrase', '')
                confidence = phrase_data.get('confidence', 0)
                html += f'<span class="keyphrase-badge keyphrase-{phrase_type}" title="Confidence: {confidence:.2f}">{phrase}</span> '
    
    return html


def display_article_card(article, index):
    """Display a single article as a beautiful card"""
    headline = article.get('headline', article.get('title', 'No headline'))
    summary = article.get('summary', article.get('content', 'No summary available'))
    url = article.get('url', '#')
    publish_date = article.get('publish_date', '')
    rank_score = article.get('rank_score', 0)
    
    # Parse sentiment
    predicted_sentiment = article.get('predicted_sentiment', '')
    sentiment_type, sentiment_reason = parse_sentiment(predicted_sentiment)
    sentiment_badge = get_sentiment_badge(sentiment_type)
    
    # Get keyphrases
    keyphrase_analysis = article.get('keyphrase_analysis', {})
    keyphrases = keyphrase_analysis.get('keyphrases', {})
    keyphrase_html = display_keyphrases(keyphrases, max_display=8)
    
    # Format date
    try:
        if publish_date:
            dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%B %d, %Y')
        else:
            formatted_date = 'Date unknown'
    except:
        formatted_date = str(publish_date) if publish_date else 'Date unknown'
    
    # Build card HTML
    card_html = f"""
    <div class="article-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #333;">#{index}. {headline}</h3>
            {sentiment_badge}
        </div>
        
        <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.8rem;">
            📅 {formatted_date} • ⭐ Rank Score: {rank_score:.3f}
        </div>
        
        <p style="color: #555; line-height: 1.6; margin-bottom: 1rem;">
            {summary[:300]}{'...' if len(summary) > 300 else ''}
        </p>
    """
    
    if sentiment_reason:
        card_html += f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <strong>🤖 AI Sentiment Analysis:</strong>
            <p style="margin: 0.5rem 0 0 0; color: #555;">{sentiment_reason[:200]}{'...' if len(sentiment_reason) > 200 else ''}</p>
        </div>
        """
    
    if keyphrase_html:
        card_html += f"""
        <div style="margin-bottom: 1rem;">
            <strong style="color: #666;">🔑 Key Phrases:</strong><br/>
            <div style="margin-top: 0.5rem;">
                {keyphrase_html}
            </div>
        </div>
        """
    
    if url and url != '#':
        card_html += f"""
        <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 500;">
            🔗 Read Full Article →
        </a>
        """
    
    card_html += "</div>"
    
    return card_html


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
                        result_data = data.get("result", [])

                        # Success message
                        st.success(
                            f"✓ Analysis complete for **{data['company_name']}** - Found {len(result_data)} articles"
                        )
                        st.markdown("<br>", unsafe_allow_html=True)

                        if isinstance(result_data, list) and len(result_data) > 0:
                            # Calculate statistics
                            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
                            total_keyphrases = {'positive': 0, 'negative': 0, 'neutral': 0}
                            
                            for article in result_data:
                                # Count sentiments
                                pred_sent = article.get('predicted_sentiment', '')
                                sent_type, _ = parse_sentiment(pred_sent)
                                if sent_type in ['good', 'positive']:
                                    sentiment_counts['positive'] += 1
                                elif sent_type in ['bad', 'negative']:
                                    sentiment_counts['negative'] += 1
                                else:
                                    sentiment_counts['neutral'] += 1
                                
                                # Count keyphrases
                                ka = article.get('keyphrase_analysis', {})
                                summary = ka.get('summary', {})
                                total_keyphrases['positive'] += summary.get('positive_count', 0)
                                total_keyphrases['negative'] += summary.get('negative_count', 0)
                                total_keyphrases['neutral'] += summary.get('neutral_count', 0)
                            
                            # Display statistics cards
                            st.markdown("### 📊 Analysis Summary")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="stats-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                                        <div class="stats-number">{sentiment_counts['positive']}</div>
                                        <div class="stats-label">🟢 Positive</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            with col2:
                                st.markdown(
                                    f"""
                                    <div class="stats-card" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
                                        <div class="stats-number">{sentiment_counts['negative']}</div>
                                        <div class="stats-label">🔴 Negative</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            with col3:
                                st.markdown(
                                    f"""
                                    <div class="stats-card" style="background: linear-gradient(135deg, #8e9eab 0%, #eef2f3 100%);">
                                        <div class="stats-number" style="color: #333;">{sentiment_counts['neutral']}</div>
                                        <div class="stats-label" style="color: #333;">⚪ Neutral</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            with col4:
                                total_phrases = sum(total_keyphrases.values())
                                st.markdown(
                                    f"""
                                    <div class="stats-card">
                                        <div class="stats-number">{total_phrases}</div>
                                        <div class="stats-label">🔑 Total Keyphrases</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            st.markdown("<br><br>", unsafe_allow_html=True)
                            st.markdown("### 📰 Top Articles")
                            st.markdown("<br>", unsafe_allow_html=True)

                            # Display articles
                            for i, article in enumerate(result_data[:15], 1):
                                card_html = display_article_card(article, i)
                                st.markdown(card_html, unsafe_allow_html=True)

                            # Show full data in expander
                            with st.expander("🔍 View Raw JSON Data"):
                                st.json(data)

                        else:
                            # Fallback
                            st.warning("No articles found or unexpected data format.")
                            with st.expander("🔍 View Raw Response"):
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
