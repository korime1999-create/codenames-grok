import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime
from pathlib import Path 

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

# ====================== ПАМЯТЬ ======================
FEEDBACK_FILE = Path("genevieve_memory.json")

if "memory" not in st.session_state:
    if FEEDBACK_FILE.exists():
        st.session_state.memory = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
    else:
        st.session_state.memory = {"good_examples": [], "bad_examples": []}
        
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

        with st.spinner("Анализирую доску..."):
            try:
                client = Groq(api_key=api_key)

                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{base64_image}"

                guessed_str = ", ".join(st.session_state.guessed_words_list)

                system_prompt = f"""Ты — Genevieve, топовый спаймастер Коднеймс.
Ты работаешь **строго** за {team_color} команду."""

                user_prompt = f"""Проанализируй скриншот доски Коднеймс.
- Шифр должен иметь **очень понятную и сильную связь** с несколькими словами своей команды.
- Обязательно указывай конкретные слова, которые должны взять игроки.
- Избегай банальных и слабых объяснений.
ПОЛЬЗУЙСЯ МУЛЬТИКУЛЬТУРНОЙ ОПОРОЙ. ИСПОЛЬЗУЙ СЛОЖНЫЕ УЗКОНАПРАВЛЕННЫЕ ЗАГАДЫВАНИЯ ДЛЯ МАКСИМАЛЬНО1 ЭФФЕКТИВНОСТИ.
ТЫ ДОЛЖНА ДЕЛАТЬ СИЛЬНЕЙШИЕ ЗАГАДЫВАНИЯ.
- Если связь слабая — лучше не предлагай такой шифр.
ЕСЛИ ТЫ ЗАГАДЫВАЕШЬ КРАСНЫЕ СЛОВА, ТО НЕ ИМЕЕШЬ ПРАВА ЗАГАДЫВАТЬ СИНИЕ И НАОБОРОТ.
ТЫ ДОЛЖНА ОЧЕНЬ ВНИМАТЕЛЬНО СМОТРЕТЬ НА ЦВЕТА КАРТОЧЕК!
# Формируем few-shot из памяти
few_shot = ""
if st.session_state.memory["good_examples"]:
    few_shot = "\n\n**Примеры сильных шифров из прошлого:**\n"
    for ex in st.session_state.memory["good_examples"][-4:]:
        few_shot += f"-\n"
Правила распознавания цветов на этой доске:
- **Ярко-синий фон** = слова {team_color} команды (наши)
- **Красный/оранжевый фон** = слова противника
- **Тёмно-серый/чёрный** = ассасин
- **Белый/светло-серый** = нейтральные (ещё не открытые)
Пользуйся категориями. 
ТВОИ ШИФРЫ ДОЛЖНЫ МИНИМАЛЬНО ЗАДЕЙСТВОВАТЬ ТРИ СЛОВА ТВОЕЙ КОМАНДЫ. ОЧЕВИДНО ЛОГИЧЕСКИ СВЯЗАННЫХ. ТРИ НЕ МЕНЬШЕ.
Если ты загадываешь человека загадывай через любого другого человека.
Если твой шифр плохо связывает 3-4+ слов = плохой шифр. Придумывай новый.
**
Обязательно перепроверяй принадлежат ли слова твоей команде. 
Твои шифры должны быть 3-4+ слов! Не меньше!!!
ТВОЯ РЕПУТАЦИЯ СТОИТ НА КОНУ.
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
Абсолютно все слова которые ты загадываешь и пишешь цифру обозначающее их количество, должны принадлежать твоей команде.
твое загадывание не должно распространяться более чем на одно слово вражеской команды.
Твой шифр не имеет права быть сильно связан с черным словом, потому что если его возьмут ты проиграешь.
Загадыйвай только слова своей команды.
Белые не загадывай.
Шифр может состоять исключительно из одного слова (можно через дефис) и одной цифры!!!
Если ты уже загадал слово, второй раз его не надо загадывать в одном шифре.
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
# ====================== ФИДБЕК ======================
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("👍 Отметь хорошие шифры")
    good_input = st.text_input("Хороший шифр (например: Рождался 0)", key="good_input")
    if st.button("Сохранить как хороший"):
        ...

with col2:
    st.subheader("👎 Отметь плохие шифры")
    bad_input = st.text_input("Плохой шифр", key="bad_input")
    if st.button("Сохранить как плохой"):
        if bad_input:
            st.session_state.bad_hints.append(bad_input)
            st.session_state.memory["bad_examples"].append(bad_input)
            FEEDBACK_FILE.write_text(json.dumps(st.session_state.memory, ensure_ascii=False, indent=2), encoding="utf-8")
            st.error("Сохранено в память!")

st.caption("Generation G • Память включена")
