# GitHub Actionsでの自動実行セットアップ

GitHub Actionsを使用すると、**無料で24時間365日自動実行**できます。

## セットアップ手順

### 1. GitHubリポジトリを作成

1. GitHubにログイン
2. 新しいリポジトリを作成（プライベート推奨）
3. このプロジェクトをプッシュ

```bash
cd /Users/user/Desktop/YUKIbot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/YUKIbot.git
git push -u origin main
```

### 2. GitHub Secretsに認証情報を設定

1. リポジトリのページで「Settings」をクリック
2. 左メニューから「Secrets and variables」→「Actions」を選択
3. 「New repository secret」をクリック
4. 以下の4つのシークレットを追加：

   - **Name**: `TWITTER_API_KEY`
     **Value**: `XNqZbCJcQFFHbiBKdsSxpTMY8`

   - **Name**: `TWITTER_API_KEY_SECRET`
     **Value**: `VPDucAW6c1Q4J8sYQkkiHrJO4llkmEXI4T34M1aMapPEjMDlLg`

   - **Name**: `TWITTER_ACCESS_TOKEN`
     **Value**: `2009223159044882432-GrW6n5OozjHWa8lIrDgQsRaZCJITPE`

   - **Name**: `TWITTER_ACCESS_TOKEN_SECRET`
     **Value**: `EfJl2NeWz952Sls6Kmo4w3Mh5W8tVfqVnyN0K7NktN1Zk`

### 3. ワークフローの確認

`.github/workflows/yuki_bot.yml` ファイルが正しく作成されていることを確認してください。

### 4. 初回実行

1. リポジトリのページで「Actions」タブをクリック
2. 左メニューから「YUKI INFO監視bot」を選択
3. 「Run workflow」ボタンをクリックして手動実行をテスト

## 動作確認

- 「Actions」タブで実行履歴を確認できます
- 緑色のチェックマークが表示されれば成功
- エラーがある場合は、ログを確認してください

## 実行スケジュール

- **自動実行**: 毎時0分（1時間ごと）
- **手動実行**: 「Actions」タブから「Run workflow」でいつでも実行可能

## GitHub Actionsの無料プラン

- **プライベートリポジトリ**: 2,000分/月まで無料
- **パブリックリポジトリ**: 無制限（無料）

1時間ごとの実行 = 約720分/月なので、**無料プランで十分利用可能**です。

## トラブルシューティング

### 認証エラーが発生する場合

- GitHub Secretsが正しく設定されているか確認
- シークレット名が正確か確認（大文字小文字を区別）

### 記事が取得できない場合

- ワークフローのログを確認
- Seleniumが必要な場合、ChromeDriverのセットアップが必要かもしれません

### 実行されない場合

- 「Actions」タブでワークフローが有効になっているか確認
- スケジュール設定（cron）が正しいか確認

## メリット

✅ **完全無料**（無料プランで十分）  
✅ **24時間365日自動実行**（PCが起動している必要がない）  
✅ **ログが自動保存**（実行履歴を確認可能）  
✅ **手動実行も可能**（いつでもテスト可能）
