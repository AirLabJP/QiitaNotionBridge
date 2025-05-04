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

import schedule
from dotenv import load_dotenv

from tasks import daily_job

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
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

def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='Qiita記事をNotion DBに転送するサービス'
    )
    
    parser.add_argument(
        '--backfill',
        type=str,
        help='過去データの一括取得（例: days=3）'
    )
    
    return parser.parse_args()

def main():
    """メイン関数"""
    # 環境変数チェック
    if not validate_environment():
        sys.exit(1)
        
    args = parse_arguments()
    
    # バックフィルモード
    if args.backfill:
        try:
            key, value = args.backfill.split('=')
            if key == 'days':
                days = int(value)
                if days > 0:
                    logger.info(f"過去 {days} 日分のデータを一括取得します")
                    daily_job(backfill_days=days)
                    return
        except (ValueError, AttributeError):
            pass
            
        logger.error("バックフィル引数の形式が不正です。正しい形式: --backfill days=3")
        sys.exit(1)
    
    # 定期実行モード
    logger.info("Qiita → Notion ハイライト・ブリッジ 起動")
    logger.info("毎日 07:00 JSTに実行されるようスケジュール設定しました")
    
    # スケジュール設定
    schedule.every().day.at("07:00").do(daily_job)
    
    try:
        # テスト実行
        logger.info("初回実行中...")
        daily_job()
        logger.info("初回実行完了。スケジュールモードに移行します")
        
        # メインループ
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにスケジュールをチェック
    except KeyboardInterrupt:
        logger.info("プログラムを終了します")
    except Exception as e:
        logger.exception(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
