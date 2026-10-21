# Learning records and continuation

At the end of a lesson segment that gives necessary understanding, make a copy of the template for [record](../assets/learning-record.json). At a pause, make this copy. Put the copy in the learner's permitted workspace. Keep the raw response and specified next part. If no workspace is available, give the same short record in chat. Do not change the installed skill for state storage.

Record the unit, part, exercise identifier, support level, response observations, feedback and next task. Answers without aid, answers with hints, solutions from a copy and course content without a test are different states. A completed page or a tutor's answer is not evidence of mastery. Do not put an expected answer into a response field.

## Exposure and assessment attempts

Use `exposure_history` with `status` (`complete` or `unknown`) and an append-only `events` list. Each event records `event_id`, `case_id`, `instrument`, `start`, `end`, and `kind` (`observed` or `revealed`). Use instrument codes with an exchange prefix. Do not use company names or exercise IDs. Date ranges include the first and last dates.

Record the first and last dates of bars that the learner can see. Include subsequent bars that you read for feedback. Keep different intervals and source events. `scripts/exposure_tools.py` calculates their union and does checks for overlaps in records with different IDs. Reject dates with an incorrect form and instrument codes that are not clear.

For `complete`, a check of all known previous observations with a record is necessary. Include source browsing, worked examples, future prices from feedback and previous attempts. An empty history from an imported record is not evidence of completeness. If the record is missing or has missing parts, keep `unknown`. Do not give a completeness status from a new session, new exercise ID or completed demonstration.

If external exposure occurs during an attempt, before the next answer or feedback, add it. If you cannot find its range, set history status to `unknown`.

Use `holdout_runs` for [the different reserve for replay in sequence](holdout-replay.md). Each run records `run_id`, `case_id`, `support`, `opened_steps`, `answered_steps`, `revealed_steps`, and `own_exposure_ids`. Keep raw responses in the `responses` list with `run_id` and the packet ID without changes. The runtime adds events for the prefix for this step and the related suffix from feedback.

For support, the runtime uses these ranks: `independent` = 0, `unknown` = 1, `assisted` = 2 and `hinted` = 3.

Exposure to the specified previous prefixes in this same run does not increase the support rank of its specified continuation. This exception uses only event IDs in `own_exposure_ids` for this run. It does not use a whitelist for case IDs or instruments. The exposure check also includes previous runs, different cases and other exposure. During an attempt, do not decrease the support rank.

The record template uses schema 1.1 and the skill version for this copy. For a schema 1.0 record, keep its cursor, raw responses and simulation records. Only if `exposure_history` is missing, add it as `{"status":"unknown","events":[]}`. Only if `holdout_runs` is missing, add it as an empty list. Do not replace a ledger that the record includes.

In previous response entries, if `run_id` is missing, add it as null. Until a migration with a record gives the source and target versions, keep the previous `skill_version` as provenance. Do not give previous answers without aid a label of new validation. Do not erase their previous support evidence.

For an `independent` response, a full history and no previous interval with overlap for the reserved case are necessary. Known overlap is `assisted`. History with missing parts is `unknown`. A hint that the learner wants makes the remaining attempt `hinted`. Before feedback, record the words without changes.

A second run keeps the first run and all its exposures. Thus, a different attempt at the reserve cannot give independent credit again. These states record support. They do not record mastery or strategy quality. During selection, replay and concept lookup, do not change `course_cursor`.

For a new session, first compare the cursor with [catalog](../assets/course-catalog.json). Read only the applicable module and record entries that the learner wants. If the record does not give evidence for the prerequisite, give a short retrieval check. Then adapt. A missing record stays unknown. It does not make a mandatory start of the full course again.

A concept lookup is a temporary branch. Unless the learner selects a different route, do not change course_cursor. When you give a lesson again, keep raw response evidence. Keep the previous result together with the new result. Without a clear statement, do not replace the previous result.

For simulation records, keep decision time, information cutoff, order submission, fill, fees, outcome and process deviation in different fields. An order without execution or an order opportunity without execution stays part of the record. Without fill evidence, do not change a plan for an operation into a trade with execution.

## Product tracks and schema 1.2

From version 0.3.0, the record template uses schema 1.2. Keep the cursor, route, raw responses, simulation records, exposure ledger and holdout attempts that the record includes. If `product_runs` or `related_exposures` is missing, add the missing field as an empty list. Do not replace lists that the record includes.

Before an upgrade with a record, keep the previous skill version in migration provenance. Read the target version from SKILL.md metadata in this copy. The 1.1 instructions in the previous section stay the migration step for this previous schema. They do not give the template schema for this version.

Use `product_runs` with the product-practice runtime. A run records the track, run identifier, step for this time, opened steps, answered steps, revealed steps and support with aid. Before feedback, record the raw response with this run and step, without changes. A different run cannot supply the missing response.

Hints or previous teaching do not give independent credit. These tracks are assisted practice. Completion of step four is not sufficient information for a conclusion about product mastery or profitability.

Use `related_exposures` for known underlying stock, benchmark/index or product observations with overlap. Record instrument or benchmark identifier, date range of observations, observation/publication time, source, relation and uncertainty. An index and an ETF are not the same instruments. Record their relation. Without a clear statement, do not put their identifiers together as one.

These records give exposure information. They are not an engine with validation for unseen eligibility for more than one asset. Keep missing history unknown.

During product lookup and track practice, do not change `course_cursor`. A learner can select `product_first`, `etf_practice`, `lof_practice`, `convertible_practice` or `listed_funds_practice` with a clear statement. Before M20, examine responses about foundations for the products and the selected product. Module membership is not evidence of understanding. Chan is optional for these routes. Record learner state in a different location from the skill.
