"""
AI-Powered Data Cleaning with Reasoning
Uses Groq API for cleaning suggestions with transparent explanations.
"""

import json
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from groq import Groq


@dataclass
class CleaningAction:
    column: str
    action: str
    reasoning: str
    before_preview: str
    after_preview: str
    rows_affected: int


def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def get_cleaning_suggestions(df: pd.DataFrame, issues: list, api_key: str) -> list[CleaningAction]:
    """Ask the LLM to analyze issues and provide cleaning suggestions with reasoning."""
    client = get_groq_client(api_key)

    issues_text = "\n".join([
        f"- Column '{i.column}': {i.issue_type} — {i.description}"
        for i in issues[:15]
    ])

    col_info = "\n".join([
        f"- {col}: dtype={df[col].dtype}, nunique={df[col].nunique()}, nulls={df[col].isnull().sum()}"
        for col in df.columns
    ])

    sample_data = df.head(5).to_string()

    prompt = f"""You are a data cleaning expert. Analyze these data quality issues and provide cleaning recommendations.

DATASET INFO:
{col_info}

SAMPLE DATA:
{sample_data}

DETECTED ISSUES:
{issues_text}

For each issue, provide a JSON array of cleaning actions. Each action must have:
- "column": column name
- "action": one of ["fill_mean", "fill_median", "fill_mode", "fill_unknown", "drop_duplicates", "strip_whitespace", "standardize_case", "convert_numeric", "convert_datetime", "clip_outliers", "drop_rows"]
- "reasoning": A clear explanation of WHY you recommend this action (2-3 sentences explaining the data context and tradeoffs)
- "description": Brief description of what changes

Respond ONLY with a valid JSON array. No markdown, no explanation outside JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        # Extract JSON from response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        suggestions_raw = json.loads(content)
    except Exception as e:
        return _get_fallback_suggestions(df, issues)

    actions = []
    for s in suggestions_raw:
        col = s.get("column", "")
        action_type = s.get("action", "")
        reasoning = s.get("reasoning", "No reasoning provided.")
        desc = s.get("description", action_type)

        before = _get_before_preview(df, col, action_type)
        after = _get_after_preview(df, col, action_type)
        affected = _count_affected(df, col, action_type)

        actions.append(CleaningAction(
            column=col, action=action_type, reasoning=reasoning,
            before_preview=before, after_preview=after, rows_affected=affected
        ))

    return actions


def apply_cleaning_action(df: pd.DataFrame, action: CleaningAction) -> pd.DataFrame:
    """Apply a single cleaning action to the DataFrame."""
    df = df.copy()
    col = action.column

    if action.action == "fill_mean" and col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())
    elif action.action == "fill_median" and col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].median())
    elif action.action == "fill_mode" and col in df.columns:
        mode_val = df[col].mode()
        if len(mode_val) > 0:
            df[col] = df[col].fillna(mode_val[0])
    elif action.action == "fill_unknown" and col in df.columns:
        df[col] = df[col].fillna("Unknown")
    elif action.action == "drop_duplicates":
        df = df.drop_duplicates(keep='first').reset_index(drop=True)
    elif action.action == "strip_whitespace" and col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    elif action.action == "standardize_case" and col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.title()
    elif action.action == "convert_numeric" and col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '').str.replace('%', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    elif action.action == "convert_datetime" and col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
    elif action.action == "clip_outliers" and col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        df[col] = df[col].clip(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
    elif action.action == "drop_rows" and col in df.columns:
        df = df.dropna(subset=[col]).reset_index(drop=True)

    return df


def _get_before_preview(df, col, action):
    if col == "[ALL]" or col not in df.columns:
        return f"{len(df)} rows"
    return str(df[col].head(3).tolist())


def _get_after_preview(df, col, action):
    if action == "drop_duplicates":
        return f"{len(df.drop_duplicates())} rows"
    return "Preview after applying"


def _count_affected(df, col, action):
    if action == "drop_duplicates":
        return int(df.duplicated().sum())
    if col in df.columns:
        if "fill" in action:
            return int(df[col].isnull().sum())
        if action == "strip_whitespace":
            s = df[col].dropna().astype(str)
            return int((s.str.strip() != s).sum())
    return 0


def _get_fallback_suggestions(df, issues):
    """Provide deterministic suggestions when LLM is unavailable."""
    actions = []
    for issue in issues[:10]:
        col = issue.column
        if issue.issue_type == 'missing':
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                actions.append(CleaningAction(col, "fill_median",
                    "Median is robust to outliers and preserves the central tendency.",
                    str(df[col].head(3).tolist()), "Filled", issue.affected_rows))
            else:
                actions.append(CleaningAction(col, "fill_mode",
                    "Mode preserves the most common category.",
                    str(df[col].head(3).tolist()) if col in df.columns else "",
                    "Filled", issue.affected_rows))
        elif issue.issue_type == 'duplicate':
            actions.append(CleaningAction("[ALL]", "drop_duplicates",
                "Duplicate rows add noise. Keeping first occurrence.",
                f"{len(df)} rows", f"{len(df.drop_duplicates())} rows",
                issue.affected_rows))
        elif issue.issue_type == 'formatting':
            actions.append(CleaningAction(col, "strip_whitespace",
                "Whitespace causes join/match failures.",
                "", "Stripped", issue.affected_rows))
        elif issue.issue_type == 'inconsistent':
            actions.append(CleaningAction(col, "standardize_case",
                "Title case provides consistent formatting.",
                "", "Standardized", issue.affected_rows))
    return actions
