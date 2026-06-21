# 2026-06-21 会话记录

> 与 AstrBot 的完整对话，涉及 akshare 数据获取、matplotlib 绘图、GitHub 备份。

---

## 1. 上证指数 − 创业板指数差值曲线

**需求**: 用 akshare 画过去十年差值曲线，后来改为 2010-05-31 至今。

**关键结果**:
- 区间: 2010-06-01 → 2026-06-18（3896 个交易日）
- 差值最高: +2057.28（2010-11-05）
- 差值最低: −161.91（2026-06-18，创业板历史性反超）
- 上证领先占比: 99.7%

**踩坑**:
- 中文字体乱码 → 系统有 WenQuanYi Micro Hei，需显式指定
- 脚本: `index_diff.py`

---

## 2. 上证指数 & 两市成交额双轴图

**需求**: 2024-09-24 至今，成交额（亿元），沪市+深市堆叠。

**关键结果**:
- 成交额最大: 3.45 万亿（2024-10-08）
- 成交额均值: 1.72 万亿
- 上证区间: 2863 → 4243

**踩坑**:
- 第一版成交量单位标错（股 vs 手）
- 第二版用户怀疑只有沪市 → 验证后两市数据都在
- 第三版要求换成交额 → 东方财富 API 被限流
- 解决方案: Sina 源成交量 × 均价，以 10/8 真实值 3.45 万亿单点校准
- Python requests/urllib 全部 `RemoteDisconnected`，curl 在 shell 里能通但在 subprocess 里偶发空响应
- 限流原因: 短时间内 ~10 次请求触发反爬临时封 IP（5~15分钟自动解）

**脚本**: `index_volume.py`（含自动降级：优先 EM API，失败回退估算）

---

## 3. GitHub 备份

**仓库**: https://github.com/junyuewang/stock-index-diff

**文件**:
- `index_diff.py` — 差值曲线脚本
- `index_volume.py` — 成交额双轴图脚本（含自动降级）
- `README.md` — 使用说明

**方法**: 通过 GitHub Contents API (PUT) 上传，绕过了 git push 超时问题。

**安全提醒**: Personal Access Token 在聊天中暴露，建议撤销重新生成。

---

## 4. 环境信息

- OS: Linux
- Python: 3.11 (miniforge3)
- 关键库: akshare, pandas, matplotlib
- Workspace: `/home/junyue/AstrBot-master/data/workspaces/webchat_FriendMessage_webchat_astrbot_fa32b748-3ebd-4ea8-badd-5ffef619eea9/`
- Root 密码: 已记录（102427）
- 中文字体: WenQuanYi Micro Hei

---

## 5. 经验总结

| 问题 | 解法 |
|------|------|
| 中文字体乱码 | 显式 `font_manager.FontProperties(fname=...)` |
| EM API 限流 | 等几分钟自动解，或用 Sina 源降级 |
| git push 超时 | GitHub Contents API 直传 |
| Python HTTP 库被封 | 换 curl subprocess 或等解封 |
