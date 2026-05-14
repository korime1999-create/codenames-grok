import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер (бесплатно)")

st.markdown("**Вставь все 25 слов с доски**:")

words_input = st.text_area("", height=200, placeholder="стоматолог, врач, медведь, прыжок...")

api_key = st.text_input("Groq API Key", type="password", help="Вставь ключ с console.groq.com")

if st.button("🚀 Сгенерировать шифры с ИИ", type="primary", use_container_width=True):
    if not words_input:
        st.error("Вставь слова")
        st.stop()
    if not api_key:
        st.error("Введи Groq API Key")
        st.stop()

    words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
    board = list(dict.fromkeys(words))
    
    st.success(f"✅ Загружено {len(board)} слов")

    # Категории
    groups_text = ""
    for cat_key, cat_name in CATEGORY_NAMES.items():
        found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
        if found:
            groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

    prompt = f"""Ты лучший спаймастер в Коднеймс.
Слова на доске: {', '.join(sorted(board))}

Категории:
{groups_text}

Придумай 6–8 сильных шифров. Следуй правилам:
- Большие группы в приоритете
- Для людей — другой человек/профессия
- Избегай слов с доски
- Правильно склоняй (чувства, движения и т.д.)

Формат:
**Шифр: "слово" — на N → слово1, слово2...**
Короткое объяснение.

Начинай сразу."""

    with st.spinner("ИИ думает..."):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000
            )
            
            st.markdown("### 🎯 Рекомендуемые шифры:")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Ошибка: {e}")

    with st.expander("Все слова"):
        st.write(", ".join(sorted(board)))
