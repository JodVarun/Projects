# 🌸 Iris Flower Classification

<div align="center">

**A classic machine learning project exploring multiple classification algorithms on the Iris dataset.**

[![Python](https://img.shields.io/badge/Python-3.x-3776ab?logo=python&logoColor=white)](https://python.org/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-f7931e?logo=scikit-learn)](https://scikit-learn.org/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JodVarun/Projects/blob/main/ML-DataScience/Iris-Classification/Iris_project1.ipynb)

</div>

---

## 📌 Overview

This project classifies Iris flowers into three species — **Setosa**, **Versicolor**, and **Virginica** — based on sepal and petal measurements. It serves as a hands-on introduction to supervised learning, covering data exploration, visualization, and model evaluation.

## 🔬 What's Inside

| Step | Description |
|------|-------------|
| **Data Loading** | Fetched from the Seaborn dataset repository |
| **EDA** | Null checks, shape, statistical summary, class distribution |
| **Visualization** | Box plots, histograms, pair plots (Seaborn) |
| **Train/Test Split** | 65/35 split with `random_state=7` |
| **Models Trained** | Decision Tree, KNN, Random Forest |
| **Evaluation** | Accuracy, Confusion Matrix, Classification Report |

## 🧠 Models & Results

| Model | Algorithm | Key Params |
|-------|-----------|------------|
| **Decision Tree** | `DecisionTreeClassifier` | Default |
| **KNN** | `KNeighborsClassifier` | Default (k=5) |
| **Random Forest** | `RandomForestClassifier` | `n_estimators=18` |

## 🛠️ Tech Stack

- **Pandas** — Data manipulation
- **Matplotlib & Seaborn** — Visualization
- **Scikit-learn** — ML models & evaluation

## 🚀 Run It

```bash
# Option 1: Open in Google Colab (click badge above)

# Option 2: Run locally
pip install pandas matplotlib seaborn scikit-learn
jupyter notebook Iris_project1.ipynb
```

---

<div align="center">
Made by <a href="https://github.com/JodVarun">@JodVarun</a>
</div>
