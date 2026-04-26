from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# ─── CRYPTO ───────────────────────────────────────────────
CRYPTO_COINS = {
    "BTC":  {"name": "Bitcoin",     "binance": "BTCUSDT",  "kraken": "XBTUSD",   "coinbase": "BTC-USD",  "bybit": "BTCUSDT"},
    "ETH":  {"name": "Ethereum",    "binance": "ETHUSDT",  "kraken": "ETHUSD",   "coinbase": "ETH-USD",  "bybit": "ETHUSDT"},
    "XRP":  {"name": "XRP",         "binance": "XRPUSDT",  "kraken": "XRPUSD",   "coinbase": "XRP-USD",  "bybit": "XRPUSDT"},
    "BNB":  {"name": "BNB",         "binance": "BNBUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BNBUSDT"},
    "SOL":  {"name": "Solana",      "binance": "SOLUSDT",  "kraken": "SOLUSD",   "coinbase": "SOL-USD",  "bybit": "SOLUSDT"},
    "DOGE": {"name": "Dogecoin",    "binance": "DOGEUSDT", "kraken": "XDGUSD",   "coinbase": "DOGE-USD", "bybit": "DOGEUSDT"},
    "ADA":  {"name": "Cardano",     "binance": "ADAUSDT",  "kraken": "ADAUSD",   "coinbase": "ADA-USD",  "bybit": "ADAUSDT"},
    "TON":  {"name": "Toncoin",     "binance": "TONUSDT",  "kraken": None,        "coinbase": None,       "bybit": "TONUSDT"},
    "TRX":  {"name": "Tron",        "binance": "TRXUSDT",  "kraken": "TRXUSD",   "coinbase": "TRX-USD",  "bybit": "TRXUSDT"},
    "AVAX": {"name": "Avalanche",   "binance": "AVAXUSDT", "kraken": "AVAXUSD",  "coinbase": "AVAX-USD", "bybit": "AVAXUSDT"},
    "SHIB": {"name": "Shiba Inu",   "binance": "SHIBUSDT", "kraken": "SHIBUSD",  "coinbase": "SHIB-USD", "bybit": "SHIBUSDT"},
    "LINK": {"name": "Chainlink",   "binance": "LINKUSDT", "kraken": "LINKUSD",  "coinbase": "LINK-USD", "bybit": "LINKUSDT"},
    "DOT":  {"name": "Polkadot",    "binance": "DOTUSDT",  "kraken": "DOTUSD",   "coinbase": "DOT-USD",  "bybit": "DOTUSDT"},
    "USDT": {"name": "Tether",      "binance": None,        "kraken": None,        "coinbase": "USDT-USD", "bybit": None},
    "USDC": {"name": "USD Coin",    "binance": None,        "kraken": None,        "coinbase": "USDC-USD", "bybit": None},
}

CRYPTO_EXCHANGE_LINKS = {
    "Binance": "https://www.binance.com",
    "Kraken": "https://www.kraken.com",
    "Coinbase": "https://www.coinbase.com",
    "Bybit": "https://www.bybit.com",
}

# ─── STOCKS ───────────────────────────────────────────────
POLYGON_API_KEY = "AHDx47kyKxiVlcwWs5jP1WjiY2ExUPkC"

TOP_STOCKS = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","JPM","V",
    "WMT","XOM","UNH","LLY","MA","JNJ","PG","HD","MRK","COST",
    "ABBV","CVX","BAC","KO","PEP","ADBE","CRM","NFLX","AMD","TMO",
    "ACN","MCD","CSCO","ABT","LIN","DHR","WFC","TXN","NEE","PM",
    "RTX","AMGN","LOW","ORCL","UPS","INTC","QCOM","CAT","NOW","INTU"
]

# ─── FOREX ────────────────────────────────────────────────
FOREX_PAIRS = [
    {"pair": "EUR/USD", "base": "EUR", "quote": "USD"},
    {"pair": "GBP/USD", "base": "GBP", "quote": "USD"},
    {"pair": "USD/JPY", "base": "USD", "quote": "JPY"},
    {"pair": "USD/CHF", "base": "USD", "quote": "CHF"},
    {"pair": "AUD/USD", "base": "AUD", "quote": "USD"},
    {"pair": "USD/CAD", "base": "USD", "quote": "CAD"},
    {"pair": "NZD/USD", "base": "NZD", "quote": "USD"},
    {"pair": "EUR/GBP", "base": "EUR", "quote": "GBP"},
    {"pair": "EUR/JPY", "base": "EUR", "quote": "JPY"},
    {"pair": "GBP/JPY", "base": "GBP", "quote": "JPY"},
]

# ─── CRYPTO DATA ──────────────────────────────────────────
def fetch_binance_prices():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=6)
        return {d["symbol"]: {"price": round(float(d["lastPrice"]),8), "change": round(float(d["priceChangePercent"]),2)} for d in r.json()}
    except:
        return {}

def fetch_kraken_prices():
    pairs = [v["kraken"] for v in CRYPTO_COINS.values() if v.get("kraken")]
    try:
        r = requests.get("https://api.kraken.com/0/public/Ticker", params={"pair": ",".join(pairs)}, timeout=6)
        result = r.json().get("result", {})
        out = {}
        for key, val in result.items():
            price = round(float(val["c"][0]), 8)
            open_price = float(val["o"])
            change = round(((price - open_price) / open_price) * 100, 2) if open_price else 0
            out[key] = {"price": price, "change": change}
        return out
    except:
        return {}

def fetch_coinbase_prices():
    out = {}
    for sym, info in CRYPTO_COINS.items():
        pair = info.get("coinbase")
        if not pair:
            continue
        try:
            r = requests.get("https://api.coinbase.com/v2/prices/" + pair + "/spot", timeout=4)
            price = round(float(r.json()["data"]["amount"]), 8)
            r2 = requests.get("https://api.coinbase.com/v2/prices/" + pair + "/historic?period=day", timeout=4)
            prices_hist = r2.json().get("data", {}).get("prices", [])
            change = 0
            if prices_hist:
                old = float(prices_hist[-1]["price"])
                change = round(((price - old) / old) * 100, 2) if old else 0
            out[pair] = {"price": price, "change": change}
        except:
            pass
    return out

