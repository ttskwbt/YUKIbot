#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YUKI公式サイトのINFOセクションを監視し、最新記事があればツイートするbot
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import tweepy
import schedule

# Selenium（JavaScriptで動的に読み込まれるコンテンツ用）
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠ Seleniumがインストールされていません。JavaScriptで読み込まれるコンテンツは取得できません。")

# 環境変数を読み込む
load_dotenv()

# 設定
YUKI_URL = "https://www.yukiweb.net/"
INFO_URL = "https://www.yukiweb.net/info/"
LAST_CHECKED_FILE = "last_checked.json"
CHECK_INTERVAL = 60  # 1時間 = 60分

class YUKIBot:
    def __init__(self):
        """初期化：Twitter API認証（OAuth 1.0a必須）"""
        # Twitter API認証情報を取得
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_key_secret = os.getenv("TWITTER_API_KEY_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        # 必須認証情報のチェック
        missing = []
        if not self.api_key:
            missing.append("TWITTER_API_KEY")
        if not self.api_key_secret:
            missing.append("TWITTER_API_KEY_SECRET")
        if not self.access_token:
            missing.append("TWITTER_ACCESS_TOKEN")
        if not self.access_token_secret:
            missing.append("TWITTER_ACCESS_TOKEN_SECRET")
        
        if missing:
            error_msg = f"以下の認証情報が不足しています: {', '.join(missing)}\n"
            error_msg += "\nツイート投稿にはOAuth 1.0a認証が必要です。\n"
            error_msg += "Twitter Developer Portalで以下を取得してください：\n"
            error_msg += "1. API Key (Consumer Key)\n"
            error_msg += "2. API Key Secret (Consumer Secret)\n"
            error_msg += "3. Access Token\n"
            error_msg += "4. Access Token Secret\n"
            error_msg += "\n取得方法はREADME.mdを参照してください。"
            raise ValueError(error_msg)
        
        # OAuth 1.0a認証（ツイート投稿に必須）
        try:
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_key_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            # 認証テスト（自分のアカウント情報を取得）
            me = self.client.get_me()
            print(f"✓ Twitter認証成功（OAuth 1.0a）")
            print(f"  認証ユーザー: @{me.data.username}")
        except tweepy.Unauthorized as e:
            raise Exception(f"Twitter認証に失敗しました。認証情報を確認してください: {e}")
        except Exception as e:
            raise Exception(f"Twitter認証エラー: {e}")
    
    def _fetch_with_selenium(self):
        """Seleniumを使ってJavaScriptで動的に読み込まれるコンテンツを取得"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # ヘッドレスモード
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # GitHub Actions環境ではchromiumを使用
            if os.getenv('GITHUB_ACTIONS') == 'true':
                chrome_options.binary_location = '/usr/bin/chromium-browser'
                from selenium.webdriver.chrome.service import Service
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.get(INFO_URL)
            
            # ページが読み込まれるまで待機（最大10秒）
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "infoTitle"))
                )
            except:
                # infoTitleが見つからなくても、少し待ってからHTMLを取得
                time.sleep(3)
            
            html = driver.page_source
            driver.quit()
            
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            print(f"   Seleniumでの取得に失敗: {e}")
            return None
    
    def fetch_info_articles(self):
        """YUKI公式サイトのINFOページから記事を取得"""
        try:
            # まず通常のrequestsで試す
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            response = requests.get(INFO_URL, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'lxml')
            articles = []
            
            # まず通常の方法で記事を探す
            info_titles = soup.find_all(class_='infoTitle')
            
            # 記事が見つからない場合、SeleniumでJavaScriptを実行して取得
            if not info_titles and SELENIUM_AVAILABLE:
                print("   JavaScriptで動的に読み込まれるコンテンツを取得中...")
                soup = self._fetch_with_selenium()
                if soup:
                    info_titles = soup.find_all(class_='infoTitle')
            
            # 複数の方法で記事を探す
            # 方法1: class="infoTitle"の要素を探す
            info_titles = soup.find_all(class_='infoTitle')
            
            # 方法2: 大文字小文字を区別しない検索
            if not info_titles:
                info_titles = soup.find_all(class_=lambda x: x and 'infotitle' in x.lower())
            
            # 方法3: すべての要素から"infoTitle"を含むクラスを探す
            if not info_titles:
                all_with_class = soup.find_all(True, class_=True)
                for elem in all_with_class:
                    classes = elem.get('class', [])
                    if any('infotitle' in str(c).lower() for c in classes):
                        info_titles.append(elem)
            
            # 方法4: リンクから記事を推測（/info/で始まるリンク）
            if not info_titles:
                info_links = soup.find_all('a', href=lambda x: x and '/info/' in x and x != '/info/')
                for link in info_links:
                    # リンクのテキストや親要素からタイトルを取得
                    title = link.get_text(strip=True)
                    if not title:
                        # 親要素からタイトルを取得
                        parent = link.find_parent(['li', 'div', 'article'])
                        if parent:
                            title = parent.get_text(strip=True)[:100]
                    
                    if title and len(title) > 5:
                        href = link.get('href', '')
                        if href.startswith('/'):
                            href = f"https://www.yukiweb.net{href}"
                        elif not href.startswith('http'):
                            href = f"{INFO_URL}{href}"
                        
                        articles.append({
                            'title': title,
                            'url': href,
                            'date': '',
                            'timestamp': datetime.now().isoformat()
                        })
            
            for title_elem in info_titles:
                # タイトルテキストを取得
                title = title_elem.get_text(strip=True)
                
                # リンクを探す（親要素または子要素のaタグ）
                link = title_elem.find('a', href=True)
                if not link:
                    # 親要素にリンクがある場合
                    parent = title_elem.find_parent('a', href=True)
                    if parent:
                        link = parent
                
                if link:
                    href = link.get('href', '')
                    
                    # 相対URLを絶対URLに変換
                    if href.startswith('/'):
                        href = f"https://www.yukiweb.net{href}"
                    elif not href.startswith('http'):
                        href = f"{INFO_URL}{href}"
                    
                    # 日付を探す（同じ親要素内または近くの要素から）
                    date_text = None
                    parent_container = title_elem.find_parent(['li', 'div', 'article', 'section'])
                    if parent_container:
                        # 日付らしい要素を探す（class="date"や"日付"を含む要素など）
                        date_elem = parent_container.find(class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                        if date_elem:
                            date_text = date_elem.get_text(strip=True)
                        else:
                            # 日付形式のテキストを探す（YYYY/MM/DD形式など）
                            import re
                            date_pattern = r'\d{4}[/\-年]\d{1,2}[/\-月]\d{1,2}[日]?'
                            container_text = parent_container.get_text()
                            date_match = re.search(date_pattern, container_text)
                            if date_match:
                                date_text = date_match.group(0)
                    
                    if title and href:
                        article = {
                            'title': title,
                            'url': href,
                            'date': date_text or '',
                            'timestamp': datetime.now().isoformat()
                        }
                        articles.append(article)
            
            if articles:
                print(f"✓ {len(articles)}件の記事を取得しました")
            else:
                print("⚠ 記事が見つかりませんでした。")
                # デバッグ用: 実際のHTML構造を確認
                print("   デバッグ: HTML構造を確認中...")
                
                # infoTitleクラスを探す
                info_titles_debug = soup.find_all(class_='infoTitle')
                print(f"   class='infoTitle'の要素数: {len(info_titles_debug)}")
                
                # 大文字小文字を区別しない検索
                all_elements = soup.find_all(class_=True)
                info_related = [elem for elem in all_elements if 'info' in str(elem.get('class', '')).lower()]
                print(f"   'info'を含むクラスの要素数: {len(info_related)}")
                
                if info_related:
                    print("   見つかったクラス名（最初の5件）:")
                    for i, elem in enumerate(info_related[:5], 1):
                        classes = elem.get('class', [])
                        text = elem.get_text(strip=True)[:50]
                        print(f"   {i}. クラス: {classes}, テキスト: {text}")
                
                # リンクを探す
                all_links = soup.find_all('a', href=True)
                info_links = [link for link in all_links if '/info/' in link.get('href', '')]
                print(f"   '/info/'を含むリンク数: {len(info_links)}")
                if info_links:
                    print("   見つかったリンク（最初の3件）:")
                    for i, link in enumerate(info_links[:3], 1):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)[:50]
                        print(f"   {i}. {text} -> {href}")
            
            return articles
            
        except Exception as e:
            print(f"❌ 記事の取得に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def load_last_checked(self):
        """前回チェックした記事の情報を読み込む"""
        if os.path.exists(LAST_CHECKED_FILE):
            try:
                with open(LAST_CHECKED_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'last_articles': []}
        return {'last_articles': []}
    
    def save_last_checked(self, articles):
        """チェックした記事の情報を保存"""
        data = {
            'last_check': datetime.now().isoformat(),
            'last_articles': articles
        }
        with open(LAST_CHECKED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def is_new_article(self, article, last_articles):
        """記事が新規かどうかを判定"""
        for last_article in last_articles:
            if article['url'] == last_article.get('url'):
                return False
        return True
    
    def create_tweet(self, article):
        """ツイート本文を作成"""
        title = article['title']
        url = article['url']
        date = article.get('date', '')
        
        # Twitterの文字数制限（280文字）を考慮
        max_length = 280
        url_length = len(url) + 3  # URL + スペース + 改行相当
        date_length = len(date) + 3 if date else 0  # 日付がある場合
        
        # タイトルが長すぎる場合は切り詰める
        available_length = max_length - url_length - date_length - 20  # 余裕を持たせる
        if len(title) > available_length:
            title = title[:available_length - 3] + "..."
        
        # ツイート本文を作成
        if date:
            tweet_text = f"【YUKI INFO更新】\n{title}\n{date}\n{url}"
        else:
            tweet_text = f"【YUKI INFO更新】\n{title}\n{url}"
        
        return tweet_text
    
    def tweet_article(self, article):
        """記事をツイート"""
        try:
            tweet_text = self.create_tweet(article)
            response = self.client.create_tweet(text=tweet_text)
            print(f"✓ ツイート成功: {article['title']}")
            print(f"  ツイートID: {response.data['id']}")
            return True
        except Exception as e:
            print(f"❌ ツイートに失敗しました: {e}")
            return False
    
    def check_and_tweet(self):
        """記事をチェックして、新規があればツイート"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 記事をチェック中...")
        
        # 記事を取得
        articles = self.fetch_info_articles()
        
        if not articles:
            print("⚠ 記事が見つかりませんでした")
            return
        
        print(f"✓ {len(articles)}件の記事を取得しました")
        
        # 前回チェックした記事を読み込む
        last_data = self.load_last_checked()
        last_articles = last_data.get('last_articles', [])
        
        # 初回実行かどうかをチェック
        is_first_run = len(last_articles) == 0
        
        if is_first_run:
            print("ℹ 初回実行のため、記事を記録します（ツイートはしません）")
            # 初回は記事を保存するだけで、ツイートしない
            self.save_last_checked(articles)
            print(f"✓ {len(articles)}件の記事を記録しました。次回から新規記事があればツイートします。")
            return
        
        # 新規記事をチェック（URLで重複判定）
        new_articles = []
        last_urls = {article.get('url', '') for article in last_articles}
        
        for article in articles:
            article_url = article.get('url', '')
            # URLが前回の記録にない場合、新規記事と判定
            if article_url and article_url not in last_urls:
                new_articles.append(article)
        
        if new_articles:
            print(f"✓ {len(new_articles)}件の新規記事を発見しました")
            
            # 新規記事をツイート（記事リストの順序に従う。通常は最新が最初）
            for article in new_articles:
                self.tweet_article(article)
                time.sleep(2)  # レート制限を避けるため少し待つ
        else:
            print("ℹ 新規記事はありませんでした（すべて既にチェック済みです）")
        
        # 今回チェックした記事を保存（最新の状態を保持）
        self.save_last_checked(articles)
    
    def run(self):
        """botを起動"""
        print("=" * 50)
        print("YUKI INFO監視botを起動しました")
        print(f"チェック間隔: {CHECK_INTERVAL}分")
        print("=" * 50)
        
        # 初回チェック
        self.check_and_tweet()
        
        # 定期実行をスケジュール
        schedule.every(CHECK_INTERVAL).minutes.do(self.check_and_tweet)
        
        # メインループ
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにスケジュールをチェック
        except KeyboardInterrupt:
            print("\n\nbotを停止します...")


def main():
    """メイン関数"""
    import sys
    
    # コマンドライン引数で実行モードを切り替え
    # --once: 1回だけチェックして終了（launchd用）
    # デフォルト: 継続実行モード
    run_once = '--once' in sys.argv
    
    try:
        bot = YUKIBot()
        
        if run_once:
            # launchd用: 1回だけチェックして終了
            print("=" * 50)
            print("YUKI INFO監視bot（1回実行モード）")
            print("=" * 50)
            bot.check_and_tweet()
            print("\n✓ チェック完了")
        else:
            # 通常モード: 継続実行
            bot.run()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
