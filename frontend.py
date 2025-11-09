import streamlit as st
import requests
import json
import re
import pandas as pd
from collections import Counter
from datetime import datetime
from streamlit.components.v1 import html as st_html

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


# Persistent state for analysis results
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "analysis_rendered_in_run" not in st.session_state:
    st.session_state["analysis_rendered_in_run"] = False
else:
    st.session_state["analysis_rendered_in_run"] = False


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
    """Parse sentiment from format: Sentiment: Good/Bad/Neutral Reason: Explanation"""
    if not sentiment_text:
        return "neutral", ""
    
    sentiment_match = re.search(r'Sentiment:\s*(\w+)', sentiment_text, re.IGNORECASE)
    reason_match = re.search(r'Reason:\s*(.*)', sentiment_text, re.IGNORECASE | re.DOTALL)
    
    sentiment_type = sentiment_match.group(1).lower() if sentiment_match else 'neutral'
    
    # Extract reason properly - if found, use it; otherwise return empty string
    if reason_match:
        reason = reason_match.group(1).strip()
    else:
        # If no "Reason:" found, check if there's text after sentiment
        if sentiment_match:
            # Get everything after the sentiment declaration
            remaining_text = sentiment_text[sentiment_match.end():].strip()
            # Remove common separators at the start
            reason = re.sub(r'^[:\-\.\,\s]+', '', remaining_text).strip()
        else:
            # Fallback: use the entire text if no structure found
            reason = sentiment_text.strip()
    
    return sentiment_type, reason


def get_sentiment_badge(sentiment_type):
    """Return HTML for sentiment badge"""
    sentiment_type = sentiment_type.lower()
    style_map = {
        "positive": "display:inline-block;padding:6px 18px;border-radius:999px;font-weight:600;color:#fff;background:linear-gradient(135deg,#1bcfb4 0%,#0baaa1 100%);",
        "negative": "display:inline-block;padding:6px 18px;border-radius:999px;font-weight:600;color:#fff;background:linear-gradient(135deg,#f5576c 0%,#f093fb 100%);",
        "neutral": "display:inline-block;padding:6px 18px;border-radius:999px;font-weight:600;color:#2f2f2f;background:linear-gradient(135deg,#fdfbfb 0%,#ebedee 100%);border:1px solid #d1d5db;",
    }
    label_map = {
        "positive": "🟢 Positive",
        "negative": "🔴 Negative",
        "neutral": "⚪ Neutral",
    }

    key = 'neutral'
    if sentiment_type in ('good', 'positive', 'bullish'):
        key = 'positive'
    elif sentiment_type in ('bad', 'negative', 'bearish'):
        key = 'negative'
    elif sentiment_type in ('neutral', 'okay', 'mixed', 'uncertain'):
        key = 'neutral'

    return f'<span style="{style_map[key]}">{label_map[key]}</span>'


def display_keyphrases(keyphrases, max_display=5):
    """Display keyphrases as colored badges"""
    if not keyphrases:
        return ""

    html = ""
    style_map = {
        "positive": "display:inline-block;padding:4px 10px;margin:3px;border-radius:12px;font-size:0.85rem;font-weight:500;background-color:#d4edda;color:#155724;border:1px solid #c3e6cb;",
        "negative": "display:inline-block;padding:4px 10px;margin:3px;border-radius:12px;font-size:0.85rem;font-weight:500;background-color:#f8d7da;color:#721c24;border:1px solid #f5c6cb;",
        "neutral": "display:inline-block;padding:4px 10px;margin:3px;border-radius:12px;font-size:0.85rem;font-weight:500;background-color:#e2e3e5;color:#383d41;border:1px solid #d6d8db;",
    }
    for phrase_type in ["positive", "negative", "neutral"]:
        phrases = keyphrases.get(phrase_type, [])[:max_display]
        if phrases:
            for phrase_data in phrases:
                phrase = phrase_data.get("phrase", "")
                confidence = phrase_data.get("confidence", 0)
                html += (
                    f'<span style="{style_map[phrase_type]}" '
                    f'title="Confidence: {confidence:.2f}">{phrase}</span>'
                )

    return html


def format_article_date(raw_date, default="-"):
    """Convert various date formats to YYYY-MM-DD for table display."""
    if raw_date is None:
        return default

    if isinstance(raw_date, str):
        raw_date = raw_date.strip()
        if not raw_date:
            return default

    if isinstance(raw_date, (int, float)):
        try:
            seconds = raw_date / 1000 if raw_date > 1e10 else raw_date
            return datetime.utcfromtimestamp(seconds).strftime("%Y-%m-%d")
        except Exception:
            return default

    if isinstance(raw_date, datetime):
        return raw_date.strftime("%Y-%m-%d")

    try:
        parsed = pd.to_datetime(raw_date, utc=False)
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return str(raw_date) if raw_date not in ("", None) else default


