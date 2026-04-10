from __future__ import annotations

import streamlit as st

from app.rag_core import answer_question, get_service

st.set_page_config(
    page_title="GEM Arabic QA",
    page_icon="🏛️",
    layout="wide",
)


@st.cache_resource
def load_service():
    return get_service()


load_service()

st.title("🏛️ نظام سؤال وجواب للمتحف المصري الكبير")
st.caption("يعتمد فقط على الصفحات الرسمية العربية للمتحف المصري الكبير")

with st.container():
    question = st.text_area(
        "اكتب سؤالك بالعربية",
        height=120,
        placeholder="مثال: ما المرافق المتاحة في المتحف المصري الكبير؟",
    )
    submit = st.button("إرسال السؤال", use_container_width=True)

if submit:
    if not question.strip():
        st.warning("من فضلك اكتب سؤالًا بالعربية.")
    else:
        with st.spinner("جارٍ استرجاع المعلومات والإجابة..."):
            result = answer_question(question)

        st.subheader("الإجابة")
        st.write(result["answer"])

        st.subheader("المصادر")
        sources = result.get("sources", [])
        if not sources:
            st.info("لا توجد مصادر معروضة.")
        else:
            for i, src in enumerate(sources, start=1):
                with st.container(border=True):
                    st.markdown(f"**المصدر {i}**")
                    st.write(f"**عنوان الصفحة:** {src.get('page_title') or '—'}")
                    st.write(f"**عنوان القسم:** {src.get('section_title') or '—'}")
                    st.write(f"**الرابط:** {src.get('source_url') or '—'}")
