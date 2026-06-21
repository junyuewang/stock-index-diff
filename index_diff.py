#!/usr/bin/env python3
"""
上证指数 − 创业板指数 差值曲线
数据来源: akshare
时间范围: 2010-05-31 至今
"""

import akshare as ak
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互后端，服务器友好
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ===== 中文字体设置（自动查找） =====
plt.rcParams['axes.unicode_minus'] = False

font_path = None
for f in fm.fontManager.ttflist:
    if 'WenQuanYi Micro Hei' in f.name and 'Mono' not in f.name:
        font_path = f.fname
        break
if font_path is None:
    import glob
    candidates = glob.glob('/usr/share/fonts/**/*.ttf', recursive=True) + \
                 glob.glob('/usr/share/fonts/**/*.otf', recursive=True)
    for c in candidates:
        if 'wqy' in c.lower() or 'wenquan' in c.lower():
            font_path = c
            break

if font_path:
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']


# ===== 主程序 =====
def main(start_date='2010-05-31'):
    print("获取上证指数数据...")
    sh = ak.stock_zh_index_daily(symbol="sh000001")

    print("获取创业板指数数据...")
    cy = ak.stock_zh_index_daily(symbol="sz399006")

    # 数据清洗
    sh['date'] = pd.to_datetime(sh['date'])
    cy['date'] = pd.to_datetime(cy['date'])
    sh = sh.set_index('date')[['close']].rename(columns={'close': '上证指数'})
    cy = cy.set_index('date')[['close']].rename(columns={'close': '创业板指'})

    # 截取起始日期
    start = pd.Timestamp(start_date)
    sh = sh[sh.index >= start]
    cy = cy[cy.index >= start]

    # 合并计算差值
    df = sh.join(cy, how='inner').dropna()
    df['差值'] = df['上证指数'] - df['创业板指']

    print(f"数据区间: {df.index[0].date()} → {df.index[-1].date()}，共 {len(df)} 个交易日")

    # ===== 绘图 =====
    fig, ax = plt.subplots(figsize=(16, 7))

    ax.plot(df.index, df['差值'], color='#2c3e50', lw=1.1, label='上证指数 − 创业板指数')
    ax.axhline(y=0, color='red', ls='--', lw=0.8, alpha=0.6)

    ax.fill_between(df.index, 0, df['差值'],
                    where=(df['差值'] >= 0), color='#e74c3c', alpha=0.15,
                    label='上证 > 创业板')
    ax.fill_between(df.index, 0, df['差值'],
                    where=(df['差值'] < 0), color='#27ae60', alpha=0.15,
                    label='上证 < 创业板')

    ax.set_title(f'上证指数 − 创业板指数 差值曲线 ({start_date} 至今)',
                 fontsize=17, fontweight='bold', pad=15)
    ax.set_ylabel('指数差值', fontsize=13)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.25)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output_path = 'index_diff.png'
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"✅ 图片已保存: {output_path}")

    # ===== 统计摘要 =====
    print(f"\n📊 统计摘要")
    print(f"  差值最高: {df['差值'].max():.2f}  ({df['差值'].idxmax().date()})")
    print(f"  差值最低: {df['差值'].min():.2f}  ({df['差值'].idxmin().date()})")
    print(f"  最新差值: {df['差值'].iloc[-1]:.2f}")
    print(f"  上证领先占比: {(df['差值'] > 0).mean() * 100:.1f}%")
    print(f"  创业板领先占比: {(df['差值'] < 0).mean() * 100:.1f}%")

    return df


if __name__ == '__main__':
    main()
