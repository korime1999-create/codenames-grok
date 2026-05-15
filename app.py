import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime

from groq import Groq

st.set_page_config(page_title="Generation G", layout="wide")

st.title("🕵️‍♂️ Generation G")
st.markdown("**GenevieveAi для Коднеймс**")

# ====================== ВЫБОР КОМАНДЫ ======================
st.markdown("### 🎯 За какую команду работаем?")
team_color = st.radio(
    label="Выберите команду",
    options=["🔵 Синие", "🔴 Красные"],
    horizontal=True,
    label_visibility="collapsed"
)

# ====================== SESSION STATE ======================
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "good_hints" not in st.session_state:
    st.session_state.good_hints = []
if "bad_hints" not in st.session_state:
    st.session_state.bad_hints = []
if "guessed_words_list" not in st.session_state:
    st.session_state.guessed_words_list = []

# ====================== UPLOAD ======================
uploaded_file = st.file_uploader("Загрузи скриншот доски", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)

    api_key = st.text_input("Groq API Key", type="password")

    guessed_input = st.text_input(
        "Уже отгаданные слова (через запятую)", 
        value=", ".join(st.session_state.guessed_words_list)
    )
    
    if guessed_input:
        st.session_state.guessed_words_list = [w.strip().lower() for w in guessed_input.split(",") if w.strip()]

    if st.button("🚀 Проанализировать доску", type="primary", use_container_width=True):
        if not api_key:
            st.error("Введите Groq API Key")
            st.stop()

        with st.spinner("Думаю как топ-мастер..."):
            try:
                client = Groq(api_key=api_key)

                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{base64_image}"

                guessed_str = ", ".join(st.session_state.guessed_words_list)

                system_prompt = f"""Ты — Genevieve, очень сильный и креативный спаймастер Коднеймс.
Ты играешь за {team_color} команду."""

                user_prompt = f"""Проанализируй скриншот доски Коднеймс.
- Шифр должен иметь **очень понятную и сильную связь** с несколькими словами своей команды.
- Обязательно указывай конкретные слова, которые должны взять игроки.
- Избегай банальных и слабых объяснений.
- Если связь слабая — лучше не предлагай такой шифр.

**
Дополнительные требования к тебе:
primary_words — это слова, которые игроки должны взять первыми (самые очевидные).
Всегда пиши реальную логику, почему этот шифр работает.
Не придумывай натянутые связи.
Предпочитай конкретные шифры (типа "Гром", "Охота") только если они действительно сильные.
Предложи 7–8 сильных шифров.
Перепроверяй по семь раз свои слова и их действительную связь предложенным шифром.
Категорически нельзя использовать однокоренные.
Обязательно используй множественное число, если есть 2+ слов категории загадываемых слов.
Используй приставки и склонения.
Не повторяйся. 
Загадыйвай только слова своей команды.
Белые не загадывай.
Объясняй каждое слово. Старайся не задевать чужие слова первоочередно.
Используй креативные интересные загадывания.
Сразу называй шифр, цифру и слова которые ты загадываешь, если нулишь, какое нулишь, если подходят чужие слова, имей ввиду, что пересечения должны браться позже твоих собственных.
Переходи сразу к шифру и цифре, затем краткое объяснение того, что загадано и логика описуемо каждого загаданного слова в порядке, в котором их будут брать."""
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]}
                    ],
                    temperature=0.5,
                    max_tokens=4000
                )

                result_text = response.choices[0].message.content

                analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.analyses.append({
                    "id": analysis_id,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "model": "Llama 4 Scout",
                    "team": team_color,
                    "result": result_text
                })

                st.success("✅ Анализ готов!")
                st.markdown("### 🎯 Рекомендуемые шифры")
                st.markdown(result_text)

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:700]}")

# ====================== ФИДБЕК ======================
if st.session_state.good_hints or st.session_state.bad_hints:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👍 Хорошие")
        for h in st.session_state.good_hints[-10:]:
            st.success(h)
    with col2:
        st.subheader("👎 Плохие")
        for h in st.session_state.bad_hints[-10:]:
            st.error(h)

st.caption("Generation G • GenevieveAi for Codenames")
