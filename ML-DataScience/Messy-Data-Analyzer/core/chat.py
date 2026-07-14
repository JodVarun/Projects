"""
Natural Language Q&A via PandasAI + Groq
Lets users ask questions about their data in plain English.
"""

import os
import pandas as pd
from groq import Groq
import json


def chat_with_data(df: pd.DataFrame, question: str, api_key: str, history: list = None) -> dict:
    """
    Ask a natural language question about the data.
    Returns a dict with 'type' (text/table/error) and 'content'.
    """
    client = Groq(api_key=api_key)

    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample = df[col].dropna().head(3).tolist()
        col_info.append(f"  - {col} ({dtype}): sample={sample}")

    schema = "\n".join(col_info)
    stats = df.describe(include='all').to_string()

    history_text = ""
    if history:
        history_text = "\nPrevious Q&A:\n" + "\n".join([
            f"Q: {h['question']}\nA: {h['answer'][:200]}" for h in history[-3:]
        ])

    prompt = f"""You are a data analyst. Answer the user's question about this dataset.

SCHEMA ({len(df)} rows × {len(df.columns)} cols):
{schema}

STATISTICS:
{stats}
{history_text}

USER QUESTION: {question}

INSTRUCTIONS:
- Write Python/Pandas code to answer the question
- Execute the code mentally on the dataset stats above
- Provide a clear, concise answer
- If the question asks for a chart/plot, describe what chart would be appropriate
- Format numbers nicely (commas, 2 decimal places)
- If you're computing aggregations, show the result as a markdown table

Respond with JSON: {{"type": "text", "answer": "your answer here"}}
For table results: {{"type": "table", "answer": "markdown table"}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        try:
            result = json.loads(content)
            return {
                'type': result.get('type', 'text'),
                'content': result.get('answer', content),
                'success': True
            }
        except json.JSONDecodeError:
            return {'type': 'text', 'content': content, 'success': True}

    except Exception as e:
        return {
            'type': 'error',
            'content': f"Error communicating with Groq: {str(e)}",
            'success': False
        }


def get_suggested_questions(df: pd.DataFrame) -> list[str]:
    """Generate starter questions based on the dataset structure."""
    questions = []
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    if len(numeric_cols) > 0:
        questions.append(f"What is the average {numeric_cols[0]}?")
        if len(numeric_cols) > 1:
            questions.append(f"What is the correlation between {numeric_cols[0]} and {numeric_cols[1]}?")

    if len(cat_cols) > 0:
        questions.append(f"What are the most common values in {cat_cols[0]}?")
        if len(numeric_cols) > 0:
            questions.append(f"What is the average {numeric_cols[0]} by {cat_cols[0]}?")

    questions.append("How many rows have missing values?")
    questions.append("Summarize this dataset in 3 sentences.")

    return questions[:6]
