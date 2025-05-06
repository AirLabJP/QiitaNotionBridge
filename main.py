#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qiita → Notion ハイライト・ブリッジ
メインスクリプト: スケジューリングとコマンドライン引数を処理します
"""

import argparse
import logging
import os
import sys
import time
import unicodedata

import schedule
from dotenv import load_dotenv

from tasks import daily_job

# ロギング設定
LOG_FILE = "app.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()

def validate_environment():
    """必要な環境変数が設定されているか確認"""
    required_vars = [
        'QIITA_TOKEN',
        'NOTION_TOKEN',
        'NOTION_DB_ID'
    ]
    
    # Raycast関連は削除されたため、必須環境変数から除外
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"環境変数が未設定です: {', '.join(missing_vars)}")
        logger.error("環境変数は Replit Secrets または .env ファイルで設定してください")
        return False
    
    return True

def get_int_input(prompt: str, default: int) -> int:
    while True:
        s = input(f"{prompt} [{default}]: ")
        s = unicodedata.normalize('NFKC', s.strip())
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            print("数字で入力してください（例: 300）")

def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='Qiita記事をNotion DBに転送するサービス'
    )
    parser.add_argument('--no-interactive', action='store_true', help='対話プロンプトをスキップ')
    parser.add_argument('--min-likes', type=int, help='最低いいね数')
    parser.add_argument('--min-stocks', type=int, help='最低ストック数')
    parser.add_argument('--backfill-days', type=int, help='バックフィル日数')
    parser.add_argument('--backfill', type=str, help='過去データの一括取得（例: days=3）')
    parser.add_argument('--schedule', action='store_true', help='定時実行モード（サーバー用）')
    return parser.parse_args()

def main():
    """メイン関数"""
    # 環境変数チェック
    if not validate_environment():
        sys.exit(1)
        
    args = parse_arguments()
    
    if args.no_interactive:
        min_likes = args.min_likes or 500
        min_stocks = args.min_stocks or 500
        backfill_days = args.backfill_days or 1
    else:
        min_likes = get_int_input("記事の最低いいね数を入力してください", 500)
        min_stocks = get_int_input("記事の最低ストック数を入力してください", 500)
        backfill_days = get_int_input("バックフィル日数を入力してください", 1)
    
    # バックフィルモード
    if args.backfill:
        try:
            key, value = args.backfill.split('=')
            if key == 'days':
                days = int(value)
                if days > 0:
                    logger.info(f"過去 {days} 日分のデータを一括取得します")
                    daily_job(backfill_days=days, min_likes=min_likes, min_stocks=min_stocks)
                    return
        except (ValueError, AttributeError):
            pass
            
        logger.error("バックフィル引数の形式が不正です。正しい形式: --backfill days=3")
        sys.exit(1)
    
    if args.no_interactive or args.schedule:
        logger.info("Qiita → Notion ハイライト・ブリッジ 起動")
        logger.info("毎日 07:00 JSTに実行されるようスケジュール設定しました")
        schedule.every().day.at("07:00").do(lambda: daily_job(backfill_days=backfill_days, min_likes=min_likes, min_stocks=min_stocks))
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("プログラムを終了します")
        except Exception as e:
            logger.exception(f"予期せぬエラーが発生しました: {e}")
            sys.exit(1)
    else:
        logger.info("手動実行モード: 1回だけ実行して終了します")
        daily_job(backfill_days=backfill_days, min_likes=min_likes, min_stocks=min_stocks)
        logger.info("手動実行完了。プログラムを終了します")
        sys.exit(0)

if __name__ == "__main__":
    main()
