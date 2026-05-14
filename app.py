import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES
from groq import Groq

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер (бесплатно через Groq)")

st.markdown("**Вставь все 25 слов с доски**:")

words_input = st.text_area("", height=200, placeholder="стоматолог, врач, медведь, прыжок, любовь, халат...")

api_key = st.text_input("Groq API Key", type="password", help="Бесплатный ключ с https://console.groq.com/keys")

if st.button("🚀 Сгенерировать шифры с помощью ИИ", type="primary", use_container_width=True):
    if not words_input:
        st.error("Вставь слова с доски")
        st.stop()
    
    if not api_key:
        st.error("Введи Groq API Key")
        st.stop()

    words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
    board = list(dict.fromkeys(words))
    
    st.success(f"✅ Загружено {len(board)} слов")

    # Категории для контекста
    groups_text = ""
    for cat_key, cat_name in CATEGORY_NAMES.items():
        found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
        if found:
            groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

    prompt = f"""Ты — лучший спаймастер в Коднеймс. Креативный, умный, с отличным чувством русского языка.

Слова на доске: {', '.join(sorted(board))}

Категории:
{groups_text}

Создай **6–8 сильных шифров**. 
Следуй моим правилам:
- Большие группы в приоритете (3+)
- если слов из одной категории 2+ то, мн. число этой категории
- Для людей — другой человек/профессия
- Для животных — зверь, хищник и т.д. 
- Для чувств — "чувства", "эмоции"
- Избегай слов, которые уже есть на доске
- Можно использовать неожиданные, но логичные ассоциации
- Используй разные конструкции и методы

Формат ответа:
**Шифр: "слово" — на N → слово1, слово2...**
Короткое объяснение.

Начинай сразу с шифров, без вступлений."""

    with st.spinner("Grok думает над шифрами... (обычно 5-12 секунд)"):
        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",   # одна из лучших бесплатных моделей
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_tokens=1200
            )
            
            result = response.choices[0].message.content
            st.markdown("### 🎯 Лучшие шифры:")
            st.markdown(result)
            
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
            st.info("Проверь, что ключ правильный и не истёк лимит.")

    with st.expander("Все слова на доске"):
        st.write(", ".join(sorted(board)))
