import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok Спаймастер — Быстрый")

st.markdown("**1. Загрузи скриншот → 2. Распознай → 3. Поправь слова**")

# ====================== СКРИНШОТ ======================
uploaded_file = st.file_uploader("📸 Загрузи скриншот доски", type=["png", "jpg", "jpeg"])

words_input = ""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Скриншот", use_column_width=True)

    if st.button("🔍 Распознать слова", type="primary", use_container_width=True):
        with st.spinner("Распознаю..."):
            try:
                # Улучшение картинки
                img = image.convert("L")
                img = ImageEnhance.Contrast(img).enhance(2.5)
                img = img.filter(ImageFilter.SHARPEN)
                
                text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 6 -l rus+eng')
                
                # Очистка
                extracted = []
                for line in text.splitlines():
                    for w in line.split():
                        clean = ''.join(c for c in w if c.isalpha() or c == '-').lower()
                        if len(clean) > 2:
                            extracted.append(clean)
                
                words_input = ", ".join(extracted)
                st.success(f"Распознано {len(extracted)} слов")
                st.write(words_input)
            except Exception as e:
                st.error("Не удалось распознать")

# ====================== ПРАВКА ======================
words_input = st.text_area("Поправь / дополни слова:", 
                           value=words_input, 
                           height=140,
                           placeholder="сторона, магистр, кроссовок...")

if not words_input:
    st.stop()

words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
board = list(dict.fromkeys(words))

st.success(f"✅ **{len(board)} слов** готово")

# ====================== ГЕНЕРАЦИЯ ======================
api_key = st.text_input("Groq API Key", type="password")

if st.button("🚀 СГЕНЕРИРОВАТЬ ШИФРЫ", type="primary", use_container_width=True):
    if not api_key:
        st.error("Введи API Key")
        st.stop()

    groups_text = ""
    for cat_key, cat_name in CATEGORY_NAMES.items():
        found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
        if found:
            groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

    prompt = f"""Ты лучший спаймастер. Время ограничено.

Слова: {', '.join(sorted(board))}

Категории:
{groups_text}

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


Выдай 6 лучших шифров.

Формат:
**Шифр: "слово" — на N → слово1, слово2...**
Короткое объяснение.

Начинай сразу с шифров."""

    with st.spinner("Думаю..."):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1100
            )
            st.markdown("### 🎯 Шифры:")
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Ошибка: {e}")