def fetch_bybit_prices():
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers", params={"category": "spot"}, timeout=6)
        return {d["symbol"]: {"price": round(float(d["lastPrice"]),8), "change": round(float(d.get("price24hPcnt","0"))*100,2)} for d in r.json().get("result",{}).get("list",[])}
    except:
        return {}

def get_crypto_prices():
    binance = fetch_binance_prices()
    kraken = fetch_kraken_prices()
    coinbase = fetch_coinbase_prices()
    bybit = fetch_bybit_prices()
    result = {}
    for sym, info in CRYPTO_COINS.items():
        exchanges = {}
        changes = []
        if info.get("binance") and info["binance"] in binance:
            d = binance[info["binance"]]
            exchanges["Binance"] = d["price"]
            changes.append(d["change"])
        if info.get("kraken"):
            for key in kraken:
                if info["kraken"].upper() in key.upper() or key.upper() in info["kraken"].upper():
                    d = kraken[key]
                    exchanges["Kraken"] = d["price"]
                    changes.append(d["change"])
                    break
        if info.get("coinbase") and info["coinbase"] in coinbase:
            d = coinbase[info["coinbase"]]
            exchanges["Coinbase"] = d["price"]
            changes.append(d["change"])
        if info.get("bybit") and info["bybit"] in bybit:
            d = bybit[info["bybit"]]
            exchanges["Bybit"] = d["price"]
            changes.append(d["change"])
        avg_change = round(sum(changes)/len(changes), 2) if changes else 0
        result[sym] = {"name": info["name"], "symbol": sym, "exchanges": exchanges, "change24h": avg_change}
    return result

def get_crypto_chart(symbol):
    info = CRYPTO_COINS.get(symbol.upper(), {})
    kraken_pair = info.get("kraken")
    if kraken_pair:
        try:
            r = requests.get("https://api.kraken.com/0/public/OHLC", params={"pair": kraken_pair, "interval": 60}, timeout=8)
            data = r.json().get("result", {})
            for key in data:
                if key != "last":
                    candles = data[key][-24:]
                    return [{"t": int(c[0])*1000, "p": round(float(c[4]), 8)} for c in candles]
        except:
            pass
    return []

# ─── STOCKS DATA (Polygon.io free tier) ───────────────────
import concurrent.futures

# Hardcoded names since reference API costs extra calls
STOCK_NAMES = {
    "AAPL":"Apple Inc.","MSFT":"Microsoft Corp.","NVDA":"NVIDIA Corp.","AMZN":"Amazon.com Inc.",
    "GOOGL":"Alphabet Inc.","META":"Meta Platforms","TSLA":"Tesla Inc.","BRK-B":"Berkshire Hathaway",
    "JPM":"JPMorgan Chase","V":"Visa Inc.","WMT":"Walmart Inc.","XOM":"Exxon Mobil",
    "UNH":"UnitedHealth Group","LLY":"Eli Lilly","MA":"Mastercard Inc.","JNJ":"Johnson & Johnson",
    "PG":"Procter & Gamble","HD":"Home Depot","MRK":"Merck & Co.","COST":"Costco Wholesale",
    "ABBV":"AbbVie Inc.","CVX":"Chevron Corp.","BAC":"Bank of America","KO":"Coca-Cola Co.",
    "PEP":"PepsiCo Inc.","ADBE":"Adobe Inc.","CRM":"Salesforce Inc.","NFLX":"Netflix Inc.",
    "AMD":"Advanced Micro Devices","TMO":"Thermo Fisher Scientific","ACN":"Accenture plc",
    "MCD":"McDonald's Corp.","CSCO":"Cisco Systems","ABT":"Abbott Laboratories",
    "LIN":"Linde plc","DHR":"Danaher Corp.","WFC":"Wells Fargo","TXN":"Texas Instruments",
    "NEE":"NextEra Energy","PM":"Philip Morris","RTX":"RTX Corp.","AMGN":"Amgen Inc.",
    "LOW":"Lowe's Companies","ORCL":"Oracle Corp.","UPS":"United Parcel Service",
    "INTC":"Intel Corp.","QCOM":"Qualcomm Inc.","CAT":"Caterpillar Inc.",
    "NOW":"ServiceNow Inc.","INTU":"Intuit Inc."
}

def get_stock_prices():
    result = {}
    # Use grouped daily bars — one call, all tickers, free tier compatible
    # Gets previous trading day data for all US stocks
    try:
        # Find the most recent trading day (skip weekends)
        check_date = datetime.now() - timedelta(days=1)
        for _ in range(7):
            if check_date.weekday() < 5:  # Mon-Fri
                break
            check_date -= timedelta(days=1)
        date_str = check_date.strftime("%Y-%m-%d")

        r = requests.get(
            f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date_str}",
            params={"adjusted": "true", "apiKey": POLYGON_API_KEY},
            timeout=20
        )
        data = r.json()
        bars = {b["T"]: b for b in data.get("results", [])}

        for sym in TOP_STOCKS:
            poly_sym = sym.replace("-", ".")
            bar = bars.get(poly_sym) or bars.get(sym)
            if not bar:
                continue
            c = float(bar.get("c", 0))
            o = float(bar.get("o", 0))
            h = float(bar.get("h", 0))
            l = float(bar.get("l", 0))
            v = int(bar.get("v", 0))
            vw = float(bar.get("vw", 0))
            change = round(((c - o) / o) * 100, 2) if o else 0
            result[sym] = {
                "name": STOCK_NAMES.get(sym, sym),
                "symbol": sym,
                "price": round(c, 2),
                "change24h": change,
                "open": round(o, 2),
                "high": round(h, 2),
                "low": round(l, 2),
                "volume": v,
                "vwap": round(vw, 2),
            }
    except Exception as e:
        pass

    return result

