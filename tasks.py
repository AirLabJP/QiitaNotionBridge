#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
タスク実行関数を定義するモジュール
"""

import logging
from datetime import datetime

from qiita import QiitaClient
from notion import NotionClient
from utils import get_jst_now

# ロギング設定
logger = logging.getLogger(__name__)

def daily_job(backfill_days=1):
    """
    Qiitaから人気記事を取得してNotionに保存する日次ジョブ
    
    Args:
        backfill_days (int): バックフィル時の日数
    """
    logger.info(f"日次ジョブ実行開始: {get_jst_now().strftime('%Y-%m-%d %H:%M:%S JST')}")
    
    try:
        # 1. Qiitaクライアントを初期化
        qiita_client = QiitaClient()
        
        # 2. 指定日数分の人気記事を取得 (LGTM/Stock 500以上)
        logger.info(f"過去 {backfill_days} 日分の人気記事を取得中...")
        articles = qiita_client.get_popular_articles(days=backfill_days, min_likes=500)
        
        if not articles:
            logger.info("条件に一致する記事が見つかりませんでした")
            return
            
        logger.info(f"{len(articles)} 件の人気記事が見つかりました")
        
        # 3. 記事をNotion用フォーマットに変換
        notion_articles = [qiita_client.format_article_for_notion(article) for article in articles]
        
        # 4. Notionクライアントを初期化
        notion_client = NotionClient()
        
        # 5. 記事をNotionデータベースに追加/更新
        logger.info(f"Notionデータベースに記事を登録中...")
        success_count, new_count, error_count, new_articles = notion_client.bulk_upsert_articles(notion_articles)
        
        # 6. 新規記事がある場合はコンソールに通知
        if new_articles:
            logger.info(f"{new_count} 件の新規記事を通知します")
            notify_new_articles(new_articles)
        else:
            logger.info("新規記事がないため、通知は送信しません")
            
        logger.info(f"日次ジョブ実行完了: 成功 {success_count}, 新規 {new_count}, エラー {error_count}")
        
    except Exception as e:
        logger.exception(f"日次ジョブ実行中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    # 単体テスト実行用
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    daily_job()
