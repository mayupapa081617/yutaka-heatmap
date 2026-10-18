from datetime import time
import pandas as pd
import yfinance as yf

def fetch_intraday(raw):
    """Estimate buy pressure from completed, same-session 5-minute bars."""
    entries = {}
    for line in raw.splitlines():
        parts = [v.strip() for v in line.split(',')]
        if len(parts) == 3 and len(parts[1]) == 4 and parts[1].isdigit():
            entries[parts[1]] = parts[2]
    if not entries:
        return pd.DataFrame(), '銘柄登録なし'
    try:
        data = yf.download([f'{c}.T' for c in entries], period='5d', interval='5m',
                           auto_adjust=False, progress=False, threads=True, group_by='ticker')
    except Exception as exc:
        return pd.DataFrame(), f'5分足の取得に失敗: {exc}'
    now = pd.Timestamp.now(tz='Asia/Tokyo')
    records = []
    for code, name in entries.items():
        try:
            frame = data[f'{code}.T'] if isinstance(data.columns, pd.MultiIndex) else data
            frame = frame.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume']).copy()
            if frame.empty:
                continue
            idx = pd.to_datetime(frame.index)
            frame.index = idx.tz_localize('Asia/Tokyo') if idx.tz is None else idx.tz_convert('Asia/Tokyo')
            frame = frame[(frame.index.date == now.date()) &
                          (frame.index + pd.Timedelta(minutes=5) <= now)]
            # Separate morning and afternoon; VWAP is reset at the start of each session.
            if now.time() < time(12, 30):
                frame = frame[(frame.index.time >= time(9, 0)) & (frame.index.time < time(11, 30))]
            else:
                frame = frame[(frame.index.time >= time(12, 30)) & (frame.index.time < time(15, 30))]
            if len(frame) < 4 or (now - frame.index[-1]) > pd.Timedelta(minutes=20):
                continue
            # Require the last 4 bars to be consecutive (no lunch break or missing bars).
            recent = frame.tail(4)
            if not all(recent.index.to_series().diff().iloc[1:] == pd.Timedelta(minutes=5)):
                continue
            volume = frame['Volume'].astype(float)
            typical = (frame['High'] + frame['Low'] + frame['Close']) / 3
            cumulative_vol = volume.cumsum()
            if cumulative_vol.iloc[-1] <= 0:
                continue
            # Approximate VWAP from 5-minute typical prices; not trade-by-trade VWAP.
            vwap = (typical * volume).cumsum() / cumulative_vol.replace(0, float('nan'))
            last = recent.iloc[-1]
            price = float(last['Close'])
            vwap_now = float(vwap.iloc[-1])
            if vwap_now <= 0 or price <= 0:
                continue
            gap = (price / vwap_now - 1) * 100
            last_vol = float(recent['Volume'].iloc[-1])
            prev_vol = float(recent['Volume'].iloc[-2])
            vol_change = (last_vol / prev_vol - 1) * 100 if prev_vol > 0 else None
            if vol_change is None:
                continue
            # Intraday rise relative to first bar's open in the current session.
            session_open = float(frame['Open'].iloc[0])
            rise = (price / session_open - 1) * 100 if session_open > 0 else 0
            bullish_count = int((recent['Close'] > recent['Open']).sum())
            higher_lows = bool(recent['Low'].iloc[-1] > recent['Low'].iloc[-2] > recent['Low'].iloc[-3])
            higher_highs = bool(recent['High'].iloc[-1] > recent['High'].iloc[-2] > recent['High'].iloc[-3])
            # Fixed, transparent 100-point heuristic; not calibrated trading probabilities.
            volume_score = 25 if vol_change >= 100 else (18 if vol_change >= 50 else (10 if vol_change >= 20 else 0))
            vwap_score = 25 if gap > 0 and vwap.iloc[-1] > vwap.iloc[-2] else (15 if gap > 0 else 0)
            price_score = 20 if 1 <= rise <= 3 else (12 if 0 < rise < 1 or 3 < rise <= 5 else 0)
            candle_score = round(bullish_count / 4 * 15)
            trend_score = 15 if higher_lows and higher_highs else (8 if higher_lows or higher_highs else 0)
            score = volume_score + vwap_score + price_score + candle_score + trend_score
            records.append({'コード': code, '銘柄': name, 'スコア': score,
                            '株価%': rise, '出来高増加%': vol_change, 'VWAP乖離%': gap,
                            '足時刻': recent.index[-1].strftime('%H:%M')})
        except Exception:
            continue
    return pd.DataFrame(records), None


def top_ten(raw):
    data, error = fetch_intraday(raw)
    if error:
        raise RuntimeError(error)
    if data.empty:
        return data
    candidates = data[(data["VWAP乖離%"] > 0) & (data["株価%"] > 0)].copy()
    return candidates.sort_values(["スコア", "出来高増加%"], ascending=False).head(10)
