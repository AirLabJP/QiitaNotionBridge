# 📚 Qiita → Notion ハイライト・ブリッジ

人気の Qiita 記事を自動で取得し、Notion データベースに転送するアプリケーションです。  
いいね（LGTM）または Stock 数が **500以上** の記事のみを対象とします。

---

## 🚀 機能概要

- Qiita API から過去24時間分の記事を取得
- LGTM または Stock 数が 500 以上の人気記事を抽出
- Notion データベースに upsert（更新 or 新規追加）
- 新規追加記事があれば、コンソールに結果を出力
- summary は `sumy` + `tinysegmenter` による日本語対応の自動要約

---

## 🔧 セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourname/qiita-notion-bridge.git
cd qiita-notion-bridge
```

---

### 2. 必要なトークンの取得

#### ✅ Qiita アクセストークンの取得方法

1. [Qiita](https://qiita.com/) にログイン
2. 右上のユーザーアイコン →「設定」→「アプリケーション」
3. 「個人用アクセストークン」を新規発行（`read_qiita`スコープを選択）

#### ✅ Notion Integration トークンと DB ID の取得方法

1. [Notion](https://www.notion.so/) にログイン
2. [My Integrations](https://www.notion.so/my-integrations) にアクセスし、「+ New integration」で作成
3. 権限を設定し、`Internal Integration Token` を取得
4. Notion データベースを作成（下記スキーマを参照）
5. データベース右上「⋮」→「Add connections」で Integration を接続
6. データベースURLから ID を取得（URL中の英数字）

---

### 3. Notion データベース スキーマ

以下のプロパティを含むデータベースを作成してください：

| プロパティ名   | 型               | 説明               |
|----------------|------------------|--------------------|
| `title`        | タイトル型       | 記事タイトル       |
| `url`          | URL型            | 記事のURL          |
| `author`       | テキスト型       | 投稿者のユーザー名 |
| `likes`        | 数値型           | LGTM数             |
| `stocks`       | 数値型           | ストック数         |
| `tags`         | マルチセレクト型 | タグ一覧           |
| `created_at`   | 日付型 or テキスト型 | 投稿日       |
| `summary`      | テキスト型       | 自動要約の内容     |

---

### 4. 環境変数の設定

`.env.example` を `.env` にコピーし、各トークンとDB IDを記入してください：

```bash
cp .env.example .env
```

#### `.env` の例：

```env
QIITA_TOKEN=your_qiita_token
NOTION_TOKEN=your_notion_token
NOTION_DB_ID=your_notion_database_id
```

※ `.env` は `.gitignore` により GitHub には含まれません。

---

### 5. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

#### requirements.txt の内容（参考）:

```
requests
schedule
notion-client
python-dotenv
sumy
tinysegmenter
lxml_html_clean
setuptools
```

---

### 6. 実行方法

#### 通常モード（毎日定期取得）

```bash
python main.py
```

#### バックフィルモード（過去データ取得）

```bash
python main.py --backfill days=3
```

> `--backfill days=3` で過去3日分の人気記事を一括取得してNotionに登録します。

---

## 📦 出力例

```bash
✅ 新規追加: 「PythonでGPTを使ってみた」 by user123
✅ 新規追加: 「FastAPI入門」 by dev567
🔁 既存記事: 「Gitの使い方」はすでにDBに存在
```

#### summary出力イメージ（Notion上）:

```text
PythonとOpenAI APIを使って簡単なチャットボットを作成する手順を紹介。実行環境、APIキーの取得、エラーハンドリングの注意点などがわかりやすく解説されている。
```

---

## 🌐 Replitで利用する場合の補足

- 「Secrets」タブで `.env` の各変数を追加してください
- `main.py` を run コマンドに設定しておくとクリック実行可能です
- スリープ防止には外部Pingサービスを使うと安定します

---

## ⚠️ 注意点

- summary は `sumy` + `tinysegmenter` による日本語自動要約
- Notion DBのプロパティは **上記スキーマに厳密に従う必要あり**
- Slack通知・Webhookなどの連携は未実装
- アプリはローカル or Replit 上で動作します（Webホスティング不要）

---

## 💡 拡張アイデア（今後の開発候補）

- ✅ Slack通知連携
- ✅ Elasticsearchでの全文検索連携
- ✅ LINE Notify 通知
- ✅ タグフィルタリング機能（Notionタグを利用）
- ✅ Notion内ダッシュボード自動生成
- ✅ フロントエンドでのビジュアライズ表示（Streamlitなど）

---

## 🔒 セキュリティに関して

- アクセストークンは環境変数 `.env` で管理してください
- Notion Integration には **必要最小限のDBへのアクセスのみ** 付与してください
- 公開リポジトリでは絶対に `.env` をコミットしないでください

---

## 🙌 協力・問い合わせ

ご意見・プルリク歓迎です！  
ご連絡は [@AirLabJP](https://github.com/AirLabJP) まで。