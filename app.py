import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime

from categories import CATEGORIES, CATEGORY_NAMES
from groq import Groq

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Продвинутый Спаймастер Коднеймс v3.1")
st.markdown("**Подробная механика 0 + агрессивный стиль**")

# ====================== SESSION STATE ======================
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "good_hints" not in st.session_state:
    st.session_state.good_hints = []
if "bad_hints" not in st.session_state:
    st.session_state.bad_hints = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Настройки")
    team_color = st.radio("🎯 За какую команду играешь?", 
                         ["🔵 Синие", "🔴 Красные"], 
                         horizontal=True)
    team = "blue" if "Синие" in team_color else "red"
    enemy = "Красные" if team == "blue" else "Синие"
    
    model_options = {
        "Llama 4 Scout (рекомендуется)": "meta-llama/llama-4-scout-17b-16e-instruct",
    }
    selected_model_name = st.selectbox("Модель:", list(model_options.keys()))
    model = model_options[selected_model_name]
    
    temperature = st.slider("Температура", 0.1, 0.55, 0.3, 0.05)

# ====================== MAIN ======================
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

                feedback_history = ""
                if st.session_state.good_hints:
                    feedback_history += "\nХорошие шифры ранее:\n" + "\n".join([f"- {h}" for h in st.session_state.good_hints[-5:]])
                if st.session_state.bad_hints:
                    feedback_history += "\nПлохие шифры (избегай):\n" + "\n".join([f"- {h}" for h in st.session_state.bad_hints[-5:]])

                system_prompt = f"""Ты — агрессивный и сильный спаймастер Коднеймс.
Ты играешь за {team_color} команду. Враги — {enemy}."""

                user_prompt = f"""Это скриншот доски Коднеймс.

Твоя команда: {team_color}
Вражеская команда: {enemy}
Уже отгаданы: {guessed_words if guessed_words else "нет"}

{feedback_history}

**Подробные правила, которые ты должен строго соблюдать:**

1. **Механика "0" (очень важно!)**  
   - "Штаны 0", "Одежды 0", "Насос 0" означает:  
     **Возьми все слова этой категории/связи, кроме самого очевидного.**  
   - 0 используется, чтобы пропустить самое кричащее/очевидное слово и взять остальные.

2. **Множественное число**  
   - "Одежды", "Ткани", "Клубники", "Места" — обозначает 2 и больше слов.

3. **Стиль игры**  
   - Ищи большие группы в первую очередь.  
   - Будь оригинальным и креативным.  
   - Предпочитай конкретные слова ("Штаны 0") перед общими категориями.

4. **Безопасность**  
   - Шифр должен быть выгоден твоей команде и относительно безопасен.

Предложи 6–8 сильных шифров.

**Ответ строго в JSON:**
```json
{{
  "hints": [
    {{
      "cipher": "Одежды",
      "number": 0,
      "words": "брюки, костюм, ремень",
      "explanation": "Одежды 0 — берём все слова одежды кроме самого очевидного (пропускаем самое кричащее)"
    }}
  ]
}}
```"""

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
                    max_tokens=3000,
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

                st.success("✅ Анализ готов!")

                st.markdown("### 🎯 Рекомендуемые шифры")
                for i, hint in enumerate(result.get("hints", [])[:8]):
                    hint_str = f"{hint.get('cipher')} — на {hint.get('number')} → {hint.get('words')}"
                    
                    with st.container(border=True):
                        st.markdown(f"**{hint.get('cipher')}** — на **{hint.get('number')}** → {hint.get('words')}")
                        st.caption(hint.get('explanation', ''))
                        
                        col1, col2 = st.columns(2)
                        if col1.button("👍 Класс", key=f"good_{i}_{analysis_id}"):
                            st.session_state.good_hints.append(hint_str)
                            st.success("Запомнил!")
                        if col2.button("👎 Не класс", key=f"bad_{i}_{analysis_id}"):
                            st.session_state.bad_hints.append(hint_str)
                            st.info("Запомнил как плохой")

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:700]}")

# ====================== ИСТОРИЯ ======================
if st.session_state.analyses:
    st.divider()
    st.subheader("📖 История")
    for a in reversed(st.session_state.analyses[-5:]):
        with st.expander(f"{a['timestamp']} — {a['model']}"):
            st.json(a["result"], expanded=False)

st.caption("Grok Коднеймс v3.1 • Подробное объяснение 0")
