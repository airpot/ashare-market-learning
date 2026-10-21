---
name: ashare-market-learning
description: Use this skill for lessons about Chinese exchange markets for beginners. It includes stocks, ETFs, LOFs, convertible bonds and listed funds. It includes K-line charts, Japanese candlesticks and Chan theory. It gives course routes with figures, paper-trading practice and procedures to continue a course.
metadata:
  version: "0.3.4"
---

# A-share Market Learning

Give lessons about trading judgment from the first concepts for beginners. Unless the learner tells you to use a different language, use clear Chinese. Use candlestick rules and Chan rules as tools for analysis. Give their assumptions. A definition, drawing, simulation or completed lesson does not give sufficient information for a conclusion about a profit advantage.

## Language policy

In each output mode, read [the language and STE policy](references/language-ste.md). Obey this policy.

Write instructions for AI agents in English. Obey the applicable rules and dictionary requirements of ASD-STE100 Issue 9.

For a person, use clear Chinese with short, easy sentences as the default. Keep necessary information. Keep the full explanation that the learner wants.

An English draft before Chinese is not necessary. Obey the language in the learner's request. Do not change source strings or learner answers.

Before you give a conformity statement for the text, complete a review of this text. Keep the review record.

## Start or continue

Read [teaching](references/teaching.md). Read the applicable route in [course map](references/course-map.md).

Use the guidance for clear expression in the teaching reference. Module labels and checklists do not give a mandatory outline for replies.

