# ✨ Twitter/X AIO 🐦

A powerful Python-based tool designed to automate various interactions on X (formerly Twitter). This bot leverages unofficial GraphQL API endpoints to perform actions like posting, commenting, liking, and searching for tweets.

![showoff](https://i.imgur.com/PSptpYP.png)

---

## 🚀 Features

*   **Post Tweets:** Create and publish new tweets directly from the command line.
*   **Comment on Tweets:**
    *   Comment on specific tweets by ID.
    *   **Mass Commenting:** Search for tweets based on a keyword and automatically post a predefined comment on them.
*   **Like Tweets:**
    *   Send a like to a specific tweet by ID.
    *   **Mass Liking:** Use multiple accounts (via `auth_token`s) to like a single tweet.
*   **Search Tweets:** Find recent tweets based on specific keywords.
*   **Proxy Support:** Route requests through an HTTP/HTTPS proxy for anonymity or to bypass restrictions.
*   **User Data Fetching:** Fetches basic user data upon login to verify session validity.
*   **Session Management:** Utilizes `requests.Session` for persistent cookies and headers.
*   **Automatic Bearer Token Extraction:** Attempts to fetch the necessary bearer token from X's JavaScript files.

---

## 📋 Prerequisites

*   Python 3.10+
*   `pip` (Python package installer)

---

## ⚙️ Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/RobMCQuack/Twitter-AIO-Tool.git
    cd Twitter-AIO-Tool
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure `proxy.txt` (Optional):**
    If you want to use a proxy, create a file named `proxy.txt` in the `config` directory of the project.
    The file should contain a single line with your proxy details in the format:
    `username:password@host:port` (if authentication is required)
    OR
    `host:port` (if no authentication)

4.  **Configure `config/comment.cfg` (For Mass Commenting):**
    Edit the file named `comment.cfg` inside the `config` directory.
    This file defines the comment text and the keyword for searching tweets to comment on.

5.  **Configure `file/tokens.txt` (For Mass Liking):**
    Edit the file named `tokens.txt` inside the `config` directory.
    Each line in this file should be an `auth_token` from a different X account. This is used for the "Mass Like" feature.

---

## 💡 Usage

Run the script from your terminal:

```bash
py twitter_aio.py
```

---

## ⚠️ Important Notes & Potential Issues

*   **Rate Limiting:** X aggressively rate-limits unofficial API usage. Performing too many actions in a short period can lead to temporary blocks or errors. The script includes `time.sleep()` calls, but you might need to adjust them.
*   **API Stability:** Since this bot relies on unofficial endpoints, any change by X to their internal API structure can break the bot. This is particularly true for bearer token extraction and GraphQL query IDs/payloads.
*   **Account Safety:** Automation can be detected. Avoid overly aggressive or spammy behavior.
*   **Error Handling:** While some error handling is present, it might not cover all scenarios. If you encounter persistent errors, it could be due to X API changes, invalid tokens, or network issues.
*   **CSRF Token (`ct0`):** This token is crucial for POST requests. It's obtained during the `login_and_sync_cookies` process. If it's missing or invalid, POST actions will fail.
*   **Bearer Token:** The `bearer_token` is essential for most API calls. If the bot fails to extract it (e.g., if X changes its JS files), most functionalities will break.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements, new features, or bug fixes, please feel free to help.

---

