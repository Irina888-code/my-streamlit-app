import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime
try:
    from docx import Document
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'python-docx'])
    from docx import Document

st.set_page_config(
    page_title="ИИ-помощник для семейного канала",
    page_icon="👨‍👩‍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_api_key(key_name):
    """Безопасное получение API ключей"""
    try:
        return st.secrets[key_name]
    except:
        return os.getenv(key_name, "")

CSS_STYLES = """
<style>
#MainMenu {visibility: hidden;}
.stAppDeployButton {display: none;}

.main-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.2em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
}   

.subtitle {
    text-align: center;
    color: #764ba2;
    font-size: 1.2em;
    margin-bottom: 30px;
    font-weight: 500;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 500;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select {
    color: white !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div > select {
    background-color: rgba(255,255,255,0.1) !important;
    color: white !important;
}
.sidebar-header {
    background: rgba(255,255,255,0.15);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}
</style>
"""

st.markdown(CSS_STYLES, unsafe_allow_html=True)

def build_prompt(topic, platform, tone, temperature, text_length):
    prompt_text = (
        f"Persona: Опытный контент-мейкер и копирайтер для семейных медиа. Эксперт по созданию лаконичных, практичных и вовлекающих материалов для родителей детей 2-10 лет.\n\n"
        f"Task: Написать готовый к публикации пост для платформы {platform} на тему: '{topic}'.\n\n"
        f"Context: Аудитория - родители дошкольников и младших школьников (2-10 лет).\n\n"
        f"Format: Структура: 1) Вступление - 2) 2-3 практических совета - 3) Вопрос к читателям. Эмодзи умеренно. В конце 8-10 хештегов включая #семья #родители #воспитание #дети #семейноевремя.\n\n"
        f"Критерии:\n"
        f"- Без воды и клише\n"
        f"- Короткие абзацы (1-3 строки)\n"
        f"- Креативность: {temperature}\n"
        f"- Объём: {text_length}\n"
        f"- Практичные советы для возраста 2-10 лет\n\n"
        f"Выводить только финальный пост."
    )
    return prompt_text

def call_yandex(prompt):
    api_key = get_api_key("YANDEX_API_KEY")
    folder_id = get_api_key("YANDEX_FOLDER_ID")
    
    if not api_key or not folder_id:
        return "Не настроен YandexGPT"
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": "Api-Key " + api_key,
        "x-folder-id": folder_id,
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {"stream": False, "temperature": 0.7, "maxTokens": 2000},
        "messages": [
            {"role": "system", "text": "Ты контент-мейкер."},
            {"role": "user", "text": prompt}
        ]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        return f"YandexGPT ошибка: {str(e)}"

def call_deepseek(prompt):
    api_key = get_api_key("DEEPSEEK_API_KEY")
    
    if not api_key:
        return "Не указан DEEPSEEK_API_KEY"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты контент-мейкер."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"DeepSeek ошибка: {str(e)}"

def save_to_word(text, filename):
    doc = Document()
    doc.add_heading("Пост для семейного канала", 0)
    doc.add_paragraph(text)
    doc.save(filename)
    return filename

def save_to_history(topic, platform, tone, text_length, yandex_text, deepseek_text):
    data = {
        "Дата": [datetime.now().strftime("%d.%m.%Y %H:%M")],
        "Тема": [topic],
        "Платформа": [platform],
        "Тон": [tone],
        "Длина": [text_length],
        "YandexGPT": [yandex_text[:100] + "..." if len(yandex_text) > 100 else yandex_text],
        "DeepSeek": [deepseek_text[:100] + "..." if len(deepseek_text) > 100 else deepseek_text]
    }
    df = pd.DataFrame(data)
    csv_file = "history.csv"
    
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

# Основной интерфейс
st.markdown("<div class='main-title'>👨‍👩‍ ИИ-помощник для семейного канала</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>✨ Генерация постов с хештегами и эмодзи через YandexGPT и DeepSeek</div>", unsafe_allow_html=True)

quick_topics = [
    "5 идей для семейных выходных",
    "Как пережить утренние сборы в детский сад без слёз",
    "Топ-10 настольных игр для детей 3-7 лет",
    "Рецепты полезных перекусов для школы",
    "Семейные традиции, которые сближают",
    "Как научить ребёнка читать через игру",
    "Идеи для домашнего праздника ребёнка",
    "Как справиться с детскими истериками в магазине"
]

col_a, col_b = st.columns([3, 1])
with col_a:
    topic = st.text_input("Тема поста", placeholder="Введите свою тему")
with col_b:
    selected_quick = st.selectbox("Или выберите:", ["- Готовые темы -"] + quick_topics)
    if selected_quick != "- Готовые темы -":
        topic = selected_quick

col1, col2, col3 = st.columns(3)
with col1:
    platform = st.selectbox("Платформа", ["Telegram", "ВКонтакте", "Дзен", "Instagram"])
with col2:
    tone = st.selectbox("Тон", ["Тёплый и искренний", "Экспертный", "Мотивирующий", "Лёгкий и юмористический"])
with col3:
    temperature = st.slider("Креативность", 0.1, 1.0, 0.7, 0.1)

if "text_length" not in st.session_state:
    st.session_state.text_length = "300-400 слов"

if st.button("Сгенерировать посты", type="primary", use_container_width=True):
    if not topic:
        st.error("Введите тему поста!")
    else:
        with st.spinner("ИИ генерирует посты... Подождите 10-20 секунд"):
            prompt = build_prompt(topic, platform, tone, temperature, st.session_state.text_length)
            yandex_result = call_yandex(prompt)
            deepseek_result = call_deepseek(prompt)
            
            st.session_state.yandex_text = yandex_result
            st.session_state.deepseek_text = deepseek_result
            st.session_state.topic = topic
            st.session_state.platform = platform
            st.session_state.tone = tone
            
            st.success("Посты успешно сгенерированы!")

if "yandex_text" in st.session_state:
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["YandexGPT", "DeepSeek", "Предпросмотр Telegram", "Сравнение"])
    
    with tab1:
        st.subheader("YandexGPT (Lite)")
        st.markdown(st.session_state.yandex_text.replace("\n", "\n\n"))
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            doc_file = save_to_word(st.session_state.yandex_text, "yandex_post.docx")
            with open(doc_file, "rb") as f:
                st.download_button("Скачать Word", f, file_name="post_yandex.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="download_yandex")
        with col_act2:
            if st.button("Скопировать текст", key="copy_yandex_btn"):
                st.code(st.session_state.yandex_text)
        with col_act3:
            if st.button("В историю", key="save_yandex_hist"):
                save_to_history(st.session_state.topic, st.session_state.platform, st.session_state.tone, st.session_state.text_length, st.session_state.yandex_text, st.session_state.deepseek_text)
                st.success("Сохранено!")
    
    with tab2:
        st.subheader("DeepSeek")
        st.markdown(st.session_state.deepseek_text.replace("\n", "\n\n"))
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            doc_file = save_to_word(st.session_state.deepseek_text, "deepseek_post.docx")
            with open(doc_file, "rb") as f:
                st.download_button("Скачать Word", f, file_name="post_deepseek.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="download_deepseek")
        with col_act2:
            if st.button("Скопировать текст", key="copy_deepseek_btn"):
                st.code(st.session_state.deepseek_text)
        with col_act3:
            if st.button("В историю", key="save_deepseek_hist"):
                save_to_history(st.session_state.topic, st.session_state.platform, st.session_state.tone, st.session_state.text_length, st.session_state.yandex_text, st.session_state.deepseek_text)
                st.success("Сохранено!")
    
    with tab3:
        st.subheader("Предпросмотр Telegram")
        st.markdown("### От YandexGPT:")
        yandex_preview = st.session_state.yandex_text[:500] + "..." if len(st.session_state.yandex_text) > 500 else st.session_state.yandex_text
        preview_html_ya = f"""<div style='background: #E7EBF0; border-radius: 15px; padding: 15px; max-width: 400px;'>
            <div style='background: white; border-radius: 12px; padding: 12px 15px; font-size: 14px; line-height: 1.5; color: #000;'>
                {yandex_preview.replace(chr(10), "<br>")}
            </div>
            <div style='text-align: right; color: #888; font-size: 11px;'>
                {datetime.now().strftime("%H:%M")}
            </div>
        </div>"""
        st.markdown(preview_html_ya, unsafe_allow_html=True)
        
        st.markdown("### От DeepSeek:")
        deepseek_preview = st.session_state.deepseek_text[:500] + "..." if len(st.session_state.deepseek_text) > 500 else st.session_state.deepseek_text
        preview_html_ds = f"""<div style='background: #E7EBF0; border-radius: 15px; padding: 15px; max-width: 400px;'>
            <div style='background: white; border-radius: 12px; padding: 12px 15px; font-size: 14px; line-height: 1.5; color: #000;'>
                {deepseek_preview.replace(chr(10), "<br>")}
            </div>
            <div style='text-align: right; color: #888; font-size: 11px;'>
                {datetime.now().strftime("%H:%M")}
            </div>
        </div>"""
        st.markdown(preview_html_ds, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Сравнение моделей")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric("YandexGPT символов", len(st.session_state.yandex_text))
        with col_c2:
            st.metric("DeepSeek символов", len(st.session_state.deepseek_text))
        
        analysis_text = (
            f"**Тема:** {st.session_state.topic}\n\n"
            f"**Платформа:** {st.session_state.platform}\n\n"
            f"**Тон:** {st.session_state.tone}\n\n"
            f"**Длина:** {st.session_state.text_length}\n\n"
            "**YandexGPT** лучше для: коротких постов и русского языка.\n\n"
            "**DeepSeek** лучше для: развёрнутых текстов и креативных идей."
        )
        st.info(analysis_text)

# Боковая панель
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h2>📋 Меню</h2></div>", unsafe_allow_html=True)
    st.write("### Настройки")
    
    model_option = st.selectbox(
        "Модель ИИ",
        ["YandexGPT + DeepSeek", "Только YandexGPT", "Только DeepSeek"]
    )
    
    text_length = st.selectbox(
        "📏 Длина текста",
        ["Менее 300 слов", "300-400 слов", "500-600 слов", "Более 600 слов"]
    )
    
    st.session_state.text_length = text_length
    
    st.divider()
    
    st.write("### Статистика")
    if os.path.exists("history.csv"):
        try:
            df_history = pd.read_csv("history.csv")
            if "Длина" not in df_history.columns:
                os.remove("history.csv")
                st.info("🔄 История обновлена")
            else:
                st.metric("Всего постов", len(df_history))
        except:
            os.remove("history.csv")
            st.info("🔄 История обновлена")
    else:
        st.info("История пуста")
    
    st.divider()
    
    st.write("### История")
    if os.path.exists("history.csv"):
        try:
            df_history = pd.read_csv("history.csv")
            if "Длина" in df_history.columns:
                st.dataframe(df_history.tail(5), use_container_width=True)
        except:
            st.write("Сохраните новый пост")
    else:
        st.write("Нет постов")
    
    st.divider()
    
    st.write("### О проекте")
    st.info("ИИ-помощник для семейного канала. Версия 2.0")