def extract_article_date(article, default="-"):
    """Pull the most relevant date field from an article dict."""
    if not article:
        return default

    for key in (
        "publish_date",
        "published_date",
        "date",
        "datetime",
        "timestamp",
        "time",
    ):
        value = article.get(key)
        if value not in (None, "", "N/A"):
            return format_article_date(value, default)
    return default


def display_article_card(article, index):
    """Display a single article as a beautiful card with expand/collapse functionality"""
    headline = article.get('headline', article.get('title', 'No headline'))
    summary = article.get('summary', article.get('content', 'No summary available'))
    url = article.get('url', '#')
    
    # Extract date from various possible fields
    publish_date = extract_article_date(article, '')
    
    rank_score = article.get('rank_score', 0)
    
    # Parse sentiment
    predicted_sentiment = article.get("predicted_sentiment", "")
    sentiment_type, sentiment_reason = parse_sentiment(predicted_sentiment)
    sentiment_badge = get_sentiment_badge(sentiment_type)

    # Get keyphrases
    keyphrase_analysis = article.get("keyphrase_analysis", {})
    keyphrases = keyphrase_analysis.get("keyphrases", {})
    keyphrase_html = display_keyphrases(keyphrases, max_display=8)

    # Format date
    try:
        if publish_date:
            dt = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%B %d, %Y")
        else:
            formatted_date = "Date unknown"
    except:
        formatted_date = str(publish_date) if publish_date else 'Date unknown'
    
    # Unique ID for expand/collapse functionality
    card_id = f"article-card-{index}"
    
    # Truncate summary for preview
    summary_preview = summary[:320] + '...' if len(summary) > 320 else summary
    summary_full = summary
    
    # Build card HTML with expand/collapse functionality
    card_html = f"""
    <div style="width:100%;max-width:100%;overflow:hidden;">
    <div id="{card_id}" style="width:100%;box-sizing:border-box;background:#ffffff;border-radius:16px;padding:24px;border-left:6px solid #667eea;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1),0 2px 4px -1px rgba(0,0,0,0.06);margin-bottom:20px;font-family:'Segoe UI',Tahoma,sans-serif;transition:all 0.3s ease;hover:box-shadow:0 20px 25px -5px rgba(0,0,0,0.1),0 10px 10px -5px rgba(0,0,0,0.04);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;gap:16px;">
            <h3 style="margin:0;color:#111827;font-size:1.35rem;font-weight:700;flex:1;line-height:1.4;word-wrap:break-word;">#{index}. {headline}</h3>
            <div style="flex-shrink:0;">{sentiment_badge}</div>
        </div>
        
        <div style="color:#6b7280;font-size:0.95rem;margin-bottom:16px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span style="display:flex;align-items:center;gap:5px;">📅 {formatted_date}</span>
            <span style="width:4px;height:4px;background:#d1d5db;border-radius:999px;display:inline-block;"></span>
            <span style="display:flex;align-items:center;gap:5px;">⭐ Rank: {rank_score:.3f}</span>
        </div>
        
        <div id="{card_id}-summary-preview" style="color:#374151;line-height:1.8;margin-bottom:18px;font-size:1rem;text-align:justify;">
            {summary_preview}
        </div>
        
        <div id="{card_id}-summary-full" style="display:none;color:#374151;line-height:1.8;margin-bottom:18px;font-size:1rem;text-align:justify;">
            {summary_full}
        </div>
    """
    
    # Add expand/collapse button if summary is truncated
    if len(summary) > 320:
        card_html += f"""
        <button id="{card_id}-toggle-btn" onclick="toggleExpand('{card_id}')" style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;padding:10px 20px;border-radius:10px;cursor:pointer;font-weight:600;margin-bottom:18px;font-size:0.9rem;transition:all 0.2s ease;box-shadow:0 2px 4px rgba(102,126,234,0.3);">
            ▼ Show More
        </button>
        """
    
    if sentiment_reason:
        card_html += f"""
        <div style="background:linear-gradient(135deg,#f0f9ff 0%,#e0e7ff 100%);padding:18px;border-radius:12px;margin-bottom:18px;border:1px solid #c7d2fe;">
            <div style="font-weight:700;color:#3730a3;margin-bottom:8px;display:flex;align-items:center;gap:8px;font-size:1rem;">
                <span>🤖 AI Sentiment Analysis</span>
            </div>
            <p style="margin:0;color:#1e293b;font-size:0.98rem;line-height:1.7;">{sentiment_reason}</p>
        </div>
        """

    if keyphrase_html:
        card_html += f"""
        <div style="margin-bottom:18px;">
            <div style="font-weight:700;color:#111827;margin-bottom:10px;font-size:1rem;display:flex;align-items:center;gap:6px;">🔑 Key Phrases</div>
            <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px;">{keyphrase_html}</div>
        </div>
        """

    if url and url != "#":
        card_html += f"""
        <a href="{url}" target="_blank" style="display:inline-flex;align-items:center;gap:10px;color:#4338ca;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:12px;background:rgba(102,126,234,0.1);transition:all 0.2s ease;border:1px solid rgba(102,126,234,0.2);">
            <span>🔗 Read Full Article</span>
            <span style="font-size:1.2rem;">→</span>
        </a>
        """
    
    card_html += "</div>"  # Close article card div
    card_html += "</div>"  # Close wrapper div
    
    # Add JavaScript for expand/collapse
    card_html += """
    <script>
    function toggleExpand(cardId) {
        const previewDiv = document.getElementById(cardId + '-summary-preview');
        const fullDiv = document.getElementById(cardId + '-summary-full');
        const toggleBtn = document.getElementById(cardId + '-toggle-btn');
        
        if (previewDiv.style.display === 'none') {
            previewDiv.style.display = 'block';
            fullDiv.style.display = 'none';
            toggleBtn.innerHTML = '▼ Show More';
        } else {
            previewDiv.style.display = 'none';
            fullDiv.style.display = 'block';
            toggleBtn.innerHTML = '▲ Show Less';
        }
    }
    </script>
    """
    
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
        if st.button("🚀 Analyze with AI", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            steps_container = st.container()

            try:
                # Step 1: Fetch & Rank
                status_placeholder.info(
                    "Step 1/3 · Fetching and ranking latest financial news..."
                )
                progress_bar.progress(5)

                fetch_response = requests.post(
                    f"{API_BASE_URL}/api/fetch-and-rank",
                    json={"company_name": selected_company},
                    timeout=90,
                )

                if fetch_response.status_code != 200:
                    status_placeholder.error(
                        f"❌ Step 1 failed: {fetch_response.status_code}"
                    )
                    st.code(fetch_response.text)
                    progress_bar.progress(0)
                    st.stop()

                fetch_data = fetch_response.json()
                ranked_articles = fetch_data.get("articles", [])

                progress_bar.progress(25)

                with steps_container:
                    step1_section = st.container()
                    step1_section.markdown("### ✅ Step 1 · Fetch & Rank")
                    step1_cols = step1_section.columns(4)
                    step1_cols[0].metric("Articles Retrieved", len(ranked_articles))
                    step1_cols[1].metric(
                        "Pipeline Status",
                        fetch_data.get("status", "success").upper(),
                    )
                    if ranked_articles:
                        latest_date = extract_article_date(ranked_articles[0], "N/A")
                        step1_cols[2].metric("Latest Article", latest_date)
                        step1_cols[3].metric(
                            "Top Rank Score",
                            f"{ranked_articles[0].get('rank_score', 0):.3f}",
                        )
                    else:
                        step1_cols[2].metric("Latest Article", "N/A")
                        step1_cols[3].metric("Top Rank Score", "0.000")

                    if ranked_articles:
                        preview_rows = []
                        for art in ranked_articles[:15]:
                            preview_rows.append(
                                {
                                    "Headline": art.get("headline")
                                    or art.get("title", "Unknown"),
                                    "Source": art.get("source", "Unknown"),
                                    "Rank Score": round(art.get("rank_score", 0), 3),
                                    "Publish Date": extract_article_date(art),
                                }
                            )
                        step1_section.dataframe(pd.DataFrame(preview_rows))
                    else:
                        step1_section.warning(
                            "No articles returned from fetch-and-rank endpoint."
                        )

                status_placeholder.info(
                    "Step 2/3 · Running AI sentiment analysis and similarity expansion..."
                )
                progress_bar.progress(45)

                enrich_response = requests.post(
                    f"{API_BASE_URL}/api/enrich-with-ai",
                    json={"company_name": selected_company},
                    timeout=240,
                )

                if enrich_response.status_code != 200:
                    status_placeholder.error(
                        f"❌ Step 2 failed: {enrich_response.status_code}"
                    )
                    st.code(enrich_response.text)
                    progress_bar.progress(0)
                    st.stop()

                ai_data = enrich_response.json()
                result_data = ai_data.get("articles", [])
                sentiment_stats = ai_data.get("sentiment_stats", {})

                progress_bar.progress(75)

                # Display Step 2 immediately after AI enrichment completes
                # Use steps_container to ensure it renders immediately after Step 1
                with steps_container:
                    st.markdown("### ✅ Step 2 · AI Sentiment Synthesis")
                    sentiment_counts = {
                        "positive": sentiment_stats.get("positive", 0),
                        "negative": sentiment_stats.get("negative", 0),
                        "neutral": sentiment_stats.get("neutral", 0),
                    }
                    total_phrases = sentiment_stats.get("total_keyphrases", 0)
                    
                    metric_cols = st.columns(4)
                    metric_cols[0].metric("Positive", sentiment_counts["positive"], delta="🟢")
                    metric_cols[1].metric("Negative", sentiment_counts["negative"], delta="🔴")
                    metric_cols[2].metric("Neutral", sentiment_counts["neutral"], delta="⚪")
                    metric_cols[3].metric("Keyphrases", total_phrases, delta="🔑")

                    if result_data:
                        sentiment_timeline = []
                        for idx, art in enumerate(result_data[:15], 1):
                            sent_type, reason = parse_sentiment(
                                art.get("predicted_sentiment", "")
                            )

                            sentiment_timeline.append(
                                {
                                    "Rank": idx,
                                    "Sentiment": sent_type.title(),
                                    "Headline": art.get("headline")
                                    or art.get("title", "Unknown"),
                                    "Reason": (
                                        reason[:120] + "..."
                                        if len(reason) > 120
                                        else reason
                                    ),
                                }
                            )
                        st.dataframe(pd.DataFrame(sentiment_timeline))
                    else:
                        st.warning("No articles available for sentiment analysis.")

                status_placeholder.info(
                    "Step 3/3 · Aggregating keyphrases and generating intelligence report..."
                )
                progress_bar.progress(90)

                # Aggregate keyphrases
                positive_phrases = Counter()
                negative_phrases = Counter()
                neutral_phrases = Counter()

                for article in result_data:
                    kp = article.get("keyphrase_analysis", {}).get("keyphrases", {})
                    for item in kp.get("positive", []):
                        positive_phrases[item.get("phrase", "")] += item.get(
                            "confidence", 0
                        )
                    for item in kp.get("negative", []):
                        negative_phrases[item.get("phrase", "")] += item.get(
                            "confidence", 0
                        )
                    for item in kp.get("neutral", []):
                        neutral_phrases[item.get("phrase", "")] += item.get(
                            "confidence", 0
                        )

                # Display Step 3 in the same steps_container
                with steps_container:
                    st.markdown("### ✅ Step 3 · Keyphrase Intelligence")

                    if positive_phrases or negative_phrases or neutral_phrases:
                        phrase_cols = st.columns(3)

                        if positive_phrases:
                            pos_df = pd.DataFrame(
                                positive_phrases.most_common(10),
                                columns=["Phrase", "Confidence"],
                            )
                            phrase_cols[0].markdown("#### 🟢 Bullish Signals")
                            phrase_cols[0].table(pos_df)

                        if negative_phrases:
                            neg_df = pd.DataFrame(
                                negative_phrases.most_common(10),
                                columns=["Phrase", "Confidence"],
                            )
                            phrase_cols[1].markdown("#### 🔴 Bearish Signals")
                            phrase_cols[1].table(neg_df)

                        if neutral_phrases:
                            neu_df = pd.DataFrame(
                                neutral_phrases.most_common(10),
                                columns=["Phrase", "Confidence"],
                            )
                            phrase_cols[2].markdown("#### ⚪ Neutral Themes")
                            phrase_cols[2].table(neu_df)
                    else:
                        st.warning("No keyphrases extracted from analyzed articles.")

                progress_bar.progress(100)
                status_placeholder.success("All steps completed successfully! 🎉")

                # Final article cards - displayed at the bottom with 2-column grid
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
                    download_payload = json.dumps(
                        result_data,
                        indent=2,
                        ensure_ascii=False,
                    )
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
                else:
                    st.warning("No enriched articles available from the AI analysis.")

            except requests.exceptions.Timeout:
                status_placeholder.error(
                    "⏱️ One of the requests timed out. Please try again."
                )
                progress_bar.progress(0)
            except Exception as e:
                status_placeholder.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)
                progress_bar.progress(0)
else:
    st.warning("⚠️ Unable to fetch companies. Make sure the API server is running.")
    st.code("python3 server.py", language="bash")
    st.info("💡 The API should be running at http://localhost:8000")