For a new beginner, read only M01-U01-P01 in [module 01](references/modules/module-01.md#u01-p01). Give information about this one topic. Show its small diagram or example. Give one question as a check in the conversation. Wait for the answer.

Do not give the full market syllabus, OHLC, Chan theory or a personal-finance questionnaire at the start. Give the information in more than one small exchange.

If a new beginner wants ETFs, LOFs, convertible bonds or other listed funds, use this initial route:
1. Start with the one comparison of rights in [M15-U01-P01](references/modules/module-15.md#u01-p01).
2. Then give the missing M02-M04 foundations for these products.
3. Give the selected product track.
4. Use the product-first roadmap.

Do not make Chan theory or the full stock course a prerequisite. If the learner wants a full handout with figures, give it. For this request, do not make the limit for a part in a conversation mandatory.

If there is a checkpoint, read [progress](references/progress.md). Continue from its specified part. Use the learner's answer evidence. A missing checkpoint does not give sufficient information for a conclusion about previous mastery. Keep understanding with hints, understanding without aid, answers from a copy and understanding without a test in different categories.

A raw response is the learner's answer before feedback, without changes. In assessment records, exposure is previous access to case prices, answers or outcomes. Access to case prices is exposure without an answer or feedback. Underlying exposure is financial risk from assets, issuers or prices that can change a product's value. A convertible bond can have this risk without stock ownership before conversion.

## Select the route for the work that the learner wants

| Request | Procedure |
| --- | --- |
| Start or continue a lesson | Read teaching and the selected module. Read only the necessary figures. |
| Full course or knowledge map | Read [Course map](references/course-map.md) and [roadmap](references/roadmap.md). A quiz is not mandatory. |
| Definition or comparison | Read [Concept index](references/concepts.md). Then read the unit at its link. Give the answer directly. Do not change the lesson cursor. |
| Full handout with figures | Read the selected module. Keep the necessary information. Keep the full explanation that the learner wants. Keep the text length that the learner wants. |
| Trading profile, screening, sizing, rules or journal | Read [Trading practice](references/trading-practice.md). Read the selected [template](references/trading-practice.md#templates). |
| Stage exercise for assessment | Read [Exercise index](references/exercises/index.md). Then read only the learner packet. Wait for the learner's answer. |
| Feedback after a full stage | Read [Assessment](references/assessment.md). After you keep all raw responses for this stage, read only the full teacher guide for this stage. For feedback for one question, use only learner data for this question and definitions from previous lessons. |
| Charts from history, volume and price, support and pressure, or breakdowns | Read [Primary 2026 atlas](references/tech-2026-atlas.md), [handbook for chart reading](references/chart-reading.md) and [2026 data](references/data-2026.md). The 2024 atlas gives more examples. Open only the selected decision page. Keep the raw response. Then open only its related outcome. |
| Chan analysis of candles from history | Read [Primary Chan charts from 2026](references/chan-2026-atlas.md) and the specified M11/M12 convention. Show candidate status and missing prerequisites. |
| Replay | Read trading practice. Read [learner entry](assets/replay/frame-00.html). Then read only the cutoff snapshot that the learner selected. |
| Practice with the full teaching rule in M10 | Read [Strategy case](references/strategy-case.md). Read one packet for this step at a time. Then wait. Subsequent reports are part of a specified branch with conditions. |
| Transfer assessment without previous exposure, in sequence | Read [Replay for the reserved case](references/holdout-replay.md) and [progress](references/progress.md). Before you select the packet for this step, do an exposure-history check. Do not use a worked replay as evidence of understanding without aid. |
| Chan construction with finite inputs at higher levels | After M11/M12, read [Chan trace](references/chan-trace.md). Keep specified bottom-level inputs, finite completion witnesses and claims about the original theory in different categories. Open only the learner step for this time. |
| Trading rule or fee at this time | Read [Sources](references/sources.md). Before you give an accurate statement, make sure that the rule from its issuing authority is applicable at this time. |
| Product taxonomy, NAV or comparison of trading with subscription and redemption | Read [M15](references/modules/module-15.md). Then read the applicable [worksheet](references/product-worked-sheets.md). |
| ETF or LOF foundations and full product practice | Read [M16 ETF](references/modules/module-16.md) or [M17 LOF](references/modules/module-17.md). Read [product atlas](references/product-atlas.md). Then read [product practice](references/product-practice.md). |
| Convertible bonds, conversion or redemption deadlines | Read [M18](references/modules/module-18.md) and [source applicability](references/product-sources-cb-other.md). Then read only the CB practice packet for this step. |
| Closed-end funds, exchange money funds or REITs | Read [M19](references/modules/module-19.md) and the applicable sources. Then read the selected CLOSED, MONEY or REIT practice track. |
| Plans for more than one product, execution, event cash flow and review | Read [M20](references/modules/module-20.md) and [six tracks for assisted practice](references/product-practice.md). Each track has four steps with gates. |
| Pause, review or continuation | Read progress and the necessary lesson. Only at a checkpoint that helps, record the record. |

Before a learner decision without aid, do not read teacher guides, the full replay source, future snapshots or worked answers. If the learner wants hints, give them. Unless the learner wants hints or you make a clear change to guided practice, do not give hints. Before feedback, keep raw responses.

## Keep the meaning of financial data and rules

- Identify Qinghe Manufacturing / 青禾制造 and learner Lin / 小林 as teaching assumptions. Identify synthetic prices, fees and share increments as teaching assumptions. Do not give them as a ticker, history, broker charge or exchange requirement from market observations.

- Record each financial rule with its venue, board, product, date, effective status and exceptions. Keep rules from history, rules applicable at this time and deferred provisions in different categories. If verification is not available, identify the field without verification. Continue with a synthetic assumption that has a clear label.

- Keep risk willingness, loss capacity, planned exit loss and realized loss in different categories. A loss cap or fill is not a necessary result of a stop level or position-sizing calculation.

- Keep observation time, publication time, signal confirmation, order submission and fill in different categories. OHLC does not show the sequence of highs and lows in a bar. If the stop/target path is not clear, record it as unknown.

- Use [case tools](scripts/case_tools.py) for synthetic arithmetic and cutoff filtering with the same results for the same inputs. These tools use teaching assumptions. They do not simulate A-share execution or brokerage eligibility. A Python installation is not necessary for the learner to read the course documents.

- For Chan analysis, read the specified convention in M11/M12. Keep chart interval, analytical level, provisional structure and confirmed structure in different categories. Three bars or strokes with overlap can be without the necessary recursive construction. Without the necessary recursive construction, do not identify this overlap as a center.

- Candles or vendor fund-flow fields do not give sufficient information for a conclusion about a participant's intention. If the evidence does not tell you which explanation is correct, keep the different explanations.

- Record process and PnL in different fields. A profit streak, small sample, diagram or satisfactory script check does not give sufficient information for a conclusion about competence or strategy efficacy.

- Keep wrapper, management objective, underlying exposure, share class, venue and operation in different categories. ETFs include index structures and structures with active management. ETF feeders are different holdings. Money ETFs are part of the ETF and cash-management teaching tracks. Keep infrastructure REITs and commercial real-estate REITs in different categories.

- Before a product operation that simulates market conditions, complete the instrument/date/operation rule card in the worksheets. Unknown eligibility, increments, tick, order/cancellation, limits/halts, resale, settlement or charge fields prevent a statement that this operation can occur. You can continue synthetic practice with assumptions that have clear labels.

- For NAV/IOPV, FX, holdings, conversion price and underlying quotes, give each input's valuation date, availability time, currency and source. Arithmetic does not give sufficient information to make sure that these inputs were available at this time. A NAV with a previous valuation date is not arbitrage evidence for the same time. Bond face value is not a minimum value for the market purchase price of the investor.

- Product practice is assisted practice. Read only the packet for the learner track, attempt and step at this time. Before the applicable step, do not read the generator, full source histories, teacher manifests, other steps or outcome files. Before the related feedback, keep the raw response without changes. Record related underlying/index exposure as information. Do not change assisted practice into assessment without aid.

## Scope and records

This skill gives instruction, analysis and simulation. It gives no authorization for broker access, orders to a broker, account changes, publication or installation. Unless the learner wants progression to money in a broker account, do not give information about this progression. This progression is not necessary to complete the course.

Keep learning state in a different location from the installed skill. Use the template for [learning record](assets/learning-record.json) in the learner's permitted workspace. Or give a checkpoint in chat.

Histories in the package are local snapshots for lessons that the authors selected after the events. They are different from Qinghe synthetic cases. Before this raw response, do not read full teacher histories, atlas manifests, generation sources or subsequent outcome pages.

Public access to a source is not a redistribution license. Until a different rights review is completed, keep this candidate and its data local. For more histories, record source, symbol, market, timezone, interval, adjustment basis and observation cutoff. Record the conditions that are applicable when you use the data. If only synthetic data is available, do not give a case as history without observations.

## Primary case selection from history

For stock lessons, first use 2026 technology cases or cases with high volatility. The cutoff is the completed 2026-10-19 session. The cutoff includes this date. The previous Moutai/Ping An examples give more information. They are not the primary examples as the default.

Keep the known corporate-action boundaries. Cambricon history for 2026, without price adjustment, includes a bonus/cash action with a May 8 date. Zhongji history includes an October 12 cash action. Do not identify an automatic raw-price adjustment as a crash from trading or a structural break. Company reports with publication times after a case cutoff are not knowledge available before this cutoff.

- For lessons about ETFs, LOFs, convertible bonds and other listed funds, select the applicable product from [product atlas](references/product-atlas.md). Use the price units, volume units and operation rules of this product. A stock chart does not give sufficient information for a conclusion about a fund NAV, a conversion price or a trading path for this product.

For lessons with figures, show the selected decision PNG in the reply. Use a local image path in Markdown. Use an absolute path for this image. You can also give an HTML link for zoom and tables. If a bitmap is not available, show its SVG or open the HTML that contains all necessary data. For teaching with figures, do not give only text and a link.

Before this raw response, unless the learner selects guided worked-example mode, do not show teacher overlays.

After this raw response without changes, use the related [topic plate](references/topic-plates.md) to show the selected 2026 concept with larger dimensions. A plate is a teacher document. Before the learner gives an answer, do not read its answers or an outcome from a different topic. Do not change the raw chart. Give information about one relation that the markings show. Before you add a different layer, wait.
