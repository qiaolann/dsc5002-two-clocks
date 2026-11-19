# 两个时钟，同一次比较

**中英老年人功能健康：日历口径与年龄口径，2011–2018**

[English](README.md) · [**简体中文**](README.zh-CN.md)

DSC5002 探索性数据分析与可视化 — 小组项目
刘汉超 · 宋伯骏 · 齐浩男 · 李政远 · 廖滨 · 陈智睿

---

## 研究问题

跨国老龄化比较通常按**日历**来做：取同一调查年份、算均值、读差距。问题在于两个样本的年龄并不相同，而且年龄结构会随追踪和补样不断变化。另一种做法是按**年龄**来比：不管数据来自哪一轮，先对齐到同一年龄再比。

本项目问的是：同一批数据，两种口径各说什么，差多少。结局变量是功能受限——日常生活活动（洗澡、穿衣、吃饭、上下床、如厕，0–5 分）和工具性日常活动（管钱、吃药、购物、做饭，0–4 分）的受限项数。

## 一句话结论

日历口径下，中英差距小而稳定：四轮平均 **+0.07** 项 ADL。年龄口径下，同一批数据给出的是 **50 岁 −0.05、79 岁 +0.33**——因为按计数尺度，中国的 ADL 受限随年龄上升的速度约为英国的 **2.3 倍**（IADL 为 4.4 倍）。两种口径只在 55–60 岁附近吻合。两者都不算错，它们回答的是不同问题；只报其中一个，就会引导出错误结论。

## 数据

两份 HRS 家族的 harmonised 追踪调查，取自 Gateway to Global Aging Data。

| | CHARLS（中国） | ELSA（英国） |
| --- | --- | --- |
| 人群 | 45 岁以上，配偶不限年龄 | 50 岁以上，私宅样本 |
| 使用轮次 | 第 1–4 轮（2011、2013、2015、2018） | 第 5、6、7、9 轮（2010–11 … 2018–19） |
| 轮次配对 | 按实地调查中点配对，平均错开约 0.8 年 | |
| 人·轮（50–79 岁） | 59,049 | 33,362 |
| 独立受访者 | 21,177 | 12,162 |

两份文件之所以可比，是因为都按美国 HRS 的框架做了统一化，`rWadlfive` 与 `rWiadlfour` 在中英两边由同一套题目加总而来。检查后主动排除了两个变量：自评健康（CHARLS 第 4 轮未调查）与即时词语回忆（CHARLS 第 4 轮在每个年龄段内下降 0.4–0.9 个词，幅度超过整个年龄梯度，判断为调查实施变化）。

## 设计

- **轴 A｜日历锚定**：逐轮计算均值及 95% 区间，并给出均值背后的年龄构成与样本流动。
- **轴 B｜年龄锚定**：结局对年龄（中心化到 65 岁）回归，纳入轮次固定效应，分国估计，标准误按个体聚类；再用含年龄 × 国家的合并模型检验两国斜率是否不同。
- **差距曲线**：由系数分布抽 2,000 次，预测 50–79 岁每一个年龄上的国家差距。
- **稳健性**：剔除第一轮（CHARLS 首轮 IADL 偏高约 0.06）、加入统一化的教育变量、个体固定效应，以及两种替代连接函数（计数用 Poisson，是否受限用 Logit）。

估计未加权，描述的是样本而非全国总体。

## 核心数字

| | 中国 | 英国 | 对比 |
| --- | --- | --- | --- |
| ADL 斜率（项/年，0–5 尺度） | 0.0221 (0.0207–0.0235) | 0.0094 (0.0078–0.0110) | 2.36× (1.93–2.79) |
| IADL 斜率（项/年，0–4 尺度） | 0.0207 (0.0194–0.0219) | 0.0047 (0.0036–0.0058) | 4.39× (3.30–5.47) |
| 同一对比，Poisson（对数发生率） | | | 1.77× / 1.66× |
| 同一对比，Logit（是否受限） | | | 1.35× / 1.87× |
| 日历口径差距，ADL | | | +0.072 |
| 年龄口径差距，ADL @50 / @65 / @79 | | | −0.047 / +0.146 / +0.326 |
| 七年间变差的比例 | 18% | 12% | |