def get_stock_chart(symbol):
    poly_sym = symbol.replace("-", ".")
    # Try last 7 days to find a trading day with intraday data
    for days_back in range(0, 7):
        date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        try:
            r = requests.get(
                f"https://api.polygon.io/v2/aggs/ticker/{poly_sym}/range/5/minute/{date}/{date}",
                params={"adjusted": "true", "sort": "asc", "limit": 200, "apiKey": POLYGON_API_KEY},
                timeout=10
            )
            results = r.json().get("results", [])
            if results:
                return [{"t": int(bar["t"]), "p": round(float(bar["c"]), 4)} for bar in results]
        except:
            continue
    return []

# ─── FOREX DATA ───────────────────────────────────────────
def get_rate_for_pair(rates_dict, base, quote):
    if not rates_dict:
        return None
    rates_dict["USD"] = 1.0
    try:
        if base == "USD":
            return rates_dict.get(quote)
        elif quote == "USD":
            br = rates_dict.get(base)
            return 1/br if br else None
        else:
            br = rates_dict.get(base)
            qr = rates_dict.get(quote)
            return qr/br if br and qr else None
    except:
        return None

def get_forex_rates():
    result = {}

    # Current rates
    try:
        r = requests.get("https://api.frankfurter.app/latest", params={"from": "USD"}, timeout=8)
        current_usd = r.json().get("rates", {})
        current_usd["USD"] = 1.0
    except:
        current_usd = {}

    # Historical rates for 1d, 10d, 30d
    hist = {}
    for days in [1, 10, 30]:
        # Frankfurter only has weekday data, so walk back until we get a hit
        got = {}
        for offset in range(days, days + 5):
            try:
                date_str = (datetime.now() - timedelta(days=offset)).strftime("%Y-%m-%d")
                r = requests.get("https://api.frankfurter.app/" + date_str, params={"from": "USD"}, timeout=8)
                got = r.json().get("rates", {})
                if got:
                    got["USD"] = 1.0
                    break
            except:
                continue
        hist[days] = got

    for fp in FOREX_PAIRS:
        base = fp["base"]
        quote = fp["quote"]
        pair = fp["pair"]
        rate = get_rate_for_pair(current_usd, base, quote)
        if not rate:
            continue
        entry = {"pair": pair, "base": base, "quote": quote, "rate": round(rate, 6)}

        for days in [1, 10, 30]:
            old_rate = get_rate_for_pair(hist[days], base, quote)
            if old_rate:
                chg = round(((rate - old_rate) / old_rate) * 100, 4)
                entry["change" + str(days) + "d"] = chg

        result[pair] = entry

    # Compare with exchangerate-api
    try:
        r2 = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        er_rates = r2.json().get("rates", {})
        er_rates["USD"] = 1.0
        for pair_key, data in result.items():
            rate2 = get_rate_for_pair(er_rates, data["base"], data["quote"])
            if rate2:
                data["rate2"] = round(rate2, 6)
    except:
        pass

    return result

def get_forex_chart(base, quote):
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        url = "https://api.frankfurter.app/" + start + ".." + end
        r = requests.get(url, params={"from": base, "to": quote}, timeout=8)
        data = r.json()
        rates = data.get("rates", {})
        result = []
        for date_str in sorted(rates.keys()):
            rate = rates[date_str].get(quote)
            if rate:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                result.append({"t": int(dt.timestamp())*1000, "p": round(float(rate), 6)})
        return result
    except:
        return []

# ─── ROUTES ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/crypto")
def api_crypto():
    return jsonify(get_crypto_prices())

@app.route("/api/crypto/chart/<symbol>")
def api_crypto_chart(symbol):
    return jsonify(get_crypto_chart(symbol))

@app.route("/api/stocks")
def api_stocks():
    return jsonify(get_stock_prices())

@app.route("/api/stocks/chart/<symbol>")
def api_stock_chart(symbol):
    return jsonify(get_stock_chart(symbol))

@app.route("/api/forex")
def api_forex():
    return jsonify(get_forex_rates())

@app.route("/api/forex/chart/<base>/<quote>")
def api_forex_chart(base, quote):
    return jsonify(get_forex_chart(base, quote))

