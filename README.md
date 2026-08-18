```
╔══════════════════════════════════════════════════════════════════════════════╗
║          HYPER-LOCAL INFLATION TRACKER  ·  B.Tech Capstone Project           ║
║          "Your wallet knows the truth. National indices don't."               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

```bash
$ cat README.md
```

---

## 📌 Project Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│  NAME    : Hyper-Local Inflation Tracker                            │
│  TYPE    : AI-Powered Streamlit Web Application                     │
│  PURPOSE : Track real grocery prices, visualize personal inflation  │
│            trends, and use AI to predict next month's budget.       │
│  AI      : OpenRouter API (Vision OCR + Text Analysis)             │
│  STACK   : Python 3.9+ · Streamlit · Pandas · OpenAI SDK           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT FRONTEND                            │
│                                                                      │
│  [Dashboard Tab]       [Log Prices Tab]       [AI Analysis Tab]      │
│  st.metric (KPIs)      st.form (manual)       st.markdown (report)   │
│  st.line_chart         st.camera_input        st.expander (raw)      │
│  st.data_editor        (receipt scan)         st.spinner             │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                   st.session_state["price_df"]
                   (pd.DataFrame: Date, Item, Price)
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
          ▼                                     ▼
┌──────────────────┐                 ┌──────────────────────┐
│  PANDAS ENGINE   │                 │   OPENROUTER API      │
│                  │                 │   (openai SDK)        │
│  - Filter        │                 │                       │
│  - Aggregate     │◄────────────────│  Vision Model:        │
│  - Delta Calc    │  JSON items     │  Receipt OCR          │
│  - to_string()  ─┼────────────────►│                       │
│    (for LLM)     │  f-string       │  Text Model:          │
└──────────────────┘  prompt         │  Budget Analysis      │
                                     └──────────────────────┘
                                              │
                                     os.environ.get()
                                              │
                                        ┌────┴────┐
                                        │  .env   │
                                        │ (secret)│
                                        └─────────┘
```

---

## ⚙️ Setup Instructions

```bash
# ─── Step 1: Clone the repository ─────────────────────────────────────
$ git clone https://github.com/jayendrasai/Hyper-Local-Inflation-Tracker.git
$ cd Hyper-Local-Inflation-Tracker

# ─── Step 2: Create a virtual environment ─────────────────────────────
$ python3 -m venv .venv
$ source .venv/bin/activate          # On Windows: .venv\Scripts\activate

# ─── Step 3: Install dependencies ─────────────────────────────────────
$ pip install -r requirements.txt

# ─── Step 4: Configure your API key ───────────────────────────────────
$ cp .env.example .env
$ nano .env                          # Or use your preferred editor

# Inside .env, add:
#   OPENROUTER_API_KEY=your_actual_key_here

# Get your free key at: https://openrouter.ai/keys

# ─── Step 5: Run the application ──────────────────────────────────────
$ streamlit run app.py

# ─── App will open in browser at: http://localhost:8501 ───────────────
```

---

## 🔐 Security Model

```
⚠  NEVER commit your .env file.
    The .gitignore in this project explicitly excludes:
    - .env
    - .venv/
    - __pycache__/

    Your OPENROUTER_API_KEY is loaded ONLY via:
    python-dotenv → load_dotenv() → os.environ.get("OPENROUTER_API_KEY")

    Zero hardcoded credentials in source code.
```


## 🔗 Live Demo

```
┌─────────────────────────────────────────────┐
│  🌐 Live App:  [ https://local-inflation.streamlit.app ]   │
│  📁 GitHub:    [ https://github.com/jayendrasai/Hyper-Local-Inflation-Tracker ]   │
└─────────────────────────────────────────────┘
```

---

## 📦 Tech Stack

```
Language   : Python 3.9+
Framework  : Streamlit
Data       : Pandas
AI/LLM     : OpenRouter (google/gemini-2.5-flash text + nvidia/nemotron-3-nano-omni vision)
Security   : python-dotenv
Deployment : Streamlit Community Cloud
```

---

## 👤 Author

```
Project   : B.Tech Capstone — Hyper-Local Inflation Tracker
Developer : JAYENDRA SAI CHENNA
Roll No   : 23P31A0571
Guide     : MIRAI School Of Technology
Year      : 2026
```

```bash
$ echo "Setup complete. Run: streamlit run app.py"
Setup complete. Run: streamlit run app.py
```
