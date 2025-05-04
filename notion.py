#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notion データベースとの連携を担当するモジュール
"""

import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# ロギング設定
logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()

class NotionClient:
    """Notion API クライアント"""
    
    def __init__(self, token=None, database_id=None):
        """初期化"""
        self.token = token or os.getenv('NOTION_TOKEN')
        if not self.token:
            raise ValueError("Notion APIトークンが設定されていません")
            
        self.database_id = database_id or os.getenv('NOTION_DB_ID')
        if not self.database_id:
            raise ValueError("Notion データベースIDが設定されていません")
            
        # Notion クライアント初期化
        self.client = Client(auth=self.token)
        
    def _check_database(self):
        """データベースが存在し、必要なプロパティを持っているか確認"""
        try:
            db = self.client.databases.retrieve(self.database_id)
            properties = db.get('properties', {})
            
            # 必要なプロパティ一覧
            required_props = {
                'title': 'title',
                'url': 'url',
                'author': 'rich_text',
                'likes': 'number',
                'tags': 'multi_select',
                'summary': 'rich_text'
            }
            
            # プロパティチェック
            missing_props = []
            for prop_name, prop_type in required_props.items():
                if prop_name not in properties:
                    missing_props.append(prop_name)
                elif properties[prop_name]['type'] != prop_type:
                    missing_props.append(f"{prop_name} ({prop_type})")
            
            if missing_props:
                logger.warning(f"データベースに必要なプロパティがありません: {', '.join(missing_props)}")
                return False
                
            return True
            
        except APIResponseError as e:
            logger.error(f"データベース接続エラー: {e}")
            return False
            
    def search_page_by_url(self, url):
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

    def upsert_article(self, article):
        """
        記事をNotionデータベースに追加/更新
        
        Args:
            article (dict): 記事データ
            
        Returns:
            tuple: (成功したか, 新規作成したか, ページID)
        """
        # データベース構造を確認
        if not self._check_database():
            logger.error("Notionデータベースの構造が不適切です")
            return False, False, None
        
        # 既存ページをURLで検索
        existing_page = self.search_page_by_url(article['url'])
        
        try:
            # Notionページ用プロパティを作成
            properties = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": article['title']
                            }
                        }
                    ]
                },
                "url": {
                    "url": article['url']
                },
                "author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article['author']
                            }
                        }
                    ]
                },
                "likes": {
                    "number": article['likes']
                },
                "tags": {
                    "multi_select": [{"name": tag} for tag in article['tags'][:10]]  # 上限に注意
                },
                "summary": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article['summary']
                            }
                        }
                    ]
                }
            }
            
            # 既存ページの更新または新規作成
            if existing_page:
                # 既存ページを更新
                page_id = existing_page['id']
                self.client.pages.update(page_id=page_id, properties=properties)
                logger.debug(f"既存ページを更新しました: {article['title']}")
                return True, False, page_id
            else:
                # 新規ページ作成
                response = self.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties
                )
                page_id = response.get('id')
                logger.info(f"新規ページを作成しました: {article['title']}")
                return True, True, page_id
                
        except APIResponseError as e:
            logger.error(f"Notion API エラー: {e}")
            return False, False, None
            
    def bulk_upsert_articles(self, articles):
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
