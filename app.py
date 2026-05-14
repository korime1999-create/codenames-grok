import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok - Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Идеальный Спаймастер для Коднеймс")

st.write("**Твоя личная система с категориями**")

# Ввод слов
words_input = st.text_area("Вставь все 25 слов с доски (через запятую или по одному в строке)", height=200)

if st.button("Анализировать доску"):
    if words_input:
        # Очистка
        words = [w.strip().lower() for w in words_input.replace(',', '\n').split('\n') if w.strip()]
        words = list(dict.fromkeys(words))  # убираем дубли
        
        st.success(f"Загружено {len(words)} слов")
        
        # Показываем категории
        st.subheader("Найденные категории:")
        for cat_key, cat_name in CATEGORY_NAMES.items():
            found = [w for w in words if w in CATEGORIES.get(cat_key, [])]
            if found:
                st.write(f"**{cat_name}**: {', '.join(found)}")
