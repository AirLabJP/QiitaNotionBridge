#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知機能のモジュール
このモジュールはRaycast機能を削除し、コンソール出力のみを行います
"""

import logging

# ロギング設定
logger = logging.getLogger(__name__)

def notify_new_articles(articles):
    """
    新しい記事があることをコンソールに出力
    
    Args:
        articles (list): 記事データのリスト
        
    Returns:
        bool: 常にTrue
    """
    if not articles:
        logger.info("通知すべき新規記事がありません")
        return True
        
    # コンソール出力
    logger.info(f"今日のQiitaハイライト ({len(articles)}件)")
    
    # 記事情報を出力
    for article in articles:
        # タイトルとURL、いいね数を含めた行を出力
        logger.info(f"- {article['title']} (LGTM: {article['likes']}) {article['url']}")
    
    return True
