import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
try:
    from docx import Document
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'python-docx'])
    from docx import Document

load_dotenv()

def get_key(name):
    return os.getenv(name)

st.set_page_config(
    page_title="ИИ-помощник для семейного канала",
    page_icon="👨‍👩‍👧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация темы в session_state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# CSS стили с поддержкой темы
def get_css_styles(theme):
    if theme == "dark":
        return """
        <style>
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display: none;}
        
        /* Тёмная тема - основные цвета */
        .stApp {
            background-color: #1a1a2e;
        }
        
        /* Принудительный светлый текст для всего основного контента */
        .main, .stMarkdown, .stTextArea, .stTextInput, div[data-testid="stMarkdownContainer"] {
            color: #e2e8f0 !important;
        }
        
        /* Текст в блоках и абзацах */
        p, h1, h2, h3, h4, h5, h6, span, div, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
            color: #e2e8f0 !important;
        }
        
        /* Карточки и контейнеры с текстом */
        .stTabs [data-baseweb="tab-panel"] {
            background-color: transparent;
            color: #e2e8f0 !important;
        }
        
        /* Текст внутри вкладок */
        .stTabs [data-baseweb="tab-panel"] p,
        .stTabs [data-baseweb="tab-panel"] div:not(.stButton) {
            color: #e2e8f0 !important;
        }
        
        /* Предпросмотр Telegram в тёмной теме */
        div[style*="background: #E7EBF0"] {
            background: #2d2d44 !important;
        }
        div[style*="background: white"] {
            background: #16213e !important;
            color: #e2e8f0 !important;
        }
        
        /* ГРАДИЕНТНЫЙ ЗАГОЛОВОК */
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
        
        /* СТИЛЬ ДЛЯ ПОДЗАГОЛОВКА */
        .subtitle {
            text-align: center;
            color: #a78bfa !important;
            font-size: 1.2em;
            margin-bottom: 30px;
            font-weight: 500;
        }
        
        .post-card {
            background: #16213e;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin: 10px 0;
            border-left: 5px solid #667eea;
            color: #e2e8f0 !important;
        }
        
        .stButton>button {
            border-radius: 10px;
            font-weight: 500;
        }
        
        /* БОКОВОЕ МЕНЮ С ГРАДИЕНТОМ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] textarea {
            color: white !important;
            background-color: rgba(255,255,255,0.1) !important;
        }
        [data-testid="stSidebar"] .stSelectbox > div > div > select {
            background-color: rgba(255,255,255,0.15) !important;
            color: white !important;
        }
        [data-testid="stSidebar"] .stSlider > div {
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
        
        /* Карточки вкладок */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            color: #e2e8f0 !important;
        }
        
        /* Метрики в тёмной теме */
        [data-testid="stMetricValue"] {
            color: #a78bfa !important;
        }
        
        /* Инфо блоки */
        .stInfo, .stAlert {
            background-color: #16213e !important;
            color: #e2e8f0 !important;
        }
        
        /* Dataframe таблицы */
        .stDataFrame, .dataframe {
            color: #e2e8f0 !important;
        }
        .stDataFrame table, .dataframe table {
            color: #e2e8f0 !important;
        }
        .stDataFrame th, .dataframe th {
            background-color: #0f0c29 !important;
            color: #a78bfa !important;
        }
        .stDataFrame td, .dataframe td {
            background-color: #16213e !important;
            color: #e2e8f0 !important;
        }
        
        /* Код блоки */
        .stCodeBlock {
            background-color: #0f0c29 !important;
        }
        </style>
        """
    else:
        return """
        <style>
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display: none;}
        
        /* ГРАДИЕНТНЫЙ ЗАГОЛОВОК */
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
        
        /* СТИЛЬ ДЛЯ ПОДЗАГОЛОВКА */
        .subtitle {
            text-align: center;
            color: #764ba2;
            font-size: 1.2em;
            margin-bottom: 30px;
            font-weight: 500;
        }
        
        .post-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin: 10px 0;
            border-left: 5px solid #667eea;
            color: black;
        }
        
        .stButton>button {
            border-radius: 10px;
            font-weight: 500;
        }
        
        /* БОКОВОЕ МЕНЮ С ГРАДИЕНТОМ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] textarea {
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

st.markdown(get_css_styles(st.session_state.theme), unsafe_allow_html=True)

def build_prompt(topic, platform, tone, temperature, text_length):
    prompt_text = (
        "Persona: Опытный контент-мейкер и копирайтер для семейных медиа. Эксперт по созданию лаконичных, практичных и вовлекающих материалов для родителей детей 2-10 лет. Пишет живо, без штампов, с фокусом на применимую пользу и эмоциональный отклик.\n\n"
        "Task: Написать готовый к публикации пост для платформы " + platform + " на тему: \"" + topic + "\".\n\n"
        "Context: Аудитория - родители дошкольников и младших школьников (2-10 лет). Цель: дать конкретную пользу за 30 секунд чтения, вызвать желание сохранить материал и ответить в комментариях. Текст должен восприниматься как рекомендация от опытного друга, а не как сухая инструкция или рекламный текст.\n\n"
        "Format: Структура: 1) Вступление (цепляющий факт, ситуация или вопрос, сразу переходящий в тему) - 2) 2-3 практических совета (конкретные шаги, микро-примеры, без абстракций) - 3) Вопрос к читателям для обсуждения в комментариях. Эмодзи: уместные, умеренное количество (максимум 1 на каждые 2-3 предложения), не заменяют знаки препинания. В конце ровно 8-10 хештегов, включая обязательные: #семья #родители #воспитание #дети #семейноевремя. Вывести ТОЛЬКО текст поста, без приветствий, комментариев или markdown-разметки, кроме переносов строк.\n\n"
        "Критерии:\n"
        "- Без воды: полный запрет на вводные клише (в современном мире, как известно, важно помнить), общие фразы, повторы и пустые связки. Каждое предложение должно нести смысл, инструкцию или эмоцию.\n"
        "- Читабельность: короткие абзацы (1-3 строки), активный залог, разговорный ритм, адаптированный под " + platform + ".\n"
        "- Интерес и креативность: при низком значении креативности (" + str(temperature) + ") - чёткие шаги и факты; при среднем - лёгкие истории из жизни и живые примеры; при высоком - неожиданные ракурсы, яркие метафоры и игровые форматы, без потери ясности.\n"
        "- Практичность советов: каждый пункт должен содержать конкретное действие, временные рамки или сценарий, применимый здесь и сейчас для возраста 2-10 лет.\n"
        "- Соблюдение объёма: " + text_length + ". Текст должен быть готов к копированию и публикации без редактуры.\n\n"
        "Выводить исключительно финальный пост."
    )
    return prompt_text

def call_yandex(prompt):
    api_key = get_key("YANDEX_API_KEY")
    folder_id = get_key("YANDEX_FOLDER_ID")
    if not api_key or not folder_id:
        return "Не настроен YandexGPT"
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": "Api-Key " + api_key,
        "x-folder-id": folder_id,
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": "gpt://" + folder_id + "/yandexgpt-lite",
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
        return "YandexGPT ошибка: " + str(e)

def call_deepseek(prompt):
    api_key = get_key("DEEPSEEK_API_KEY")
    if not api_key:
        return "Не указан DEEPSEEK_API_KEY"
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
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
        return "DeepSeek ошибка: " + str(e)

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

st.markdown("<div class='main-title'>👨‍👩‍👧 ИИ-помощник для семейного канала</div>", unsafe_allow_html=True)
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

# Инициализация text_length по умолчанию
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
        preview_html_ya = "<div style='background: #E7EBF0; border-radius: 15px; padding: 15px; max-width: 400px;'><div style='background: white; border-radius: 12px; padding: 12px 15px; font-size: 14px; line-height: 1.5;'>" + yandex_preview.replace(chr(10), "<br>") + "</div><div style='text-align: right; color: #888; font-size: 11px;'>" + datetime.now().strftime("%H:%M") + "</div></div>"
        st.markdown(preview_html_ya, unsafe_allow_html=True)
        
        st.markdown("### От DeepSeek:")
        deepseek_preview = st.session_state.deepseek_text[:500] + "..." if len(st.session_state.deepseek_text) > 500 else st.session_state.deepseek_text
        preview_html_ds = "<div style='background: #E7EBF0; border-radius: 15px; padding: 15px; max-width: 400px;'><div style='background: white; border-radius: 12px; padding: 12px 15px; font-size: 14px; line-height: 1.5;'>" + deepseek_preview.replace(chr(10), "<br>") + "</div><div style='text-align: right; color: #888; font-size: 11px;'>" + datetime.now().strftime("%H:%M") + "</div></div>"
        st.markdown(preview_html_ds, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Сравнение моделей")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric("YandexGPT символов", len(st.session_state.yandex_text))
        with col_c2:
            st.metric("DeepSeek символов", len(st.session_state.deepseek_text))
        analysis_text = (
            "**Тема:** " + st.session_state.topic + "\n\n"
            "**Платформа:** " + st.session_state.platform + "\n\n"
            "**Тон:** " + st.session_state.tone + "\n\n"
            "**Длина:** " + st.session_state.text_length + "\n\n"
            "**YandexGPT** лучше для: коротких постов и русского языка.\n\n"
            "**DeepSeek** лучше для: развёрнутых текстов и креативных идей."
        )
        st.info(analysis_text)

# УЛУЧШЕННАЯ БОКОВАЯ ПАНЕЛЬ
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h2>⚙️ Настройки</h2></div>", unsafe_allow_html=True)
    
    # Выбор темы оформления
    theme_options = {"🌞 Светлая": "light", "🌙 Тёмная": "dark"}
    selected_theme = st.selectbox("🎨 Тема оформления", list(theme_options.keys()), index=0 if st.session_state.theme == "light" else 1)
    if theme_options[selected_theme] != st.session_state.theme:
        st.session_state.theme = theme_options[selected_theme]
        st.rerun()
    
    st.divider()
    
    # Настройки генерации
    st.write("### 📝 Параметры генерации")
    
    selected_model = st.radio(
        "🤖 Модель ИИ",
        ["Обе модели", "Только YandexGPT", "Только DeepSeek"],
        index=0,
        help="Выберите, какие модели будут использоваться для генерации"
    )
    
    text_length = st.select_slider(
        "📏 Длина текста",
        options=["Менее 300 слов", "300-400 слов", "500-600 слов", "Более 600 слов"],
        value=st.session_state.text_length,
        help="Выберите желаемый объём текста"
    )
    
    # Сохраняем выбранную длину в session_state
    st.session_state.text_length = text_length
    
    # Дополнительные настройки
    with st.expander("🔧 Дополнительные настройки"):
        st.caption("Для более точной настройки генерации")
        use_emojis = st.checkbox("Использовать эмодзи", value=True)
        use_hashtags = st.checkbox("Добавлять хештеги", value=True)
    
    st.divider()
    
    # Статистика
    st.write("### 📊 Статистика")
    if os.path.exists("history.csv"):
        try:
            df_history = pd.read_csv("history.csv")
            if "Длина" in df_history.columns:
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Всего постов", len(df_history))
                with col_stat2:
                    st.metric("Последний пост", df_history["Дата"].iloc[-1] if len(df_history) > 0 else "—")
            else:
                os.remove("history.csv")
                st.info("🔄 История обновлена (старый формат)")
        except Exception:
            if os.path.exists("history.csv"):
                os.remove("history.csv")
            st.info("🔄 История пуста")
    else:
        st.info("📭 Нет сохранённых постов")
    
    st.divider()
    
    # История
    with st.expander("📜 История постов", expanded=False):
        if os.path.exists("history.csv"):
            try:
                df_history = pd.read_csv("history.csv")
                if "Длина" in df_history.columns and len(df_history) > 0:
                    st.dataframe(df_history[["Дата", "Тема", "Платформа"]].tail(5), use_container_width=True)
                    if st.button("🗑️ Очистить историю", use_container_width=True):
                        os.remove("history.csv")
                        st.rerun()
                else:
                    st.write("📭 Нет постов в истории")
            except Exception:
                st.write("📭 Нет постов в истории")
        else:
            st.write("📭 Нет сохранённых постов")
    
    st.divider()
    
    # О проекте
    with st.expander("ℹ️ О проекте", expanded=False):
        st.markdown("""
        **ИИ-помощник для семейного канала**  
        Версия 2.1
        
        🚀 **Возможности:**
        - Генерация постов через YandexGPT и DeepSeek
        - Настройка тона и креативности
        - Сохранение в Word и историю
        - Тёмная/светлая тема
        
        💡 **Совет:** Экспериментируйте с креативностью для разных форматов постов!
        """)