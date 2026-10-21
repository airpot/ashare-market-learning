# ETF and LOF primary sources

The public release date is the publication date of the source document. The effective date is the date when its specified terms start. The intraday availability time is the first time during the day when the information was available. A date with day precision does not give this time.

Check date: **2026-10-20, Asia/Shanghai**. This portable guide gives source information for M16 and M17. It contains product facts and examples with dates, not recommendations. The observation date does not show that a previous document has all subsequent changes. A missing effective date, status at the previous decision time or availability timestamp stays unknown.

Tutor: Use the specified product, share class, operation, and date. We recommend that you use the applicable rule for the specified date and the product notice. We recommend these sources as an alternative to general information in training material. Give the explanation of one applicable fact at a time. Do not use data from after the decision time to fill missing values for previous decision times.

A publication after a cutoff can give evidence for an explanation after the fact. But do not put this publication into the previous decision packet.

Record worked examples as practice with `assisted` status. Do not get fills from trades that occurred or same-time NAV from OHLCV.

<a id="selected-products"></a>
## Product names and codes

| Code | Identified product and exposure | Manager document for product name and code | Applicable to |
| --- | --- | --- | --- |
| 510300 | Huatai-PineBridge CSI 300 equity ETF | S05 | Equity ETF for exchange-listed shares in mainland China. Do not use its primary-processing rules for a different ETF without other evidence. |
| 588000 | ChinaAMC STAR 50 equity ETF | S06 | This is a selected equity index. It is not each STAR stock or a portfolio of the full market. |
| 518880 | HuaAn gold ETF. Gold spot contracts in mainland China | S07 | This is not a gold-miner equity fund or a commodity-futures roll portfolio. |
| 511010 | Cathay SSE 5-year Treasury-bond ETF | S08 | Treasury exposure. A synthetic corporate-credit shock is not the holdings that the fund has. |
| 513100 | Cathay Nasdaq 100 QDII ETF | S09 | Cross-border equity exposure. Use its calendars, FX, valuation and primary terms. |
| 161725 | China Merchants CSI Liquor Index A. Listed LOF units | S10, S11 | Equity index fund for exchange-listed shares in mainland China. Registration and fees are different for the A and C classes. |
| 161226 | UBS SDIC Silver Futures LOF A | S12 | LOF for commodity futures in mainland China. For these terms, C 019005 has no exchange listing. |

ETF is a product structure. The structure does not give all ETFs a passive objective. S03 identifies Shenzhen's active ETF rules. An ETF feeder is a different fund with its units and terms.

The specified 161130 A RMB feeder LOF in S20 has a feeder strategy and a listed product structure.

<a id="timing"></a>

需要办理具体申购时再读：RTGS是“实时全额结算”，可先理解为逐笔办理交收。这里的“勾单”是核对申购申请与相应资金划付指令是否对应，资金还须足额；一边有申请、另一边缺对应资金，不能当成申购已经完成。这是具体操作核验项，不是二级市场买入者必须先背下的术语。
## Times for each operation

From “T+0” exchange resale, you cannot be sure of same-day completion of each settlement leg, redemption payment or bank withdrawal. Count days with the applicable definition.

