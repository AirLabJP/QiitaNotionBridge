#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notion データベースとの連携を担当するモジュール
"""

import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError



# ロギング設定
logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()

class NotionClient:
    """Notion API クライアント"""
    
    def __init__(self, token: Optional[str] = None, database_id: Optional[str] = None) -> None:
        """初期化"""
        self.token = token or os.getenv('NOTION_TOKEN')
        if not self.token or len(self.token) < 32:
            raise ValueError("Notion APIトークンの形式が不正です（32文字以上の英数字）")
        self.database_id = database_id or os.getenv('NOTION_DB_ID')
        if not self.database_id:
            raise ValueError("Notion データベースIDが設定されていません")
            
        # Notion クライアント初期化
        self.client = Client(auth=self.token)
        
    def _check_database(self) -> bool:
        try:
            db = self.client.databases.retrieve(self.database_id)
            properties = db.get('properties', {})
            required_props = {
                'title': {'type': 'title', 'property': {"title": {}}},
                'url': {'type': 'url', 'property': {"url": {}}},
                'author': {'type': 'rich_text', 'property': {"rich_text": {}}},
                'likes': {'type': 'number', 'property': {"number": {}}},
                'stocks': {'type': 'number', 'property': {"number": {}}},
                'tags': {'type': 'multi_select', 'property': {"multi_select": {}}},
                'summary': {'type': 'rich_text', 'property': {"rich_text": {}}},
                'created_at': {'type': 'date', 'property': {"date": {}}}
            }
            missing_props = {}
            for prop_name, prop_info in required_props.items():
                if prop_name not in properties:
                    missing_props[prop_name] = prop_info['property']
                elif properties[prop_name]['type'] != prop_info['type']:
                    logger.warning(f"プロパティ {prop_name} の型が違います（{properties[prop_name]['type']} != {prop_info['type']}）")
            if missing_props:
                logger.warning(f"データベースに必要なプロパティがありません: {', '.join(missing_props.keys())}。追加します。")
                self.client.databases.update(
                    database_id=self.database_id,
                    properties=missing_props
                )
                return True
            return True
        except APIResponseError as e:
            logger.error(f"データベース接続エラー: {e}")
            return False
            
    def search_page_by_url(self, url: str) -> Optional[dict]:
        """
        URLに基づいてページを検索
        
        Args:
            url (str): 検索するページのURL
            
        Returns:
            dict or None: 見つかったページ情報、または None
        """
        try:
            # URLフィルタでページを検索
            filter_params = {
                "filter": {
                    "property": "url",
                    "url": {
                        "equals": url
                    }
                },
                "page_size": 1
            }
            
            response = self.client.databases.query(
                database_id=self.database_id,
                **filter_params
            )
            
            results = response.get('results', [])
            return results[0] if results else None
            
        except APIResponseError as e:
            logger.error(f"Notionページ検索エラー: {e}")
            return None

    def upsert_article(self, article: dict) -> Tuple[bool, bool, Optional[str]]:
        max_retries = 3
        for attempt in range(max_retries):
            # データベース構造を確認
            if not self._check_database():
                logger.error("Notionデータベースの構造が不適切です")
                return False, False, None
            existing_page = self.search_page_by_url(article['url'])
            try:
                properties = {
                    "title": {"title": [{"text": {"content": article['title']}}]},
                    "url": {"url": article['url']},
                    "author": {"rich_text": [{"text": {"content": article['author']}}]},
                    "likes": {"number": article['likes']},
                    "stocks": {"number": article.get('stocks', 0)},
                    "tags": {"multi_select": [{"name": tag} for tag in article['tags'][:10]]},
                    "summary": {"rich_text": [{"text": {"content": article['summary']}}]},
                    "created_at": {"date": {"start": article.get('created_at', None)}}
                }
                if existing_page:
                    page_id = existing_page['id']
                    self.client.pages.update(page_id=page_id, properties=properties)
                    logger.debug(f"既存ページを更新しました: {article['title']}")
                    return True, False, page_id
                else:
                    response = self.client.pages.create(
                        parent={"database_id": self.database_id},
                        properties=properties
                    )
                    page_id = response.get('id')
                    logger.info(f"新規ページを作成しました: {article['title']}")
                    return True, True, page_id
            except APIResponseError as e:
                if hasattr(e, 'status') and e.status == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Notion API レート制限。{wait_time}秒後にリトライします (試行{attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Notion API エラー: {e}")
                    return False, False, None
            except Exception as e:
                logger.error(f"Notion API その他エラー: {e}")
                return False, False, None
        logger.error("Notion API リトライ上限に達しました")
        return False, False, None
        
    def bulk_upsert_articles(self, articles: List[dict]) -> Tuple[int, int, int, List[dict]]:
        """
        複数の記事を一括でアップサート
        
        Args:
            articles (list): 記事データのリスト
            
        Returns:
            tuple: (成功件数, 新規作成件数, エラー件数)
        """
        success_count = 0
        new_count = 0
        error_count = 0
        new_articles = []
        
        for article in articles:
            try:
                success, is_new, page_id = self.upsert_article(article)
                
                if success:
                    success_count += 1
                    if is_new:
                        new_count += 1
                        new_articles.append(article)
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"記事アップサート中にエラーが発生: {e}")
                error_count += 1
        
        logger.info(f"Notionデータベース更新結果: 成功 {success_count}, 新規 {new_count}, エラー {error_count}")
        return success_count, new_count, error_count, new_articles