结论的方向在每一种设定下都成立，但**倍数取决于尺度**——所以报告中给出计数尺度倍数的同时，附带了这个限定。

## 仓库结构

```
code/                 分析管线，按此顺序运行
  xj_common.py        路径、配色、轮次映射、置信区间工具
  01_extract.py       .dta / .tab  ->  parquet，只抽需要的列
  04_build_panel.py   宽表 -> 长表，限定 50–79 岁，四轮对齐
  05_analysis.py      描述统计、年龄模型、差距分解、稳健性
  05b_link_functions.py  Poisson 与 Logit 复核、尺度对比
  06_figures.py       十张图
  10_tables.py        两张表
  09_typeset.py       markdown -> A4 PDF
  07_build_report.py  markdown -> docx
  02_*, 03_*          探索与数据体检脚本，留档

output/figures/       十张图（PNG 300dpi + PDF）、两张表图
output/tables/        报告中引用的全部数值，CSV 格式
report/               提交版报告（PDF）

Group project/        原始调查数据——不在仓库中（体积大，课程授权）
data_clean/           派生缓存——不在仓库中（由管线重新生成）
```

## 十张图

| # | 文件 | 展示内容 |
| --- | --- | --- |
| 1 | `F1_design` | 四轮如何在实地时间上配对 |
| 2 | `F2_calendar_anchored` | 日历口径：两条线都平，差距小 |
| 3 | `F3_composition` | 补样与流失如何改变年龄结构 |
| 4 | `F4_sample_flow` | 两个面板的流失与补样对比 |
| 5 | `F5_age_adl` | ADL 的年龄曲线，约 54 岁交叉 |
| 6 | `F6_age_iadl` | IADL 的年龄曲线，分歧更陡 |
| 7 | `F7_gap_by_age` | 两种口径叠在一张图——核心结果 |
| 8 | `F8_within_person` | 个体层面：变差的是少数 |
| 9 | `F9_slope_robustness` | 四种设定，以及倍数随尺度的变化 |
| 10 | `F10_diabetes` | 反例：糖尿病的时间趋势相反 |

## 复现

原始文件不在仓库中。把 `GH_CHARLS_d2.dta` 与 `gh_elsa_h.tab` 放到 `Group project/` 下后：

```bash
python -u code/01_extract.py
python -u code/04_build_panel.py
python -u code/05_analysis.py
python -u code/05b_link_functions.py
python -u code/06_figures.py
python -u code/10_tables.py
python -u code/09_typeset.py
```

依赖：`pandas`、`numpy`、`scipy`、`statsmodels`、`matplotlib`、`pymupdf`；生成可编辑报告另需 `python-docx`（已在 `code/vendor` 中）。

## 解读时要注意

- 横截面的年龄梯度把年龄与出生队列混在一起；个体固定效应能去掉队列成分，但会引入失访选择。
- 自评的功能困难会被期望与适应所过滤。统一题目能减轻但不能消除这个问题，且本项目没有锚定情景题（anchoring vignettes）可用来检验。这是跨国比较最大的威胁。
- 糖尿病记的是"是否曾被医生告知"，其时间趋势混合了发病率与诊断水平的变化。
- 哪个坐标轴有信息取决于结局：功能受限由年龄轴承载结论，糖尿病则由日历轴承载。

## 参考文献

Zhao Y, Hu Y, Smith JP, Strauss J, Yang G. Cohort profile: the China Health and Retirement Longitudinal Study (CHARLS). *International Journal of Epidemiology*. 2014;43(1):61–68.

Steptoe A, Breeze E, Banks J, Nazroo J. Cohort profile: the English Longitudinal Study of Ageing. *International Journal of Epidemiology*. 2013;42(6):1640–1648.

Gateway to Global Aging Data. *Harmonized CHARLS Documentation, Version D.2*; *Harmonized ELSA Documentation, Version H*.

Katz S, Ford AB, Moskowitz RW, Jackson BA, Jaffe MW. Studies of illness in the aged: the index of ADL. *JAMA*. 1963;185:914–919.

Lawton MP, Brody EM. Assessment of older people: self-maintaining and instrumental activities of daily living. *The Gerontologist*. 1969;9(3):179–186.
