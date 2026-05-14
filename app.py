import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime
import os

# Импорт твоих категорий
from categories import CATEGORIES, CATEGORY_NAMES

from groq import Groq

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Продвинутый Спаймастер Коднеймс")
st.markdown("**Анализирует доску + использует твои категории + учится на отзывах**")

# ====================== SESSION STATE ======================
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Настройки")
    
    team_color = st.radio("Твоя команда:", ["🔵 Синие", "🔴 Красные"], horizontal=True)
    team = "blue" if "Синие" in team_color else "red"
    
    model_options = {
        "Llama 4 Scout (лучший сейчас)": "meta-llama/llama-4-scout-17b-16e-instruct",
        "Llama 4 Maverick": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "Llama 3.2 11B Vision": "llama-3.2-11b-vision-preview",
    }
    selected_model_name = st.selectbox("Модель:", list(model_options.keys()))
    model = model_options[selected_model_name]
    
    temperature = st.slider("Температура (креативность)", 0.1, 0.8, 0.35, 0.05)
    
    st.divider()
    st.info(f"Категорий загружено: **{len(CATEGORIES)}**")

# ====================== MAIN ======================
uploaded_file = st.file_uploader("Загрузи скриншот доски Коднеймс", 
                                type=["png", "jpg", "jpeg"], 
                                label_visibility="collapsed")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)

    api_key = st.text_input("Groq API Key", type="password", 
                           help="Можно задать через .env как GROQ_API_KEY")

    guessed_words = st.text_input("Уже отгаданные слова (через запятую)", 
                                 placeholder="солнце, мастер, битва")

    if st.button("🚀 Проанализировать и дать шифры", 
                 type="primary", 
                 use_container_width=True):
        
        if not api_key:
            st.error("Введите Groq API Key")
            st.stop()

        with st.spinner("ИИ анализирует доску..."):
            try:
                client = Groq(api_key=api_key)

                # Изображение → base64
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

                # Системный промпт с категориями
                system_prompt = f"""Ты — элитный спаймастер Коднеймс.
Ты отлично знаешь все категории из базы:

{CATEGORY_NAMES}

Твоя команда: {team.upper()}. Помогай ей выигрывать максимально быстро."""

                user_prompt = f"""Это текущая доска.

Уже отгаданные: {guessed_words if guessed_words else "ничего"}

Предложи 6–8 самых сильных шифров на сейчас.
Правила:
- Можно использовать "0" для того, чтобы команда не брала самое очевидное слово из категории и брала остальные.
- Можно использовать шифр во множественном числе для обозначения 2+ слов одной категории, но не делать этого, если слишком много слов этой категории не принадлежат твоей команде или если вреди них есть черное.
- "0" на шифр множественного числа нулит либо 2 слова одной категории если слов из этой категории много, либо одно слово и заданной категории и самое близкое по смыслу слово, если слов в этой категории на столе только 2 или меньше.
- Если команда пишет клэйм, то ты отвечаешь в первую очередь на него. Это значит любой твой ноль будет распространяться только на клэйм. А все слова зашаданные поверх будут рассматриваться только после того, как разберут клэйм.
- Клэйм всегда ранжирован. Например, если тебе пишут "Соль, перец, человек, сметана", а у тебя осталось неразгадано 8 слов, то если ты в шифре укажешь цифру 5, то ты перезагадешь 5 слов и тебе не возьмут сметану (8-5=3, три первых слова из клэйма).
- Ты можешь связывать категорию совокупности с любым шифром. Например, "перцев 3" это в первую очередь любая совокупность и две еды, которые больше всего подходят под перец.
- Ищи большие группы в первую очередь.
- Твоя задача победить в 2-3 хода, если ты ходишь первым. Или в 2 хода, если вторым.
- Такие шифры как "Банщика" могут подразумевать три категории: Человек, чувство/качество (что-то банщика, например, отзывчивасть, воля и тд), место (баня)

Начинай сразу с шифров."""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    temperature=temperature,
                    max_tokens=2200,
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)

                # Сохранение в историю
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

                # Вывод результатов
                st.markdown("### 🎯 Лучшие шифры")
                for i, hint in enumerate(result.get("hints", result.get("шифры", []))[:8]):
                    with st.container(border=True):
                        cipher = hint.get("cipher") or hint.get("шифр", "")
                        number = hint.get("number") or hint.get("число", "")
                        words = hint.get("words") or hint.get("слова", "")
                        explanation = hint.get("explanation") or hint.get("объяснение", "")
                        
                        st.markdown(f"**{cipher}** — на **{number}** → {words}")
                        st.caption(explanation)
                        
                        col1, col2 = st.columns(2)
                        if col1.button("👍 Хороший шифр", key=f"good_{i}_{analysis_id}"):
                            st.session_state.feedback[analysis_id] = "good"
                            st.success("Отзыв сохранён!")
                        if col2.button("👎 Не очень", key=f"bad_{i}_{analysis_id}"):
                            st.session_state.feedback[analysis_id] = "bad"
                            st.info("Спасибо за отзыв")

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:500]}")
                st.info("Проверь ключ и попробуй другую модель.")

# ====================== ИСТОРИЯ ======================
if st.session_state.analyses:
    st.divider()
    st.subheader("📖 История анализов")
    for analysis in reversed(st.session_state.analyses[-6:]):
        fb = analysis.get("feedback", "—")
        with st.expander(f"{analysis['timestamp']} — {analysis['model']} | Оценка: {fb}"):
            st.json(analysis["result"], expanded=False)

st.caption("Grok Коднеймс v2.2 • categories.py + Groq Vision + обучение на отзывах")
