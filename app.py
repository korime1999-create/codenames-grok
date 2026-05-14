import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime

from categories import CATEGORIES, CATEGORY_NAMES, get_categories, get_primary_category
from groq import Groq

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Продвинутый Спаймастер Коднеймс v2.6")
st.markdown("**Правильное использование ед./мн. числа + механика 0**")

# Session State
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Sidebar
with st.sidebar:
    st.header("⚙️ Настройки")
    team_color = st.radio("Твоя команда:", ["🔵 Синие", "🔴 Красные"], horizontal=True)
    team = "blue" if "Синие" in team_color else "red"
    
    model_options = {
        "Llama 4 Scout (рекомендуется)": "meta-llama/llama-4-scout-17b-16e-instruct",
    }
    selected_model_name = st.selectbox("Модель:", list(model_options.keys()))
    model = model_options[selected_model_name]
    
    temperature = st.slider("Температура", 0.1, 0.6, 0.25, 0.05)

# Main
uploaded_file = st.file_uploader("Загрузи скриншот доски", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)

    api_key = st.text_input("Groq API Key", type="password")
    guessed_words = st.text_input("Уже отгаданные слова (через запятую)", 
                                 value="солнце, мастер, битва")

    if st.button("🚀 Проанализировать доску", type="primary", use_container_width=True):
        if not api_key:
            st.error("Введите Groq API Key")
            st.stop()

        with st.spinner("Анализирую..."):
            try:
                client = Groq(api_key=api_key)

                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

                system_prompt = f"""Ты — сильный спаймастер Коднеймс.
Правильно используй единственное и множественное число."""

                user_prompt = f"""Это доска Коднеймс. Твоя команда: {team.upper()}.
Уже отгаданы: {guessed_words if guessed_words else "нет"}.

**Важные правила русского Коднеймса:**

- Множественное число ("Одежды", "Клубники", "Места", "Профессии") = шифр на 2 и больше слов одной категории.
- Единственное число ("Одежда", "Клубника") = когда в категории одно слово.
- "Слово (в ед.ч.) 0" (например, "Паровоз 0", "Котлета 0") = взять все слова зануленной категории кроме самого очевидного, которым обычно бывает вражеское слово или черное.
- "Слово (во мн.ч.) 0" (например "Одежды 0", "Клубники 0") = взять несколько слов этой связи, **кроме двух самых очевидных**.
- Предпочитай конкретные сильные слова + 0 ("Штаны 0", "Насос 0"), когда это возможно.
- Категорию во множественном числе используй только при хорошей большой группе твоих слов и когда нет черного.
- Знай, что когда пишешь "(Категории в мн.ч.) 7+", то тебе будут брать слова этой категории, если их много слева направо сверху вниз. Так что это может стать подспорьем для тактики. Загадать при разноцвете (Слова одной категории принадлежат разным цветам на поле), чтобы команда уперлась в белое слово (если взять белое слово, команда пропускает ход).

Предложи 6–8 лучших шифров.

Ответ строго в JSON:
{{
  "hints": [
    {{
      "cipher": "Одежды",
      "number": 0,
      "words": "брюки, костюм",
      "explanation": "Одежды 0 — берём одежду кроме самого очевидного"
    }}
  ]
}}"""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    temperature=temperature,
                    max_tokens=2800,
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)

                analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.analyses.append({
                    "id": analysis_id,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "model": selected_model_name,
                    "team": team,
                    "result": result,
                    "feedback": None
                })

                st.success("✅ Готово!")

                st.markdown("### 🎯 Рекомендуемые шифры")
                for i, hint in enumerate(result.get("hints", [])[:8]):
                    with st.container(border=True):
                        st.markdown(f"**{hint.get('cipher')}** — на **{hint.get('number')}** → {hint.get('words')}")
                        st.caption(hint.get('explanation', ''))
                        
                        col1, col2 = st.columns(2)
                        col1.button("👍 Хорошо", key=f"good_{i}_{analysis_id}")
                        col2.button("👎 Плохо", key=f"bad_{i}_{analysis_id}")

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:700]}")

# История
if st.session_state.analyses:
    st.divider()
    st.subheader("📖 История")
    for a in reversed(st.session_state.analyses[-6:]):
        with st.expander(f"{a['timestamp']} — {a['model']}"):
            st.json(a["result"], expanded=False)

st.caption("Grok Коднеймс v2.6 • Правильное ед./мн. число")
