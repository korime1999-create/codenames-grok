import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime

from categories import CATEGORIES, CATEGORY_NAMES
from groq import Groq

st.set_page_config(page_title="Generation G", layout="wide")

st.title("🕵️‍♂️ Generation G")
st.markdown("**GenevieveAi for Codenames**")

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
    
    temperature = st.slider("Температура", 0.1, 0.55, 0.3, 0.05)

# ====================== MAIN ======================
uploaded_file = st.file_uploader("Загрузи скриншот доски", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)

    api_key = st.text_input("Groq API Key", type="password")

    guessed_input = st.text_input("Уже отгаданные слова (через запятую)", 
                                 value=", ".join(st.session_state.guessed_words_list))
    
    if guessed_input:
        st.session_state.guessed_words_list = [w.strip() for w in guessed_input.split(",") if w.strip()]

    if st.button("🚀 Проанализировать доску", type="primary", use_container_width=True):
        if not api_key:
            st.error("Введите Groq API Key")
            st.stop()

        with st.spinner("Генерирую шифры..."):
            try:
                client = Groq(api_key=api_key)

                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

                guessed_str = ", ".join(st.session_state.guessed_words_list)

                # Base64 URL вынесен отдельно, чтобы избежать ошибки вложенности f-string
                image_url = f"data:image/jpeg;base64,{base64_image}"

                system_prompt = f"""Ты — сильный и агрессивный спаймастер Коднеймс.
Ты играешь за {team_color} команду. Враги — {enemy}."""

                user_prompt = f"""Это скриншот доски Коднеймс.

Твоя команда: {team_color}
Вражеская команда: {enemy}
Уже отгаданы: {guessed_str}

(Правила игры, где ты Капитан:
Руководитель команды в свой ход даёт игрокам шифрованный намёк и указывает, сколько слов связаны с ним (далее «шифр»), ничего более говорить или показывать нельзя. Позволяется уточнить, куда падает ударение в загаданном слове. Шифр состоит из одного слова и одного числа. Например, руководитель хочет намекнуть на два кодовых слова, написанные на картах стола, – СЛОН и ЛЕВ – и говорит: «африка - 2». Шифр должен относиться к смыслу кодовых имён. Нельзя использовать слова с одинаковыми окончаниями, суффиксами и приставками, если они не связаны по смыслу («человечек» и «грибочек» связаны, они оба описывают маленькие предметы, «воскресение» и «мнение» не связаны). Нельзя использовать шифры с созвучными корнями, если они не связаны по смыслу («порт» нельзя использовать для слова СПОРТ, но «ребёнок» можно использовать для слова ЖЕРЕБЁНОК). Нельзя говорить об их первых буквах или о геометрическом расположении этих карт в таблице. Нельзя связывать слова ЛУК, ЛЁН и ЛЕВ шифрами «л - 3» или «три - 3». Буквы и числа допустимы, если они касаются смысла кодовых имён, например, «восемь - 2» – о словах ПАУК и ЧИСЛО. Число в шифре нельзя использовать в качестве шифра: «цитрусовые - 8» недопустимо для слов ЛИМОН и ОСЬМИНОГ. В качестве шифра нельзя использовать слово однокоренное с присутствующими среди неразгаданных кодовых имён. В шифре запрещено использовать несуществующие слова, делать намеки в виде нарочных ошибок или изменений регистра букв, например, для слов ЛУНА и БАСНЯ недопустимо «АПОЛЛОг - 2». Если используется шифр не на русском языке, он не должен иметь однокоренных прямых переводов со словами на столе. Аббревиатуры использовать можно, но к их составляющим применяются те же правила, что к обычным подсказкам (нельзя загадывать СССР, если на столе есть карточка со словом «союз»). Запрещено использовать несуществующие слова, если такие слова вместе с загаданным и, возможно, дополнительными буквами образуют существующее слово. В качестве чисел можно использовать — 0-9; при этом команда может называть любое количество слов. Руководителю команды допустимо произнести вслух шифр, в том числе и по просьбам игроков. Наказание за неправильный шифр: Если руководитель команды дал шифр с нарушением правил, ход его команды немедленно заканчивается, и руководитель команды соперников открывает одно слово своей команды, прежде чем давать шифр.)

***Как ты должен играть (общая стратегия):**

- Твоя цель — закрыть 8–10 слов за 2–3 хода.
- На первых двух ходах старайся давать шифры на 4–6 слов.
- В первую очередь ищи самые большие возможные группы (даже если они неочевидные).
- Будь смелым и оригинальным. Хороший шифр может связывать разные категории.
- Предпочитай конкретные слова + 0 ("Галстук 0", "Насос 0", "Костюм 0").
- Широкие категории ("Одежды 0", "Ткани 0") используй только когда действительно большая группа.

**Механика "0":**
- "Галстук 0" — нулим самое очевидное слово из группы, связанной с галстуком/одеждой.
- "Одежды 0" — нулим самые кричащие слова всей категории одежды.
- Такой шифр должен открывать минимум 3–4 слова.

   - "Одежды", "Ткани", "Клубники", "Места" — обозначает 2 и больше слов.

3. **Стиль игры**  
   - Ищи большие группы в первую очередь.  
   - Будь оригинальным и креативным.  
   - Предпочитай конкретные слова ("Штаны 0") перед общими категориями.

4. **Безопасность**  
   - Шифр должен быть выгоден твоей команде и относительно безопасен.

Предложи 6–8 сильных шифров.

**JSON формат:**
```json
{{
  "hints": [
    {{
      "cipher": "Галстук",
      "number": 0,
      "words": ["шарф", "вышивка", "строчка"],
      "explanation": "Галстук 0 — нулим самое очевидное, открываем остальную одежду"
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
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url}
                                }
                            ]
                        }
                    ],
                    temperature=temperature,
                    max_tokens=3200,
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
                    words_list = hint.get("words", [])
                    words_str = ", ".join(words_list) if isinstance(words_list, list) else str(words_list)
                    
                    with st.container(border=True):
                        st.markdown(f"**{hint.get('cipher')}** — на **{hint.get('number')}** → {words_str}")
                        st.caption(hint.get('explanation', ''))
                        
                        col1, col2 = st.columns(2)
                        if col1.button("👍 Класс", key=f"good_{i}_{analysis_id}"):
                            st.session_state.good_hints.append(f"{hint.get('cipher')} {hint.get('number')}")
                        if col2.button("👎 Не класс", key=f"bad_{i}_{analysis_id}"):
                            st.session_state.bad_hints.append(f"{hint.get('cipher')} {hint.get('number')}")

            except Exception as e:
                st.error(f"Ошибка: {str(e)[:700]}")

# История
if st.session_state.analyses:
    st.divider()
    st.subheader("📖 История")
    for a in reversed(st.session_state.analyses[-5:]):
        with st.expander(f"{a['timestamp']} — {a['model']}"):
            st.json(a["result"], expanded=False)

st.caption("Generation G • GenevieveAi for Codenames")
