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

    

 prompt = f"""Ты лучший спаймастер в мире в Коднеймс. Твоя задача — выиграть как можно быстрее, давая большие и точные шифры.



Категории (используй их максимально):
{groups_text}

Ключевые правила (строго соблюдай):
- Приоритет — максимально большие группы (старайся находить связи на 5+ слов, идеально 6-8).
- Сначала ищи самые крупные возможные пересечения по категориям.
- Для людей/профессий: ищи общую сферу, черту характера, известного представителя, стереотип, фильм/книгу, а не просто "ещё один человек".
- Для совокупностей (врачи, овощи, животные, инструменты и т.д.) используй сильные объединяющие слова: "специалисты", "продукты", "фауна", "семья" и т.п. — но только если связь действительно сильная.
- Никогда не используй слова с доски (даже в склонении).
- Склоняй правильно, используй русский язык естественно.
- Избегай слишком очевидных и слабых связей, которые могут зацепить слова противника.

Стратегия:
1. Найди 1–2 самые большие возможные группы.
2. Затем группы поменьше (3–5).
3. В конце — одиночки, если нужно.

Выдай ровно 5–7 лучших шифров, отсортированных от самого сильного (самой большой группы) к меньшим.

Формат строго:
**Шифр: "ключевое_слово" — на N → слово1, слово2, слово3...**
Короткое, но точное объяснение, почему эта связь работает.

Начинай сразу с первого шифра, без вступлений."""

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
