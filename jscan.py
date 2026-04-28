from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime, timedelta
import os
import yfinance as yf

app = Flask(__name__)

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ CRYPTO Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
CRYPTO_COINS = {
    "BTC":  {"name": "Bitcoin",       "binance": "BTCUSDT",  "kraken": "XBTUSD",   "coinbase": "BTC-USD",  "bybit": "BTCUSDT"},
    "ETH":  {"name": "Ethereum",      "binance": "ETHUSDT",  "kraken": "ETHUSD",   "coinbase": "ETH-USD",  "bybit": "ETHUSDT"},
    "XRP":  {"name": "XRP",           "binance": "XRPUSDT",  "kraken": "XRPUSD",   "coinbase": "XRP-USD",  "bybit": "XRPUSDT"},
    "BNB":  {"name": "BNB",           "binance": "BNBUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BNBUSDT"},
    "SOL":  {"name": "Solana",        "binance": "SOLUSDT",  "kraken": "SOLUSD",   "coinbase": "SOL-USD",  "bybit": "SOLUSDT"},
    "DOGE": {"name": "Dogecoin",      "binance": "DOGEUSDT", "kraken": "XDGUSD",   "coinbase": "DOGE-USD", "bybit": "DOGEUSDT"},
    "ADA":  {"name": "Cardano",       "binance": "ADAUSDT",  "kraken": "ADAUSD",   "coinbase": "ADA-USD",  "bybit": "ADAUSDT"},
    "TON":  {"name": "Toncoin",       "binance": "TONUSDT",  "kraken": None,        "coinbase": None,       "bybit": "TONUSDT"},
    "TRX":  {"name": "Tron",          "binance": "TRXUSDT",  "kraken": "TRXUSD",   "coinbase": "TRX-USD",  "bybit": "TRXUSDT"},
    "AVAX": {"name": "Avalanche",     "binance": "AVAXUSDT", "kraken": "AVAXUSD",  "coinbase": "AVAX-USD", "bybit": "AVAXUSDT"},
    "SHIB": {"name": "Shiba Inu",     "binance": "SHIBUSDT", "kraken": "SHIBUSD",  "coinbase": "SHIB-USD", "bybit": "SHIBUSDT"},
    "LINK": {"name": "Chainlink",     "binance": "LINKUSDT", "kraken": "LINKUSD",  "coinbase": "LINK-USD", "bybit": "LINKUSDT"},
    "DOT":  {"name": "Polkadot",      "binance": "DOTUSDT",  "kraken": "DOTUSD",   "coinbase": "DOT-USD",  "bybit": "DOTUSDT"},
    "USDT": {"name": "Tether",        "binance": None,        "kraken": None,        "coinbase": "USDT-USD", "bybit": None},
    "USDC": {"name": "USD Coin",      "binance": None,        "kraken": None,        "coinbase": "USDC-USD", "bybit": None},
    "UNI":  {"name": "Uniswap",       "binance": "UNIUSDT",  "kraken": "UNIUSD",   "coinbase": "UNI-USD",  "bybit": "UNIUSDT"},
    "LTC":  {"name": "Litecoin",      "binance": "LTCUSDT",  "kraken": "XLTCZUSD", "coinbase": "LTC-USD",  "bybit": "LTCUSDT"},
    "BCH":  {"name": "Bitcoin Cash",  "binance": "BCHUSDT",  "kraken": "BCHUSD",   "coinbase": "BCH-USD",  "bybit": "BCHUSDT"},
    "XLM":  {"name": "Stellar",       "binance": "XLMUSDT",  "kraken": "XXLMZUSD", "coinbase": "XLM-USD",  "bybit": "XLMUSDT"},
    "ATOM": {"name": "Cosmos",        "binance": "ATOMUSDT", "kraken": "ATOMUSD",  "coinbase": "ATOM-USD", "bybit": "ATOMUSDT"},
    "NEAR": {"name": "NEAR Protocol", "binance": "NEARUSDT", "kraken": "NEARUSD",  "coinbase": "NEAR-USD", "bybit": "NEARUSDT"},
    "APT":  {"name": "Aptos",         "binance": "APTUSDT",  "kraken": None,        "coinbase": "APT-USD",  "bybit": "APTUSDT"},
    "SUI":  {"name": "Sui",           "binance": "SUIUSDT",  "kraken": None,        "coinbase": "SUI-USD",  "bybit": "SUIUSDT"},
    "OP":   {"name": "Optimism",      "binance": "OPUSDT",   "kraken": "OPUSD",    "coinbase": "OP-USD",   "bybit": "OPUSDT"},
    "ARB":  {"name": "Arbitrum",      "binance": "ARBUSDT",  "kraken": "ARBUSD",   "coinbase": "ARB-USD",  "bybit": "ARBUSDT"},
    "MATIC":{"name": "Polygon",       "binance": "MATICUSDT","kraken": "MATICUSD", "coinbase": "MATIC-USD","bybit": "MATICUSDT"},
    "FIL":  {"name": "Filecoin",      "binance": "FILUSDT",  "kraken": "FILUSD",   "coinbase": "FIL-USD",  "bybit": "FILUSDT"},
    "ICP":  {"name": "Internet Computer","binance":"ICPUSDT", "kraken": "ICPUSD",  "coinbase": "ICP-USD",  "bybit": "ICPUSDT"},
    "HBAR": {"name": "Hedera",        "binance": "HBARUSDT", "kraken": "HBARUSD",  "coinbase": "HBAR-USD", "bybit": "HBARUSDT"},
    "VET":  {"name": "VeChain",       "binance": "VETUSDT",  "kraken": "VETUSD",   "coinbase": None,       "bybit": "VETUSDT"},
    "ALGO": {"name": "Algorand",      "binance": "ALGOUSDT", "kraken": "ALGOUSD",  "coinbase": "ALGO-USD", "bybit": "ALGOUSDT"},
    "GRT":  {"name": "The Graph",     "binance": "GRTUSDT",  "kraken": "GRTUSD",   "coinbase": "GRT-USD",  "bybit": "GRTUSDT"},
    "AAVE": {"name": "Aave",          "binance": "AAVEUSDT", "kraken": "AAVEUSD",  "coinbase": "AAVE-USD", "bybit": "AAVEUSDT"},
    "MKR":  {"name": "Maker",         "binance": "MKRUSDT",  "kraken": "MKRUSD",   "coinbase": "MKR-USD",  "bybit": "MKRUSDT"},
    "SNX":  {"name": "Synthetix",     "binance": "SNXUSDT",  "kraken": "SNXUSD",   "coinbase": "SNX-USD",  "bybit": "SNXUSDT"},
    "SAND": {"name": "The Sandbox",   "binance": "SANDUSDT", "kraken": "SANDUSD",  "coinbase": "SAND-USD", "bybit": "SANDUSDT"},
    "MANA": {"name": "Decentraland",  "binance": "MANAUSDT", "kraken": "MANAUSD",  "coinbase": "MANA-USD", "bybit": "MANAUSDT"},
    "AXS":  {"name": "Axie Infinity", "binance": "AXSUSDT",  "kraken": "AXSUSD",   "coinbase": "AXS-USD",  "bybit": "AXSUSDT"},
    "THETA":{"name": "Theta Network", "binance": "THETAUSDT","kraken": "THETAUSD", "coinbase": None,       "bybit": "THETAUSDT"},
    "FTM":  {"name": "Fantom",        "binance": "FTMUSDT",  "kraken": "FTMUSD",   "coinbase": "FTM-USD",  "bybit": "FTMUSDT"},
    "CRV":  {"name": "Curve DAO",     "binance": "CRVUSDT",  "kraken": "CRVUSD",   "coinbase": "CRV-USD",  "bybit": "CRVUSDT"},
    "LDO":  {"name": "Lido DAO",      "binance": "LDOUSDT",  "kraken": "LDOUSD",   "coinbase": "LDO-USD",  "bybit": "LDOUSDT"},
    "INJ":  {"name": "Injective",     "binance": "INJUSDT",  "kraken": "INJUSD",   "coinbase": "INJ-USD",  "bybit": "INJUSDT"},
    "SEI":  {"name": "Sei",           "binance": "SEIUSDT",  "kraken": None,        "coinbase": "SEI-USD",  "bybit": "SEIUSDT"},
    "WIF":  {"name": "dogwifhat",     "binance": "WIFUSDT",  "kraken": None,        "coinbase": "WIF-USD",  "bybit": "WIFUSDT"},
    "PEPE": {"name": "Pepe",          "binance": "PEPEUSDT", "kraken": None,        "coinbase": "PEPE-USD", "bybit": "PEPEUSDT"},
    "BONK": {"name": "Bonk",          "binance": "BONKUSDT", "kraken": None,        "coinbase": "BONK-USD", "bybit": "BONKUSDT"},
    "JUP":  {"name": "Jupiter",       "binance": "JUPUSDT",  "kraken": None,        "coinbase": "JUP-USD",  "bybit": "JUPUSDT"},
    "RUNE": {"name": "THORChain",     "binance": "RUNEUSDT", "kraken": "RUNEUSD",  "coinbase": None,       "bybit": "RUNEUSDT"},
    "FLOW": {"name": "Flow",          "binance": "FLOWUSDT", "kraken": "FLOWUSD",  "coinbase": "FLOW-USD", "bybit": "FLOWUSDT"},
    # Extended coins
    "BNB":  {"name": "BNB",           "binance": "BNBUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BNBUSDT"},
    "TON":  {"name": "Toncoin",       "binance": "TONUSDT",  "kraken": None,        "coinbase": None,       "bybit": "TONUSDT"},
    "VET":  {"name": "VeChain",       "binance": "VETUSDT",  "kraken": "VETUSD",   "coinbase": None,       "bybit": "VETUSDT"},
    "THETA":{"name": "Theta Network", "binance": "THETAUSDT","kraken": "THETAUSD", "coinbase": None,       "bybit": "THETAUSDT"},
    "EOS":  {"name": "EOS",           "binance": "EOSUSDT",  "kraken": "EOSUSD",   "coinbase": "EOS-USD",  "bybit": "EOSUSDT"},
    "XTZ":  {"name": "Tezos",         "binance": "XTZUSDT",  "kraken": "XTZUSD",   "coinbase": "XTZ-USD",  "bybit": "XTZUSDT"},
    "EGLD": {"name": "MultiversX",    "binance": "EGLDUSDT", "kraken": None,        "coinbase": None,       "bybit": "EGLDUSDT"},
    "KAVA": {"name": "Kava",          "binance": "KAVAUSDT", "kraken": None,        "coinbase": "KAVA-USD", "bybit": "KAVAUSDT"},
    "ONE":  {"name": "Harmony",       "binance": "ONEUSDT",  "kraken": None,        "coinbase": "ONE-USD",  "bybit": "ONEUSDT"},
    "ZIL":  {"name": "Zilliqa",       "binance": "ZILUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ZILUSDT"},
    "BAT":  {"name": "Basic Attention","binance":"BATUSDT",  "kraken": "BATUSD",   "coinbase": "BAT-USD",  "bybit": "BATUSDT"},
    "ZRX":  {"name": "0x Protocol",   "binance": "ZRXUSDT",  "kraken": "ZRXUSD",   "coinbase": "ZRX-USD",  "bybit": "ZRXUSDT"},
    "ENJ":  {"name": "Enjin Coin",    "binance": "ENJUSDT",  "kraken": "ENJUSD",   "coinbase": "ENJ-USD",  "bybit": "ENJUSDT"},
    "CHZ":  {"name": "Chiliz",        "binance": "CHZUSDT",  "kraken": None,        "coinbase": "CHZ-USD",  "bybit": "CHZUSDT"},
    "HOT":  {"name": "Holo",          "binance": "HOTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "HOTUSDT"},
    "ONT":  {"name": "Ontology",      "binance": "ONTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ONTUSDT"},
    "IOTA": {"name": "IOTA",          "binance": "IOTAUSDT", "kraken": "IOTAUSD",  "coinbase": None,       "bybit": "IOTAUSDT"},
    "RVN":  {"name": "Ravencoin",     "binance": "RVNUSDT",  "kraken": None,        "coinbase": None,       "bybit": "RVNUSDT"},
    "QTUM": {"name": "Qtum",          "binance": "QTUMUSDT", "kraken": "QTUMUSD",  "coinbase": None,       "bybit": "QTUMUSDT"},
    "ICX":  {"name": "ICON",          "binance": "ICXUSDT",  "kraken": "ICXUSD",   "coinbase": None,       "bybit": "ICXUSDT"},
    "WAVES":{"name": "Waves",         "binance": "WAVESUSDT","kraken": "WAVESUSD", "coinbase": None,       "bybit": "WAVESUSDT"},
    "COMP": {"name": "Compound",      "binance": "COMPUSDT", "kraken": "COMPUSD",  "coinbase": "COMP-USD", "bybit": "COMPUSDT"},
    "YFI":  {"name": "Yearn Finance", "binance": "YFIUSDT",  "kraken": "YFIUSD",   "coinbase": "YFI-USD",  "bybit": "YFIUSDT"},
    "SUSHI":{"name": "SushiSwap",     "binance": "SUSHIUSDT","kraken": "SUSHIUSD", "coinbase": "SUSHI-USD","bybit": "SUSHIUSDT"},
    "1INCH":{"name": "1inch Network", "binance": "1INCHUSDT","kraken": "1INCHUSD", "coinbase": "1INCH-USD","bybit": "1INCHUSDT"},
    "ANKR": {"name": "Ankr",          "binance": "ANKRUSDT", "kraken": None,        "coinbase": "ANKR-USD", "bybit": "ANKRUSDT"},
    "DYDX": {"name": "dYdX",          "binance": "DYDXUSDT", "kraken": "DYDXUSD",  "coinbase": "DYDX-USD", "bybit": "DYDXUSDT"},
    "BLUR": {"name": "Blur",          "binance": "BLURUSDT", "kraken": None,        "coinbase": "BLUR-USD", "bybit": "BLURUSDT"},
    "GMX":  {"name": "GMX",           "binance": "GMXUSDT",  "kraken": None,        "coinbase": None,       "bybit": "GMXUSDT"},
    "MAGIC":{"name": "Magic",         "binance": "MAGICUSDT","kraken": None,        "coinbase": None,       "bybit": "MAGICUSDT"},
    "GALA": {"name": "Gala",          "binance": "GALAUSDT", "kraken": None,        "coinbase": "GALA-USD", "bybit": "GALAUSDT"},
    "IMX":  {"name": "Immutable X",   "binance": "IMXUSDT",  "kraken": "IMXUSD",   "coinbase": "IMX-USD",  "bybit": "IMXUSDT"},
    "APE":  {"name": "ApeCoin",       "binance": "APEUSDT",  "kraken": "APEUSD",   "coinbase": "APE-USD",  "bybit": "APEUSDT"},
    "GMT":  {"name": "STEPN",         "binance": "GMTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "GMTUSDT"},
    "STX":  {"name": "Stacks",        "binance": "STXUSDT",  "kraken": "STXUSD",   "coinbase": "STX-USD",  "bybit": "STXUSDT"},
    "CFX":  {"name": "Conflux",       "binance": "CFXUSDT",  "kraken": None,        "coinbase": None,       "bybit": "CFXUSDT"},
    "SSV":  {"name": "SSV Network",   "binance": "SSVUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SSVUSDT"},
    "PENDLE":{"name":"Pendle",        "binance": "PENDLEUSDT","kraken":None,         "coinbase": None,       "bybit": "PENDLEUSDT"},
    "TIA":  {"name": "Celestia",      "binance": "TIAUSDT",  "kraken": "TIAUSD",   "coinbase": "TIA-USD",  "bybit": "TIAUSDT"},
    "PYTH": {"name": "Pyth Network",  "binance": "PYTHUSDT", "kraken": None,        "coinbase": "PYTH-USD", "bybit": "PYTHUSDT"},
    "JTO":  {"name": "Jito",          "binance": "JTOUSDT",  "kraken": None,        "coinbase": "JTO-USD",  "bybit": "JTOUSDT"},
    "STRK": {"name": "Starknet",      "binance": "STRKUSDT", "kraken": None,        "coinbase": "STRK-USD", "bybit": "STRKUSDT"},
    "DYM":  {"name": "Dymension",     "binance": "DYMUSDT",  "kraken": None,        "coinbase": None,       "bybit": "DYMUSDT"},
    "ALT":  {"name": "AltLayer",      "binance": "ALTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ALTUSDT"},
    "PIXEL":{"name": "Pixels",        "binance": "PIXELUSDT","kraken": None,        "coinbase": None,       "bybit": "PIXELUSDT"},
    "PORTAL":{"name":"Portal",        "binance":"PORTALUSDT","kraken": None,        "coinbase": None,       "bybit": "PORTALUSDT"},
    "MANTA":{"name": "Manta Network", "binance": "MANTAUSDT","kraken": None,        "coinbase": None,       "bybit": "MANTAUSDT"},
    "OMNI": {"name": "Omni Network",  "binance": "OMNIUSDT", "kraken": None,        "coinbase": None,       "bybit": "OMNIUSDT"},
    "REZ":  {"name": "Renzo",         "binance": "REZUSDT",  "kraken": None,        "coinbase": None,       "bybit": "REZUSDT"},
    "ETHFI":{"name": "Ether.fi",      "binance": "ETHFIUSDT","kraken": None,        "coinbase": None,       "bybit": "ETHFIUSDT"},
    "SAFE": {"name": "Safe",          "binance": "SAFEUSDT", "kraken": None,        "coinbase": None,       "bybit": "SAFEUSDT"},
    "TNSR": {"name": "Tensor",        "binance": "TNSRUSDT", "kraken": None,        "coinbase": None,       "bybit": "TNSRUSDT"},
    "W":    {"name": "Wormhole",      "binance": "WUSDT",    "kraken": None,        "coinbase": None,       "bybit": "WUSDT"},
    "LISTA":{"name": "Lista DAO",     "binance": "LISTAUSDT","kraken": None,        "coinbase": None,       "bybit": "LISTAUSDT"},
    "ZK":   {"name": "ZKsync",        "binance": "ZKUSDT",   "kraken": None,        "coinbase": None,       "bybit": "ZKUSDT"},
    "IO":   {"name": "io.net",        "binance": "IOUSDT",   "kraken": None,        "coinbase": None,       "bybit": "IOUSDT"},
    "ZRO":  {"name": "LayerZero",     "binance": "ZROUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ZROUSDT"},
    "EIGEN":{"name": "EigenLayer",    "binance": "EIGENUSDT","kraken": None,        "coinbase": None,       "bybit": "EIGENUSDT"},
    "CATI": {"name": "Catizen",       "binance": "CATIUSDT", "kraken": None,        "coinbase": None,       "bybit": "CATIUSDT"},
    "HMSTR":{"name": "Hamster Kombat","binance":"HMSTRUSDT", "kraken": None,        "coinbase": None,       "bybit": "HMSTRUSDT"},
    "NEIRO":{"name": "Neiro",         "binance": "NEIROUSDT","kraken": None,        "coinbase": None,       "bybit": "NEIROUSDT"},
    "DOGS": {"name": "Dogs",          "binance": "DOGSUSDT", "kraken": None,        "coinbase": None,       "bybit": "DOGSUSDT"},
    "MOODENG":{"name":"Moo Deng",     "binance":"MOODENGUSDT","kraken":None,        "coinbase": None,       "bybit": "MOODENGUSDT"},
    "PNUT": {"name": "Peanut",        "binance": "PNUTUSDT", "kraken": None,        "coinbase": None,       "bybit": "PNUTUSDT"},
    "ACT":  {"name": "Act I",         "binance": "ACTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ACTUSDT"},
    "GOAT": {"name": "Goat",          "binance": "GOATUSDT", "kraken": None,        "coinbase": None,       "bybit": "GOATUSDT"},
    "CELO": {"name": "Celo",          "binance": "CELOUSDT", "kraken": "CELOUSD",  "coinbase": "CGLD-USD", "bybit": "CELOUSDT"},
    "FET":  {"name": "Fetch.ai",      "binance": "FETUSDT",  "kraken": "FETUSD",   "coinbase": "FET-USD",  "bybit": "FETUSDT"},
    "OCEAN":{"name": "Ocean Protocol","binance": "OCEANUSDT","kraken": "OCEANUSD", "coinbase": "OCEAN-USD","bybit": "OCEANUSDT"},
    "AGIX": {"name": "SingularityNET","binance": "AGIXUSDT", "kraken": None,        "coinbase": None,       "bybit": "AGIXUSDT"},
    "RENDER":{"name":"Render",        "binance":"RENDERUSDT","kraken": None,        "coinbase":"RENDER-USD","bybit": "RENDERUSDT"},
    "AR":   {"name": "Arweave",       "binance": "ARUSDT",   "kraken": "ARUSD",    "coinbase": "AR-USD",   "bybit": "ARUSDT"},
    "HNT":  {"name": "Helium",        "binance": "HNTUSDT",  "kraken": "HNTUSD",   "coinbase": "HNT-USD",  "bybit": "HNTUSDT"},
    "STORJ":{"name": "Storj",         "binance": "STORJUSDT","kraken": "STORJUSD", "coinbase": "STORJ-USD","bybit": "STORJUSDT"},
    "AKT":  {"name": "Akash Network", "binance": "AKTUSDT",  "kraken": None,        "coinbase": "AKT-USD",  "bybit": "AKTUSDT"},
    "ROSE": {"name": "Oasis Network",  "binance": "ROSEUSDT", "kraken": None,        "coinbase": "ROSE-USD", "bybit": "ROSEUSDT"},
    "BAND": {"name": "Band Protocol", "binance": "BANDUSDT", "kraken": "BANDUSD",  "coinbase": None,       "bybit": "BANDUSDT"},
    "OGN":  {"name": "Origin Protocol","binance":"OGNUSDT",  "kraken": None,        "coinbase": "OGN-USD",  "bybit": "OGNUSDT"},
    "NMR":  {"name": "Numeraire",     "binance": "NMRUSDT",  "kraken": "NMRUSD",   "coinbase": "NMR-USD",  "bybit": "NMRUSDT"},
    "RLC":  {"name": "iExec RLC",     "binance": "RLCUSDT",  "kraken": "RLCUSD",   "coinbase": "RLC-USD",  "bybit": "RLCUSDT"},
    "SKL":  {"name": "SKALE",         "binance": "SKLUSDT",  "kraken": "SKLUSD",   "coinbase": "SKL-USD",  "bybit": "SKLUSDT"},
    "LPT":  {"name": "Livepeer",      "binance": "LPTUSDT",  "kraken": "LPTUSD",   "coinbase": "LPT-USD",  "bybit": "LPTUSDT"},
    "CTSI": {"name": "Cartesi",       "binance": "CTSIUSDT", "kraken": None,        "coinbase": "CTSI-USD", "bybit": "CTSIUSDT"},
    "RAD":  {"name": "Radicle",       "binance": "RADUSDT",  "kraken": None,        "coinbase": "RAD-USD",  "bybit": "RADUSDT"},
    "IDEX": {"name": "IDEX",          "binance": "IDEXUSDT", "kraken": None,        "coinbase": None,       "bybit": "IDEXUSDT"},
    "DESO": {"name": "DeSo",          "binance": "DESOUSDT", "kraken": None,        "coinbase": None,       "bybit": "DESOUSDT"},
    "MASK": {"name": "Mask Network",  "binance": "MASKUSDT", "kraken": "MASKUSD",  "coinbase": "MASK-USD", "bybit": "MASKUSDT"},
    "BICO": {"name": "Biconomy",      "binance": "BICOUSDT", "kraken": None,        "coinbase": None,       "bybit": "BICOUSDT"},
    "API3": {"name": "API3",          "binance": "API3USDT", "kraken": None,        "coinbase": None,       "bybit": "API3USDT"},
    "OP":   {"name": "Optimism",      "binance": "OPUSDT",   "kraken": "OPUSD",    "coinbase": "OP-USD",   "bybit": "OPUSDT"},
    "LOOKS":{"name": "LooksRare",     "binance": "LOOKSUSDT","kraken": None,        "coinbase": None,       "bybit": "LOOKSUSDT"},
    "HIGH": {"name": "Highstreet",    "binance": "HIGHUSDT", "kraken": None,        "coinbase": None,       "bybit": "HIGHUSDT"},
    "SPELL":{"name": "Spell Token",   "binance": "SPELLUSDT","kraken": None,        "coinbase": None,       "bybit": "SPELLUSDT"},
    "SPA":  {"name": "Sperax",        "binance": "SPAUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SPAUSDT"},
    "CHESS":{"name": "Tranchess",     "binance": "CHESSUSDT","kraken": None,        "coinbase": None,       "bybit": "CHESSUSDT"},
    "AXL":  {"name": "Axelar",        "binance": "AXLUSDT",  "kraken": None,        "coinbase": "AXL-USD",  "bybit": "AXLUSDT"},
    "OSMO": {"name": "Osmosis",       "binance": "OSMOUSDT", "kraken": None,        "coinbase": "OSMO-USD", "bybit": "OSMOUSDT"},
    "EVMOS":{"name": "Evmos",         "binance": "EVMOSUSDT","kraken": None,        "coinbase": None,       "bybit": "EVMOSUSDT"},
    "KLAY": {"name": "Klaytn",        "binance": "KLAYUSDT", "kraken": None,        "coinbase": None,       "bybit": "KLAYUSDT"},
    "METIS":{"name": "Metis",         "binance": "METISUSDT","kraken": None,        "coinbase": None,       "bybit": "METISUSDT"},
    "BOBA": {"name": "Boba Network",  "binance": "BOBAUSDT", "kraken": None,        "coinbase": None,       "bybit": "BOBAUSDT"},
    "CELR": {"name": "Celer Network", "binance": "CELRUSDT", "kraken": None,        "coinbase": None,       "bybit": "CELRUSDT"},
    "SYS":  {"name": "Syscoin",       "binance": "SYSUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SYSUSDT"},
    "POLS": {"name": "Polkastarter",  "binance": "POLSUSDT", "kraken": None,        "coinbase": None,       "bybit": "POLSUSDT"},
    "XEC":  {"name": "eCash",         "binance": "XECUSDT",  "kraken": None,        "coinbase": None,       "bybit": "XECUSDT"},
    "TWT":  {"name": "Trust Wallet",  "binance": "TWTUSDT",  "kraken": None,        "coinbase": None,       "bybit": "TWTUSDT"},
    "COMBO":{"name": "Furucombo",     "binance": "COMBOUSDT","kraken": None,        "coinbase": None,       "bybit": "COMBOUSDT"},
    "GAS":  {"name": "Gas",           "binance": "GASUSDT",  "kraken": None,        "coinbase": None,       "bybit": "GASUSDT"},
    "NULS": {"name": "Nuls",          "binance": "NULSUSDT", "kraken": None,        "coinbase": None,       "bybit": "NULSUSDT"},
    "VIDT": {"name": "VIDT DAO",      "binance": "VIDTUSDT", "kraken": None,        "coinbase": None,       "bybit": "VIDTUSDT"},
    "DATA": {"name": "Streamr",       "binance": "DATAUSDT", "kraken": None,        "coinbase": None,       "bybit": "DATAUSDT"},
    "ORN":  {"name": "Orion Protocol","binance": "ORNUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ORNUSDT"},
    "TRIBE":{"name": "Tribe",         "binance": "TRIBEUSDT","kraken": None,        "coinbase": "TRIBE-USD","bybit": "TRIBEUSDT"},
    "CLV":  {"name": "Clover Finance","binance": "CLVUSDT",  "kraken": None,        "coinbase": "CLV-USD",  "bybit": "CLVUSDT"},
    "QI":   {"name": "BENQI",         "binance": "QIUSDT",   "kraken": None,        "coinbase": None,       "bybit": "QIUSDT"},
    "LINA": {"name": "Linear Finance","binance": "LINAUSDT", "kraken": None,        "coinbase": None,       "bybit": "LINAUSDT"},
    "SFP":  {"name": "SafePal",       "binance": "SFPUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SFPUSDT"},
    "XVGOLD":{"name":"XV Gold",       "binance": None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "XVG":  {"name": "Verge",         "binance": "XVGUSDT",  "kraken": None,        "coinbase": None,       "bybit": "XVGUSDT"},
    "FIO":  {"name": "FIO Protocol",  "binance": "FIOUSDT",  "kraken": None,        "coinbase": None,       "bybit": "FIOUSDT"},
    "WOO":  {"name": "WOO Network",   "binance": "WOOUSDT",  "kraken": None,        "coinbase": "WOO-USD",  "bybit": "WOOUSDT"},
    "FLUX": {"name": "Flux",          "binance": "FLUXUSDT", "kraken": None,        "coinbase": None,       "bybit": "FLUXUSDT"},
    "DUSK": {"name": "Dusk Network",  "binance": "DUSKUSDT", "kraken": None,        "coinbase": None,       "bybit": "DUSKUSDT"},
    "PROM": {"name": "Prom",          "binance": "PROMUSDT", "kraken": None,        "coinbase": None,       "bybit": "PROMUSDT"},
    "HARD": {"name": "HARD Protocol", "binance": "HARDUSDT", "kraken": None,        "coinbase": None,       "bybit": "HARDUSDT"},
    "COCOS":{"name": "Cocos-BCX",     "binance": "COCOSUSDT","kraken": None,        "coinbase": None,       "bybit": "COCOSUSDT"},
    "KSM":  {"name": "Kusama",        "binance": "KSMUSDT",  "kraken": "KSMUSD",   "coinbase": "KSM-USD",  "bybit": "KSMUSDT"},
    "ATA":  {"name": "Automata",      "binance": "ATAUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ATAUSDT"},
    "AVA":  {"name": "Travala",       "binance": "AVAUSDT",  "kraken": None,        "coinbase": None,       "bybit": "AVAUSDT"},
    "BEL":  {"name": "Bella Protocol","binance": "BELUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BELUSDT"},
    "WING": {"name": "Wing Finance",  "binance": "WINGUSDT", "kraken": None,        "coinbase": None,       "bybit": "WINGUSDT"},
    "TRB":  {"name": "Tellor",        "binance": "TRBUSDT",  "kraken": "TRBUSD",   "coinbase": "TRB-USD",  "bybit": "TRBUSDT"},
    "PERP": {"name": "Perpetual",     "binance": "PERPUSDT", "kraken": "PERPUSD",  "coinbase": "PERP-USD", "bybit": "PERPUSDT"},
    "FARM": {"name": "Harvest Finance","binance":"FARMUSDT", "kraken": None,        "coinbase": None,       "bybit": "FARMUSDT"},
    "BURGER":{"name":"BurgerSwap",    "binance":"BURGERUSDT","kraken": None,        "coinbase": None,       "bybit": "BURGERUSDT"},
    "UNFI": {"name": "Unifi Protocol","binance": "UNFIUSDT", "kraken": None,        "coinbase": None,       "bybit": "UNFIUSDT"},
    "OXT":  {"name": "Orchid",        "binance": "OXTUSDT",  "kraken": "OXTUSD",   "coinbase": "OXT-USD",  "bybit": "OXTUSDT"},
    "POND": {"name": "Marlin",        "binance": "PONDUSDT", "kraken": None,        "coinbase": None,       "bybit": "PONDUSDT"},
    "SRM":  {"name": "Serum",         "binance": "SRMUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SRMUSDT"},
    "MDX":  {"name": "Mdex",          "binance": "MDXUSDT",  "kraken": None,        "coinbase": None,       "bybit": "MDXUSDT"},
    "DEGO": {"name": "Dego Finance",  "binance": "DEGOUSDT", "kraken": None,        "coinbase": None,       "bybit": "DEGOUSDT"},
    "FOR":  {"name": "ForTube",       "binance": "FORUSDT",  "kraken": None,        "coinbase": None,       "bybit": "FORUSDT"},
    "ALPHA":{"name": "Alpha Venture", "binance": "ALPHAUSDT","kraken": None,        "coinbase": None,       "bybit": "ALPHAUSDT"},
    "GTC":  {"name": "Gitcoin",       "binance": "GTCUSDT",  "kraken": "GTCUSD",   "coinbase": "GTC-USD",  "bybit": "GTCUSDT"},
    "ILA":  {"name": "Infinite Launch","binance":None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "FORTH":{"name": "Ampleforth Gov","binance": "FORTHUSDT","kraken": None,        "coinbase": "FORTH-USD","bybit": "FORTHUSDT"},
    "RARE": {"name": "SuperRare",     "binance": "RAREUSDT", "kraken": None,        "coinbase": "RARE-USD", "bybit": "RAREUSDT"},
    "BAKE": {"name": "BakeryToken",   "binance": "BAKEUSDT", "kraken": None,        "coinbase": None,       "bybit": "BAKEUSDT"},
    "SLP":  {"name": "Smooth Love Potion","binance":"SLPUSDT","kraken":None,        "coinbase": None,       "bybit": "SLPUSDT"},
    "TLM":  {"name": "Alien Worlds",  "binance": "TLMUSDT",  "kraken": None,        "coinbase": None,       "bybit": "TLMUSDT"},
    "ALICE":{"name": "My Neighbor Alice","binance":"ALICEUSDT","kraken":None,       "coinbase": None,       "bybit": "ALICEUSDT"},
    "MBOX": {"name": "Mobox",         "binance": "MBOXUSDT", "kraken": None,        "coinbase": None,       "bybit": "MBOXUSDT"},
    "VOXEL":{"name": "Voxies",        "binance": "VOXELUSDT","kraken": None,        "coinbase": None,       "bybit": "VOXELUSDT"},
    "PYR":  {"name": "Vulcan Forged", "binance": "PYRUSDT",  "kraken": None,        "coinbase": None,       "bybit": "PYRUSDT"},
    "GHST": {"name": "Aavegotchi",    "binance": "GHSTUSDT", "kraken": None,        "coinbase": "GHST-USD", "bybit": "GHSTUSDT"},
    "ERN":  {"name": "Ethernity",     "binance": "ERNUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ERNUSDT"},
    "HERO": {"name": "Metahero",      "binance": "HEROUSDT", "kraken": None,        "coinbase": None,       "bybit": "HEROUSDT"},
    "DIVI": {"name": "Divi",          "binance": "DIVIUSDT", "kraken": None,        "coinbase": None,       "bybit": "DIVIUSDT"},
    "PAXG": {"name": "PAX Gold",      "binance": "PAXGUSDT", "kraken": "PAXGUSD",  "coinbase": "PAXG-USD", "bybit": "PAXGUSDT"},
    "XAUT": {"name": "Tether Gold",   "binance": None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "POND2":{"name": "Pond2",         "binance": None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "KNC":  {"name": "Kyber Network", "binance": "KNCUSDT",  "kraken": "KNCUSD",   "coinbase": "KNC-USD",  "bybit": "KNCUSDT"},
    "BAL":  {"name": "Balancer",      "binance": "BALUSDT",  "kraken": "BALUSD",   "coinbase": "BAL-USD",  "bybit": "BALUSDT"},
    "REP":  {"name": "Augur",         "binance": "REPUSDT",  "kraken": "REPUSD",   "coinbase": None,       "bybit": "REPUSDT"},
    "UMA":  {"name": "UMA",           "binance": "UMAUSDT",  "kraken": "UMAUSD",   "coinbase": "UMA-USD",  "bybit": "UMAUSDT"},
    "OGV":  {"name": "Origin DeFi Gov","binance":None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "LQTY": {"name": "Liquity",       "binance": "LQTYUSDT", "kraken": "LQTYUSD",  "coinbase": "LQTY-USD", "bybit": "LQTYUSDT"},
    "FRAX": {"name": "Frax",          "binance": None,        "kraken": None,        "coinbase": "FRAX-USD", "bybit": None},
    "FXS":  {"name": "Frax Share",    "binance": "FXSUSDT",  "kraken": "FXSUSD",   "coinbase": "FXS-USD",  "bybit": "FXSUSDT"},
    "LUSD": {"name": "Liquity USD",   "binance": None,        "kraken": None,        "coinbase": "LUSD-USD", "bybit": None},
    "ALBT": {"name": "AllianceBlock", "binance": "ALBTUSDT", "kraken": None,        "coinbase": None,       "bybit": "ALBTUSDT"},
    "SXP":  {"name": "Solar",         "binance": "SXPUSDT",  "kraken": None,        "coinbase": None,       "bybit": "SXPUSDT"},
    "COMET":{"name": "Comet",         "binance": None,        "kraken": None,        "coinbase": None,       "bybit": None},
    "ACH":  {"name": "Alchemy Pay",   "binance": "ACHUSDT",  "kraken": None,        "coinbase": "ACH-USD",  "bybit": "ACHUSDT"},
    "XNO":  {"name": "Nano",          "binance": "XNOUSDT",  "kraken": "NANOUSD",  "coinbase": None,       "bybit": "XNOUSDT"},
    "POWR": {"name": "Power Ledger",  "binance": "POWRUSDT", "kraken": "POWRUSD",  "coinbase": "POWR-USD", "bybit": "POWRUSDT"},
    "MLN":  {"name": "Enzyme",        "binance": "MLNUSDT",  "kraken": "MLNUSD",   "coinbase": "MLN-USD",  "bybit": "MLNUSDT"},
    "DNT":  {"name": "district0x",    "binance": "DNTUSDT",  "kraken": "DNTUSD",   "coinbase": "DNT-USD",  "bybit": "DNTUSDT"},
    "SUPER":{"name": "SuperVerse",    "binance": "SUPERUSDT","kraken": None,        "coinbase": None,       "bybit": "SUPERUSDT"},
    "BADGER":{"name":"Badger DAO",    "binance":"BADGERUSDT","kraken": None,        "coinbase":"BADGER-USD","bybit": "BADGERUSDT"},
    "BNT":  {"name": "Bancor",        "binance": "BNTUSDT",  "kraken": "BNTUSD",   "coinbase": "BNT-USD",  "bybit": "BNTUSDT"},
    "INDEX":{"name": "Index Coop",    "binance": None,        "kraken": None,        "coinbase": "INDEX-USD","bybit": None},
    "DPI":  {"name": "DeFi Pulse Index","binance":None,       "kraken": None,        "coinbase": "DPI-USD",  "bybit": None},
    "MVI":  {"name": "Metaverse Index","binance":None,        "kraken": None,        "coinbase": "MVI-USD",  "bybit": None},
    "JASMY":{"name": "JasmyCoin",     "binance": "JASMYUSDT","kraken": None,        "coinbase": "JASMY-USD","bybit": "JASMYUSDT"},
    "ACA":  {"name": "Acala",         "binance": "ACAUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ACAUSDT"},
    "GLMR": {"name": "Moonbeam",      "binance": "GLMRUSDT", "kraken": None,        "coinbase": "GLMR-USD", "bybit": "GLMRUSDT"},
    "MOVR": {"name": "Moonriver",     "binance": "MOVRUSDT", "kraken": None,        "coinbase": None,       "bybit": "MOVRUSDT"},
    "ASTR": {"name": "Astar",         "binance": "ASTRUSDT", "kraken": None,        "coinbase": None,       "bybit": "ASTRUSDT"},
    "BSW":  {"name": "Biswap",        "binance": "BSWUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BSWUSDT"},
    "LAZIO":{"name": "Lazio Fan Token","binance":"LAZIOUSDT","kraken": None,        "coinbase": None,       "bybit": "LAZIOUSDT"},
    "PORTO":{"name": "Porto Fan Token","binance":"PORTOUSDT","kraken": None,        "coinbase": None,       "bybit": "PORTOUSDT"},
    "SANTOS":{"name":"Santos FC",     "binance":"SANTOSUSDT","kraken":None,         "coinbase": None,       "bybit": "SANTOSUSDT"},
    "PSG":  {"name": "PSG Fan Token", "binance": "PSGUSDT",  "kraken": None,        "coinbase": None,       "bybit": "PSGUSDT"},
    "ATM":  {"name": "Atletico Fan",  "binance": "ATMUSDT",  "kraken": None,        "coinbase": None,       "bybit": "ATMUSDT"},
    "CITY": {"name": "ManCity Fan",   "binance": "CITYUSDT", "kraken": None,        "coinbase": None,       "bybit": "CITYUSDT"},
    "BAR":  {"name": "FC Barcelona",  "binance": "BARUSDT",  "kraken": None,        "coinbase": None,       "bybit": "BARUSDT"},
    "JUV":  {"name": "Juventus Fan",  "binance": "JUVUSDT",  "kraken": None,        "coinbase": None,       "bybit": "JUVUSDT"},
}

CRYPTO_EXCHANGE_LINKS = {
    "Binance": "https://www.binance.com",
    "Kraken": "https://www.kraken.com",
    "Coinbase": "https://www.coinbase.com",
    "Bybit": "https://www.bybit.com",
}

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ STOCKS Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
POLYGON_API_KEY = "AHDx47kyKxiVlcwWs5jP1WjiY2ExUPkC"

TOP_STOCKS = [
    # Top 50 (original)
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","JPM","V",
    "WMT","XOM","UNH","LLY","MA","JNJ","PG","HD","MRK","COST",
    "ABBV","CVX","BAC","KO","PEP","ADBE","CRM","NFLX","AMD","TMO",
    "ACN","MCD","CSCO","ABT","LIN","DHR","WFC","TXN","NEE","PM",
    "RTX","AMGN","LOW","ORCL","UPS","INTC","QCOM","CAT","NOW","INTU",
    # Next 50
    "SPGI","AXP","GS","BLK","MS","C","USB","PNC","SCHW","CB",
    "MMC","AON","TRV","ALL","PRU","MET","AFL","HIG","UNM","LNC",
    "DE","EMR","HON","GE","MMM","ITW","PH","ROK","ETN","DOV",
    "FDX","DAL","UAL","LUV","AAL","UBER","LYFT","ABNB","BKNG","EXPE",
    "AMZN","TGT","DG","DLTR","FIVE","BBY","KR","SYY","MKC","HRL",
    # Next 50
    "PFE","BMY","GILD","BIIB","REGN","VRTX","MRNA","ALNY","INCY","SGEN",
    "MDT","BSX","EW","SYK","ZBH","BAX","BDX","ZTS","IDXX","ALGN",
    "AMT","PLD","CCI","EQIX","PSA","EXR","AVB","EQR","MAA","UDR",
    "NEE","DUK","SO","D","AEP","EXC","XEL","WEC","ES","PPL",
    "CVS","MCK","CAH","ABC","WBA","RAD","RHHBY","NVO","SNY","AZN",
    # Next 50
    "SNOW","PLTR","DDOG","NET","CRWD","ZS","OKTA","MDB","GTLB","HUBS",
    "TWLO","ZM","DOCU","BOX","WORK","PATH","APPN","VCRA","CDAY","PEGA",
    "SHOP","PYPL","AFRM","COIN","HOOD","SOFI","UPST","LC","OPFI",
    "RIVN","LCID","NIO","XPEV","LI","FSR","GOEV","WKHS","RIDE","SOLO",
    "RBLX","U","EA","TTWO","ATVI","NTES","BILI","IQ","TME","HUYA",
    # Next 50
    "DIS","CMCSA","WBD","FOXA","NYT","NWSA","IPG","OMC","WPP",
    "SPOT","SNAP","PINS","MTCH","BMBL","YELP","ANGI","IAC","CARS","CDK",
    "CHTR","T","VZ","TMUS","LUMN","SIRI","IACI","GTN","SSP",
    "GS","MS","BX","KKR","APO","CG","ARES","OWL","STEP","BLUE",
    "WM","RSG","CWST","CLH","GFL","SRCL","HCCI","NREO","FNV","GOLD",
    # Next 50
    "FCX","NEM","AA","X","NUE","STLD","CLF","RS","CMC","ATI",
    "LNG","COP","PSX","VLO","MPC","HES","DVN","FANG","PXD","OXY",
    "SLB","HAL","BKR","NOV","HP","RIG","VAL","NR","PUMP","LBRT",
    "JPM","BAC","WFC","C","USB","PNC","TFC","RF","CFG","HBAN",
    "GS","MS","SCHW","STT","BK","NTRS","FIS","FISV","GPN","WEX",
]

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ FOREX Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
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

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ CRYPTO DATA Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ


COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "BNB": "binancecoin",
    "SOL": "solana", "DOGE": "dogecoin", "ADA": "cardano", "TRX": "tron",
    "AVAX": "avalanche-2", "SHIB": "shiba-inu", "DOT": "polkadot", "LINK": "chainlink",
    "MATIC": "matic-network", "TON": "the-open-network", "BCH": "bitcoin-cash", "LTC": "litecoin",
    "UNI": "uniswap", "XLM": "stellar", "ATOM": "cosmos", "ETC": "ethereum-classic",
    "NEAR": "near", "APT": "aptos", "FIL": "filecoin", "ICP": "internet-computer",
    "HBAR": "hedera-hashgraph", "ARB": "arbitrum", "VET": "vechain", "OP": "optimism",
    "MKR": "maker", "AAVE": "aave", "GRT": "the-graph", "INJ": "injective-protocol",
    "SUI": "sui", "TIA": "celestia", "SEI": "sei-network", "RUNE": "thorchain",
    "FLOW": "flow", "ALGO": "algorand", "PEPE": "pepe", "WIF": "dogwifcoin",
    "BONK": "bonk", "FLOKI": "floki", "JUP": "jupiter-exchange-solana", "RENDER": "render-token",
    "FET": "fetch-ai", "IMX": "immutable-x", "STX": "blockstack", "QNT": "quant-network",
    "USDT": "tether", "USDC": "usd-coin", "DAI": "dai", "FDUSD": "first-digital-usd"
}

def fetch_coingecko_prices():
    try:
        ids = ",".join(set(COINGECKO_IDS.values()))
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return {}
        data = r.json()
        out = {}
        for sym, cg_id in COINGECKO_IDS.items():
            if cg_id in data:
                d = data[cg_id]
                out[sym] = {"price": round(float(d.get("usd", 0)), 8), "change": round(float(d.get("usd_24h_change", 0) or 0), 2)}
        return out
    except Exception as e:
        return {}

def fetch_cryptocompare_for_exchange(exchange):
    """Per-exchange spot prices via CryptoCompare relay (proxies blocked exchanges)."""
    syms = ",".join(CRYPTO_COINS.keys())
    try:
        r = requests.get(
            "https://min-api.cryptocompare.com/data/pricemultifull",
            params={"fsyms": syms, "tsyms": "USD", "e": exchange},
            timeout=10
        )
        if r.status_code != 200:
            return {}
        raw = r.json().get("RAW", {})
        out = {}
        for sym, mapping in raw.items():
            usd = mapping.get("USD") or {}
            price = usd.get("PRICE")
            if price is None:
                continue
            change = usd.get("CHANGEPCT24HOUR") or 0
            out[sym] = {"price": round(float(price), 8), "change": round(float(change), 2)}
        return out
    except Exception:
        return {}

def get_crypto_prices():
    """Multi-exchange prices via CryptoCompare relay.
    Direct Binance/Kraken/Bybit calls are blocked from Railway US-East;
    CryptoCompare proxies them and is reachable."""
    from concurrent.futures import ThreadPoolExecutor
    exchange_names = ["Binance", "Kraken", "Coinbase", "Bybit"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {name: pool.submit(fetch_cryptocompare_for_exchange, name) for name in exchange_names}
        per_exchange = {name: f.result() for name, f in futures.items()}

    result = {}
    for sym, info in CRYPTO_COINS.items():
        exchanges = {}
        changes = []
        for ex_name in exchange_names:
            ex_data = per_exchange.get(ex_name, {})
            if sym in ex_data:
                exchanges[ex_name] = ex_data[sym]["price"]
                changes.append(ex_data[sym]["change"])
        avg_change = round(sum(changes) / len(changes), 2) if changes else 0
        result[sym] = {"name": info["name"], "symbol": sym, "exchanges": exchanges, "change24h": avg_change}
    return result

def get_crypto_chart(symbol):
    """24h chart via CoinGecko market_chart endpoint."""
    coin_id = COINGECKO_IDS.get(symbol.upper())
    if not coin_id:
        return []
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": 1},
            timeout=10
        )
        if r.status_code != 200:
            return []
        prices = r.json().get("prices", [])
        # Trim to ~50 points for payload size
        if len(prices) > 50:
            step = max(1, len(prices) // 50)
            prices = prices[::step]
        return [{"t": int(p[0]), "p": round(float(p[1]), 8)} for p in prices]
    except Exception:
        return []

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ STOCKS DATA (Polygon.io free tier) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
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
    "NOW":"ServiceNow Inc.","INTU":"Intuit Inc.",
    "SPGI":"S&P Global","AXP":"American Express","GS":"Goldman Sachs","BLK":"BlackRock",
    "MS":"Morgan Stanley","C":"Citigroup","USB":"US Bancorp","PNC":"PNC Financial",
    "SCHW":"Charles Schwab","CB":"Chubb Ltd.","MMC":"Marsh McLennan","AON":"Aon plc",
    "TRV":"Travelers Companies","ALL":"Allstate Corp.","PRU":"Prudential Financial",
    "MET":"MetLife","AFL":"Aflac","HIG":"Hartford Financial","UNM":"Unum Group","LNC":"Lincoln National",
    "DE":"John Deere","EMR":"Emerson Electric","HON":"Honeywell","GE":"GE Aerospace",
    "MMM":"3M Company","ITW":"Illinois Tool Works","PH":"Parker Hannifin","ROK":"Rockwell Automation",
    "ETN":"Eaton Corp.","DOV":"Dover Corp.","FDX":"FedEx Corp.","DAL":"Delta Air Lines",
    "UAL":"United Airlines","LUV":"Southwest Airlines","AAL":"American Airlines",
    "UBER":"Uber Technologies","LYFT":"Lyft Inc.","ABNB":"Airbnb Inc.","BKNG":"Booking Holdings","EXPE":"Expedia Group",
    "TGT":"Target Corp.","DG":"Dollar General","DLTR":"Dollar Tree","FIVE":"Five Below",
    "BBY":"Best Buy","KR":"Kroger Co.","SYY":"Sysco Corp.","MKC":"McCormick & Co.","HRL":"Hormel Foods",
    "PFE":"Pfizer Inc.","BMY":"Bristol-Myers Squibb","GILD":"Gilead Sciences","BIIB":"Biogen Inc.",
    "REGN":"Regeneron Pharma","VRTX":"Vertex Pharma","MRNA":"Moderna Inc.","ALNY":"Alnylam Pharma",
    "INCY":"Incyte Corp.","SGEN":"Seagen Inc.","MDT":"Medtronic plc","BSX":"Boston Scientific",
    "EW":"Edwards Lifesciences","SYK":"Stryker Corp.","ZBH":"Zimmer Biomet","BAX":"Baxter International",
    "BDX":"Becton Dickinson","ZTS":"Zoetis Inc.","IDXX":"IDEXX Laboratories","ALGN":"Align Technology",
    "AMT":"American Tower","PLD":"Prologis","CCI":"Crown Castle","EQIX":"Equinix Inc.",
    "PSA":"Public Storage","EXR":"Extra Space Storage","AVB":"AvalonBay Communities",
    "EQR":"Equity Residential","MAA":"Mid-America Apartment","UDR":"UDR Inc.",
    "DUK":"Duke Energy","SO":"Southern Company","D":"Dominion Energy","AEP":"American Electric Power",
    "EXC":"Exelon Corp.","XEL":"Xcel Energy","WEC":"WEC Energy","ES":"Eversource Energy","PPL":"PPL Corp.",
    "CVS":"CVS Health","MCK":"McKesson Corp.","CAH":"Cardinal Health","ABC":"AmerisourceBergen",
    "WBA":"Walgreens Boots","RAD":"Rite Aid","NVO":"Novo Nordisk","SNY":"Sanofi","AZN":"AstraZeneca",
    "SNOW":"Snowflake Inc.","PLTR":"Palantir Technologies","DDOG":"Datadog Inc.","NET":"Cloudflare Inc.",
    "CRWD":"CrowdStrike","ZS":"Zscaler Inc.","OKTA":"Okta Inc.","MDB":"MongoDB Inc.",
    "GTLB":"GitLab Inc.","HUBS":"HubSpot Inc.","TWLO":"Twilio Inc.","ZM":"Zoom Video",
    "DOCU":"DocuSign Inc.","BOX":"Box Inc.","PATH":"UiPath Inc.","APPN":"Appian Corp.",
    "SHOP":"Shopify Inc.","PYPL":"PayPal Holdings","AFRM":"Affirm Holdings",
    "COIN":"Coinbase Global","HOOD":"Robinhood Markets","SOFI":"SoFi Technologies",
    "UPST":"Upstart Holdings","LC":"LendingClub","OPFI":"OppFi Inc.",
    "RIVN":"Rivian Automotive","LCID":"Lucid Group","NIO":"NIO Inc.","XPEV":"XPeng Inc.",
    "LI":"Li Auto","FSR":"Fisker Inc.","GOEV":"Canoo Inc.","WKHS":"Workhorse Group",
    "RBLX":"Roblox Corp.","U":"Unity Software","EA":"Electronic Arts","TTWO":"Take-Two Interactive",
    "ATVI":"Activision Blizzard","NTES":"NetEase Inc.","BILI":"Bilibili Inc.","IQ":"iQIYI Inc.",
    "TME":"Tencent Music","HUYA":"Huya Inc.","DIS":"Walt Disney Co.","CMCSA":"Comcast Corp.",
    "WBD":"Warner Bros Discovery","FOXA":"Fox Corp.",
    "NYT":"New York Times","NWSA":"News Corp","IPG":"Interpublic Group","OMC":"Omnicom Group",
    "SPOT":"Spotify Technology","SNAP":"Snap Inc.","PINS":"Pinterest Inc.","MTCH":"Match Group",
    "BMBL":"Bumble Inc.","YELP":"Yelp Inc.","ANGI":"Angi Inc.","IAC":"IAC Inc.",
    "CHTR":"Charter Communications","T":"AT&T Inc.","VZ":"Verizon Communications",
    "TMUS":"T-Mobile US","LUMN":"Lumen Technologies","SIRI":"Sirius XM",
    "BX":"Blackstone Inc.","KKR":"KKR & Co.","APO":"Apollo Global","CG":"Carlyle Group",
    "ARES":"Ares Management","OWL":"Blue Owl Capital",
    "WM":"Waste Management","RSG":"Republic Services","CWST":"Casella Waste","CLH":"Clean Harbors",
    "GOLD":"Barrick Gold","FNV":"Franco-Nevada","FCX":"Freeport-McMoRan","NEM":"Newmont Corp.",
    "AA":"Alcoa Corp.","X":"US Steel","NUE":"Nucor Corp.","STLD":"Steel Dynamics",
    "CLF":"Cleveland-Cliffs","RS":"Reliance Steel","CMC":"Commercial Metals","ATI":"ATI Inc.",
    "LNG":"Cheniere Energy","COP":"ConocoPhillips","PSX":"Phillips 66","VLO":"Valero Energy",
    "MPC":"Marathon Petroleum","HES":"Hess Corp.","DVN":"Devon Energy","FANG":"Diamondback Energy",
    "PXD":"Pioneer Natural","OXY":"Occidental Petroleum","SLB":"SLB","HAL":"Halliburton",
    "BKR":"Baker Hughes","NOV":"NOV Inc.","HP":"Helmerich & Payne",
    "TFC":"Truist Financial","RF":"Regions Financial","CFG":"Citizens Financial","HBAN":"Huntington Bancshares",
    "STT":"State Street","BK":"Bank of New York","NTRS":"Northern Trust",
    "FIS":"Fidelity National Info","FISV":"Fiserv Inc.","GPN":"Global Payments","WEX":"WEX Inc.",
    "RHHBY":"Roche Holding","GFL":"GFL Environmental","SRCL":"Stericycle","HCCI":"Heritage Crystal Clean",
    "LBRT":"Liberty Oilfield","RIG":"Transocean","VAL":"Valaris","NR":"Newpark Resources",
    "CARS":"Cars.com","CDK":"CDK Global","GTN":"Gray Television","SSP":"E.W. Scripps",
    "IACI":"IAC","STEP":"StepStone Group","BLUE":"bluebird bio","PUMP":"ProPetro Holding",
}

def get_stock_prices():
    result = {}
    # Use grouped daily bars - one call, all tickers, free tier compatible
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
    """Intraday chart via yfinance. Polygon free tier doesn't include intraday bars."""
    try:
        ticker = yf.Ticker(symbol)
        # Most recent trading day at 5-min granularity
        hist = ticker.history(period="1d", interval="5m", auto_adjust=True)
        if hist.empty or len(hist) < 2:
            # Fallback: last 5 days hourly (covers weekends/holidays)
            hist = ticker.history(period="5d", interval="60m", auto_adjust=True)
        if hist.empty:
            return []
        result = []
        for ts, row in hist.iterrows():
            close = row.get("Close")
            if close is None:
                continue
            try:
                close_f = float(close)
            except (ValueError, TypeError):
                continue
            if close_f != close_f:  # NaN
                continue
            try:
                t_ms = int(ts.timestamp() * 1000)
            except Exception:
                continue
            result.append({"t": t_ms, "p": round(close_f, 4)})
        return result
    except Exception:
        return []

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ FOREX DATA Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
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

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ ROUTES Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
@app.route("/")
def index():
    return render_template_string(HTML)

_crypto_cache = {"data": None, "ts": 0}

@app.route("/api/crypto")
def api_crypto():
    import time
    now = time.time()
    if _crypto_cache["data"] and now - _crypto_cache["ts"] < 30:
        return jsonify(_crypto_cache["data"])
    data = get_crypto_prices()
    has_data = any(len(v.get("exchanges", {})) > 0 for v in data.values())
    if has_data:
        _crypto_cache["data"] = data
        _crypto_cache["ts"] = now
    elif _crypto_cache["data"]:
        return jsonify(_crypto_cache["data"])
    return jsonify(data)

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

@app.route("/api/accuracy")
def api_accuracy():
    try:
        import sqlite3, os
        db_path = os.environ.get("AGENT_DB", "agent.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT ca.symbol, ca.flag, ca.price, ca.date, cr.outcome
            FROM calls ca
            JOIN call_results cr ON ca.id = cr.call_id
            WHERE cr.days_later = 1
            ORDER BY ca.date DESC
            LIMIT 100
        """)
        rows = c.fetchall()
        conn.close()
        calls = [{"symbol": r[0], "flag": r[1], "price": r[2], "date": r[3], "outcome": r[4]} for r in rows]
        correct = len([c for c in calls if c["outcome"] == "correct"])
        return jsonify({"calls": calls, "correct": correct, "total": len(calls)})
    except Exception as e:
        return jsonify({"calls": [], "correct": 0, "total": 0, "error": str(e)})

HTML = """<!DOCTYPE html>
<html>
<head>
<title>JSCAN</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23050505'/%3E%3Ctext x='4' y='23' font-family='Arial' font-weight='900' font-size='18' fill='%2300ff88'%3EJ%3C/text%3E%3Cpolyline points='14,22 18,12 22,18 26,10' stroke='%2300ff88' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
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
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:12px}
.card{background:#0d0d0d;border:1px solid #1c1c1c;border-radius:14px;overflow:hidden;transition:border-color .2s}
.card:hover{border-color:#2a2a2a}
.card-header{padding:18px 22px 14px;display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid #141414}
.card-ticker{display:flex;align-items:center;gap:8px;margin-bottom:3px}
.card-symbol{font-size:1.15em;font-weight:700;color:#fff;letter-spacing:-.3px}
.star-btn{background:transparent;border:none;cursor:pointer;font-size:1.1em;padding:0 2px;line-height:1;opacity:.6;transition:opacity .2s,transform .2s;color:#888}
.star-btn:hover{opacity:1;transform:scale(1.2);color:#ffd700}
.star-btn.active{opacity:1;color:#ffd700}
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

.sort-label{font-size:.75em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500}
.sort-select{background:#0d0d0d;border:1px solid #1c1c1c;color:#aaa;padding:6px 12px;border-radius:7px;font-size:.8em;font-family:inherit;cursor:pointer;outline:none;transition:border-color .2s}
.sort-select:hover,.sort-select:focus{border-color:#00ff88;color:#fff}
.search-input{background:#0d0d0d;border:1px solid #1c1c1c;color:#e0e0e0;padding:7px 14px;border-radius:7px 0 0 7px;font-size:.85em;font-family:inherit;outline:none;transition:border-color .2s;width:200px}
.search-input:focus{border-color:#00ff88}
.search-input::placeholder{color:#333}
.search-btn{background:#00ff88;border:none;color:#000;padding:7px 14px;border-radius:0 7px 7px 0;font-size:.85em;font-weight:600;font-family:inherit;cursor:pointer;transition:opacity .2s}
.search-btn:hover{opacity:.85}
.controls-bar{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}
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
    document.getElementById('modal-title').textContent=title+' - 24h Chart';
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
    if(tab==='accuracy'&&!window.accuracyLoaded) loadAccuracy();
    if(tab==='sentiment'&&!window.sentimentLoaded) loadSentiment();
}

function loadSentiment(){
    window.sentimentLoaded=true;
    var container=document.getElementById('sentiment-data');
    container.innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Loading sentiment...</div></div>';

    fetch('https://api.alternative.me/fng/?limit=7').then(function(r){return r.json();}).then(function(fgJson){
        var fgData=fgJson.data||[];
        if(!fgData.length){container.innerHTML='<div style="text-align:center;padding:60px;color:#444">Sentiment data unavailable</div>';return;}

        var val=parseInt(fgData[0].value);
        var label=fgData[0].value_classification;
        var prev=fgData[1]?parseInt(fgData[1].value):null;
        var col=val<=25?'#ff4444':val<=45?'#ff8800':val<=55?'#f0c040':val<=75?'#88dd00':'#00ff88';
        var diff=prev!==null?val-prev:0;
        var sign=diff>0?'+':'';

        var h='<div style="max-width:700px;margin:0 auto">';
        h+='<div style="margin-bottom:8px"><h2 style="font-size:1.3em;font-weight:700;color:#fff;margin-bottom:6px">Fear &amp; Greed Index</h2>';
        h+='<p style="color:#555;font-size:.85em;line-height:1.6">A daily measure of crypto market emotion. Low scores mean investors are fearful and selling Ã¢ÂÂ often a buying opportunity. High scores mean greed is driving prices up Ã¢ÂÂ often a sign of overheating.</p></div>';

        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:14px;padding:28px;text-align:center;margin-bottom:20px">';
        h+='<div style="font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;margin-bottom:16px;font-weight:500">Todays Reading</div>';
        h+='<div style="font-size:4em;font-weight:800;color:'+col+'">'+val+'</div>';
        h+='<div style="font-size:1.1em;color:'+col+';font-weight:600;margin-top:4px">'+label+'</div>';
        h+='<div style="margin:20px auto;height:10px;width:80%;background:#1a1a1a;border-radius:5px;overflow:hidden">';
        h+='<div style="height:100%;width:'+val+'%;background:'+col+';border-radius:5px;transition:width 1s ease"></div></div>';
        if(prev!==null){
            h+='<div style="font-size:.78em;color:#444">Yesterday: '+prev+' &nbsp;|&nbsp; Change: <span style="color:'+(diff>0?'#00ff88':diff<0?'#ff4444':'#555')+'">'+sign+diff+'</span></div>';
        }
        h+='<div style="display:flex;justify-content:space-between;margin-top:12px;font-size:.65em;color:#333;width:80%;margin-left:auto;margin-right:auto">';
        h+='<span>0 Extreme Fear</span><span>50 Neutral</span><span>100 Extreme Greed</span></div>';
        h+='</div>';

        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px;margin-bottom:20px">';
        h+='<div style="font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;margin-bottom:14px;font-weight:500">7-Day History</div>';
        h+='<div style="display:flex;gap:8px;align-items:flex-end;height:80px">';
        fgData.slice().reverse().forEach(function(d){
            var v=parseInt(d.value);
            var c=v<=25?'#ff4444':v<=45?'#ff8800':v<=55?'#f0c040':v<=75?'#88dd00':'#00ff88';
            var pct=v;
            var date=new Date(parseInt(d.timestamp)*1000).toLocaleDateString([],{weekday:'short'});
            h+='<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px">';
            h+='<div style="font-size:.65em;color:'+c+';font-weight:600">'+v+'</div>';
            h+='<div style="width:100%;background:'+c+';border-radius:3px 3px 0 0;height:'+pct+'%"></div>';
            h+='<div style="font-size:.6em;color:#444">'+date+'</div>';
            h+='</div>';
        });
        h+='</div></div>';

        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px">';
        h+='<div style="font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;margin-bottom:14px;font-weight:500">Most Influenced Assets</div>';
        h+='<p style="color:#555;font-size:.8em;margin-bottom:14px;line-height:1.5">These assets move most closely with market sentiment.</p>';
        h+='<div id="sentiment-assets" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px"><div style="color:#333;font-size:.8em;padding:20px;text-align:center">Loading prices...</div></div>';
        h+='</div></div>';

        container.innerHTML=h;

        // Now fetch crypto prices for the asset boxes
        fetch('/api/crypto').then(function(r){return r.json();}).then(function(cd){
            var btc=cd['BTC'],eth=cd['ETH'],sol=cd['SOL'];
            var assetHtml='';
            [[btc,'BTC','Bitcoin'],[eth,'ETH','Ethereum'],[sol,'SOL','Solana']].forEach(function(item){
                var asset=item[0],sym=item[1],name=item[2];
                if(!asset){assetHtml+='';return;}
                var prices=Object.values(asset.exchanges||{});
                var price=prices.length?prices.reduce(function(a,b){return a+b;},0)/prices.length:0;
                var chg=asset.change24h||0;
                var cc=chg>0?'#00ff88':'#ff4444';
                assetHtml+='<div style="background:#111;border:1px solid #1c1c1c;border-radius:10px;padding:14px;text-align:center">';
                assetHtml+='<div style="font-size:.95em;font-weight:700;color:#fff;margin-bottom:2px">'+sym+'</div>';
                assetHtml+='<div style="font-size:.7em;color:#555;margin-bottom:8px">'+name+'</div>';
                assetHtml+='<div style="font-size:1em;font-weight:600;color:#e0e0e0;margin-bottom:4px">$'+price.toLocaleString('en-US',{maximumFractionDigits:0})+'</div>';
                assetHtml+='<div style="font-size:.78em;font-weight:600;color:'+cc+'">'+(chg>0?'+':'')+chg.toFixed(2)+'%</div>';
                assetHtml+='<div style="margin-top:8px;font-size:.65em;color:#444">Correlation: <span style="color:#f0c040">High</span></div>';
                assetHtml+='</div>';
            });
            var el=document.getElementById('sentiment-assets');
            if(el) el.innerHTML=assetHtml;
        }).catch(function(){});

    }).catch(function(){
        container.innerHTML='<div style="text-align:center;padding:60px;color:#444">Error loading sentiment data</div>';
    });
}

function loadAccuracy(){
    window.accuracyLoaded=true;
    fetch('/api/accuracy').then(function(r){return r.json();}).then(function(data){
        if(!data||!data.calls||!data.calls.length){
            var emptyMsg='<div style="text-align:center;padding:60px;color:#333"><div style="font-size:1.2em;color:#444;margin-bottom:8px">No scored calls yet</div><div style="color:#333;font-size:.85em">Check back after Monday first run</div></div>';
            document.getElementById('accuracy-data').innerHTML=emptyMsg;
            return;
        }
        var calls=data.calls;
        var correct=calls.filter(function(c){return c.outcome==='correct';}).length;
        var total=calls.length;
        var pct=Math.round(correct/total*100);
        var col=pct>=60?'#00ff88':pct>=50?'#f0c040':'#ff4444';
        var h='<div style="max-width:800px;margin:0 auto">';
        h+='<div style="display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap">';
        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px 28px;flex:1;min-width:140px;text-align:center">';
        h+='<div style="font-size:2.2em;font-weight:700;color:'+col+'">'+pct+'%</div><div style="font-size:.75em;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:.5px">Accuracy</div></div>';
        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px 28px;flex:1;min-width:140px;text-align:center">';
        h+='<div style="font-size:2.2em;font-weight:700;color:#fff">'+total+'</div><div style="font-size:.75em;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:.5px">Total Calls</div></div>';
        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px 28px;flex:1;min-width:140px;text-align:center">';
        h+='<div style="font-size:2.2em;font-weight:700;color:#00ff88">'+correct+'</div><div style="font-size:.75em;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:.5px">Correct</div></div>';
        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;padding:20px 28px;flex:1;min-width:140px;text-align:center">';
        h+='<div style="font-size:2.2em;font-weight:700;color:#ff4444">'+(total-correct)+'</div><div style="font-size:.75em;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:.5px">Incorrect</div></div>';
        h+='</div>';
        h+='<div style="background:#0d0d0d;border:1px solid #1c1c1c;border-radius:12px;overflow:hidden">';
        h+='<table style="width:100%;border-collapse:collapse">';
        h+='<thead><tr style="background:#111;border-bottom:1px solid #1c1c1c">';
        h+='<th style="padding:12px 18px;text-align:left;font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500">Date</th>';
        h+='<th style="padding:12px 18px;text-align:left;font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500">Symbol</th>';
        h+='<th style="padding:12px 18px;text-align:left;font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500">Signal</th>';
        h+='<th style="padding:12px 18px;text-align:left;font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500">Price</th>';
        h+='<th style="padding:12px 18px;text-align:left;font-size:.7em;color:#444;text-transform:uppercase;letter-spacing:.7px;font-weight:500">Result</th>';
        h+='</tr></thead><tbody>';
        calls.slice().reverse().forEach(function(c){
            var fc=c.flag==='GREEN'?'#00ff88':c.flag==='RED'?'#ff4444':'#f0c040';
            var oc=c.outcome==='correct'?'#00ff88':'#ff4444';
            var oe=c.outcome==='correct'?'CORRECT':'WRONG';
            h+='<tr style="border-bottom:1px solid #111">';
            h+='<td style="padding:12px 18px;font-size:.82em;color:#555">'+c.date+'</td>';
            h+='<td style="padding:12px 18px;font-size:.9em;font-weight:700;color:#fff">'+c.symbol+'</td>';
            h+='<td style="padding:12px 18px;font-size:.82em;font-weight:600;color:'+fc+'">'+c.flag+'</td>';
            h+='<td style="padding:12px 18px;font-size:.82em;color:#aaa">$'+c.price+'</td>';
            h+='<td style="padding:12px 18px;font-size:.82em;font-weight:700;color:'+oc+'">'+oe+'</td>';
            h+='</tr>';
        });
        h+='</tbody></table></div></div>';
        document.getElementById('accuracy-data').innerHTML=h;
    }).catch(function(){
        document.getElementById('accuracy-data').innerHTML='<div style="text-align:center;padding:60px;color:#444">Error loading accuracy data</div>';
    });
}

// --- FAVORITES ---
function getFavs(key) {
    try { return JSON.parse(localStorage.getItem(key)||'[]'); } catch(e) { return []; }
}
function toggleFav(key, sym) {
    var favs = getFavs(key);
    var idx = favs.indexOf(sym);
    if(idx >= 0) favs.splice(idx,1); else favs.push(sym);
    localStorage.setItem(key, JSON.stringify(favs));
    return favs.indexOf(sym) >= 0;
}

// --- SORT ---
var cryptoSort = 'default';
var stockSort = 'default';

function sortItems(arr, sortBy) {
    return arr.slice().sort(function(a, b) {
        var af = a.fav, bf = b.fav;
        if(sortBy === 'default') {
            if(af && !bf) return -1;
            if(bf && !af) return 1;
            return 0;
        }
        if(sortBy === 'price-hl') return b.price - a.price;
        if(sortBy === 'price-lh') return a.price - b.price;
        if(sortBy === 'change-hl') return b.chg - a.chg;
        if(sortBy === 'change-lh') return a.chg - b.chg;
        if(sortBy === 'alpha') return a.sym.localeCompare(b.sym);
        if(sortBy === 'spread-hl') return (b.spread||0) - (a.spread||0);
        return 0;
    });
}

function makeSortBar(tabKey, extraOpts) {
    var id = 'sort-sel-' + tabKey;
    var opts = '<option value="default">Default</option><option value="alpha">A-Z</option><option value="change-hl">Change High-Low</option><option value="change-lh">Change Low-High</option><option value="price-hl">Price High-Low</option><option value="price-lh">Price Low-High</option>' + (extraOpts || '');
    var bar = '<div class="controls-bar">';
    bar += '<span class="sort-label">Sort</span>';
    bar += '<select id="' + id + '" class="sort-select-ctrl sort-select" data-tab="' + tabKey + '">' + opts + '</select>';
    bar += '<div style="display:flex">';
    bar += '<input class="search-input" id="search-' + tabKey + '" placeholder="Search ticker..." type="text">';
    bar += '<button class="search-btn" id="sbtn-' + tabKey + '">Search</button>';
    bar += '</div>';
    bar += '<span id="count-' + tabKey + '" style="font-size:.75em;color:#333;margin-left:4px"></span>';
    bar += '</div>';
    return bar;
}

function doSearch(tabKey, q) {
    q = (q || '').toLowerCase().trim();
    var s = vState[tabKey];
    if(!s) return;
    s.items = s.allItems.filter(function(item) {
        return !q || item.sym.toLowerCase().includes(q) || (item.name||'').toLowerCase().includes(q);
    });
    s.page = 1;
    renderVirtualPage(tabKey);
    if(tabKey === 'crypto-tab') {
        setTimeout(function(){
            document.querySelectorAll('#crypto-tab-grid .chart-wrap').forEach(function(wrap){
                var sym = wrap.id.replace('cw-','');
                loadChartInto('crypto', sym, wrap.id, 'tt-'+sym);
            });
        }, 100);
    }
}

// Virtual scroll state
var vState = {};

function initVirtualScroll(tabKey, items, renderFn) {
    var PAGE = 30;
    vState[tabKey] = {items: items, allItems: items, page: 1, renderFn: renderFn, PAGE: PAGE};
    var gridId = tabKey + '-grid';
    var grid = document.getElementById(gridId);
    if(!grid) return;
    renderVirtualPage(tabKey);
    var sentinel = document.getElementById('sentinel-' + tabKey);
    if(!sentinel) return;
    var obs = new IntersectionObserver(function(entries) {
        if(entries[0].isIntersecting) loadMoreVirtual(tabKey);
    }, {threshold: 0.1});
    obs.observe(sentinel);
    vState[tabKey].observer = obs;
}

function renderVirtualPage(tabKey) {
    var s = vState[tabKey];
    if(!s) return;
    var grid = document.getElementById(tabKey + '-grid');
    if(!grid) return;
    var visible = s.items.slice(0, s.page * s.PAGE);
    grid.innerHTML = visible.map(s.renderFn).join('');
    var countEl = document.getElementById('count-' + tabKey);
    if(countEl) countEl.textContent = visible.length + ' of ' + s.items.length;
    wireCardEvents(tabKey);
    // Load charts for all visible cards
    if(tabKey === 'crypto-tab') {
        grid.querySelectorAll('.chart-wrap').forEach(function(wrap){
            var sym = wrap.id.replace('cw-','');
            if(sym) loadChartInto('crypto', sym, wrap.id, 'tt-'+sym);
        });
    } else if(tabKey === 'stocks-tab') {
        grid.querySelectorAll('.chart-wrap').forEach(function(wrap){
            var sym = wrap.id.replace('scw-','');
            if(sym) {
                var ckey = 'stocks-' + sym;
                if(chartCache[ckey]) { drawChart(wrap.id, chartCache[ckey], 'stt-'+sym, false); }
                else { fetch('/api/stocks/chart/'+sym).then(function(r){return r.json();}).then(function(pts){chartCache[ckey]=pts;drawChart(wrap.id,pts,'stt-'+sym,false);}).catch(function(){}); }
            }
        });
    }
}

function loadMoreVirtual(tabKey) {
    var s = vState[tabKey];
    if(!s) return;
    if(s.page * s.PAGE >= s.items.length) return;
    s.page++;
    renderVirtualPage(tabKey);
}

function filterItems(tabKey, query) {
    var s = vState[tabKey];
    if(!s) return;
    var q = query.toLowerCase().trim();
    s.items = s.allItems.filter(function(item) {
        return !q || item.sym.toLowerCase().includes(q) || (item.name||'').toLowerCase().includes(q);
    });
    s.page = 1;
    renderVirtualPage(tabKey);
}

function wireCardEvents(tabKey) {
    // Star buttons
    document.querySelectorAll('#' + tabKey + '-grid .star-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            toggleFav(this.dataset.key, this.dataset.sym);
            if(tabKey === 'crypto-tab') { vState['crypto-tab'].allItems = vState['crypto-tab'].allItems; renderCrypto(cryptoData); }
            if(tabKey === 'stocks-tab') renderStocks(stockData.raw);
        });
    });
    // Chart buttons
    document.querySelectorAll('#' + tabKey + '-grid .chart-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var type = this.dataset.type || 'stocks';
            var sym = this.dataset.coin || this.dataset.sym;
            var title = this.dataset.title || sym;
            openModal(type, sym, title);
        });
    });
    // Stock chart buttons
    document.querySelectorAll('#' + tabKey + '-grid .stock-chart-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var sym = this.dataset.sym, title = this.dataset.title;
            document.getElementById('modal-title').textContent = title + ' - Intraday Chart';
            document.getElementById('modal-chart').innerHTML = '<div class="ld" style="text-align:center;padding-top:70px">Loading...</div>';
            document.getElementById('chart-modal').classList.add('open');
            var ckey = 'stocks-' + sym;
            if(chartCache[ckey]) { setTimeout(function(){drawChart('modal-chart',chartCache[ckey],'modal-tooltip',false);},50); }
            else { fetch('/api/stocks/chart/'+sym).then(function(r){return r.json();}).then(function(pts){chartCache[ckey]=pts;drawChart('modal-chart',pts,'modal-tooltip',false);}).catch(function(){document.getElementById('modal-chart').innerHTML='<div class="no-chart">Chart unavailable</div>';}); }
        });
    });
}

function handleSort(tabKey) {
    var sel = document.getElementById('sort-sel-' + tabKey);
    if(!sel) return;
    if(tabKey === 'crypto') { cryptoSort = sel.value; renderCrypto(cryptoData); }
    if(tabKey === 'stocks') { stockSort = sel.value; renderStocks(stockData.raw); }
    if(tabKey === 'crypto-tab') {
        cryptoSort = sel.value;
        var s = vState['crypto-tab'];
        if(s) { s.allItems = sortItems(s.allItems, cryptoSort); s.page=1; renderVirtualPage('crypto-tab'); }
    }
    if(tabKey === 'stocks-tab') {
        stockSort = sel.value;
        var s = vState['stocks-tab'];
        if(s) { s.allItems = sortItems(s.allItems, stockSort); s.page=1; renderVirtualPage('stocks-tab'); }
    }
}

function wireSortBars() {
    document.querySelectorAll('.sort-select-ctrl').forEach(function(sel) {
        sel.addEventListener('change', function() { handleSort(this.dataset.tab); });
    });
    // Wire search buttons
    ['crypto', 'stocks'].forEach(function(tabKey) {
        var btn = document.getElementById('sbtn-' + tabKey);
        var inp = document.getElementById('search-' + tabKey);
        var vsKey = tabKey + '-tab';
        if(btn && inp) {
            btn.onclick = function() { doSearch(vsKey, inp.value); };
            inp.onkeydown = function(e) { if(e.key === 'Enter') doSearch(vsKey, inp.value); };
        }
    });
}function isFav(key, sym) { return getFavs(key).indexOf(sym) >= 0; }

// --- CRYPTO ---
function renderCrypto(data){
    var favs=getFavs('crypto-favs');
    var arr=[];
    Object.keys(data).forEach(function(sym){
        var c=data[sym],ex=c.exchanges,keys=Object.keys(ex);
        if(!keys.length)return;
        var prices=keys.map(function(k){return ex[k];});
        var minP=Math.min.apply(null,prices),maxP=Math.max.apply(null,prices);
        var avg=prices.reduce(function(a,b){return a+b;},0)/prices.length;
        var spread=maxP>minP?((maxP-minP)/minP*100):0;
        arr.push({sym:sym,name:c.name,price:avg,chg:c.change24h||0,fav:favs.indexOf(sym)>=0,spread:spread,data:c,ex:ex,keys:keys,minP:minP,maxP:maxP});
    });
    arr=sortItems(arr,cryptoSort);
    // Favorites first
    arr.sort(function(a,b){ if(a.fav&&!b.fav)return -1; if(b.fav&&!a.fav)return 1; return 0; });

    function renderCard(item) {
        var sym=item.sym,c=item.data,ex=item.ex,keys=item.keys,minP=item.minP,maxP=item.maxP;
        var spread=item.spread.toFixed(4);
        var bestBuy=keys[Object.values(ex).indexOf(minP)]||keys[0];
        var sc=parseFloat(spread)>0.5?'green':parseFloat(spread)>0.1?'yellow':'gray';
        var chg=item.chg;
        var cwId='cw-'+sym,ttId='tt-'+sym;
        var fav=item.fav;
        var h='<div class="card">';
        h+='<div class="card-header">';
        h+='<div class="card-left"><div class="card-ticker"><span class="card-symbol">'+sym+'</span><button class="chart-btn" data-type="crypto" data-coin="'+sym+'" data-title="'+c.name+' ('+sym+')">24h</button><button class="star-btn'+(fav?' active':'')+'" data-key="crypto-favs" data-sym="'+sym+'" title="Favorite">'+(fav?'&#11088;':'&#9734;')+'</button></div><div class="card-name">'+c.name+'</div></div>';
        h+='<div class="card-right"><div class="card-price">'+fmt(item.price)+'</div><div class="card-change '+changeClass(chg)+'">'+changeStr(chg)+'</div></div>';
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
            h+='<tr><td><a href="'+link+'" target="_blank" class="ex-link">'+e+'</a></td>';
            h+='<td class="ex-price">'+fmt(p)+'</td>';
            h+='<td class="'+(parseFloat(diff)>0?'diff-pos':'diff-zero')+'">'+(parseFloat(diff)>0?'+':'')+diff+'%</td>';
            h+='<td>'+(isBest?'<span class="badge badge-buy">BEST BUY</span>':isHigh?'<span class="badge badge-sell">HIGHEST</span>':'')+'</td></tr>';
        });
        h+='</table></div>';
        return h;
    }

    var h=makeSortBar('crypto','<option value="spread-hl">Spread: High to Low</option>');
    h+='<div id="crypto-tab-grid" class="grid"></div>';
    h+='<div id="sentinel-crypto-tab" style="height:40px"></div>';
    document.getElementById('crypto-data').innerHTML=h;

    if(!vState['crypto-tab']) vState['crypto-tab']={};
    initVirtualScroll('crypto-tab', arr, renderCard);

    wireSortBars();
}

function loadCrypto(){

    document.getElementById('last-updated').textContent='Updating...';
    fetch('/api/crypto').then(function(r){return r.json();}).then(function(data){
        var hasAny=Object.keys(data).some(function(k){return Object.keys(data[k].exchanges).length>0;});
        if(hasAny){cryptoData=data;renderCrypto(data);document.getElementById('last-updated').textContent='Updated '+new Date().toLocaleTimeString();}
        else{document.getElementById('last-updated').textContent='Error loading. Will retry in 30s.';setTimeout(loadCrypto,30000);}
    }).catch(function(){document.getElementById('last-updated').textContent='Error';});
}

// --- STOCKS ---
function fmtVol(v){
    if(!v||v===0) return '-';
    if(v>=1e9) return (v/1e9).toFixed(2)+'B';
    if(v>=1e6) return (v/1e6).toFixed(2)+'M';
    if(v>=1e3) return (v/1e3).toFixed(1)+'K';
    return v;
}

function renderStocks(data){
    var favs=getFavs('stocks-favs');
    var arr=Object.keys(data).map(function(sym){
        var s=data[sym];
        return {sym:sym,name:s.name,price:s.price,chg:s.change24h||0,fav:favs.indexOf(sym)>=0,data:s};
    });
    arr=sortItems(arr,stockSort);
    arr.sort(function(a,b){ if(a.fav&&!b.fav)return -1; if(b.fav&&!a.fav)return 1; return 0; });

    function renderCard(item) {
        var sym=item.sym,s=item.data;
        var chg=item.chg;
        var cwId='scw-'+sym.replace(/[^a-z0-9]/gi,'');
        var ttId='stt-'+sym.replace(/[^a-z0-9]/gi,'');
        var sc=chg>2?'green':chg<-2?'red':'yellow';
        var fav=item.fav;
        var h='<div class="card">';
        h+='<div class="card-header">';
        h+='<div class="card-left"><div class="card-ticker"><span class="card-symbol">'+sym+'</span><button class="chart-btn stock-chart-btn" data-sym="'+sym+'" data-title="'+s.name+' ('+sym+')">1d</button><button class="star-btn'+(fav?' active':'')+'" data-key="stocks-favs" data-sym="'+sym+'" title="Favorite">'+(fav?'&#11088;':'&#9734;')+'</button></div><div class="card-name">'+s.name+'</div></div>';
        h+='<div class="card-right"><div class="card-price">'+fmt(s.price)+'</div><div class="card-change '+changeClass(chg)+'">'+changeStr(chg)+'</div></div>';
        h+='</div>';
        h+='<div class="stats-bar">';
        h+='<div class="stat"><div class="stat-label">Open</div><div class="stat-value gray">'+fmt(s.open)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">High</div><div class="stat-value green">'+fmt(s.high)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Low</div><div class="stat-value red">'+fmt(s.low)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Volume</div><div class="stat-value gray">'+fmtVol(s.volume)+'</div></div>';
        h+='</div>';
        h+='<div class="chart-section"><div class="section-label">Intraday trend (5-min)</div><div class="chart-wrap" id="'+cwId+'"></div><div class="tooltip" id="'+ttId+'"><div class="tooltip-price"></div><div class="tooltip-time"></div></div></div>';
        h+='<div class="stats-bar" style="border-top:1px solid #141414;border-bottom:none">';
        h+='<div class="stat"><div class="stat-label">VWAP</div><div class="stat-value gray">'+(s.vwap?fmt(s.vwap):'-')+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Day Move</div><div class="stat-value '+sc+'">'+changeStr(chg)+'</div></div>';
        h+='<div class="stat"><div class="stat-label">Source</div><div class="stat-value gray">Polygon.io</div></div>';
        h+='<div class="stat"><div class="stat-label">Prev Close</div><div class="stat-value gray">EOD</div></div>';
        h+='</div>';
        h+='</div>';
        return h;
    }

    var h=makeSortBar('stocks');
    h+='<div id="stocks-tab-grid" class="grid"></div>';
    h+='<div id="sentinel-stocks-tab" style="height:40px"></div>';
    document.getElementById('stocks-data').innerHTML=h;

    if(!vState['stocks-tab']) vState['stocks-tab']={};
    initVirtualScroll('stocks-tab', arr, renderCard);

    wireSortBars();
    stockData.loaded=true;
    stockData.raw=data;
}

function loadStocks(){
    document.getElementById('stocks-data').innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Loading stock data from Polygon.io...</div></div>';
    fetch('/api/stocks').then(function(r){return r.json();}).then(function(data){
        if(Object.keys(data).length) renderStocks(data);
        else document.getElementById('stocks-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Stock data unavailable - market may be closed</div>';
    }).catch(function(){document.getElementById('stocks-data').innerHTML='<div class="ld" style="text-align:center;padding:40px">Error loading stocks</div>';});
}

// --- FOREX ---
function renderForex(data){
    var h='<div class="section-header">Major Forex Pairs - Rates from Frankfurter & ExchangeRate-API</div>';
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
                h+='<div class="forex-change-item"><div class="stat-label">'+label+'</div><div class="stat-value gray">-</div></div>';
            } else {
                var cls=val>0?'green':val<0?'red':'gray';
                var sign=val>0?'+':'';
                h+='<div class="forex-change-item"><div class="stat-label">'+label+'</div><div class="stat-value '+cls+'">'+sign+val.toFixed(2)+'%</div></div>';
            }
        });
        h+='</div>';

        h+='<div class="forex-rates">';
        h+='<div class="forex-source"><div class="forex-source-name"><a href="https://www.frankfurter.app" target="_blank" class="ex-link">Frankfurter  ^</a></div><div class="forex-rate">'+d.rate.toFixed(5)+'</div></div>';
        if(d.rate2){
            h+='<div class="forex-source"><div class="forex-source-name"><a href="https://www.exchangerate-api.com" target="_blank" class="ex-link">ExchangeRate-API  ^</a></div><div class="forex-rate">'+d.rate2.toFixed(5)+'</div></div>';
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
            document.getElementById('modal-title').textContent=pair+' - 90 Day Chart';
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

// --- INIT ---
setInterval(function(){
    var active=document.querySelector('.tab-content.active');
    if(active&&active.id==='content-crypto') loadCrypto();
},15000);

window.onload=function(){
    document.getElementById('crypto-data').innerHTML='<div class="loading-screen"><div class="spinner"></div><div class="ld">Fetching prices...</div></div>';
    loadCrypto();
    loadStocks();
    loadForex();
    loadSentiment();
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
  <button class="tab-btn" id="tab-sentiment" onclick="switchTab('sentiment')">&#128200; Sentiment</button>
  <button class="tab-btn" id="tab-brief" onclick="switchTab('brief')">&#128202; Daily Brief</button>
  <button class="tab-btn" id="tab-accuracy" onclick="switchTab('accuracy')">&#129302; AI Accuracy</button>
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
  <div class="tab-content" id="content-sentiment">
    <div id="sentiment-data"><div class="loading-screen"><div class="spinner"></div><div class="ld">Loading sentiment data...</div></div></div>
  </div>
  <div class="tab-content" id="content-brief">
    <div style="max-width:660px;margin:40px auto;text-align:center">
      <div style="font-size:1.4em;font-weight:700;color:#fff;margin-bottom:8px">JSCAN Daily Brief</div>
      <div style="color:#555;font-size:.9em;margin-bottom:32px;line-height:1.6">Get an AI-powered stock research report delivered to your inbox every morning at 8am. Claude analyzes 100 stocks, flags signals, and executes paper trades automatically.</div>
      <a href="https://jscan-agent.up.railway.app" target="_blank" style="display:inline-block;background:#00ff88;color:#000;font-weight:700;font-size:1em;padding:14px 32px;border-radius:8px;text-decoration:none;transition:opacity .2s">Subscribe Free -></a>
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
  <div class="tab-content" id="content-accuracy">
    <div style="max-width:800px;margin:0 auto 28px">
      <h2 style="font-size:1.3em;font-weight:700;color:#fff;margin-bottom:10px">AI Model Accuracy</h2>
      <p style="color:#555;font-size:.85em;line-height:1.7">JSCAN uses a multi-agent AI system powered by Claude. Each morning, four specialized sub-agents independently analyze news sentiment, technical indicators, market momentum, and macro context for 100+ stocks. Their signals are synthesized by a portfolio manager agent into a final GREEN, YELLOW, or RED call. Results are scored the following day against actual price movement. This tracker shows every call made and whether it was correct Ã¢ÂÂ fully transparent, no cherry picking.</p>
    </div>
    <div id="accuracy-data"><div class="loading-screen"><div class="spinner"></div><div class="ld">Loading accuracy data...</div></div></div>
  </div>
</div>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
