from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # Use a different model
config["quick_think_llm"] = "gpt-4o-mini"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Example integration with FinnHub and DeepSeek APIs
import os
import finnhub
from openai import OpenAI


def get_market_data(symbol: str, resolution: str = 'D', start: int = None, end: int = None):
    """Fetch market data from FinnHub API"""
    api_key = os.environ.get('FINNHUB_API_KEY')
    client = finnhub.Client(api_key=api_key)
    return client.stock_candles(symbol, resolution, start, end)


def deepseek_decision(market_data):
    """Generate trading decision using DeepSeek API"""
    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )
    messages = [
        {"role": "system", "content": "你是一个交易决策助手，根据行情数据给出买/卖或观望建议。"},
        {"role": "user", "content": f"以下是市场行情数据：{market_data}\n请给出买入、卖出或观望的建议，并说明理由。"}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
