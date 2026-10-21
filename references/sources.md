# 资料来源与核验范围

多品种扩展另见[ETF与LOF原始来源及适用范围](product-sources-etf-lof.md)、[可转债与其他场内基金来源](product-sources-cb-other.md)。它们与[业务规则卡和估值时间表](product-worked-sheets.md)一起使用；某条规则经核验不等于某只产品的全部业务均已核验。新增[2026产品图谱](product-atlas.md)使用冻结的真实日线，缺少的历史净值、权限、权益和交易状态资料保留未知。

课程使用规则原文、教材原著、开源实现和合成案例四类资料。它们承担不同作用：交易规则决定适用约束；教材提供概念和分析框架；软件展示某一种实现；案例用于练习。软件画出一个结果，不会自动证明某个定义唯一或某套策略有收益优势。

## 交易基础的主要来源

核验基准日为2026年10月20日。具体课节还需注明产品、板块和生效范围。新的一次实时咨询涉及规则变更时，应再次核验。

| 来源 | 本课程使用范围与限制 |
| --- | --- |
| [上交所交易规则2026年修订发布通知](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml) | 发布于2026-04-24，通知载明2026-07-06施行，同时继续暂缓实施附件列明的部分条文。查看正文还须核对暂缓条文和证券专门规则。已核对正文中交收前卖出及例外、部分成交、价格时间优先等规定 |
| [上交所交易规则目录](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/) | 查后续规则和适用指引，不能仅凭搜索结果时间确认全部条文已生效 |
| [深交所投资者教育](https://investor.szse.cn/) | 股票入门、产品机制和规则解读的主要入口。历史投教资料的数字须与当前规则复核 |
| [深交所股票入市手册](https://investor.szse.cn/institute/bookshelf/manualseriesbook/P020190322685818724112.pdf) | 用于基础概念和机制解释，不独立作为2026年全部具体规则的证明 |
| [北交所交易规则发布公告](https://www.bse.cn/jygl_list/200028217.html) | 北交所股票规则来源之一。不得直接套用沪深普通股票的申报及交易限制 |
| [证监会](https://www.csrc.gov.cn/) | 投资者保护、风险提示、监管要求。具体品种的案例不自动适用于另一品种 |

佣金采用学习者实际券商协议及交割单；税费和过户等项目需按当前适用规定核验。教材中的固定费用或申报单位若未绑定规则来源，均明确标记为题设，不作为实际收费或权限承诺。

## 蜡烛图与缠论

- 史蒂夫·尼森《Japanese Candlestick Charting Techniques》的[出版社书目](https://www.penguinrandomhouse.com/books/350650/japanese-candlestick-charting-techniques-by-steve-nison/)用于识别原著。课程按知识依赖自编讲解与图例，不声称已逐页核验全部版本、译名或原书案例，也不复制整书。
- 缠论主要依据缠中说禅《教你炒股票》系列。[作者博客](https://blog.sina.com.cn/chzhshch)与[第69课原文](https://blog.sina.com.cn/s/blog_486e105c01000c5b.html)是直接来源入口。M11/M12另列本章采用的划分口径和查到的原文。
- 原文、后续解释、教学简化与软件算法须分别标明。课件中以给定次级别走势区间讲中枢交集时，必须保留次级别与走势类型的前提。不能推广成任意三笔或三根K线。
- 完整历史图上可定位结构，不等于该位置发生时就可确认。保留确认时间及后续可能修改的候选结构。

## 借鉴的开源项目与教学方法

| 项目 | 借鉴什么 | 未据此证明什么 |
| --- | --- | --- |
| [Datawhale Quant for Beginners](https://github.com/datawhalechina/quant-for-beginners) | 概念、实例、图示和交互观察结合；分阶段路线 | 其课程或示例策略不替代完整A股规则和交易训练 |
| [The Carpentries课程设计](https://carpentries.github.io/lesson-development-training/lesson-design.html) | 先写学习成果，再设计检验与讲解 | 一份课程设计不能证明实际教学有效 |
| [认知负荷与渐隐示例](https://carpentries.github.io/instructor-training/05-memory.html) | 小步讲解、完整示范、逐步减少提示、图文对齐 | 不把初学者自行绘制复杂图谱当作第一份作业 |
| [KLineChart](https://github.com/klinecharts/KLineChart) | K线和标注的展示方式 | 图表库不提供行情真实性、规则适用性或收益证据 |
| [Lightweight Charts](https://github.com/tradingview/lightweight-charts) | 金融图表的交互方式 | 本版未把其运行时纳入核心课程；采用时另查归属标注要求 |
| [chan.py说明](https://github.com/Vespa314/chan.py/blob/main/quick_guide.md) | 增量行情、候选线段与确认状态 | 未将某套实现认定为原文的唯一解释 |
| [CZSC](https://github.com/waditu/czsc) | 结构叠加、回放、多周期及报告组织 | 未将项目示例回测视为课程策略的有效性证明 |
| [AKShare](https://akshare.akfamily.xyz/introduction.html) | 历史数据获取的候选途径 | 本版核心练习无数据API依赖；具体接口及数据使用条件需另查 |
| [Backtesting.py](https://github.com/kernc/backtesting.py) | 完整规则、费用与结果指标的联系 | 通用回测不能自动复现A股交易约束；实际引入须复核许可证 |

本版自编合成数据与本地展示，不要求学习者安装这些项目。调研范围是项目说明与关键文档，不能等同完整源码、性能或安全审计。

## 验证与结论的边界

回测可能因反复筛选参数和样本得到过于乐观的结果。[Bailey等人的原始研究](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)讨论此类过拟合。本课先用小例子理解费用、基准、样本、未来信息和规则修改，再按需深入统计方法。

可观察的学习成果是解释、判断、计算、记录与修正。方法收益、实时成交、极端情景和真实情绪反应各有验证范围。请在结论中写清“什么数据、什么规则、什么时期支持了什么判断”。


## 0.2.0真实图数据

新增三只股票2024年下半年375根不复权日线，主源新浪、对照腾讯。完整口径、单位差异和上游使用权边界见[数据说明](chart-data.md)。不得沿用0.1.0“所有图均为合成”的结论；青禾示意图与真实历史包分开标识。公开数据可访问不等于发布授权，本次数据包限本地教学审阅。


## 最新主案例：2026

主案例已切换为四只2026科技与高波动股票，共751根、截至10月19日；来源、逐股成交量换算、原始披露与已核实权益事件见[2026数据](data-2026.md)。上节375根2024数据是补充材料，不再作为默认案例。
