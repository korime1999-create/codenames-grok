import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Generation G", layout="wide")

st.title("🕵️‍♂️ Generation G")
st.markdown("**GenevieveAi для Коднеймс**")

# ====================== SESSION STATE ======================
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "good_hints" not in st.session_state:
    st.session_state.good_hints = []
if "bad_hints" not in st.session_state:
    st.session_state.bad_hints = []
if "guessed_words_list" not in st.session_state:
    st.session_state.guessed_words_list = ["солнце", "мастер", "битва"]

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Настройки")
    team_color = st.radio("🎯 За какую команду играешь?", 
                         ["🔵 Синие", "🔴 Красные"], horizontal=True)
    team = "blue" if "Синие" in team_color else "red"
    enemy = "Красные" if team == "blue" else "Синие"
    
    model_options = {
        "Llama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    }
    selected_model_name = st.selectbox("Модель:", list(model_options.keys()))
    model = model_options[selected_model_name]
    
    temperature = st.slider("Температура", 0.1, 0.55, 0.35, 0.05)

# ====================== MAIN ======================
uploaded_file = st.file_uploader("Загрузи скриншот доски", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)

    api_key = st.text_input("Groq API Key", type="password")

    guessed_input = st.text_input(
        "Уже отгаданные слова (через запятую)", 
        value=", ".join(st.session_state.guessed_words_list)
    )
    
    if guessed_input:
        st.session_state.guessed_words_list = [w.strip() for w in guessed_input.split(",") if w.strip()]

    if st.button("🚀 Проанализировать доску", type="primary", use_container_width=True):
        if not api_key:
            st.error("Введите Groq API Key")
            st.stop()

        with st.spinner("Генерирую шифры..."):
            try:
                from groq import Groq
                client = Groq(api_key=api_key)

                # Подготовка изображения
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{base64_image}"

                guessed_str = ", ".join(st.session_state.guessed_words_list)

                system_prompt = f"""Ты — Genevieve, один из лучших спаймастеров в мире Коднеймс.
Ты играешь за {team_color}. Враг — {enemy}.
Ты агрессивна, креативна и стратегически очень сильна. Твоя цель — закрывать по 8–10 слов за 2–3 хода."""

                user_prompt = f"""Проанализируй скриншот доски Коднеймс и предложи лучшие шифры.

Уже отгаданы: {guessed_str if guessed_str else "ничего"}

**Строгие правила шифров (обязательно соблюдать):**
- Шифр состоит из одного слова + одного числа.
- ЗАПРЕЩЕНО использовать однокоренные слова (даже если они кажутся связанными). Нельзя использовать "порт" для "спорт", "воскресение" для "воскресенье" и т.д.
- Нельзя использовать слова с одинаковыми приставками/суффиксами, если связь только морфологическая.
- Нельзя использовать прямые переводы, если шифр на другом языке.
- "X 0" разрешён и очень желателен.

**Процесс мышления (обязательно следуй этому порядку):**
1. Внимательно изучи все слова на доске.
2. Найди все возможные смысловые группы (включая неочевидные и кросс-категорийные).
3. Оцени размер группы, силу связи и риск (ассасин + слова противника).
4. Выбери самые сильные варианты.

**Стратегия:**
- В приоритете группы на 4+ слов.
- Смело используй "X 0" для обнуления самого очевидного слова в сильной группе.
- Будь оригинальной и креативной.
- Максимально избегай риска попасть в ассассина.

Предложи **7–8 лучших шифров** в следующем JSON-формате:

```json
{{
  "analysis": "Краткий обзор доски: сильные группы в одежде, мифологии, технике и т.д.",
  "hints": [
    {{
      "cipher": "Галстук",
      "number": 0,
      "words": ["шарф", "галстук", "вышивка", "костюм"],
      "explanation": "Классический 'Галстук 0' — обнуляем самое очевидное, остальные слова должны зайти легко",
      "expected_hits": 3,
      "risk": 2,
      "style": "safe"
    }}
  ]
}}
```

Для каждого шифра обязательно указывай `risk` (от 1 до 10) и `style`: "safe", "balanced" или "aggressive".
"""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    temperature=temperature,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)

                # Сохранение анализа
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

                # Отображение результатов
                st.markdown("### 🎯 Рекомендуемые шифры")
                for i, hint in enumerate(result.get("hints", [])[:8]):
                    words_list = hint.get("words", [])
                    words_str = ", ".join(words_list) if isinstance(words_list, list) else str(words_list)

                    with st.container(border=True):
                        st.markdown(f"**{hint.get('cipher')}** — на **{hint.get('number')}** → {words_str}")
                        st.caption(hint.get('explanation', ''))
                        
                        col1, col2 = st.columns(2)
                        if col1.button("👍 Класс", key=f"good_{i}_{analysis_id}"):
                            hint_text = f"{hint.get('cipher')} {hint.get('number')}"
                            st.session_state.good_hints.append(hint_text)
                            st.success(f"Сохранено как хороший: {hint_text}")
                        if col2.button("👎 Не класс", key=f"bad_{i}_{analysis_id}"):
                            hint_text = f"{hint.get('cipher')} {hint.get('number')}"
                            st.session_state.bad_hints.append(hint_text)
                            st.error(f"Сохранено как плохой: {hint_text}")

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:700]}")

# ====================== ФИДБЕК ======================
if st.session_state.good_hints or st.session_state.bad_hints:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👍 Хорошие шифры")
        for h in st.session_state.good_hints[-12:]:
            st.success(h)
    with col2:
        st.subheader("👎 Плохие шифры")
        for h in st.session_state.bad_hints[-12:]:
            st.error(h)

# ====================== ИСТОРИЯ ======================
if st.session_state.analyses:
    st.divider()
    st.subheader("📖 История анализов")
    for a in reversed(st.session_state.analyses[-6:]):
        with st.expander(f"{a['timestamp']} — {a['model']}"):
            st.json(a["result"], expanded=False)

st.caption("Generation G • GenevieveAi for Codenames")

