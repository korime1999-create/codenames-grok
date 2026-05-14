import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — ИИ Спаймастер для Коднеймс")

st.markdown("**Вставь все 25 слов с доски**:")

words_input = st.text_area("", height=180, placeholder="стоматолог, врач, медведь, прыжок...")

# === Настройки ИИ ===
api_key = st.text_input("Groq API Key (если есть)", type="password", help="Можно оставить пустым на первое время")
model = "llama3-70b-8192"  # можно поменять на mixtral, gemma2 и т.д.

if st.button("🔥 Сгенерировать лучшие шифры", type="primary", use_container_width=True):
    if words_input:
        words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
        board = list(dict.fromkeys(words))
        
        st.success(f"✅ Загружено {len(board)} слов")

        # Собираем категории (для контекста)
        groups = {}
        for cat_key, cat_name in CATEGORY_NAMES.items():
            found = [w for w in board if w in CATEGORIES.get(cat_key, [])]
            if found:
                groups[cat_name] = found

        context = "Найденные группы:\n"
        for name, ws in groups.items():
            context += f"- {name} ({len(ws)}): {', '.join(ws)}\n"

        prompt = f"""Ты — лучший в мире спаймастер в Коднеймс. 
У тебя очень сильная интуиция и креативность.

Слова на доске: {', '.join(board)}

{context}

Придумай **5–7 очень сильных шифров** по следующим приоритетам:
1. Большие группы (3+), если безопасно
2. Используй категории (человек → человек, животные → зверь/хищник и т.д.)
3. Избегай однокоренных слов и слов с доски
4. Предпочитай красивые, неожиданные, но логичные ассоциации
5. Для множественного числа правильно склоняй ("чувства 4", "движения 3" и т.д.)

Для каждого шифра укажи:
- Шифр
- На сколько
- Какие слова
- Краткое объяснение почему хорошо

Начинай сразу с шифров."""
        
        st.info("Думаю... (это может занять 5-15 секунд)")

        # Пока без реального API — показываем контекст
        with st.expander("Что будет отправлено ИИ"):
            st.write(prompt)

        st.warning("🔴 Пока ИИ не подключён. Хочешь подключить Groq или Grok API?")
