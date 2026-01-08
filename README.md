# YUKI INFO監視bot

YUKI公式サイト（https://www.yukiweb.net/）のINFOセクションを1時間ごとに監視し、最新記事があれば自動的にツイートするbotです。

## 機能

- YUKI公式サイトのINFOセクションを1時間ごとにクロール
- 新規記事を自動検出
- 新規記事をTwitterに自動投稿
- 重複投稿を防止（前回チェックした記事を記録）

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip3 install -r requirements.txt
```

**注意**: macOSでは`pip`ではなく`pip3`を使用してください。

### 2. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の内容を記述してください：

```env
# Twitter API認証情報（OAuth 1.0a - ツイート投稿に必須）
TWITTER_API_KEY=
TWITTER_API_KEY_SECRET=
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```



### 3. Twitter APIのAccess TokenとAccess Token Secretの取得

**ツイート投稿にはOAuth 1.0a認証が必須です。** 以下の手順でAccess TokenとAccess Token Secretを取得してください：

#### 手順

1. **Twitter Developer Portalにアクセス**
   - https://developer.twitter.com/en/portal/dashboard にログイン

2. **アプリを選択または作成**
   - 既存のアプリを選択するか、新しいアプリを作成

3. **Keys and tokensタブを開く**
   - アプリの詳細ページで「Keys and tokens」タブをクリック

4. **Access Token and Secretを生成**
   - 「Access Token and Secret」セクションで「Generate」ボタンをクリック
   - 表示されたAccess TokenとAccess Token Secretをコピー

5. **権限設定の確認**
   - 「App permissions」で「Read and Write」が選択されていることを確認
   - 変更した場合は「Save」をクリック

6. **`.env`ファイルに追加**
   - 取得したAccess TokenとAccess Token Secretを`.env`ファイルに追加

#### 注意事項

- Access TokenとAccess Token Secretは一度しか表示されません。必ず安全な場所に保存してください
- アプリの権限を「Read and Write」に変更した場合、Access TokenとAccess Token Secretを再生成する必要があります
- アプリの設定で「OAuth 1.0a」が有効になっていることを確認してください

## 使い方

### botの起動

```bash
python3 yuki_bot.py
```

**注意**: macOSでは`python`ではなく`python3`を使用してください。

botは起動後、すぐに初回チェックを実行し、その後1時間ごとに自動的にチェックを続けます。

### 停止方法

`Ctrl + C` を押すとbotが停止します。

### 24時間自動実行（launchd使用）

PCを閉じていても自動実行するには、macOSのlaunchdを使用します。

#### セットアップ

```bash
cd /Users/user/Desktop/YUKIbot
./setup_launchd.sh
```

これで、1時間ごとに自動的にチェックが実行されます。

#### 管理コマンド

```bash
# 停止
launchctl unload ~/Library/LaunchAgents/com.yukibot.plist

# 開始
launchctl load ~/Library/LaunchAgents/com.yukibot.plist

# 状態確認
launchctl list | grep yukibot

# ログ確認
tail -f /Users/user/Desktop/YUKIbot/yuki_bot.log
```

#### 注意事項

- launchdを使用する場合、PCが起動している必要があります
- PCをスリープさせると実行されません（スリープ解除時に再開）
- 完全に24時間365日実行するには、常時起動しているサーバーやクラウドサービスを使用することを推奨します

## ファイル構成

- `yuki_bot.py` - メインのbotコード
- `.env` - 環境変数（認証情報、手動作成が必要）
- `last_checked.json` - 前回チェックした記事の記録（自動生成）
- `requirements.txt` - 必要なPythonパッケージ
- `.gitignore` - Git除外設定

## 動作の仕組み

1. YUKI公式サイトにアクセスし、INFOセクションから記事を取得
2. 前回チェックした記事と比較して新規記事を判定
3. 新規記事があれば、Twitterにツイート
4. チェックした記事の情報を `last_checked.json` に保存
5. 1時間後に再度チェック

## トラブルシューティング

### 認証エラーが発生する場合

- `.env` ファイルが正しく作成されているか確認
- Twitter Developer Portalでアプリの権限設定を確認
- OAuth 1.0a認証が必要な場合は、Access TokenとAccess Token Secretを取得して追加

### 記事が取得できない場合

- インターネット接続を確認
- YUKI公式サイトのHTML構造が変更されている可能性があります（`yuki_bot.py`の`fetch_info_articles`メソッドを調整）

### ツイートが投稿されない場合

- Twitter APIのレート制限に達していないか確認
- アプリに「Read and Write」権限が付与されているか確認
- OAuth 1.0a認証が必要な場合は、Access Tokenを設定

## 注意事項

- このbotは個人利用を想定しています
- Twitter APIの利用規約を遵守してください
- 過度なリクエストは避け、レート制限に注意してください
- ウェブサイトのHTML構造が変更されると、記事の取得に失敗する可能性があります

## ライセンス

このプロジェクトは個人利用を目的としています。
