import pandas as pd
from datetime import datetime
from datetime import datetime
from Indicators import Indicators
from Crypto_Data import CryptoData


class AlertLive:
    def __init__(self):
        self.symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "ADAUSDT",
            "XRPUSDT",
            "SOLUSDT",
            "DOTUSDT",
            "DOGEUSDT",
            "LINKUSDT",
            "LTCUSDT",
        ]
        self.timeinterval = 1
        self.temporalidad = f"{self.timeinterval}m"

    async def fetch_data(self, symbol: str):
        df_live_data = CryptoData(symbol, self.temporalidad)
        return await df_live_data.get_live_data()

    async def check_rsi(self):
       # -- = 0 -- BUY -- = 1 -- SELL -- = 2 -- 
        results = []
        now = datetime.now()
        now = str(now.strftime("%H:%M:%S"))
        for symbol in self.symbols:
            df_live_data = CryptoData(symbol, self.temporalidad)
            D = pd.DataFrame(await df_live_data.get_live_data())
            rsi = await Indicators.rsi(D)
            last_rsi = rsi.iloc[-1].round(2)
            if last_rsi <= 30:
                signal = 1
            elif last_rsi >= 70:
                signal = 2
            else:
                signal = 0
            results.append((symbol, now, signal))
        return results

    async def check_stochastic_rsi(self):
        results = []
        for symbol in self.symbols:
            data = await self.fetch_data(symbol)
            rsi_values = await Indicators.rsi(data)
            k, d = await Indicators.stochastic_rsi(rsi_values)
            if k.iloc[-1] <= 15 and k.iloc[-1] > d.iloc[-1] and k.iloc[-2] < d.iloc[-2]:
                signal = 1
            elif (
                k.iloc[-1] >= 85 and k.iloc[-1] < d.iloc[-1] and k.iloc[-2] > d.iloc[-2]
            ):
                signal = 2
            else:
                signal = 0
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            results.append((symbol, now, signal))

            
        return results

    async def check_macd(self):
        results = []
        for symbol in self.symbols:
            data = await self.fetch_data(symbol)
            macd_line, signal_line, histogram = await Indicators.macd(data)
            data_macd = pd.DataFrame()
            data_macd["MACD"] = macd_line
            data_macd["Signal"] = signal_line
            data_macd["Histogram"] = histogram
            if (
                data_macd["MACD"].iloc[-2] > data_macd["Signal"].iloc[-2]
                and data_macd["Histogram"].iloc[-2] > 0
            ) and (
                data_macd["MACD"].iloc[-1] < data_macd["Signal"].iloc[-1]
                and data_macd["Histogram"].iloc[-1] < 0
            ):
                signal = 2
            elif (
                data_macd["MACD"].iloc[-2] < data_macd["Signal"].iloc[-2]
                and data_macd["Histogram"].iloc[-2] < 0
            ) and (
                data_macd["MACD"].iloc[-1] > data_macd["Signal"].iloc[-1]
                and data_macd["Histogram"].iloc[-1] > 0
            ):
                signal = 1
            else:
                signal = 0
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            results.append((symbol, now, signal))
        return results

    async def check_bollinger_bands(self):
        results = []
        for symbol in self.symbols:
            data = await self.fetch_data(symbol)
            sma_21, lower, upper = await Indicators.bollinger_bands(data)
            data["close"] = data["close"].astype(float)
            if data["close"].iloc[-1] > upper.iloc[-1]:
                signal = 2
            elif data["close"].iloc[-1] < lower.iloc[-1]:
                signal = 1
            else:
                signal = 0
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            results.append((symbol, now, signal))
        return results

    async def check_ema_200(self):
        results = []
        for symbol in self.symbols:
            data = await self.fetch_data(symbol)
            data["close"] = data["close"].astype(float)
            ema200 = await Indicators.ema_200(data)
            if (
                data["close"].iloc[-1] > ema200.iloc[-1]
                and data["close"].iloc[-2] < ema200.iloc[-1]
            ):
                # support
                signal = 1
            elif data["close"].iloc[-1] < ema200.iloc[-1] and data["close"].iloc[-2] > ema200.iloc[-1]:
                # resistance
                signal = 2
            else:
                signal = 0
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            results.append((symbol, now, signal))
        return results

    async def check_moving_averages(self):
        results = []
        for symbol in self.symbols:
            data = await self.fetch_data(symbol)
            moving_average = pd.DataFrame()
            moving_average = await Indicators.moving_averages(data)
            if (
                moving_average["MM_5"].iloc[-2] and moving_average["MM_10"].iloc[-2]
            ) < moving_average["MM_20"].iloc[-2] and (
                moving_average["MM_5"].iloc[-1] and moving_average["MM_10"].iloc[-1]
            ) > moving_average[
                "MM_20"
            ].iloc[
                -1
            ]:
                signal = 1
            elif (
                moving_average["MM_5"].iloc[-2] and moving_average["MM_10"].iloc[-2]
            ) > moving_average["MM_20"].iloc[-2] and (
                moving_average["MM_5"].iloc[-1] and moving_average["MM_10"].iloc[-1]
            ) < moving_average[
                "MM_20"
            ].iloc[
                -1
            ]:
                signal = 2
            else:
                signal = 0
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            results.append((symbol, now, signal))
        return results

    async def run(self, indicator):
        results = []
        if indicator == "1":
            results = await self.check_rsi()
        elif indicator == "2":
            results = await self.check_stochastic_rsi()
        elif indicator == "3":
            results = await self.check_macd()
        elif indicator == "4":
            results = await self.check_bollinger_bands()
        elif indicator == "5":
            results = await self.check_ema_200()
        elif indicator == "6":
            results = await self.check_moving_averages()
        return results