| Product / operation | Source evidence | Fields without a full source check |
| --- | --- | --- |
| 510300 exchange purchase and primary creation | S05: Same-day resale of units from an exchange purchase is not permitted, but their redemption is permitted. Same-day sale of units from primary creation is permitted, but their redemption is not permitted. | Basket for each day, the full cash schedule for primary operations, availability of the broker channel for this operation and subsequent amendments. |
| 588000 exchange purchase | Name/code from S06 and S01: The usual restriction for resale before settlement is applicable to equity in mainland China. | Primary schedule for the specified product and basket for each day. Do not use the 510300 terms for this product. |
| 518880 exchange purchase | In S01, the same-day resale exception for gold ETFs is applicable to the product in S07. | Primary-operation times for cash and gold contracts, accounts, minimums and fees in the client's transaction record. |
| 511010 exchange purchase | In S01, the same-day resale exception for bond ETFs is applicable to the product in S08. | Full primary schedule and bond/cash availability for the specified operation. |
| 513100 primary application | S09 gives acceptance-day confirmation. For RTGS (real-time gross settlement) creation, the application and funding instructions must agree with each other. Sufficient funding is also necessary. Clearing of the cash difference occurs T+2. Settlement occurs T+3. Usual remittance of redemption substitution cash occurs in 10 working days or less, with specified extensions. | Funding that occurred, matching, PCF, broker receipt/withdrawal and subsequent notices. |
| 513100 calendar and valuation | S09: working day = SSE day. The primary open day = a trading day for SSE and Nasdaq. Calculation of T NAV occurs T+1. Publication occurs at or before T+2. For the qualifying cross-border exception, S01 gives permission for same-day exchange resale. | First availability time at the previous decision cutoff, IOPV snapshot from the specified cutoff, FX operands, banking calendar and status at each cutoff. |
| 161725 and 161226 subscription/redemption | S10/S12: usual confirmation in T+1 or less. Inquiry starts from T+2. Redemption of newly subscribed units is possible from T+2. Redemption remittance occurs in T+7 or less, with exceptions. | Accurate exchange-sale availability, receipt that occurred and withdrawal. From a usual procedure, you cannot be sure of subscription availability. |
| Cross-system custody transfer for LOFs | S10/S12 identify eligible A units. S18 gives a T-to-T+2 baseline from training material with a source date. This baseline is for off-exchange-to-exchange transfer applications that obey the source requirements. | ChinaClear implementation for the registry check date, class eligibility, account matching, channel capability, fees, acceptance, completion and operation-specific availability. |
| 161725 / 161226 exchange resale | S02's general rule is applicable to identified LOFs in mainland China. A LOF for silver futures in mainland China does not get the commodity-futures **ETF** exception. | Registration that occurred and availability of the specified operation, possible subsequent exceptions for the specified product, halts and order restrictions. |

<a id="fee-boundaries"></a>
## Fees and valuation limits

| Source | Selected fee fact in the source | Do not get |
| --- | --- | --- |
| S05: 510300 | Management fee for each year: 0.15%. Custody fee for each year: 0.05%. | Total ownership cost, broker bill or a charge for each trade. |
| S06: 588000 | Management fee for each year: 0.15%. Custody fee for each year: 0.05%. | A tracking result that you are sure to get. |
| S07: 518880 | Management fee for each year: 0.50%. Custody fee for each year: 0.10%. Primary commission ceiling for cash: 0.5%. Gold-contract primary ceiling: 0.1%. | Commission rate in the specified client's bill or the same terms for the two primary routes. |
| S09: 513100 | Management fee for each year: 0.6%. Custody fee for each year: 0.2%. | That these are the only fund expenses or the commission for the completed trade. |
| S11: 161725 A | Exchange redemption: 1.5% for less than 7 days, 0.5% from 7 days. Off-exchange redemption has more tiers. | From this, you cannot be sure of the exchange **sale** commission or the same tiers for C class. |
| S12: 161226 A | Standard subscription for less than CNY 1m: 1%. Redemption for less than 7 days: 1.5%, for other holding periods, 0.5%. | Subscription permission, sales discounts that the client gets or a holding-period calculation with no possible error. |

Fund expenses change NAV. Do not subtract them again from a NAV-based return or account ledger. Record external fees, the basis for their calculation, and rounding as different items.

S10 gives permission for specified transfer charges. Do not give S18's previous training material as evidence that all transfers have zero fees.

Tracking difference is the difference between fund returns and applicable benchmark returns during the same interval. Tracking error gives the variability of return differences with a method that the source gives. These two quantities are not exchange premiums or spreads.

For a NAV observation, the value date, availability time, currency, and source are necessary. For IOPV, its calculation method and timestamp are also necessary. This reference does not show that redemption at this value is possible. S09/S21 give different cross-border terms for each specified product.

<a id="operation-fields"></a>
## Necessary lookup fields

For each operation with market conditions, get these fields:

- Instrument
- Share class
- Venue
- Date/cutoff
- Operation
- Eligibility
- Minimum/increment
- Quote denominator
- Tick
- Phase
- Order type
- Cancellation
- Price limit
- Halt
- Resale
- Settlement calendar
- Fees
- Source
- Effective date
- Exceptions.

 This guide does **not give a full check of these fields**. If a mandatory field is unknown, do not give the operation as possible in the market. A synthetic exercise can give specified assumptions. Do not give these assumptions as terms that source checks show are correct for previous decision times.

Keep these as different items:

- Opening and closing units/cash
- Available and frozen balances
- Pending applications
- Transfers
- Refunds
- Settlement
- Withdrawal.

 Submission is not confirmation. Confirmation is not availability for each operation. Custody transfer changes the registration location. It does not make one more holding.

The parent worksheets give full examples. This guide does not give a live account balance. It does not give permission information for all products in the market.