HTML = """<!DOCTYPE html>
<html>
<head>
<title>JSCAN</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230a0a0a'/><text y='.9em' font-size='80' font-family='Arial' font-weight='bold' fill='%2300ff88'>J</text></svg>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.header{padding:20px 40px;border-bottom:1px solid #1c1c1c;display:flex;align-items:center;justify-content:space-between;background:#050505;position:sticky;top:0;z-index:100}
.logo{font-size:1.4em;font-weight:700;color:#00ff88;letter-spacing:-0.5px}
.logo span{color:#fff}
.subtitle{color:#555;font-size:.78em;margin-top:2px}
.header-right{display:flex;align-items:center;gap:15px}
.last-updated{color:#444;font-size:.78em}
.refresh-btn{background:transparent;border:1px solid #222;color:#555;padding:6px 14px;border-radius:7px;cursor:pointer;font-size:.78em;font-family:inherit;transition:all .2s}
.refresh-btn:hover{border-color:#00ff88;color:#00ff88}
.tabs{display:flex;gap:0;border-bottom:1px solid #1c1c1c;background:#050505;padding:0 40px}
.tab-btn{background:transparent;border:none;color:#555;padding:14px 24px;cursor:pointer;font-size:.9em;font-weight:500;font-family:inherit;border-bottom:2px solid transparent;transition:all .2s;letter-spacing:.2px}
.tab-btn:hover{color:#ccc}
.tab-btn.active{color:#00ff88;border-bottom-color:#00ff88}
.tab-content{display:none}
.tab-content.active{display:block}
.container{padding:28px 40px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(560px,1fr));gap:14px}
.card{background:#0d0d0d;border:1px solid #1c1c1c;border-radius:14px;overflow:hidden;transition:border-color .2s}
.card:hover{border-color:#2a2a2a}
.card-header{padding:18px 22px 14px;display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid #141414}
.card-ticker{display:flex;align-items:center;gap:8px;margin-bottom:3px}
.card-symbol{font-size:1.15em;font-weight:700;color:#fff;letter-spacing:-.3px}
.card-name{font-size:.78em;color:#555}
.chart-btn{color:#2a2a2a;font-size:.7em;cursor:pointer;padding:2px 7px;border:1px solid #1c1c1c;border-radius:4px;transition:all .2s;text-decoration:none;background:transparent;font-family:inherit}
.chart-btn:hover{color:#00ff88;border-color:#00ff88}
.card-right{text-align:right}
.card-price{font-size:1.45em;font-weight:600;color:#00ff88;font-variant-numeric:tabular-nums;letter-spacing:-.5px}
.card-change{font-size:.82em;font-weight:600;margin-top:3px}
.change-pos{color:#00ff88}
.change-neg{color:#ff4444}
.change-flat{color:#555}
.stats-bar{display:flex;background:#080808;border-bottom:1px solid #141414}
.stat{flex:1;padding:10px 14px;border-right:1px solid #141414}
.stat:last-child{border-right:none}
.stat-label{font-size:.65em;color:#444;text-transform:uppercase;letter-spacing:.7px;margin-bottom:3px;font-weight:500}
.stat-value{font-size:.86em;font-weight:600}
.green{color:#00ff88}.red{color:#ff4444}.yellow{color:#f0c040}.gray{color:#444}
.chart-section{padding:14px 22px 12px;border-bottom:1px solid #141414;position:relative;background:#090909}
.section-label{font-size:.65em;color:#333;text-transform:uppercase;letter-spacing:.7px;margin-bottom:8px;font-weight:500}
.chart-wrap{position:relative;height:68px;width:100%;cursor:crosshair}
.chart-wrap svg{width:100%;height:100%}
.tooltip{position:absolute;background:#111;border:1px solid #1c1c1c;border-radius:7px;padding:5px 9px;font-size:.73em;pointer-events:none;display:none;white-space:nowrap;z-index:10;box-shadow:0 4px 12px rgba(0,0,0,.6)}
.tooltip-price{color:#00ff88;font-weight:600}
.tooltip-time{color:#444;margin-top:1px;font-size:.9em}
.no-chart{color:#222;font-size:.76em;text-align:center;padding-top:22px}
.ex-table{width:100%;border-collapse:collapse}
.ex-table th{padding:9px 22px;text-align:left;font-size:.65em;color:#444;text-transform:uppercase;letter-spacing:.7px;border-bottom:1px solid #141414;font-weight:500}
.ex-table td{padding:10px 22px;font-size:.84em;border-bottom:1px solid #111;color:#ccc}
.ex-table tr:last-child td{border-bottom:none}
.ex-table tbody tr:hover td{background:#0f0f0f}
.ex-link{color:#bbb;font-weight:500;text-decoration:none;transition:color .15s}
.ex-link:hover{color:#00ff88}
.ex-price{font-variant-numeric:tabular-nums;color:#e0e0e0;font-weight:500}
.badge{display:inline-block;padding:2px 8px;border-radius:5px;font-size:.68em;font-weight:600}
.badge-buy{background:rgba(0,255,136,.08);color:#00ff88;border:1px solid rgba(0,255,136,.2)}
.badge-sell{background:rgba(255,68,68,.08);color:#ff4444;border:1px solid rgba(255,68,68,.2)}
.diff-pos{color:#ff5555;font-weight:500}.diff-zero{color:#333}
.stocks-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.stock-card{background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:16px 18px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:border-color .2s}
.stock-card:hover{border-color:#2a2a2a}
.stock-sym{font-size:1em;font-weight:700;color:#fff}
.stock-name{font-size:.75em;color:#555;margin-top:2px;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.stock-right{text-align:right}
.stock-price{font-size:1.05em;font-weight:600;color:#e0e0e0;font-variant-numeric:tabular-nums}
.stock-change{font-size:.78em;font-weight:600;margin-top:3px}
.stock-meta{font-size:.68em;color:#444;margin-top:4px;font-variant-numeric:tabular-nums}
.stock-prev{font-size:.68em;color:#444;margin-top:3px;font-variant-numeric:tabular-nums}
.forex-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}
.forex-card{background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:18px 20px;transition:border-color .2s}
.forex-card:hover{border-color:#2a2a2a}
.forex-pair{font-size:1.1em;font-weight:700;color:#fff}
.forex-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.forex-changes{display:flex;margin-bottom:12px;border:1px solid #141414;border-radius:8px;overflow:hidden;background:#080808}
.forex-change-item{flex:1;padding:8px 12px;border-right:1px solid #141414;text-align:center}
.forex-change-item:last-child{border-right:none}
.forex-rates{display:flex;gap:12px;flex-wrap:wrap}
.forex-source{background:#080808;border:1px solid #141414;border-radius:8px;padding:10px 14px;flex:1;min-width:130px}
.forex-source-name{font-size:.65em;color:#444;text-transform:uppercase;letter-spacing:.7px;margin-bottom:4px}
.forex-rate{font-size:1.05em;font-weight:600;color:#00ff88;font-variant-numeric:tabular-nums}
.forex-spread{font-size:.75em;color:#555;margin-top:8px}
.forex-spread span{color:#f0c040;font-weight:600}
.forex-chart-section{margin-top:12px;position:relative}
.loading-screen{display:flex;flex-direction:column;align-items:center;justify-content:center;height:40vh;gap:14px}
.spinner{width:32px;height:32px;border:2px solid #1a1a1a;border-top-color:#00ff88;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.ld{color:#333;font-size:.85em}
.section-header{font-size:.8em;color:#444;text-transform:uppercase;letter-spacing:.8px;font-weight:500;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #141414}
.modal-bg{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.93);z-index:999;align-items:center;justify-content:center;padding:30px}
.modal-bg.open{display:flex}
.modal-box{background:#0d0d0d;border:1px solid #1c1c1c;border-radius:16px;padding:26px;max-width:660px;width:100%;position:relative}
.modal-close{position:absolute;top:14px;right:14px;background:transparent;border:1px solid #1c1c1c;color:#555;width:26px;height:26px;border-radius:6px;cursor:pointer;transition:all .2s}
.modal-close:hover{border-color:#ff4444;color:#ff4444}
.modal-title{font-size:1em;font-weight:600;color:#fff;margin-bottom:16px}
.modal-chart-wrap{height:180px;width:100%;position:relative;cursor:crosshair}
</style>
<script>
var chartCache = {};
var cryptoData = {};
var stockData = {};

var CRYPTO_LINKS = {
    "Binance":"https://www.binance.com",
    "Kraken":"https://www.kraken.com",
    "Coinbase":"https://www.coinbase.com",
    "Bybit":"https://www.bybit.com"
};

function fmt(p) {
    if(p>=1000) return '$'+p.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
    if(p>=1) return '$'+p.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
    if(p>=0.0001) return '$'+p.toFixed(6);
    return '$'+p.toFixed(8);
}
function fmtTime(ts){return new Date(ts).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});}
function changeClass(c){return c>0?'change-pos':c<0?'change-neg':'change-flat';}
function changeStr(c){return (c>0?'+':'')+c.toFixed(2)+'%';}

function drawChart(wrapId,points,tooltipId,dateMode){
    var wrap=document.getElementById(wrapId);
    if(!wrap)return;
    if(!points||!points.length){wrap.innerHTML='<div class="no-chart">No chart data</div>';return;}
    var pp=points.map(function(p){return p.p;});
    var mn=Math.min.apply(null,pp),mx=Math.max.apply(null,pp),rng=mx-mn||1;
    var W=600,H=wrap.clientHeight||68,pad=5;
    var pts=pp.map(function(p,i){
        return{x:pad+(i/(pp.length-1))*(W-pad*2),y:H-pad-((p-mn)/rng)*(H-pad*2),p:p,t:points[i].t};
    });
    var col=pp[pp.length-1]>=pp[0]?'#00ff88':'#ff4444';
    var pathD='M '+pts.map(function(p){return p.x+','+p.y;}).join(' L ');
    var areaD='M '+pad+','+H+' L '+pts.map(function(p){return p.x+','+p.y;}).join(' L ')+' L '+(W-pad)+','+H+' Z';
    var gid='g'+wrapId.replace(/[^a-z0-9]/gi,'');
    wrap.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" style="width:100%;height:100%">'+
        '<defs><linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1">'+
        '<stop offset="0%" stop-color="'+col+'" stop-opacity="0.1"/>'+
        '<stop offset="100%" stop-color="'+col+'" stop-opacity="0"/>'+
        '</linearGradient></defs>'+
        '<path d="'+areaD+'" fill="url(#'+gid+')"/>'+
        '<path d="'+pathD+'" stroke="'+col+'" stroke-width="1.5" fill="none"/>'+
        '<line class="vline" x1="-1" y1="0" x2="-1" y2="'+H+'" stroke="#1c1c1c" stroke-width="1" stroke-dasharray="3,3"/>'+
        '</svg>';
    wrap.addEventListener('mousemove',function(e){
        var rect=wrap.getBoundingClientRect();
        var idx=Math.round((e.clientX-rect.left)/rect.width*(pts.length-1));
        idx=Math.max(0,Math.min(idx,pts.length-1));
        var svgX=pad+(idx/(pts.length-1))*(W-pad*2);
        var vl=wrap.querySelector('.vline');
        if(vl){vl.setAttribute('x1',svgX);vl.setAttribute('x2',svgX);}
        var tip=document.getElementById(tooltipId);
        if(tip){
            tip.style.display='block';
            tip.style.left=Math.min(e.clientX-rect.left+12,rect.width-145)+'px';
            tip.style.top='2px';
            tip.querySelector('.tooltip-price').textContent=fmt(pts[idx].p);
            var label=dateMode?new Date(pts[idx].t).toLocaleDateString([],{month:'short',day:'numeric'}):fmtTime(pts[idx].t);
            tip.querySelector('.tooltip-time').textContent=label;
        }
    });
    wrap.addEventListener('mouseleave',function(){
        var vl=wrap.querySelector('.vline');
        if(vl){vl.setAttribute('x1','-1');vl.setAttribute('x2','-1');}
        var tip=document.getElementById(tooltipId);
        if(tip) tip.style.display='none';
    });
}

function loadChartInto(type,sym,wrapId,tooltipId){
    var ckey=type+'-'+sym;
    if(chartCache[ckey]){setTimeout(function(){drawChart(wrapId,chartCache[ckey],tooltipId);},50);return;}
    var url=type==='crypto'?'/api/crypto/chart/'+sym:'/api/stocks/chart/'+sym;
    fetch(url).then(function(r){return r.json();}).then(function(data){
        chartCache[ckey]=data;
        drawChart(wrapId,data,tooltipId);
    }).catch(function(){});
}

function openModal(type,sym,title){
    document.getElementById('modal-title').textContent=title+' — 24h Chart';
    document.getElementById('modal-chart').innerHTML='<div class="ld" style="text-align:center;padding-top:70px">Loading...</div>';
    document.getElementById('chart-modal').classList.add('open');
    var ckey=type+'-'+sym;
    var draw=function(data){chartCache[ckey]=data;drawChart('modal-chart',data,'modal-tooltip');};
    if(chartCache[ckey]){setTimeout(function(){draw(chartCache[ckey]);},50);}
    else{
        var url=type==='crypto'?'/api/crypto/chart/'+sym:'/api/stocks/chart/'+sym;
        fetch(url).then(function(r){return r.json();}).then(draw).catch(function(){
            document.getElementById('modal-chart').innerHTML='<div class="no-chart">Chart unavailable</div>';
        });
    }
}

function closeModal(){document.getElementById('chart-modal').classList.remove('open');}

function switchTab(tab){
    document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active');});
    document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active');});
    document.getElementById('tab-'+tab).classList.add('active');
    document.getElementById('content-'+tab).classList.add('active');
    if(tab==='stocks'&&!stockData.loaded) loadStocks();
    if(tab==='forex'&&!window.forexLoaded) loadForex();
}

// ─── CRYPTO ───────────────────────────────────────────────
function renderCrypto(data){
    var h='<div class="grid">';
    Object.keys(data).forEach(function(sym){
        var c=data[sym],ex=c.exchanges,keys=Object.keys(ex);
        if(!keys.length)return;
        var prices=keys.map(function(k){return ex[k];});
        var minP=Math.min.apply(null,prices),maxP=Math.max.apply(null,prices);
        var spread=maxP>minP?((maxP-minP)/minP*100).toFixed(4):'0.0000';
        var bestBuy=keys[prices.indexOf(minP)];
        var avg=prices.reduce(function(a,b){return a+b;},0)/prices.length;
        var sc=parseFloat(spread)>0.5?'green':parseFloat(spread)>0.1?'yellow':'gray';
        var chg=c.change24h||0;
        var cwId='cw-'+sym,ttId='tt-'+sym;
        h+='<div class="card">';
        h+='<div class="card-header">';
        h+='<div class="card-left"><div class="card-ticker"><span class="card-symbol">'+sym+'</span><button class="chart-btn" data-type="crypto" data-coin="'+sym+'" data-title="'+c.name+' ('+sym+')">24h</button></div><div class="card-name">'+c.name+'</div></div>';
        h+='<div class="card-right"><div class="card-price">'+fmt(avg)+'</div><div class="card-change '+changeClass(chg)+'">'+changeStr(chg)+'</div></div>';
        h+='</div>';
        h+='<div class="stats-bar">';
        h+='<div class="stat"><div class="stat-label">Best Buy</div><div class="stat-value green">'+bestBuy+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Lowest</div><div class="stat-value green">'+fmt(minP)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Spread</div><div class="stat-value '+sc+'">'+spread+'%</div></div>';
        h+='<div class="stat"><div class="stat-label">Exchanges</div><div class="stat-value gray">'+keys.length+'</div></div>';
        h+='</div>';
        h+='<div class="chart-section"><div class="section-label">24h price trend</div><div class="chart-wrap" id="'+cwId+'"></div><div class="tooltip" id="'+ttId+'"><div class="tooltip-price"></div><div class="tooltip-time"></div></div></div>';
        var sorted=keys.slice().sort(function(a,b){return ex[a]-ex[b];});
        h+='<table class="ex-table"><tr><th>Exchange</th><th>Price</th><th>vs Cheapest</th><th></th></tr>';
        sorted.forEach(function(e){
            var p=ex[e],diff=((p-minP)/minP*100).toFixed(4);
            var isBest=p===minP,isHigh=p===maxP&&maxP!==minP;
            var link=CRYPTO_LINKS[e]||'#';
            h+='<tr><td><a href="'+link+'" target="_blank" class="ex-link">'+e+' ↗</a></td>';
            h+='<td class="ex-price">'+fmt(p)+'</td>';
            h+='<td class="'+(parseFloat(diff)>0?'diff-pos':'diff-zero')+'">'+(parseFloat(diff)>0?'+':'')+diff+'%</td>';
            h+='<td>'+(isBest?'<span class="badge badge-buy">BEST BUY</span>':isHigh?'<span class="badge badge-sell">HIGHEST</span>':'')+'</td></tr>';
        });
        h+='</table></div>';
    });
    h+='</div>';
    document.getElementById('crypto-data').innerHTML=h;
    Object.keys(data).forEach(function(sym){
        if(Object.keys(data[sym].exchanges).length) loadChartInto('crypto',sym,'cw-'+sym,'tt-'+sym);
    });
    document.querySelectorAll('#crypto-data .chart-btn').forEach(function(btn){
        btn.addEventListener('click',function(){openModal('crypto',this.dataset.coin,this.dataset.title);});
    });
}

function loadCrypto(){
    document.getElementById('last-updated').textContent='Updating...';
    fetch('/api/crypto').then(function(r){return r.json();}).then(function(data){
        var hasAny=Object.keys(data).some(function(k){return Object.keys(data[k].exchanges).length>0;});
        if(hasAny){cryptoData=data;renderCrypto(data);document.getElementById('last-updated').textContent='Updated '+new Date().toLocaleTimeString();}
        else{document.getElementById('last-updated').textContent='Retrying...';setTimeout(loadCrypto,5000);}
    }).catch(function(){document.getElementById('last-updated').textContent='Error';});
}

// ─── STOCKS ───────────────────────────────────────────────
function fmtVol(v){
    if(!v||v===0) return '—';
    if(v>=1e9) return (v/1e9).toFixed(2)+'B';
    if(v>=1e6) return (v/1e6).toFixed(2)+'M';
    if(v>=1e3) return (v/1e3).toFixed(1)+'K';
    return v;
}

function renderStocks(data){
    var keys=Object.keys(data);
    var h='<div class="section-header">Top 50 Stocks — Prev day close · Powered by Polygon.io · '+keys.length+' loaded</div>';
    h+='<div class="grid">';
    keys.forEach(function(sym){
        var s=data[sym];
        var chg=s.change24h||0;
        var cwId='scw-'+sym.replace(/[^a-z0-9]/gi,'');
        var ttId='stt-'+sym.replace(/[^a-z0-9]/gi,'');
        var sc=chg>2?'green':chg<-2?'red':'yellow';

        h+='<div class="card">';

        // Header
        h+='<div class="card-header">';
        h+='<div class="card-left"><div class="card-ticker"><span class="card-symbol">'+sym+'</span><button class="chart-btn stock-chart-btn" data-sym="'+sym+'" data-title="'+s.name+' ('+sym+')">1d</button></div><div class="card-name">'+s.name+'</div></div>';
        h+='<div class="card-right"><div class="card-price">'+fmt(s.price)+'</div><div class="card-change '+changeClass(chg)+'">'+changeStr(chg)+'</div></div>';
        h+='</div>';

        // Stats bar
        h+='<div class="stats-bar">';
        h+='<div class="stat"><div class="stat-label">Open</div><div class="stat-value gray">'+fmt(s.open)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">High</div><div class="stat-value green">'+fmt(s.high)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Low</div><div class="stat-value red">'+fmt(s.low)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Volume</div><div class="stat-value gray">'+fmtVol(s.volume)+'</div></div>';
        h+='</div>';

        // Chart
        h+='<div class="chart-section"><div class="section-label">Intraday trend (5-min)</div><div class="chart-wrap" id="'+cwId+'"></div><div class="tooltip" id="'+ttId+'"><div class="tooltip-price"></div><div class="tooltip-time"></div></div></div>';

        // VWAP row
        h+='<div class="stats-bar" style="border-top:1px solid #141414;border-bottom:none">';
        h+='<div class="stat"><div class="stat-label">VWAP</div><div class="stat-value gray">'+(s.vwap?fmt(s.vwap):'—')+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Day Move</div><div class="stat-value '+sc+'">'+changeStr(chg)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Source</div><div class="stat-value gray">Polygon.io</div></div>';
        h+='<div class="stat"><div class="stat-label">Delay</div><div class="stat-value gray">15-min</div></div>';
        h+='</div>';

        h+='</div>';
    });
    h+='</div>';
    document.getElementById('stocks-data').innerHTML=h;

    // Load charts
    keys.forEach(function(sym){
        var cwId='scw-'+sym.replace(/[^a-z0-9]/gi,'');
        var ttId='stt-'+sym.replace(/[^a-z0-9]/gi,'');
        var ckey='stocks-'+sym;
        if(chartCache[ckey]){
            drawChart(cwId,chartCache[ckey],ttId,false);
        } else {
            fetch('/api/stocks/chart/'+sym)
                .then(function(r){return r.json();})
                .then(function(pts){
                    chartCache[ckey]=pts;
                    drawChart(cwId,pts,ttId,false);
                }).catch(function(){});
        }
    });

    // Wire chart modal buttons
    document.querySelectorAll('.stock-chart-btn').forEach(function(btn){
        btn.addEventListener('click',function(){
            var sym=this.dataset.sym;
            var title=this.dataset.title;
            document.getElementById('modal-title').textContent=title+' — Intraday Chart';
            document.getElementById('modal-chart').innerHTML='<div class="ld" style="text-align:center;padding-top:70px">Loading...</div>';
            document.getElementById('chart-modal').classList.add('open');
            var ckey='stocks-'+sym;
            if(chartCache[ckey]){setTimeout(function(){drawChart('modal-chart',chartCache[ckey],'modal-tooltip',false);},50);}
            else{fetch('/api/stocks/chart/'+sym).then(function(r){return r.json();}).then(function(pts){chartCache[ckey]=pts;drawChart('modal-chart',pts,'modal-tooltip',false);}).catch(function(){document.getElementById('modal-chart').innerHTML='<div class="no-chart">Chart unavailable</div>';});}
        });
    });

    stockData.loaded=true;
}

function loadStocks(){
    document.getElementById('stocks-data').innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Loading stock data from Polygon.io...</div></div>';
    fetch('/api/stocks').then(function(r){return r.json();}).then(function(data){
        if(Object.keys(data).length) renderStocks(data);
        else document.getElementById('stocks-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Stock data unavailable — market may be closed</div>';
    }).catch(function(){document.getElementById('stocks-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Error loading stocks</div>';});
}

// ─── FOREX ────────────────────────────────────────────────
function renderForex(data){
    var h='<div class="section-header">Major Forex Pairs — Rates from Frankfurter & ExchangeRate-API</div>';
    h+='<div class="forex-grid">';
    Object.keys(data).forEach(function(pair){
        var d=data[pair];
        var cwId='fcw-'+pair.replace('/','');
        var ttId='ftt-'+pair.replace('/','');
        h+='<div class="forex-card">';
        h+='<div class="forex-header">';
        h+='<div class="forex-pair">'+pair+'</div>';
        h+='<button class="chart-btn forex-chart-btn" data-base="'+d.base+'" data-quote="'+d.quote+'" data-pair="'+pair+'">90d</button>';
        h+='</div>';

        // Percent change bars (1d / 10d / 30d)
        h+='<div class="forex-changes">';
        [['1d','change1d'],['10d','change10d'],['30d','change30d']].forEach(function(p){
            var label=p[0], key=p[1];
            var val=d[key];
            if(val===undefined||val===null){
                h+='<div class="forex-change-item"><div class="stat-label">'+label+'</div><div class="stat-value gray">—</div></div>';
            } else {
                var cls=val>0?'green':val<0?'red':'gray';
                var sign=val>0?'+':'';
                h+='<div class="forex-change-item"><div class="stat-label">'+label+'</div><div class="stat-value '+cls+'">'+sign+val.toFixed(2)+'%</div></div>';
            }
        });
        h+='</div>';

        h+='<div class="forex-rates">';
        h+='<div class="forex-source"><div class="forex-source-name"><a href="https://www.frankfurter.app" target="_blank" class="ex-link">Frankfurter ↗</a></div><div class="forex-rate">'+d.rate.toFixed(5)+'</div></div>';
        if(d.rate2){
            h+='<div class="forex-source"><div class="forex-source-name"><a href="https://www.exchangerate-api.com" target="_blank" class="ex-link">ExchangeRate-API ↗</a></div><div class="forex-rate">'+d.rate2.toFixed(5)+'</div></div>';
            var spread=Math.abs(d.rate-d.rate2);
            var spreadPct=(spread/Math.min(d.rate,d.rate2)*100).toFixed(4);
            h+='</div><div class="forex-spread">Spread: <span>'+spreadPct+'%</span> ('+spread.toFixed(5)+')</div>';
        } else {
            h+='</div>';
        }
        h+='<div class="forex-chart-section"><div class="section-label">90d trend</div><div class="chart-wrap" id="'+cwId+'" style="height:60px"></div><div class="tooltip" id="'+ttId+'"><div class="tooltip-price"></div><div class="tooltip-time"></div></div></div>';
        h+='</div>';
    });
    h+='</div>';
    document.getElementById('forex-data').innerHTML=h;
    window.forexLoaded=true;

    Object.keys(data).forEach(function(pair){
        var d=data[pair];
        var cwId='fcw-'+pair.replace('/','');
        var ttId='ftt-'+pair.replace('/','');
        var ckey='forex-'+pair;
        if(!chartCache[ckey]){
            fetch('/api/forex/chart/'+d.base+'/'+d.quote)
                .then(function(r){return r.json();})
                .then(function(pts){
                    chartCache[ckey]=pts;
                    drawChart(cwId,pts,ttId,true);
                }).catch(function(){});
        } else {
            drawChart(cwId,chartCache[ckey],ttId,true);
        }
    });

    document.querySelectorAll('.forex-chart-btn').forEach(function(btn){
        btn.addEventListener('click',function(){
            var pair=this.dataset.pair;
            var base=this.dataset.base;
            var quote=this.dataset.quote;
            document.getElementById('modal-title').textContent=pair+' — 90 Day Chart';
            document.getElementById('modal-chart').innerHTML='<div class="ld" style="text-align:center;padding-top:70px">Loading...</div>';
            document.getElementById('chart-modal').classList.add('open');
            var ckey='forex-'+pair;
            if(chartCache[ckey]){setTimeout(function(){drawChart('modal-chart',chartCache[ckey],'modal-tooltip',true);},50);}
            else{fetch('/api/forex/chart/'+base+'/'+quote).then(function(r){return r.json();}).then(function(data){chartCache[ckey]=data;drawChart('modal-chart',data,'modal-tooltip',true);}).catch(function(){document.getElementById('modal-chart').innerHTML='<div class="no-chart">Chart unavailable</div>';});}
        });
    });
}

function loadForex(){
    document.getElementById('forex-data').innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Loading forex rates...</div></div>';
    fetch('/api/forex').then(function(r){return r.json();}).then(function(data){
        if(Object.keys(data).length) renderForex(data);
        else document.getElementById('forex-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Forex data unavailable</div>';
    }).catch(function(){document.getElementById('forex-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Error loading forex</div>';});
}

// ─── INIT ─────────────────────────────────────────────────
setInterval(function(){
    var active=document.querySelector('.tab-content.active');
    if(active&&active.id==='content-crypto') loadCrypto();
},15000);

window.onload=function(){
    document.getElementById('crypto-data').innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Fetching prices...</div></div>';
    loadCrypto();
};
</script>
</head>
<body>
<div class="modal-bg" id="chart-modal" onclick="if(event.target===this)closeModal()">
  <div class="modal-box">
    <button class="modal-close" onclick="closeModal()">&#x2715;</button>
    <div class="modal-title" id="modal-title"></div>
    <div class="modal-chart-wrap" id="modal-chart"></div>
    <div class="tooltip" id="modal-tooltip" style="position:absolute"><div class="tooltip-price"></div><div class="tooltip-time"></div></div>
  </div>
</div>
<div class="header">
  <div>
    <div class="logo">J<span>SCAN</span></div>
    <div class="subtitle">Real-time market data across exchanges & brokers</div>
  </div>
  <div class="header-right">
    <span class="last-updated" id="last-updated">Loading...</span>
    <button class="refresh-btn" onclick="loadCrypto()">&#8635; Refresh</button>
  </div>
</div>
<div class="tabs">
  <button class="tab-btn active" id="tab-crypto" onclick="switchTab('crypto')">Crypto</button>
  <button class="tab-btn" id="tab-stocks" onclick="switchTab('stocks')">Stocks</button>
  <button class="tab-btn" id="tab-forex" onclick="switchTab('forex')">Forex</button>
  <button class="tab-btn" id="tab-brief" onclick="switchTab('brief')">📊 Daily Brief</button>
</div>
<div class="container">
  <div class="tab-content active" id="content-crypto">
    <div id="crypto-data"></div>
  </div>
  <div class="tab-content" id="content-stocks">
    <div id="stocks-data"></div>
  </div>
  <div class="tab-content" id="content-forex">
    <div id="forex-data"></div>
  </div>
  <div class="tab-content" id="content-brief">
    <div style="max-width:560px;margin:40px auto;text-align:center">
      <div style="font-size:2em;margin-bottom:12px">📊</div>
      <div style="font-size:1.4em;font-weight:700;color:#fff;margin-bottom:8px">JSCAN Daily Brief</div>
      <div style="color:#555;font-size:.9em;margin-bottom:32px;line-height:1.6">Get an AI-powered stock research report delivered to your inbox every morning at 8am. Claude analyzes 100 stocks, flags signals, and executes paper trades automatically.</div>
      <a href="https://jscan-agent.up.railway.app" target="_blank" style="display:inline-block;background:#00ff88;color:#000;font-weight:700;font-size:1em;padding:14px 32px;border-radius:8px;text-decoration:none;transition:opacity .2s">Subscribe Free →</a>
      <div style="margin-top:40px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
        <div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:10px;padding:20px 24px;flex:1;min-width:140px">
          <div style="font-size:1.6em;font-weight:700;color:#00ff88">100</div>
          <div style="font-size:.78em;color:#555;margin-top:4px">Stocks Tracked</div>
        </div>
        <div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:10px;padding:20px 24px;flex:1;min-width:140px">
          <div style="font-size:1.6em;font-weight:700;color:#00ff88">8am</div>
          <div style="font-size:.78em;color:#555;margin-top:4px">Daily Delivery</div>
        </div>
        <div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:10px;padding:20px 24px;flex:1;min-width:140px">
          <div style="font-size:1.6em;font-weight:700;color:#00ff88">Free</div>
          <div style="font-size:.78em;color:#555;margin-top:4px">Always</div>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
