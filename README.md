# Qiita → Notion ハイライト・ブリッジ

毎日人気の Qiita 記事を自動的に取得し、Notion データベースに転送するアプリケーションです。
500以上のいいね（LGTM）または Stock を獲得した記事を抽出します。

## 機能

- Qiita APIから過去24時間の記事を取得
- LGTM または Stock 数が 500 以上の記事を抽出
- Notion データベースに記事情報を upsert
- 新規追加記事があればコンソールに出力

## セットアップ手順

### 1. 必要なトークンの取得

#### Qiita アクセストークン
1. [Qiita](https://qiita.com/) にログイン
2. 右上のユーザーアイコンをクリック → 「設定」を選択
3. 左メニューから「アプリケーション」を選択
4. 「個人用アクセストークン」セクションで「新しくトークンを発行する」をクリック
5. トークンの説明と有効期限を設定し、`read_qiita` スコープを選択
6. 「発行する」をクリックしてトークンを取得

#### Notion トークンとデータベース ID
1. [Notion](https://www.notion.so/) にログイン
2. [My Integrations](https://www.notion.so/my-integrations) ページにアクセス
3. 「+ New integration」をクリックして新しいインテグレーションを作成
4. インテグレーション名を入力し、アクセス権限を設定して「Submit」をクリック
5. 表示された「Internal Integration Token」を保存
6. Notion内で転送先のデータベースを作成（下記の必須プロパティを含む）
   - title (タイトル): タイトル型
   - url (URL): URL型
   - author (著者): テキスト型
   - likes (いいね数): 数値型
   - stocks (ストック数): 数値型
   - tags (タグ): マルチセレクト型
   - created_at (作成日): 日付型またはテキスト型
   - summary (概要): テキスト型
7. データベースページで「⋮」→「Add connections」からインテグレーションを連携
8. データベースのURLから ID を取得:
   `https://www.notion.so/{workspace}/{database_id}?v=...`

### 2. 環境変数の設定

このプロジェクトでは Replit Secrets を使用して環境変数を管理します。

1. Replit プロジェクトページで「Secrets」タブを開く
2. 以下の環境変数を追加:
   - `QIITA_TOKEN`: Qiita アクセストークン
   - `NOTION_TOKEN`: Notion インテグレーショントークン
   - `NOTION_DB_ID`: Notion データベース ID

ローカル開発の場合は、`.env.example` をコピーして `.env` ファイルを作成し、値を設定してください。

### 3. 依存関係のインストール

```bash
pip install requests schedule notion-client python-dotenv
```

### 4. 実行方法

#### 通常実行（スケジュールモード）
```bash
python main.py
```

#### バックフィル実行（過去データの一括取得）
```bash
python main.py --backfill days=3
```

## 拡張アイデア

以下のような機能拡張が考えられます：

- Slack通知機能の追加
- Elasticsearch連携によるタグベース検索
- LINE Notify連携
- ダッシュボード機能の追加
- タグベースのフィルタリング
