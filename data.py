import logging
import time

import yfinance as yf

from config import SYMBOLS
from pivot import calculate_pivot, calculate_cpr


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class YahooMarketData:

    def __init__(self, retries=3, delay=3):
        self.retries = retries
        self.delay = delay

    def fetch_previous_day_ohlc(self, symbol):

        for attempt in range(self.retries):

            try:

                ticker = yf.Ticker(symbol)

                df = ticker.history(
                    period="10d",
                    interval="1d",
                    auto_adjust=False
                )

                if df.empty:
                    raise Exception("Yahoo Finance returned no data")

                df = df.dropna(
                    subset=["High", "Low", "Close"]
                )

                if len(df) < 1:
                    raise Exception("No valid OHLC data")

                # Latest completed daily candle
                previous = df.iloc[-1]

                return {
                    "High": round(float(previous["High"]), 2),
                    "Low": round(float(previous["Low"]), 2),
                    "Close": round(float(previous["Close"]), 2),
                    "Date": str(previous.name.date())
                }

            except Exception as error:

                logging.warning(
                    f"{symbol} attempt "
                    f"{attempt + 1}/{self.retries} failed: "
                    f"{error}"
                )

                if attempt < self.retries - 1:
                    time.sleep(self.delay)

        logging.error(
            f"Could not fetch data for {symbol}"
        )

        return None


def get_all_market_data():

    market = YahooMarketData()

    results = {}

    for name, symbol in SYMBOLS.items():

        logging.info(
            f"Fetching data for {name} ({symbol})"
        )

        ohlc = market.fetch_previous_day_ohlc(symbol)

        if ohlc is None:

            logging.warning(
                f"Skipping {name} - data unavailable"
            )

            continue

        try:

            pivot_levels = calculate_pivot(
                ohlc["High"],
                ohlc["Low"],
                ohlc["Close"]
            )

            cpr_levels = calculate_cpr(
                ohlc["High"],
                ohlc["Low"],
                ohlc["Close"]
            )

            results[name] = {

                "symbol": symbol,

                "date": ohlc["Date"],

                "high": ohlc["High"],

                "low": ohlc["Low"],

                "close": ohlc["Close"],

                "pivot": pivot_levels,

                "cpr": cpr_levels

            }

        except Exception as error:

            logging.error(
                f"Calculation error for {name}: {error}"
            )

    return results


if __name__ == "__main__":

    print("\n")
    print("=" * 50)
    print("ParthTraderAlerts Market Data Test")
    print("=" * 50)

    market_data = get_all_market_data()

    if not market_data:

        print("\n❌ No market data received.")

    else:

        for name, data in market_data.items():

            print("\n")
            print(f"📊 {name}")
            print("-" * 40)

            print(f"Date  : {data['date']}")
            print(f"High  : {data['high']}")
            print(f"Low   : {data['low']}")
            print(f"Close : {data['close']}")

            print("\nPivot Levels")

            print(
                f"Pivot : {data['pivot']['Pivot']}"
            )

            print(
                f"R1    : {data['pivot']['R1']}"
            )

            print(
                f"R2    : {data['pivot']['R2']}"
            )

            print(
                f"R3    : {data['pivot']['R3']}"
            )

            print(
                f"S1    : {data['pivot']['S1']}"
            )

            print(
                f"S2    : {data['pivot']['S2']}"
            )

            print(
                f"S3    : {data['pivot']['S3']}"
            )

            print("\nCPR Levels")

            print(
                f"TC    : {data['cpr']['TC']}"
            )

            print(
                f"Pivot : {data['cpr']['Pivot']}"
            )

            print(
                f"BC    : {data['cpr']['BC']}"
            )

    print("\n")
    print("=" * 50)
