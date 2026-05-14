import streamlit as st
from PIL import Image
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер")

st.markdown("**Загрузи скриншот и быстро скопируй слова**")

# ====================== СКРИНШОТ ======================
uploaded_file = st.file_uploader("📸 Загрузи скриншот доски", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Скриншот доски", use_column_width=True)
    st.caption("👇 Скопируй слова из картинки ниже")

# ====================== ВВОД СЛОВ ======================
words_input = st.text_area(
    "Вставь все 25 слов сюда (через запятую или строку):", 
    height=180,
    placeholder="сторона, магистр, кроссовок, подножка, брюки, директор..."
)

if not words_input:
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

# ====================== СОСТОЯНИЕ ======================
st.subheader("🎨 Состояние доски")

team = st.radio("Твоя команда:", ["🔵 Синие", "🔴 Красные"], horizontal=True)

if "board_state" not in st.session_state or len(st.session_state.board_state) != len(board):
    st.session_state.board_state = {w: "Не открыто" for w in board}

cols = st.columns(5)
for i, word in enumerate(board):
    with cols[i % 5]:
        status = st.selectbox(word.capitalize(), 
                            ["Не открыто", "✅ Моё", "❌ Чужое", "☠️ Чёрный"], 
                            key=f"s_{i}")
        st.session_state.board_state[word] = status

# ====================== ГЕНЕРАЦИЯ ======================
api_key = st.text_input("Groq API Key", type="password")

if st.button("🚀 Сгенерировать шифры", type="primary", use_container_width=True):
    if not api_key:
        st.error("Введи Groq API Key")
        st.stop()

    my = [w for w, s in st.session_state.board_state.items() if "Моё" in s]
    opp = [w for w, s in st.session_state.board_state.items() if "Чужое" in s]
    black = any("Чёрный" in s for s in st.session_state.board_state.values())

    state_info = f"Моя команда ({team.split()[0]}): {len(my)} открыто. Противник: {len(opp)} открыто. Чёрный: {'да' if black else 'нет'}"

    prompt = f"""Ты лучший спаймастер Коднеймса.

Слова: {', '.join(sorted(board))}

Категории:
{groups_text}

{state_info}

- Можно использовать "0" для того, чтобы команда не брала самое очевидное слово из категории и брала остальные.
- Можно использовать шифр во множественном числе для обозначения 2+ слов одной категории, но не делать этого, если слишком много слов этой категории не принадлежат твоей команде или если вреди них есть черное.
- "0" на шифр множественного числа нулит либо 2 слова одной категории если слов из этой категории много, либо одно слово и заданной категории и самое близкое по смыслу слово, если слов в этой категории на столе только 2 или меньше.
- Если команда пишет клэйм, то ты отвечаешь в первую очередь на него. Это значит любой твой ноль будет распространяться только на клэйм. А все слова зашаданные поверх будут рассматриваться только после того, как разберут клэйм.
- Клэйм всегда ранжирован. Например, если тебе пишут "Соль, перец, человек, сметана", а у тебя осталось неразгадано 8 слов, то если ты в шифре укажешь цифру 5, то ты перезагадешь 5 слов и тебе не возьмут сметану (8-5=3, три первых слова из клэйма).
- Ты можешь связывать категорию совокупности с любым шифром. Например, "перцев 3" это в первую очередь любая совокупность и две еды, которые больше всего подходят под перец.
- Ищи большие группы в первую очередь.
- Твоя задача победить в 2-3 хода, если ты ходишь первым. Или в 2 хода, если вторым.
- Такие шифры как "Банщика" могут подразумевать три категории: Человек, чувство/качество (что-то банщика, например, отзывчивасть, воля и тд), место (баня)


Дай 6–7 сильных шифров. Только одно слово или через дефис. Можно "0".
Начинай с самых больших групп.

Формат:
**Шифр: "слово" — на N → слово1, слово2...**
Короткое объяснение."""

    with st.spinner("ИИ думает..."):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.75,
                max_tokens=1200
            )
            st.markdown("### 🎯 Рекомендуемые шифры:")
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Ошибка: {e}")

with st.expander("Все слова"):
    st.write(", ".join(sorted(board)))