<a id="actual-events"></a>
## Examples of 2026 facts with specified limits

| Product and date | Source facts | Do not get |
| --- | --- | --- |
| 161226, 2026-04-03, S13 | Manager's premium warning. The notice gives a halt schedule from the opening to 10:30. Redemption continues. The subscription suspension from Jan 28 includes periodic investment. If there is a subsequent notice, refer to it for reopening information. | A same-time premium value. Evidence that the suspension continues to Aug 31/Sep 30. Minute-by-minute records of reopening that occurred. |
| 161226, 2026-08-07, S14 | The manager gives an Aug 6 close of CNY 2.035 and an **Aug 5** NAV of CNY 1.6639. The notice gives a halt schedule. It also gives continued redemption. | Aug 5 NAV as a correct NAV for Aug 6, or a synthetic Aug 31/Sep 30 premium. |
| 513100, 2026-09-30, S15 | Manager's reference-NAV premium warning. The notice gives a halt schedule from the opening to 10:30. | A synthetic NAV, premium value or evidence of the subsequent trading status that was applicable. |
| 513100, public release date: Sep 30, S16 | Subscription suspension effective date **Oct 8**. Redemption continues. For reopening, a different notice is necessary. | Subscription suspension from Sep 30, or quota exhaustion as the cause. |
| 513100, S17 | Sep 2 announcement: The notice gives this schedule for US Labor Day: primary services stop Sep 7. The notice gives Sep 8 for the services to start again after the holiday. The holiday schedule does not remove other applicable restrictions. | The end of each restriction at Sep 8, or an exchange halt as a necessary result of the holiday. |
| 161130 A RMB and other specified funds, S20 | Jan 14 announcement: the specified services stop Jan 19 and start again Jan 20 for the foreign holiday. | The same NAV or payment timetable for all QDII LOFs. |

A same-date premium has a price and NAV with the same value date. Keep source evidence for the two values, their availability at the cutoff, and the calculation. This guide gives no same-date premium value for Aug 31/Sep 30 with this evidence for 513100 or 161226.

For subsequent NAV with the same value date, identify its publication as information available after the fact. OHLCV without other evidence cannot supply this missing information.

## Source information

The observation date for each entry is 2026-10-20. An unknown field does not give an effective date. The start dates of prospectus contracts do not show the start date of each changed term.

<a id="s01"></a>
### S01 — SSE 2026 trading rules

