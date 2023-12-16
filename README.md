# 🚀 Crypto AI Tweet Trader 🚀 

A powerful, innovative, and real-time crypto trading bot that triggers trades based on keywords from Twitter tweets.

## 🎯 Features

- 📱 **Real-time Twitter Monitoring**: Our bot monitors keywords from Tweets in real-time, triggering trades in a split second.
- 📈 **Trade Multiple Cryptos Concurrently**: Multi-threading enables multiple trades to occur at the same time.
- 💰 **Dynamic Adjustments**: Buy amounts are requested in $ and dynamically adjusted to valid crypto amounts based on the latest exchange rate.
- 🛠️ **Customizable Trading Strategies**: Specify your own keywords and coins to implement any trade strategies.
- 💼 **Supports Binance & Kraken Exchanges**: API keys are kept securely in a separate json file.
- ⌛ **Graceful Exit**: When you hit ctrl-c, it waits for the trades to sell automatically according to the specification then closes the program.

<p align="center">
  <img src="https://github.com/jaimindp/Twitter_Activated_Crypto_Trading_Bot/blob/main/elon_2.gif">
</p>


## 🚀 Getting Started

### Installation


pip install -r requirements.txt
Running with Binance (single ticker):
Edit config.json to add your API keys.

Example config.json


{
    "twitter_keys": {
        "consumer_key": "YOUR_CONSUMER_KEY",
        "consumer_secret": "YOUR_CONSUMER_SECRET",
        "access_token_key": "YOUR_ACCESS_TOKEN_KEY",
        "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    }
}


## 📝 Notes
A Twitter Developer API is required to detect tweets through Tweepy.
A crypto exchange (Kraken/Binance) API is required and used through ccxt (cryptocurrency exchange trading library).
ccxt allows universal function calls to be used on multiple exchanges; adding a new exchange should not be difficult as long as ccxt has the same functions implemented.
If anything is not working correctly, please let us know!


## 💡 Future Improvements
Futures trading up to 100x leverage.
More exchanges to be supported.
Advanced trading strategies based on more complex tweet analysis.

## 🚩 Disclaimer
Investing in cryptocurrencies is risky, and you may lose all your capital. Please use this bot responsibly and at your own risk.

## 📭 Contact
For any queries or issues, feel free to contact us. We appreciate your feedback.

🌟 Don't forget to star the repository if you find it useful. Happy trading! 🌟
