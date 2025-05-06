#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qiitaからの記事取得を担当するモジュール
"""

import logging
import os
import time
from datetime import datetime, timedelta
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import requests
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

from utils import format_datetime, parse_iso_datetime

# ロギング設定
logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()


class QiitaClient:
    """Qiita API クライアント"""

    BASE_URL = "https://qiita.com/api/v2"
    PER_PAGE = 100  # 1リクエストあたりの最大取得件数
    RATE_LIMIT = 60  # 1分あたりのリクエスト上限

    def __init__(self, token: Optional[str] = None) -> None:
        """初期化"""
        self.token = token or os.getenv("QIITA_TOKEN")
        if not self.token or len(self.token) < 20:
            raise ValueError("Qiita APIトークンの形式が不正です（20文字以上の英数字）")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """APIリクエストを実行"""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            # レート制限情報をログ出力
            remaining = response.headers.get("Rate-Remaining", "Unknown")
            logger.debug(f"Qiita API レート制限残り: {remaining}")

            # レート制限に達しそうな場合は待機
            if remaining and int(remaining) < 5:
                logger.warning(
                    f"Qiita API レート制限に近づいています（残り: {remaining}）"
                )
                time.sleep(10)  # 10秒待機

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Qiita API リクエストエラー: {e}")
            if hasattr(e.response, "status_code") and e.response.status_code == 429:
                wait_time = int(e.response.headers.get("Retry-After", 60))
                logger.warning(f"レート制限に達しました。{wait_time}秒待機します")
                time.sleep(wait_time)
            raise

    @staticmethod
    def get_summary(
        text: str, language: str = "japanese", sentences_count: int = 3
    ) -> str:
        """
        テキストを要約する関数

        Args:
            text (str): 要約するテキスト
            language (str): 言語（日本語の場合は"japanese"）
            sentences_count (int): 要約後の文の数

        Returns:
            str: 要約されたテキスト
        """
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        stemmer = Stemmer(language)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        # 要約を生成
        summary_sentences = summarizer(parser.document, sentences_count)
        summary = " ".join([str(sentence) for sentence in summary_sentences])

        return summary

    def get_popular_articles(
        self, days: int = 1, min_likes: int = 500, min_stocks: int = 500
    ) -> List[dict]:
        """
        指定日数以内の人気記事を取得

        Args:
            days (int): 何日前までの記事を取得するか
            min_likes (int): 最低いいね数（LGTM or Stock）
            min_stocks (int): 最低ストック数（LGTM or Stock）

        Returns:
            list: 条件を満たす記事のリスト
        """
        # 日付範囲を計算 (タイムゾーン情報を含む)
        from utils import get_date_range

        start_date, end_date = get_date_range(days)

        # 日付文字列に変換
        date_str = format_datetime(start_date)

        logger.info(f"{date_str} 以降の記事を検索中...")

        page = 1
        all_articles = []
        popular_articles = []
        has_next = True

        # ページネーションで全記事を取得
        while has_next:
            # 検索クエリ
            query = f"created:>={date_str}"
            params = {"query": query, "per_page": self.PER_PAGE, "page": page}

            logger.debug(f"Qiita検索: {query} (ページ {page})")

            try:
                results = self._make_request("items", params)

                if not results:
                    logger.debug("検索結果がありません")
                    break

                all_articles.extend(results)
                logger.info(
                    f"合計 {len(all_articles)} 記事を取得しました (ページ {page})"
                )

                # 次のページがあるか判断
                has_next = len(results) == self.PER_PAGE
                page += 1

                # API制限に達しないよう1秒スリープ
                time.sleep(1)

            except Exception as e:
                logger.error(f"記事取得中にエラーが発生しました: {e}")
                break

        # 人気記事をフィルタリング
        for article in all_articles:
            article_date = parse_iso_datetime(article["created_at"])

            # 日付が範囲内かチェック
            # タイムゾーン情報を無視してUTCとして比較
            article_date_naive = article_date.replace(tzinfo=None)
            start_date_naive = start_date.replace(tzinfo=None)
            end_date_naive = end_date.replace(tzinfo=None)

            if start_date_naive <= article_date_naive <= end_date_naive:
                # いいね数またはストック数が条件を満たすか
                likes = article.get("likes_count", 0)
                stocks = article.get("stocks_count", 0)

                if likes >= min_likes or stocks >= min_stocks:
                    popular_articles.append(article)

        logger.info(
            f"{len(all_articles)} 記事中、{len(popular_articles)} 件が条件に一致しました"
        )
        return popular_articles

    def format_article_for_notion(self, article: dict) -> dict:
        """
        Qiita記事をNotion用に整形

        Args:
            article (dict): Qiita API から取得した記事データ

        Returns:
            dict: Notion用にフォーマットされた記事データ
        """
        # タグ情報を抽出
        tags = [tag["name"] for tag in article.get("tags", [])]

        # 本文を要約
        body = article.get("body", "")
        if len(body) > 300:
            summary = self.get_summary(body)
        else:
            summary = body[:300]

        return {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "author": article.get("user", {}).get(
                "name", article.get("user", {}).get("id", "")
            ),
            "likes": article.get("likes_count", 0),
            "stocks": article.get("stocks_count", 0),
            "tags": tags,
            "created_at": article.get("created_at", ""),
            "summary": summary,
        }

    @staticmethod
    def summarize_text(text: str, sentence_count: int = 3) -> str:
        # Implementation of summarize_text method
        pass
