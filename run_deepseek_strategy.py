import os
import time
from datetime import datetime, timedelta
import finnhub
from openai import OpenAI

# Load API keys from environment
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not FINNHUB_API_KEY or not DEEPSEEK_API_KEY:
    raise RuntimeError("Please set FINNHUB_API_KEY and DEEPSEEK_API_KEY in the environment or .env file.")

# Initialize FinnHub client
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# Initialize DeepSeek client (using OpenAI SDK)
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def get_market_data(symbol: str, days: int = 30):
    """Fetch recent market data for the given symbol from FinnHub."""
    end_time = int(time.time())
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())
    data = finnhub_client.stock_candles(symbol, "D", start_time, end_time)
    return data

def deepseek_decision(market_data):
    """Call DeepSeek API to generate buy/sell/hold recommendation."""
    messages = [
        {"role": "system", "content": "你是一个交易决策助手，根据行情数据给出买/卖或观望建议。"},
        {"role": "user", "content": f"以下是市场行情数据：{market_data}\n请给出买入、卖出或观望的建议，并说明理由。"}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    symbol = "NVDA"
    data = get_market_data(symbol, days=30)
    suggestion = deepseek_decision(data)
    print(f"{symbol} 的交易建议：\n{suggestion}")
