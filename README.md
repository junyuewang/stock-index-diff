# 📈 上证指数 - 创业板指数 差值曲线

使用 [akshare](https://github.com/akfamily/akshare) 获取 A 股指数数据，绘制上证综指与创业板指的差值曲线。

## 快速开始

```bash
pip install akshare pandas matplotlib
python index_diff.py
```

运行后在当前目录生成 `index_diff.png`。

## 数据说明

- **上证指数**: `sh000001`
- **创业板指**: `sz399006`
- **默认时间范围**: 2010-05-31 至今
- **差值**: 上证指数收盘价 − 创业板指收盘价

## 图表解读

| 区域 | 含义 |
|------|------|
| 红色填充、零轴上方 | 上证 > 创业板，主板相对强势 |
| 绿色填充、零轴下方 | 创业板 > 上证，成长股相对强势 |

## License

MIT