[Publication notice](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml) · [rule text](https://www.sse.com.cn/lawandrules/sselawsrules2025/fund/trading/c/c_20260424_10817739.shtml). Public release date: 2026-04-24. Effective date: 2026-07-06. Articles 3.1.4–3.1.5 give different terms for turnover before settlement and the specified exceptions.

Underlying-market turnover is a condition for cross-border exceptions. The publication notice keeps deferred provisions. It is not a sheet that gives all conditions necessary for each operation for each product.

<a id="s02"></a>
### S02 — SZSE 2026 trading rules

[Publication notice](https://www.szse.cn/lawrules/rule/trade/current/t20260424_620190.html) · [SZSE rule PDF](https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020260424690713155663.pdf). Public release date: 2026-04-24. Effective date: 2026-07-06. Articles 3.1.4–3.1.5 supply Shenzhen's general rule and product exceptions. Do not get an exception for a LOF for futures in mainland China from the futures ETF wording.

<a id="s03"></a>
### S03 — Active ETFs

[SZSE rule notice](https://www.szse.cn/www/lawrules/rule/fund/list/t20260617_621085.html) · [exchange explanation](https://www.szse.cn/aboutus/trends/news/t20260617_621086.html). Public release date and effective date: 2026-06-17. A specified index is not the investment objective of an active ETF. From this text, you cannot be sure of the listing or operating terms of an identified active ETF.

<a id="s04"></a>
### S04 — Exchange trade and primary creation/redemption

[SSE mechanisms, 2022-06-23](https://etf.sse.com.cn/fund/learning/knowledge/c/5704300.shtml) · [ETF FAQ, publication date unknown](https://www.sse.com.cn/assortment/fund/etf/question/). This training material gives explanations of secondary price, basket consideration and minimum units for the specified product. This guide gives no effective date for this explanation as a rule. Use the rules and fund terms for the registry check date first.

<a id="s05"></a>
### S05 — 510300

[Manager prospectus, 2026 No. 1, CNInfo disclosure host](https://dataclouds.cninfo.com.cn/sjother2/fund/2026/20260812/6a7c6e0f67f7a41dfb1d5f232fe948ec.pdf). Cover month: Aug 2026. Host path: Aug 12. Public disclosure listings identify Aug 13. From the PDF path without other evidence, you cannot be sure of the publication day. Content cutoff: Jul 31. Financial data/fund performance cutoff: Jun 30.

Important notice and sections 10/17 give evidence for these routes/fees.

The different amendment-effective date is unknown.

<a id="s06"></a>
### S06 — 588000

[Manager product summary](https://www.chinaamc.com/upload/resources/file/2026/05/29/9ffa5179b7af4248a2c92b949f2cf617.pdf) · [publication page](https://www.chinaamc.com/c/2026-05-29/941856.shtml). Preparation date: May 28. Public release date: May 29, 2026. The summary gives only the product name/code, objective and fees. The fee-change date and full primary timetable are unknown here.

<a id="s07"></a>
### S07 — 518880

[Manager product summary](https://www.huaan.com.cn/upload2010/2026/03/17/001306125_63166fc3-c425-334c-a857-f4cd187a7cea.pdf). Preparation date: Mar 16. Dispatch date: Mar 17, 2026. The summary gives spot-gold exposure, different primary fee ceilings and embedded expenses. Different primary routes have different settlement risks. The supplied information does not contain the full primary timetable for the registry check date.

<a id="s08"></a>
### S08 — 511010

[Manager prospectus, SSE host](https://www.sse.com.cn/disclosure/fund/announcement/c/new/2026-09-21/511010_20260921_4HQ6.pdf). Public release date: Sep 21, 2026. General content cutoff: Aug 31. Fund performance/portfolio cutoff: Jun 30. Personnel cutoff: Sep 11.

The prospectus gives evidence for Treasury product name/code and tracking/valuation risks. It is a subsequent publication for an Aug 31 decision. The accurate duration for the previous decision time and the full cash timetable for primary operations stay unknown.

<a id="s09"></a>
### S09 — 513100

[Manager prospectus, 2026 No. 1](https://st.gtfund.com//GSGG/2026/09/15/842733829339.PDF). Public release date: Sep 15, 2026. Other content cutoff: Aug 31. Portfolio/fund performance cutoff: Jun 30. Personnel cutoff: Sep 11.

Sections 2/10/11/12 give evidence for these distinctions in calendar, IOPV, NAV, settlement and fees.

The different amendment-effective date is unknown. The supplied information does not contain valuation/FX availability at previous decision times or PCFs for each day.

<a id="s10"></a>
### S10 — 161725 prospectus

[Manager prospectus](https://static.cmfchina.com/fundarticle/20260526/20023108540498.pdf). Host publication: May 26, 2026. Content cutoff: May 15. Financial data/fund performance cutoff: Mar 31.

Sections 8/10 give evidence for confirmation, redeemability, remittance and A-only cross-system transfer. The transfer timetable and charge for the registry check date are unknown. Specified transfer fees are permitted.

<a id="s11"></a>
### S11 — 161725 A product summary

[Manager product summary](https://static.cmfchina.com/fundarticle/20260526/20023109919683.pdf). Preparation date: May 15. Dispatch date: May 26, 2026. The summary gives evidence for the name and code of listed A units, passive objective and route/holding-period fee distinctions. The different change-effective dates and client commission are unknown.

<a id="s12"></a>
### S12 — 161226 prospectus

[CNInfo disclosure copy](https://static.cninfo.com.cn/finalpage/2026-06-12/1225364296.PDF) · [manager copy](https://www.ubssdic.com/upload/20260612/161226_国投瑞银白银期货证券投资基金（LOF）招募说明书（2026年6月第1次更新）.pdf). Public release date: Jun 12, 2026. Content cutoff: Apr 30. Financial data/fund performance cutoff: Mar 31.

The prospectus gives evidence for futures exposure, class restrictions, conditional processing and fees. From the document's usual procedure, you cannot be sure of business permission for each day.

<a id="s13"></a>
### S13 — 161226 premium, halt and subscription suspension

[Manager announcement in SZSE disclosure files](https://disc.static.szse.cn/disc/disk03/finalpage/2026-04-03/1299e90f-e6ed-428e-b2cf-ae652ad2b13e.PDF). The registry records Apr 3, 2026 as the publication/event date. The notice gives this date for the halt/resume schedule. It gives a subscription suspension from Jan 28. This guide gives no premium value or subsequent reopening evidence.

<a id="s14"></a>
### S14 — 161226 example: price and NAV with dates

[Manager announcement in SZSE disclosure files](https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-07/43e6572f-15eb-4377-bcbb-c1d9efb73209.PDF). The registry records Aug 7, 2026 as the publication/event date. The notice gives this date for the halt/resume schedule.

Price value date: Aug 6. NAV value date: Aug 5. Keep the two dates without change. Do not use a reconstructed NAV for the price value date.

<a id="s15"></a>
### S15 — 513100 Sep 30 premium and halt

[Manager announcement](https://st.gtfund.com//GSGG/2026/09/30/844051107192.PDF). The registry records Sep 30, 2026, as the publication/event date. The warning gives no premium value. The intraday publication availability, reference NAV value, and subsequent reopening that occurred are unknown.

<a id="s16"></a>
### S16 — 513100 subscription suspension from Oct 8

[Manager announcement](https://st.gtfund.com//GSGG/2026/09/30/844035490422.PDF). Public release date: Sep 30. Suspension effective date: Oct 8, 2026.

The notice gives protection of holders' interests as the cause. Redemption continues. This guide does not show reopening at or before Oct 20. It does not show quota exhaustion.

<a id="s17"></a>
### S17 — 513100 foreign-market holiday

[Manager announcement](https://st.gtfund.com//GSGG/2026/09/02/841618793296.PDF). Public release date: Sep 2, 2026. The notice gives Sep 7 for the specified primary services to stop. The notice gives Sep 8 for the services to start again after the holiday. The notice identifies 513100.

The holiday schedule does not remove other applicable restrictions. It does not show exchange trading status.

<a id="s18"></a>
### S18 — Custody transfer: training material and baseline limits

[SZSE investor education](https://investor.szse.cn/warning/activities/fundIntroduction/t20210104_584079.html). Public release date: Jan 4, 2021. Effective date for this operation: unknown. The text from the source search gives this timing. After a T-day off-exchange-to-exchange transfer application that obeys the source requirements, sale/redemption applications are available from T+2.

The direct retrieval had a timeout. These source checks do not show the full ChinaClear rules and channel implementation for the registry check date. Use S10's fee terms before the previous no-fee explanation.

<a id="s19"></a>
### S19 — LOF consultation with no evidence of an applicable change

[SSE consultation notice](https://www.sse.com.cn/lawandrules/publicadvice/c/c_20260807_10828305.shtml). Public release date: Aug 7, 2026. Feedback deadline: Aug 22. From this document, you cannot be sure of an effective date for the final rule or the termination of the specified product. A consultation is not a completed delisting.

<a id="s20"></a>
### S20 — QDII feeder LOF holiday example

[E Fund manager announcement](https://cdn.efunds.com.cn/owch/data/bulletin/20260114/关于旗下部分基金2026年1月19日因境外主要投资市场节假日暂停申购、赎回、转换、定期定额投资业务的提示性公告.pdf). Public release date: Jan 14, 2026. The notice gives Jan 19 for the specified services to stop. The notice gives Jan 20 for the services to start again after the holiday. The appendix identifies 161130 A RMB and other specified classes.

The holiday schedule does not remove other applicable restrictions. The supplied information does not contain accurate NAV availability or each class's settlement timetable.

<a id="s21"></a>
### S21 — A foreign-exchange quota risk for the specified product

[E Fund 159696 prospectus, Feb 2026](https://cdn.efunds.com.cn/owch/data/bulletin/20260228/易方达纳斯达克100交易型开放式指数证券投资基金（QDII）更新的招募说明书.pdf?from=org). Cover: Feb 2026. Host path: Feb 28. General content cutoff: Jan 16. Personnel cutoff: Feb 27. Financial data/fund performance cutoff: Dec 31, 2025. From the host path without other evidence, you cannot be sure of the publication day.

The important notice gives possible subscription suspension near the fund's FX quota limit. This risk has a condition for 159696. It gives no evidence of the cause of subscription suspension for 513100 or a LOF.

## Remaining evidence limits

The source registry does not include these items:

- Full archives of source PDFs with hashes
- Order books for previous times
- Each PCF
- Sales-channel fees
- Evidence for allocations/refunds
- Bank receipts for payments that occurred.

The dynamic PCF page for SSE 513100 gave data placeholders during direct extraction. The frozen values for previous decision times do not include figures from a search index. From source retrieval and arithmetic checks, you cannot be sure of live semantics or strategy efficacy. From these checks, you cannot be sure of assessment without previous access or a check from a different reviewer.
