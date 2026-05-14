import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok Спаймастер — Быстрый режим")

st.markdown("**Слова сохраняются автоматически** — просто редактируй нужное")

# ====================== СОХРАНЕНИЕ СЛОВ ======================
if "saved_board" not in st.session_state:
    st.session_state.saved_board = [""] * 25

board_list = st.session_state.saved_board

st.subheader("Доска 5×5 (редактируй слова)")

cols = st.columns(5)
for i in range(25):
    with cols[i % 5]:
        board_list[i] = st.text_input(
            label=" ",
            value=board_list[i],
            key=f"word_{i}",
            label_visibility="collapsed"
        )

# Собираем актуальные слова
board = [w.strip().lower() for w in board_list if w.strip()]
board = list(dict.fromkeys(board))

if len(board) > 0:
    st.success(f"✅ **{len(board)} слов** готово")

# Кнопка быстрой очистки
if st.button("🗑️ Очистить всю доску"):
    st.session_state.saved_board = [""] * 25
    st.rerun()

# ====================== ГЕНЕРАЦИЯ ======================
api_key = st.text_input("Groq API Key", type="password")

if st.button("🚀 СГЕНЕРИРОВАТЬ ШИФРЫ СЕЙЧАС", type="primary", use_container_width=True):
    if not api_key or len(board) < 15:
        st.error("Введи API Key и хотя бы 15 слов")
        st.stop()

    # Категории
    groups_text = ""
    for cat_key, cat_name in CATEGORY_NAMES.items():
        found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
        if found:
            groups_text += f"- {cat_name} ({len(found)}): {', '.join(found)}\n"

    prompt = f"""Ты лучший спаймастер. Время ограничено.

Слова на доске: {', '.join(sorted(board))}

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

with st.expander("Все текущие слова"):
    st.write(", ".join(sorted(board)))
