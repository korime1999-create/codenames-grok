import streamlit as st
from PIL import Image
import easyocr
import numpy as np
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер (бесплатно)")

st.markdown("**Лучший помощник для Коднеймса**")

# ====================== ВВОД СЛОВ ======================
tab1, tab2 = st.tabs(["📝 Ввести текст", "📸 Загрузить скриншот"])

words_input = ""

with tab1:
    words_input = st.text_area(
        "Вставь все 25 слов с доски:", 
        height=180, 
        placeholder="стоматолог, врач, медведь, прыжок, ведьма..."
    )

with tab2:
    uploaded_file = st.file_uploader("Загрузи скриншот доски", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Загруженный скриншот", use_column_width=True)
        
        if st.button("🔍 Распознать слова (OCR)"):
            with st.spinner("Распознавание текста..."):
                try:
                    reader = easyocr.Reader(['ru', 'en'], gpu=False)
                    result = reader.readtext(np.array(image), detail=0)
                    
                    extracted = [text.strip().lower() for text in result if len(text.strip()) > 2]
                    words_input = ", ".join(extracted)
                    st.success(f"✅ Распознано {len(extracted)} слов!")
                    st.write("Распознанные слова:", words_input)
                except Exception as e:
                    st.error(f"Ошибка распознавания: {e}")

# ====================== ОСНОВНАЯ ЛОГИКА ======================
if not words_input:
    st.info("Введи слова или загрузи скриншот")
    st.stop()

words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
board = list(dict.fromkeys(words))

st.success(f"✅ Загружено **{len(board)}** слов")

# Категории
groups_text = ""
for cat_key, cat_name in CATEGORY_NAMES.items():
    found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
    if found:
        groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

# ====================== СОСТОЯНИЕ СТОЛА ======================
st.subheader("🎨 Состояние доски")

team = st.radio("Ты играешь за:", ["🔵 Синие", "🔴 Красные"], horizontal=True)

if "board_state" not in st.session_state:
    st.session_state.board_state = {}

cols = st.columns(5)
for i, word in enumerate(board):
    with cols[i % 5]:
        status = st.selectbox(
            word.capitalize(),
            ["Не открыто", "✅ Моё (открыто)", "❌ Чужое (открыто)", "☠️ Чёрный"],
            key=f"status_{i}"
        )
        st.session_state.board_state[word] = status

# ====================== КЛЭЙМ ======================
st.subheader("🗣️ Клэйм")
claim = st.text_input("Твой клэйм (если нужно оспорить предыдущий шифр)", 
                      placeholder="Не согласен с 'животноводы' — там только 4...")

# ====================== ПРОМПТ ======================
api_key = st.text_input("Groq API Key", type="password", help="console.groq.com")

if st.button("🚀 Сгенерировать шифры", type="primary", use_container_width=True):
    if not api_key:
        st.error("Введи Groq API Key")
        st.stop()

    # Состояние доски
    my_opened = [w for w, s in st.session_state.board_state.items() if "Моё" in s]
    opp_opened = [w for w, s in st.session_state.board_state.items() if "Чужое" in s]
    black_taken = any("Чёрный" in s for s in st.session_state.board_state.values())

    state_info = f"""
Моя команда ({team}): {len(my_opened)} открыто → {', '.join(my_opened) if my_opened else 'ничего'}
Противник: {len(opp_opened)} открыто → {', '.join(opp_opened) if opp_opened else 'ничего'}
Чёрная карточка: {'взята' if black_taken else 'ещё нет'}
"""

    prompt = f"""Ты — лучший спаймастер в русскоязычном Коднеймсе. Идеально знаешь правила, тактики, нуление и клэймы.

Слова на доске: {', '.join(sorted(board))}

Категории:
{groups_text}

{state_info}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
- Шифр — **только одно слово** или **слово через дефис** (животноводы, скотоводы, ведьмы, человек-паук, баба-яга).
- Нельзя использовать слова с доски.
- Можно использовать "0" (нулевой шифр).
- Можно использовать феминитивы и грамматические приёмы русского языка.

Стратегия:
- В первую очередь — самые большие группы (5+ слов).
- Для животных + людей: животноводы, скотоводы, фермеры, зоологи, ветеринары.
- Учитывай уже открытые слова.

Выдай 6–7 лучших шифров, начиная с самого сильного.

Формат строго:
**Шифр: "слово" — на N → слово1, слово2, слово3...**
Короткое объяснение (1 предложение).

Начинай сразу."""

    with st.spinner("ИИ думает..."):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.75,
                max_tokens=1300
            )
            
            st.markdown("### 🎯 Рекомендуемые шифры:")
            st.markdown(response.choices[0].message.content)
            
            if claim:
                st.info(f"**Твой клэйм:** {claim}")
                
        except Exception as e:
            st.error(f"Ошибка Groq: {e}")

# ====================== ВСЕ СЛОВА ======================
with st.expander("Все слова на доске"):
    st.write(", ".join(sorted(board)))
