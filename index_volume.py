#!/usr/bin/env python3
"""
上证指数 & 沪深两市成交额双轴图 (2024-09-24 至今)
数据源: akshare (Sina) + 东方财富 API 单点校准

左轴: 上证指数
右轴: 两市成交额（亿元），沪市+深市堆叠柱形图
"""

import akshare as ak
import pandas as pd
import subprocess
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# ==================== 字体设置 ====================
for f in fm.fontManager.ttflist:
    if 'WenQuanYi Micro Hei' in f.name and 'Mono' not in f.name:
        prop = fm.FontProperties(fname=f.fname)
        plt.rcParams['font.family'] = prop.get_name()
        break
plt.rcParams['axes.unicode_minus'] = False


def get_data_em_amount():
    """
    尝试用东方财富 API 获取精确成交额（amount 字段）
    如果成功则返回精确数据，失败则回退到估算模式
    """
    try:
        def fetch(secid):
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=0&beg=20240924&end=20260621"
            result = subprocess.run(['curl', '-s', '--max-time', '10', url],
                                    capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)['data']['klines']
            rows = []
            for line in data:
                parts = line.split(',')
                rows.append({'date': parts[0], 'close': float(parts[2]), 'amount': float(parts[6])})
            df = pd.DataFrame(rows)
            df['date'] = pd.to_datetime(df['date'])
            return df.set_index('date')

        sh = fetch("1.000001")
        sz = fetch("0.399001")

        df = pd.DataFrame({
            '上证指数': sh['close'],
            '沪市成交额(亿)': sh['amount'] / 1e8,
            '深市成交额(亿)': sz['amount'] / 1e8,
        }).dropna()
        df['两市合计(亿)'] = df['沪市成交额(亿)'] + df['深市成交额(亿)']
        print("[INFO] 使用东方财富精确成交额数据")
        return df

    except Exception as e:
        print(f"[WARN] 东方财富 API 不可用 ({e})，回退到 Sina 源估算模式")
        return None


def get_data_estimated():
    """
    回退方案: 用 Sina 源成交量 × 均价估算成交额
    以 2024-10-08 真实成交额 ~34500亿 做单点校准
    """
    sh = ak.stock_zh_index_daily(symbol="sh000001")
    sz = ak.stock_zh_index_daily(symbol="sz399001")

    sh['date'] = pd.to_datetime(sh['date'])
    sz['date'] = pd.to_datetime(sz['date'])
    sh = sh.set_index('date')
    sz = sz.set_index('date')

    start = pd.Timestamp('2024-09-24')
    sh = sh[sh.index >= start]
    sz = sz[sz.index >= start]

    # 均价 ≈ (high+low+close)/3
    sh_avg = (sh['high'] + sh['low'] + sh['close']) / 3
    sz_avg = (sz['high'] + sz['low'] + sz['close']) / 3

    sh_amt_raw = sh_avg * sh['volume'] / 1e8
    sz_amt_raw = sz_avg * sz['volume'] / 1e8

    # 2024-10-08 真实两市成交额 ~34500亿
    ref = pd.Timestamp('2024-10-08')
    scale = 34500 / (sh_amt_raw.loc[ref] + sz_amt_raw.loc[ref])

    df = pd.DataFrame({
        '上证指数': sh['close'],
        '沪市成交额(亿)': sh_amt_raw * scale,
        '深市成交额(亿)': sz_amt_raw * scale,
    }).dropna()
    df['两市合计(亿)'] = df['沪市成交额(亿)'] + df['深市成交额(亿)']
    print(f"[INFO] 使用估算模式，校准系数: {scale:.6f}")
    return df


def plot_chart(df, output='index_volume.png'):
    """绘制双轴图"""
    fig, ax1 = plt.subplots(figsize=(18, 8))

    color_idx = '#e74c3c'
    color_sh = '#e67e22'
    color_sz = '#3498db'
    color_ma = '#8e44ad'

    # 左轴: 上证指数
    ax1.plot(df.index, df['上证指数'], color=color_idx, lw=1.6, label='上证指数(左轴)')
    ax1.set_ylabel('上证指数', fontsize=13, color=color_idx)
    ax1.tick_params(axis='y', labelcolor=color_idx)
    ax1.axhline(y=3000, color='#999', ls=':', lw=0.8, alpha=0.5)

    # 右轴: 成交额
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['沪市成交额(亿)'], color=color_sh, alpha=0.35,
            width=0.8, label='沪市成交额(右轴)')
    ax2.bar(df.index, df['深市成交额(亿)'], color=color_sz, alpha=0.35,
            width=0.8, bottom=df['沪市成交额(亿)'], label='深市成交额(右轴)')
    ax2.plot(df.index, df['两市合计(亿)'].rolling(5).mean(),
             color=color_ma, lw=1.5, alpha=0.95, label='两市合计5日均线')
    ax2.set_ylabel('成交额', fontsize=13, color='#555')
    ax2.tick_params(axis='y', labelcolor='#555')

    def y_fmt(x, p):
        return f'{x/10000:.1f}万亿' if x >= 10000 else f'{x:.0f}亿'
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))

    ax1.set_title('上证指数 & 沪深两市成交额 (2024-09-24 至今)',
                  fontsize=18, fontweight='bold', pad=15)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=9, framealpha=0.9, ncol=2)

    ax1.grid(True, alpha=0.2)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"[OK] 图表已保存: {output}")


# ==================== 主程序 ====================
if __name__ == '__main__':
    # 优先尝试东方财富精确数据，失败则用估算
    df = get_data_em_amount()
    if df is None:
        df = get_data_estimated()

    print(f"区间: {df.index[0].date()} → {df.index[-1].date()}，共 {len(df)} 条")
    print(f"成交额最大: {df['两市合计(亿)'].max():.0f}亿 "
          f"({df['两市合计(亿)'].idxmax().date()})")
    print(f"成交额均值: {df['两市合计(亿)'].mean():.0f}亿")
    print(f"上证区间: {df['上证指数'].min():.0f} ~ {df['上证指数'].max():.0f}")

    plot_chart(df)
