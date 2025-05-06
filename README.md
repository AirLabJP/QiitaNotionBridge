# 📚 Qiita → Notion ハイライト・ブリッジ

人気の Qiita 記事を自動で取得し、Notion データベースに転送するアプリケーション。  
いいね（LGTM）または Stock 数が**指定した閾値以上**の記事のみを対象とします。  
**Notion DBのカラム（プロパティ）が足りなければ自動で追加**します。

---

## 🚀 主な機能

- Qiita API から過去N日分の記事を取得
- LGTM または Stock 数が指定値以上の人気記事を抽出
- 本文を自動要約（sumy + tinysegmenter）
- Notion データベースに upsert（新規追加 or 更新）
- 新規追加記事があればコンソール＆app.logに出力
- **Notion DBにカラムがなければ自動で追加**
- CLI対話式・自動化（定時実行）どちらも対応
- **全自動テスト（pytest）付き**

---

## 🔧 セットアップ手順

### 1. リポジトリのクローン

```sh
git clone https://github.com/AirLabJP/QiitaNotionBridge.git
cd QiitaNotionBridge
```

---

### 2. 必要なトークンの取得

#### Qiita アクセストークン

1. [Qiita](https://qiita.com/) で「個人用アクセストークン」を発行（`read_qiita`スコープ）

#### Notion Integration トークンと DB ID

1. [Notion](https://www.notion.so/) でインテグレーションを作成し、Internal Integration Tokenを取得
2. Notionでデータベースを作成（下記スキーマを参照）
3. データベース右上「⋮」→「Add connections」で Integration を接続
4. データベースURLからIDを取得（32桁のハイフン付きID）

---

### 3. Notion データベース スキーマ

| プロパティ名 | 型               | 説明               |
| ------------ | ---------------- | ------------------ |
| `title`      | タイトル型       | 記事タイトル       |
| `url`        | URL型            | 記事のURL          |
| `author`     | テキスト型       | 投稿者のユーザー名 |
| `likes`      | 数値型           | LGTM数             |
| `stocks`     | 数値型           | ストック数         |
| `tags`       | マルチセレクト型 | タグ一覧           |
| `created_at` | 日付型           | 投稿日             |
| `summary`    | テキスト型       | 自動要約の内容     |

> **カラムが足りない場合は自動で追加されます！**

---

### 4. 環境変数の設定

`.env.example` を `.env` にコピーし、各トークンとDB IDを記入：

```sh
cp .env.example .env
```

---

### 5. 依存パッケージのインストール

```sh
pip install -r requirements.txt
```

---

### 6. テストの実行

```sh
pytest
```

---

## 🖥️ 使い方

### 対話式（手動実行）

```sh
python main.py
```

- CLIで「最低いいね数」「最低ストック数」「バックフィル日数」を日本語で入力
- 1回だけ実行して終了

### 自動化（定時実行・サーバー運用）

```sh
python main.py --schedule --min-likes 500 --min-stocks 500 --backfill-days 1
```

- 毎日07:00に自動実行
- CLIプロンプトはスキップ

### バックフィル実行（過去データの一括取得）

```sh
python main.py --backfill days=3 --min-likes 300 --min-stocks 200
```

---

## 📝 ログファイル出力

- すべてのログは`app.log`にも出力されます（INFO以上）

---

## 🛡️ セキュリティ・注意事項

- `.env`は`.gitignore`済み。**絶対に公開しないこと**
- Notion Integrationには必要最小限の権限のみ付与
- summary（要約）は著作権・フェアユースに注意
- トークンの形式・長さチェックあり

---

## 🧪 テスト・保守

- pytestによる自動テスト付き
- requirements.txtはバージョン固定
- Notion DBのカラム自動追加
- 型ヒント・docstring・ロギングも充実

---

## 💡 拡張アイデア

- Slack通知・Webhook連携
- タグごとの閾値設定
- Notion DBプロパティの自動検証・自動作成
- Web UIやダッシュボード

---

## 📝 ライセンス

MIT License

---

## 🙌 コントリビューション

PR・Issue歓迎！  
テストが通ることを確認してから送ってください。
