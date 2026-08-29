import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from ingest import ingest_pdf
from search import search_documents
from generator import generate_answer
from vector_store import get_collection, list_sources, delete_document


st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS — MODERN TEMA
# =========================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #f7f8fc 0%, #ffffff 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #14142b;
    }
    section[data-testid="stSidebar"] * {
        color: #e8e8f5 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: #4d4dff;
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #2c2c4a;
    }

    /* Header */
    .hero {
        padding: 8px 0 28px 0;
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #4d4dff, #7b5cff);
        color: white;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 14px;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 46px;
        font-weight: 800;
        color: #16162b;
        margin: 0 0 6px 0;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 17px;
        color: #6b6b85;
        font-weight: 500;
        margin-bottom: 0;
    }

    /* Stat pill */
    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: white;
        border: 1px solid #e6e6f0;
        padding: 10px 18px;
        border-radius: 14px;
        font-size: 14px;
        font-weight: 600;
        color: #33334d;
        box-shadow: 0 2px 10px rgba(20,20,60,0.04);
        margin-bottom: 24px;
    }

    /* Question card */
    .question-card {
        background: white;
        border: 1px solid #ececf5;
        border-radius: 20px;
        padding: 28px 30px;
        box-shadow: 0 4px 24px rgba(20,20,60,0.05);
        margin-bottom: 24px;
    }
    .section-label {
        font-size: 13px;
        font-weight: 700;
        color: #4d4dff;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }

    .stTextInput input {
        border-radius: 12px !important;
        border: 1.5px solid #e6e6f0 !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    .stTextInput input:focus {
        border-color: #4d4dff !important;
        box-shadow: 0 0 0 3px rgba(77,77,255,0.12) !important;
    }

    .stButton button {
        background: linear-gradient(90deg, #4d4dff, #7b5cff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 700;
        font-size: 15px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 4px 14px rgba(77,77,255,0.25);
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(77,77,255,0.35);
    }

    /* Answer card */
    .answer-card {
        background: linear-gradient(135deg, #f4f4ff 0%, #fbfbff 100%);
        border: 1px solid #e0e0ff;
        border-radius: 20px;
        padding: 28px 30px;
        margin-top: 8px;
        margin-bottom: 24px;
        position: relative;
    }
    .answer-card-title {
        font-size: 14px;
        font-weight: 700;
        color: #4d4dff;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .answer-text {
        font-size: 18px;
        color: #16162b;
        font-weight: 500;
        line-height: 1.65;
        white-space: pre-wrap;
    }

    /* Sources */
    .sources-label {
        font-size: 15px;
        font-weight: 700;
        color: #16162b;
        margin: 20px 0 12px 0;
    }

    .doc-pill {
        background: #f4f4ff;
        border: 1px solid #e0e0ff;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #33334d;
    }

    div[data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid #ececf5 !important;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Yerel &nbsp;·&nbsp; Güvenli &nbsp;·&nbsp; RAG Tabanlı</div>
        <div class="hero-title">📚 DocuMind</div>
        <div class="hero-subtitle">Belgelerinizi yükleyin, yapay zekâ ile içerikleri hakkında sorular sorun.</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR — Belge Yönetimi
# =========================================================

with st.sidebar:
    st.markdown("### 📄 Belgeler")
    st.caption("PDF yükleyin ve sisteme ekleyin")

    uploaded_file = st.file_uploader("PDF seç", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.button("📥 Belgeyi Ekle", use_container_width=True):
            temp_dir = Path("data/uploads")
            temp_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = temp_dir / uploaded_file.name

            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                with st.spinner("PDF işleniyor..."):
                    ingest_pdf(str(pdf_path))
                st.success(f"{uploaded_file.name} eklendi.")
                st.rerun()
            except Exception as e:
                st.error(f"Hata:\n{e}")

    st.divider()
    st.markdown("### 🗂️ Yüklü Belgeler")

    try:
        sources = list_sources()
    except Exception:
        sources = []

    if not sources:
        st.caption("Henüz belge yüklenmedi.")
    else:
        for source in sources:
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"📘 **{source}**")
            if col2.button("🗑️", key=f"del_{source}"):
                delete_document(source)
                st.rerun()


# =========================================================
# VERİTABANI DURUMU
# =========================================================

try:
    chunk_count = get_collection().count()
    doc_count = len(list_sources())
    st.markdown(
        f'<div class="stat-pill">📊 &nbsp;{doc_count} belge &nbsp;·&nbsp; {chunk_count} parça indekslendi</div>',
        unsafe_allow_html=True
    )
except Exception as e:
    st.warning(f"Veritabanı henüz hazır değil: {e}")


# =========================================================
# SORU KARTI
# =========================================================

st.markdown('<div class="question-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">💬 Sorunuzu Sorun</div>', unsafe_allow_html=True)

col_q, col_btn = st.columns([5, 1])

with col_q:
    question = st.text_input(
        "Sorunuz",
        placeholder="Örneğin: Staj süresi kaç iş günüdür?",
        label_visibility="collapsed"
    )

with col_btn:
    answer_button = st.button("✓ Cevapla", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# CEVAP
# =========================================================

if answer_button:
    if not question.strip():
        st.warning("Lütfen önce bir soru yazın.")
    else:
        with st.spinner("Belgeler aranıyor..."):
            try:
                results = search_documents(question, n_results=5)
            except Exception as e:
                st.error(f"Arama sırasında hata oluştu:\n{e}")
                results = []

        if not results:
            st.warning("Sorunuzla ilgili belge bulunamadı.")
        else:
            with st.spinner("Cevap hazırlanıyor..."):
                try:
                    answer = generate_answer(question, results)
                except Exception as e:
                    st.error(f"Cevap oluşturulurken hata oluştu:\n{e}")
                    answer = None

            if answer:
                st.markdown(
                    f"""
                    <div class="answer-card">
                        <div class="answer-card-title">🤖 DocuMind'in Cevabı</div>
                        <div class="answer-text">{answer}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div class="sources-label">📑 Kullanılan Kaynaklar</div>', unsafe_allow_html=True)

                for i, result in enumerate(results, 1):
                    text = result.get("text", "")
                    score = result.get("score", 0)
                    source = result.get("metadata", {}).get("source", "Bilinmeyen")
                    page = result.get("metadata", {}).get("page", "")

                    with st.expander(f"📄 Kaynak {i} — {source} (Sayfa {page})  ·  Skor: {score:.3f}"):
                        st.write(text)