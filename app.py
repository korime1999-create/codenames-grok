import streamlit as st
from PIL import Image
import pytesseract
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер для Коднеймса")
st.markdown("**Загрузи скриншот доски — ИИ поможет найти сильные шифры**")

# ====================== ЗАГРУЗКА СКРИНШОТА ======================
uploaded_file = st.file_uploader("📸 Загрузи скриншот доски 5×5", 
                                 type=["png", "jpg", "jpeg"], 
                                 help="Чем лучше качество — тем точнее распознавание")

words_input = ""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Загруженный скриншот", use_column_width=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔍 Распознать слова (OCR)", use_container_width=True):
            with st.spinner("Распознавание текста..."):
                try:
                    custom_config = r'--oem 3 --psm 6 -l rus+eng'
                    text = pytesseract.image_to_string(image, config=custom_config)
                    
                    # Очистка текста
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    extracted = []
                    for line in lines:
                        for word in line.replace(',', ' ').split():
                            cleaned = word.strip().lower()
                            if len(cleaned) > 2 and cleaned.isalpha():
                                extracted.append(cleaned)
                    
                    words_input = ", ".join(extracted)
                    st.success(f"✅ Распознано {len(extracted)} слов!")
                    st.write("**Распознанные слова:**", words_input)
                except Exception as e:
                    st.error(f"Ошибка OCR: {e}")

# ====================== РУЧНОЙ ВВОД ======================
words_input = st.text_area(
    "Или вставь/отредактируй слова вручную:", 
    value=words_input,
    height=130,
    placeholder="сторона, магистр, кроссовок, подножка, директор..."
)

if not words_input:
    st.info("Загрузи скриншот или введи слова")
    st.stop()

# ====================== ОБРАБОТКА СЛОВ ======================
words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
board = list(dict.fromkeys(words))

st.success(f"✅ Работает с **{len(board)}** словами")

# Категории
groups_text = ""
for cat_key, cat_name in CATEGORY_NAMES.items():
    found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
    if found:
        groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

# ====================== СОСТОЯНИЕ СТОЛА ======================
st.subheader("🎨 Состояние доски")

team = st.radio("Ты играешь за:", ["🔵 Синие", "🔴 Красные"], horizontal=True, key="team")

if "board_state" not in st.session_state or len(st.session_state.board_state) != len(board):
    st.session_state.board_state = {word: "Не открыто" for word in board}

cols = st.columns(5)
for i, word in enumerate(board):
    with cols[i % 5]:
        status = st.selectbox(
            word.capitalize(),
            ["Не открыто", "✅ Моё (открыто)", "❌ Чужое (открыто)", "☠️ Чёрный"],
            key=f"status_{i}_{word}"
        )
        st.session_state.board_state[word] = status

# ====================== КЛЭЙМ ======================
st.subheader("🗣️ Клэйм")
claim = st.text_input("Твой клэйм (по желанию)", placeholder="Не согласен с 'животноводы' потому что...")

# ====================== API KEY И ГЕНЕРАЦИЯ ======================
api_key = st.text_input("Groq API Key", type="password", help="Получить можно на console.groq.com")

if st.button("🚀 Сгенерировать шифры", type="primary", use_container_width=True):
    if not api_key:
        st.error("Введите Groq API Key")
        st.stop()

    # Сбор информации о состоянии
    my_opened = [w for w, s in st.session_state.board_state.items() if "Моё" in s]
    opp_opened = [w for w, s in st.session_state.board_state.items() if "Чужое" in s]
    black_taken = any("Чёрный" in s for s in st.session_state.board_state.values())

    state_info = f"""
Моя команда ({team}): {len(my_opened)} открыто → {', '.join(my_opened) if my_opened else 'нет'}
Противник: {len(opp_opened)} открыто → {', '.join(opp_opened) if opp_opened else 'нет'}
Чёрная карточка: {'взята' if black_taken else 'нет'}
"""

    prompt = f"""Ты — лучший спаймастер в русскоязычном Коднеймсе.

Слова на доске: {', '.join(sorted(board))}

Категории:
{groups_text}

{state_info}

ПРАВИЛА ШИФРА:
- Можно использовать "0" для того, чтобы команда не брала самое очевидное слово из категории и брала остальные.
- Можно использовать шифр во множественном числе для обозначения 2+ слов одной категории, но не делать этого, если слишком много слов этой категории не принадлежат твоей команде или если вреди них есть черное.
- "0" на шифр множественного числа нулит либо 2 слова одной категории если слов из этой категории много, либо одно слово и заданной категории и самое близкое по смыслу слово, если слов в этой категории на столе только 2 или меньше.
- Если команда пишет клэйм, то ты отвечаешь в первую очередь на него. Это значит любой твой ноль будет распространяться только на клэйм. А все слова зашаданные поверх будут рассматриваться только после того, как разберут клэйм.
- Клэйм всегда ранжирован. Например, если тебе пишут "Соль, перец, человек, сметана", а у тебя осталось неразгадано 8 слов, то если ты в шифре укажешь цифру 5, то ты перезагадешь 5 слов и тебе не возьмут сметану (8-5=3, три первых слова из клэйма).
- Ты можешь связывать категорию совокупности с любым шифром. Например, "перцев 3" это в первую очередь любая совокупность и две еды, которые больше всего подходят под перец.
- Ищи большие группы в первую очередь.
- Твоя задача победить в 2-3 хода, если ты ходишь первым. Или в 2 хода, если вторым.
- Такие шифры как "Банщика" могут подразумевать три категории: Человек, чувство/качество (что-то банщика, например, отзывчивасть, воля и тд), место (баня)


Выдай 6–7 лучших шифров, начиная с самого сильного.

Формат:
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
                max_tokens=1400
            )
            
            st.markdown("### 🎯 Рекомендуемые шифры:")
            st.markdown(response.choices[0].message.content)
            
            if claim:
                st.info(f"**Твой клэйм:** {claim}")
                
        except Exception as e:
            st.error(f"Ошибка Groq: {e}")

with st.expander("Все слова на доске"):
    st.write(", ".join(sorted(board)))
