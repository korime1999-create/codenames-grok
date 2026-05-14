import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер")
st.markdown("**Загрузи скриншот — постараемся вытащить слова как можно точнее**")

# ====================== ЗАГРУЗКА ======================
uploaded_file = st.file_uploader("📸 Загрузи скриншот доски", type=["png", "jpg", "jpeg"])

words_input = ""

if uploaded_file:
    original_image = Image.open(uploaded_file)
    st.image(original_image, caption="Оригинальный скриншот", use_column_width=True)

    if st.button("🔍 Улучшенное распознавание слов"):
        with st.spinner("Улучшаем изображение и распознаём..."):
            try:
                # Улучшение изображения
                img = original_image.convert('L')  # в grayscale
                img = ImageEnhance.Contrast(img).enhance(2.0)
                img = img.filter(ImageFilter.SHARPEN)
                
                # Лучшая конфигурация для Коднеймса
                custom_config = r'--oem 3 --psm 6 -l rus+eng --dpi 300'
                
                text = pytesseract.image_to_string(img, config=custom_config)
                
                # Более агрессивная очистка
                extracted = []
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    for word in line.replace(',', ' ').replace('.', ' ').split():
                        cleaned = ''.join(c for c in word if c.isalpha() or c == '-').lower()
                        if len(cleaned) > 2:
                            extracted.append(cleaned)
                
                words_input = ", ".join(extracted)
                st.success(f"✅ Распознано {len(extracted)} слов!")
                st.write("**Распознанные слова:**", words_input)
                
            except Exception as e:
                st.error(f"Ошибка: {e}")

# ====================== РУЧНОЙ ВВОД ======================
words_input = st.text_area("Отредактируй / дополни слова:", 
                           value=words_input, 
                           height=150,
                           placeholder="сторона, магистр, кроссовок, подножка...")

if not words_input:
    st.stop()

# ====================== ОБРАБОТКА ======================
words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
board = list(dict.fromkeys(words))

st.success(f"✅ Загружено **{len(board)}** слов")

# Категории
groups_text = ""
for cat_key, cat_name in CATEGORY_NAMES.items():
    found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
    if found:
        groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

# ====================== ЦВЕТА И СОСТОЯНИЕ ======================
st.subheader("🎨 Состояние доски (пока вручную)")

team = st.radio("Твоя команда:", ["🔵 Синие", "🔴 Красные"], horizontal=True)

if "board_state" not in st.session_state or len(st.session_state.board_state) != len(board):
    st.session_state.board_state = {}

cols = st.columns(5)
for i, word in enumerate(board):
    with cols[i % 5]:
        status = st.selectbox(
            word.capitalize(),
            ["Не открыто", "✅ Моё", "❌ Чужое", "☠️ Чёрный"],
            key=f"status_{i}"
        )
        st.session_state.board_state[word] = status

# ====================== КЛЭЙМ И ГЕНЕРАЦИЯ ======================
st.subheader("🗣️ Клэйм")
claim = st.text_input("Клэйм:", placeholder="Не согласен...")

api_key = st.text_input("Groq API Key", type="password")

if st.button("🚀 Сгенерировать шифры", type="primary", use_container_width=True):
    if not api_key:
        st.error("Введи Groq API Key")
        st.stop()

    my_opened = [w for w, s in st.session_state.board_state.items() if "Моё" in s]
    opp_opened = [w for w, s in st.session_state.board_state.items() if "Чужое" in s]
    black = any("Чёрный" in s for s in st.session_state.board_state.values())

    state_info = f"Моя команда: {len(my_opened)} открыто. Противник: {len(opp_opened)} открыто. Чёрный: {'да' if black else 'нет'}"

    prompt = f"""Ты — лучший спаймастер Коднеймса.

Слова: {', '.join(sorted(board))}

Категории:
{groups_text}

{state_info}

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


Выдай 6 лучших шифров в формате:
**Шифр: "слово" — на N → слово1, слово2...**
Короткое объяснение."""

    with st.spinner("Генерирую..."):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1200
            )
            st.markdown("### 🎯 Рекомендуемые шифры:")
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Ошибка: {e}")

with st.expander("Все слова"):
    st.write(", ".join(sorted(board)))
