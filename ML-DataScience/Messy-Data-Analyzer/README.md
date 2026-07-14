# 🔍 Messy Data Analyzer

<div align="center">

**AI-powered data cleaning & analysis tool — upload any messy CSV and get instant insights, AI-driven cleaning, and natural language Q&A.**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white)](https://python.org/)
[![Groq](https://img.shields.io/badge/Groq-LLM_Inference-000?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48L3N2Zz4=)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Auto Analysis** | Detects missing values, duplicates, outliers, type mismatches, formatting issues |
| 🧠 **AI Reasoning** | Every cleaning suggestion comes with an explanation of *why* it's recommended |
| 🛠️ **One-Click Cleaning** | Apply individual fixes or bulk-clean with a single click |
| 📈 **Smart Charts** | Auto-generated Plotly visualizations based on your data types |
| 🎨 **Custom Charts** | Build your own charts with the interactive chart builder |
| 💬 **AI Chat** | Ask questions about your data in plain English |
| 📥 **Export** | Download your cleaned data as CSV |

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Your API Key

Get a **free** API key from [console.groq.com](https://console.groq.com/) (no credit card needed).

```bash
# Option A: Environment variable
cp .env.example .env
# Edit .env and add your key

# Option B: Streamlit secrets (for deployment)
mkdir -p .streamlit
echo 'GROQ_API_KEY = "gsk_your_key_here"' > .streamlit/secrets.toml
```

### 3. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Sample Datasets

Three messy datasets are included for demo purposes:

- **Messy Sales** — Mixed date formats, inconsistent casing, price formatting issues, outliers
- **Dirty Survey** — Missing emails, inconsistent city names, mixed rating formats
- **Messy Employees** — Department casing issues, salary outliers, date format inconsistencies

You can also try messy datasets from Kaggle:
- [Cafe Sales (Dirty)](https://www.kaggle.com/datasets/bhanupratapbiswas/cafe-sales-dirty-data-for-cleaning-training)
- [FIFA 21 (Messy)](https://www.kaggle.com/datasets/rachittoshniwal/fifa-21-messy-raw-dataset-for-cleaning-exploring)
- [Retail Sales (Dirty)](https://www.kaggle.com/datasets/ahmedmohamed1997/retail-store-sales-dirty-for-data-cleaning)

---

## 🏗️ Architecture

```
messy-data-analyzer/
├── app.py                  # Main entry point
├── core/
│   ├── analyzer.py         # Data quality analysis (pure Pandas)
│   ├── cleaner.py          # AI cleaning with Groq
│   ├── chat.py             # Natural language Q&A
│   └── visualizer.py       # Plotly chart generation
├── ui/
│   ├── sidebar.py          # Sidebar UI
│   ├── overview_tab.py     # Dataset overview
│   ├── quality_tab.py      # Data quality & cleaning
│   ├── explore_tab.py      # Data exploration
│   └── chat_tab.py         # AI chat interface
├── sample_data/            # Demo datasets
└── .streamlit/config.toml  # Theme configuration
```

## 🔧 Tech Stack

- **Streamlit** — UI framework
- **Groq** — LLM inference (free tier, Llama 3.3 70B)
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts
- **python-dotenv** — Environment management

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `GROQ_API_KEY` in **Secrets** under Advanced Settings
5. Deploy!

---

## 📄 License

MIT License — Feel free to use and modify.

---

<div align="center">
Made by <a href="https://github.com/JodVarun">@JodVarun</a>
</div>
