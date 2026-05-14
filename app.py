import streamlit as st
from categories import CATEGORIES, CATEGORY_NAMES

st.set_page_config(page_title="Grok Коднеймс", layout="wide")
st.title("🕵️‍♂️ Grok — Идеальный Спаймастер для Коднеймс")

st.markdown("**Вставь все 25 слов с доски** (через запятую или с новой строки):")

words_input = st.text_area("", height=200, placeholder="врач, стоматолог, халат, сердце, пистолет, гном...")

if st.button("🔍 Проанализировать и предложить шифры", type="primary", use_container_width=True):
    if words_input:
        words = [w.strip().lower() for line in words_input.splitlines() for w in line.split(',') if w.strip()]
        board_words = list(dict.fromkeys(words))
        
        st.success(f"✅ Загружено {len(board_words)} слов")

        # === Категории ===
        st.subheader("📊 Найденные категории:")
        groups = {}
        for cat_key, cat_name in CATEGORY_NAMES.items():
            found = [w for w in board_words if w in CATEGORIES.get(cat_key, [])]
            if found:
                groups[cat_key] = found
                emoji = {"person": "👤", "mythical_being": "🧌", "clothing": "👕", "furniture": "🪑",
                         "organ": "🫀", "weapon": "⚔️", "animal": "🐺", "feeling_quality": "❤️",
                         "positive": "✅", "negative": "❌"}.get(cat_key, "•")
                st.write(f"{emoji} **{cat_name}** ({len(found)}): {', '.join(found)}")

        # === ГЕНЕРАЦИЯ ШИФРОВ ПО ТВОИМ ПРАВИЛАМ ===
        st.subheader("🚀 Рекомендуемые шифры:")
        suggestions = []

        for cat_key, found_words in groups.items():
            n = len(found_words)
            if n < 2:
                continue
                
            cat_name = CATEGORY_NAMES[cat_key]
            
            if cat_key == "person":
                clue = "профессия" if "профессия" not in board_words else "медик" if "медик" not in board_words else "специалист"
                suggestions.append(f"**{clue}** — на {n} → {', '.join(found_words)}")
            
            elif cat_key == "animal":
                suggestions.append(f"**зверь / хищник** — на {n} → {', '.join(found_words)}")
            
            elif cat_key == "clothing":
                suggestions.append(f"**одежда** — на {n} → {', '.join(found_words)}")
            
            elif cat_key == "organ":
                suggestions.append(f"**орган** — на {n} → {', '.join(found_words)}")
            
            elif cat_key == "weapon":
                suggestions.append(f"**оружие** — на {n} → {', '.join(found_words)}")
            
            elif cat_key == "mythical_being":
                suggestions.append(f"**сказка / миф** — на {n} → {', '.join(found_words)}")
            
            elif cat_key in ["feeling_quality", "positive", "negative"]:
                suggestions.append(f"**эмоция** — на {n} → {', '.join(found_words)}")
            
            else:
                suggestions.append(f"**{cat_name.lower()}** — на {n} → {', '.join(found_words)}")

        # Вывод шифров
        if suggestions:
            for i, sug in enumerate(suggestions[:8], 1):
                st.success(f"{i}. {sug}")
        else:
            st.warning("Не нашлось групп из 2+ слов одной категории.")

        with st.expander("Все слова на доске"):
            st.write(", ".join(sorted(board_words)))
