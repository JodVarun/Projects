"""
Data Quality Analysis Engine
Analyzes uploaded CSVs for data quality issues using pure Pandas logic.
"""

import re
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DataIssue:
    column: str
    issue_type: str
    severity: str
    description: str
    affected_rows: int
    affected_percentage: float
    details: dict = field(default_factory=dict)


@dataclass
class AnalysisReport:
    total_rows: int
    total_columns: int
    quality_score: float
    issues: list = field(default_factory=list)
    column_types: dict = field(default_factory=dict)
    memory_usage_mb: float = 0.0
    duplicate_rows: int = 0
    total_missing: int = 0
    summary_stats: Optional[pd.DataFrame] = None


def analyze_dataset(df: pd.DataFrame) -> AnalysisReport:
    issues = []
    total_rows = len(df)
    total_columns = len(df.columns)

    # 1. Missing Values
    missing_counts = df.isnull().sum()
    total_missing = int(missing_counts.sum())
    for col in df.columns:
        missing = int(missing_counts[col])
        if missing > 0:
            pct = (missing / total_rows) * 100
            sev = 'critical' if pct > 30 else ('warning' if pct > 10 else 'info')
            issues.append(DataIssue(col, 'missing', sev,
                f"{missing} missing values ({pct:.1f}%)", missing, pct,
                {'missing_count': missing, 'missing_pct': round(pct, 2)}))

    # 2. Duplicates
    dup_count = int(df.duplicated(keep='first').sum())
    if dup_count > 0:
        pct = (dup_count / total_rows) * 100
        sev = 'critical' if pct > 20 else ('warning' if pct > 5 else 'info')
        issues.append(DataIssue('[ALL]', 'duplicate', sev,
            f"{dup_count} duplicate rows ({pct:.1f}%)", dup_count, pct))

    # 3. Type Mismatches
    for col in df.select_dtypes(include=['object']).columns:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        sample = non_null.head(100)
        num_ct = sum(1 for v in sample if _is_numeric_str(str(v)))
        if len(sample) > 0 and num_ct / len(sample) > 0.7:
            issues.append(DataIssue(col, 'type_mismatch', 'warning',
                f"Appears numeric but stored as text ({num_ct}/{len(sample)} numeric)",
                len(non_null), 100.0,
                {'detected_type': 'numeric', 'current_type': 'object'}))

    # 4. Outliers (IQR)
    for col in df.select_dtypes(include=[np.number]).columns:
        col_data = df[col].dropna()
        if len(col_data) < 10:
            continue
        Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        lb, ub = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        out_ct = int(((col_data < lb) | (col_data > ub)).sum())
        if out_ct > 0:
            pct = (out_ct / len(col_data)) * 100
            issues.append(DataIssue(col, 'outlier', 'warning' if pct > 5 else 'info',
                f"{out_ct} outliers ({pct:.1f}%)", out_ct, pct,
                {'lower': round(lb, 2), 'upper': round(ub, 2)}))

    # 5. Formatting Issues
    for col in df.select_dtypes(include=['object']).columns:
        non_null = df[col].dropna().astype(str)
        if len(non_null) == 0:
            continue
        ws_ct = int((non_null.str.strip() != non_null).sum())
        if ws_ct > 0:
            issues.append(DataIssue(col, 'formatting', 'info',
                f"{ws_ct} values with leading/trailing whitespace", ws_ct,
                (ws_ct / len(non_null)) * 100))
        unique = non_null.str.strip().unique()
        lower_set = set(v.lower() for v in unique)
        if len(unique) > len(lower_set) and len(unique) <= 100:
            issues.append(DataIssue(col, 'inconsistent', 'warning',
                f"Inconsistent casing: {len(unique)} → {len(lower_set)} when lowercased",
                len(unique) - len(lower_set),
                ((len(unique) - len(lower_set)) / len(unique)) * 100))

    # Quality Score
    quality_score = _calc_score(issues, total_rows)

    # Column Types
    col_types = {}
    for col in df.columns:
        dt = str(df[col].dtype)
        if dt == 'object':
            col_types[col] = 'categorical' if df[col].nunique() <= 20 else 'text'
        elif 'int' in dt or 'float' in dt:
            col_types[col] = 'numeric'
        elif 'datetime' in dt:
            col_types[col] = 'datetime'
        else:
            col_types[col] = dt

    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    try:
        stats = df.describe(include='all')
    except Exception:
        stats = df.describe()

    return AnalysisReport(total_rows, total_columns, quality_score, issues,
        col_types, round(mem_mb, 2), dup_count, total_missing, stats)


def _is_numeric_str(s):
    try:
        float(s.strip().replace(',', '').replace('$', '').replace('%', ''))
        return True
    except (ValueError, TypeError):
        return False


def _calc_score(issues, total_rows):
    if total_rows == 0:
        return 0.0
    weights = {'critical': 3.0, 'warning': 1.5, 'info': 0.5}
    type_mult = {'duplicate': 8, 'missing': 10, 'type_mismatch': 5, 'outlier': 3, 'formatting': 2, 'inconsistent': 2}
    penalty = sum(
        (i.affected_rows / total_rows) * weights.get(i.severity, 1) * type_mult.get(i.issue_type, 1)
        for i in issues
    )
    return round(max(0.0, min(100.0, 100.0 - penalty)), 1)
