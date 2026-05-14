import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Твой Идеальный Спаймастер для Коднеймс")

st.markdown("**Вставь все 25 слов с доски** (через запятую или с новой строки):")

words_input = st.text_area("", height=180, placeholder="врач, стоматолог, халат, сердце, пистолет, гном...")

if st.button("🔍 Проанализировать и предложить шифры", type="primary", use_container_width=True):
    if words_input:
        # Обработка слов
        words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
        board_words = list(dict.fromkeys(words))
        
        st.success(f"✅ Загружено {len(board_words)} слов")

        # Поиск групп
        st.subheader("📊 Найденные категории:")
        groups = {}
        for cat_key, cat_name in CATEGORY_NAMES.items():
            found = [w for w in board_words if w in CATEGORIES.get(cat_key, [])]
            if found:
                groups[cat_key] = found
                emoji = {
                    "person": "👤", "mythical_being": "🧌", "clothing": "👕", "furniture": "🪑",
                    "item": "🔧", "organ": "🫀", "weapon": "⚔️", "paper": "📄", "food": "🍎",
                    "animal": "🐺", "action": "🏃", "feeling_quality": "❤️", "positive": "✅",
                    "negative": "❌", "science": "🔬", "sound": "🔊"
                }.get(cat_key, "•")
                st.write(f"{emoji} **{cat_name}** ({len(found)}): {', '.join(found)}")

        # Генерация шифров
        st.subheader("🚀 Рекомендуемые шифры:")
        suggestions = []

        if "person" in groups and len(groups["person"]) >= 2:
            n = len(groups["person"])
            clue = "медик" if "медик" not in board_words else "профессия" if "профессия" not in board_words else "специалист"
            suggestions.append(f"**{clue}** — на {n} → {', '.join(groups['person'])}")

        if "animal" in groups and len(groups["animal"]) >= 2:
            suggestions.append(f"**хищник** — на {len(groups['animal'])} → {', '.join(groups['animal'])}")

        if "clothing" in groups and len(groups["clothing"]) >= 2:
            suggestions.append(f"**одежда** — на {len(groups['clothing'])} → {', '.join(groups['clothing'])}")

        if "organ" in groups and len(groups["organ"]) >= 2:
            suggestions.append(f"**орган** — на {len(groups['organ'])} → {', '.join(groups['organ'])}")

        if "weapon" in groups and len(groups["weapon"]) >= 2:
            suggestions.append(f"**оружие** — на {len(groups['weapon'])} → {', '.join(groups['weapon'])}")

        if "mythical_being" in groups and len(groups["mythical_being"]) >= 2:
            suggestions.append(f"**сказка** / **миф** — на {len(groups['mythical_being'])} → {', '.join(groups['mythical_being'])}")

        if suggestions:
            for i, sug in enumerate(suggestions, 1):
                st.success(f"{i}. {sug}")
        else:
            st.info("Пока не нашлось сильных групп. Попробуй добавить больше слов.")

        # Для отладки
        with st.expander("Все слова на доске"):
            st.write(", ".join(board_words))            n = len(groups["person"])
            # Предлагаем шифры, которых точно нет на доске
            possible_clues = ["доктор", "профессия", "специалист", "медик", "лекарь"]
            clue = next((c for c in possible_clues if c not in board_words), "человек")
            suggestions.append(f"**{clue}** — на {n} → {', '.join(groups['person'])}")

        # Животные
        if "animal" in groups and len(groups["animal"]) >= 2:
            possible_clues = ["хищник", "зверь", "животное", "фауна", "дикий"]
            clue = next((c for c in possible_clues if c not in board_words), "зверь")
            suggestions.append(f"**{clue}** — на {len(groups['animal'])} → {', '.join(groups['animal'])}")

        # Действия
        if "action" in groups and len(groups["action"]) >= 2:
            possible_clues = ["движение", "активность", "спорт", "манёвр"]
            clue = next((c for c in possible_clues if c not in board_words), "действие")
            suggestions.append(f"**{clue}** — на {len(groups['action'])} → {', '.join(groups['action'])}")

        # Чувства
        if "feeling_quality" in groups and len(groups["feeling_quality"]) >= 2:
            possible_clues = ["эмоция", "чувство", "настроение"]
            clue = next((c for c in possible_clues if c not in board_words), "эмоция")
            suggestions.append(f"**{clue}** — на {len(groups['feeling_quality'])} → {', '.join(groups['feeling_quality'])}")

        # Вывод
        if suggestions:
            for i, sug in enumerate(suggestions, 1):
                st.success(f"{i}. {sug}")
        else:
            st.info("Не нашлось сильных групп. Попробуй ввести больше слов.")

        # Показываем все слова на доске (для контроля)
        st.caption("Слова на доске: " + ", ".join(board_words))            clue = "врач" if "врач" in words else "человек" if "человек" in words else "стоматолог"
            suggestions.append(f"**{clue}** — на {n} → {', '.join(groups['person'])}")

        if "animal" in groups and len(groups["animal"]) >= 2:
            suggestions.append(f"**хищник** / **зверь** — на {len(groups['animal'])} → {', '.join(groups['animal'])}")

        if "action" in groups and len(groups["action"]) >= 2:
            suggestions.append(f"**движение** — на {len(groups['action'])} → {', '.join(groups['action'])}")

        if "feeling_quality" in groups and len(groups["feeling_quality"]) >= 2:
            suggestions.append(f"**эмоция** — на {len(groups['feeling_quality'])} → {', '.join(groups['feeling_quality'])}")

        if "science" in groups and len(groups["science"]) >= 2:
            suggestions.append(f"**наука** — на {len(groups['science'])} → {', '.join(groups['science'])}")

        for i, sug in enumerate(suggestions, 1):
            st.success(f"{i}. {sug}")

        if not suggestions:
            st.info("Не нашлось сильных групп по категориям. Добавь больше слов.")
