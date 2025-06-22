import streamlit as st
import feedparser
import re
from datetime import datetime

st.set_page_config(page_title="AI Haber Akışı", page_icon="🤖", layout="wide")
st.title("🤖 AI / GenAI / ML Haber Akışı")
st.markdown("RSS kaynaklarından en güncel haberleri çek ve filtrele.")

# RSS kaynakları
rss_feeds = {
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "TechCrunch AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "ArXiv AI": "https://export.arxiv.org/rss/cs.AI",
    "ArXiv ML": "https://export.arxiv.org/rss/cs.LG",
    "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
    "OpenAI Blog": "https://openai.com/blog/rss/",
    "Towards Data Science": "https://towardsdatascience.com/feed",
}

# Sidebar ayarları
sources = list(rss_feeds.keys())
selected_sources = st.sidebar.multiselect("Kaynak seç:", options=sources, default=sources)

keywords = st.sidebar.text_input("Anahtar kelimeler (virgülle):", "AI,ML,GenAI,GPT")
keyword_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]

today = datetime.today().date()
start_date_input = st.sidebar.date_input("Tarih aralığı:", [today, today])

if isinstance(start_date_input, (list, tuple)) and len(start_date_input) == 2:
    start_date, end_date = start_date_input
else:
    start_date = start_date_input
    end_date = start_date_input

if start_date == end_date:
    start_date = datetime(2000, 1, 1).date()  # Tarih filtresini genişlet

max_items = st.sidebar.slider("Her kaynak için max haber:", 1, 20, 5)
show_date = st.sidebar.checkbox("Tarihi göster", value=True)
st.sidebar.markdown("---")

@st.cache_data(ttl=600)
def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries:
            entries.append({
                'title': entry.title,
                'link': entry.link,
                'published_parsed': entry.get('published_parsed', None),
                'summary': entry.get('summary', '')
            })
        return entries
    except Exception as e:
        st.error(f"RSS çekme hatası: {e}")
        return []

cols = st.columns(2)
idx = 0

for source in selected_sources:
    url = rss_feeds[source]
    with cols[idx]:
        st.subheader(source)
        with st.spinner(f"{source} çekiliyor..."):
            entries = fetch_feed(url)
        matched = []
        for entry in entries:
            entry_date = None
            if entry['published_parsed']:
                entry_date = datetime(*entry['published_parsed'][:6]).date()
            text = f"{entry['title']} {entry['summary']}".lower()
            if keyword_list and not any(re.search(rf"\b{k}\b", text) for k in keyword_list):
                continue
            if entry_date and (entry_date < start_date or entry_date > end_date):
                continue
            matched.append((entry, entry_date))
        if matched:
            for entry, entry_date in matched[:max_items]:
                if show_date and entry_date:
                    st.markdown(f"**[{entry['title']}]({entry['link']})**  *({entry_date.isoformat()})*")
                else:
                    st.markdown(f"**[{entry['title']}]({entry['link']})**")
                if entry['summary']:
                    st.markdown(entry['summary'], unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.write("Eşleşen haber yok.")
    idx = (idx + 1) % len(cols)
