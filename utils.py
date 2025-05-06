#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ユーティリティ関数を定義するモジュール
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

# ロギング設定
logger = logging.getLogger(__name__)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    datetime オブジェクトを文字列にフォーマット
    
    Args:
        dt (datetime): 日時オブジェクト
        format_str (str): フォーマット文字列
        
    Returns:
        str: フォーマットされた日時文字列
    """
    return dt.strftime(format_str)

def parse_iso_datetime(iso_string: str) -> datetime:
    """
    ISO 8601形式の日時文字列をdatetimeオブジェクトに変換
    
    Args:
        iso_string (str): ISO形式の日時文字列
        
    Returns:
        datetime: 変換後のdatetimeオブジェクト
    """
    try:
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        logger.error(f"日時文字列のパースエラー: {e}")
        # エラー時は現在時刻を返す
        return datetime.now(timezone.utc)

def get_jst_now() -> datetime:
    """
    現在の日本時間を取得
    
    Returns:
        datetime: 日本時間の現在時刻
    """
    # JSTタイムゾーン (UTC+9)
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)

def get_date_range(days: int) -> Tuple[datetime, datetime]:
    """
    指定日数前から現在までの日付範囲を取得
    
    Args:
        days (int): 何日前から取得するか
        
    Returns:
        tuple: (開始日, 終了日) の形式で返す
    """
    end_date = get_jst_now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def truncate_text(text: Optional[str], max_length: int = 100) -> str:
    """
    テキストを指定の長さに切り詰める
    
    Args:
        text (str): 元のテキスト
        max_length (int): 最大長
        
    Returns:
        str: 切り詰められたテキスト
    """
    if not text:
        return ""
        
    if len(text) <= max_length:
        return text
        
    return text[:max_length] + "..."
