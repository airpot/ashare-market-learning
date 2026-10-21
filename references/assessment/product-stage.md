# Assessment procedure for product practice

Use this procedure only for the six product tracks with tutor aid. This procedure gives no status `independent` or indications sufficient to show investment efficacy.

## Packet sequence

The runtime keeps attempts in `product_runs` and keeps raw responses in `responses`. Each response has `run_id`, `track`, `step`, and `PRODUCT-<TRACK>-<step>`. It also has the learner's words without changes. Keep the course cursors, holdout attempts, and exposure history. Here, exposure history records access to learning material before this step.

After `answer` completes correctly for this run and step, use `reveal`. Before it reads a tutor packet, the runtime makes sure that these conditions are correct:
- The `raw_response` text is not empty.
- The `run_id`, `track`, `step`, and `exercise` values agree with this run and step.
- The number of responses with these values is one.
Then, the runtime reads only `references/assessment/product-practice/<TRACK>/<step>.json`. Do not preload the teacher directory. For this question, do not read a subsequent tutor packet.

## Feedback about the recorded answer

1. Find the result that the learner gives in the raw response and the indications supplied for this result.
2. Examine product identity, units, price denominator, dates, and information available at the cutoff.
3. Find missing mandatory fields for the procedure. If the learner stops the procedure with an explanation, record the missing item, blocked step, and method to get data.
4. Compare the trading plan with cash, loss from the plan, clear external fees, and increments in product units. A stop price does not give a guarantee of execution. Use the units specified in the packet.
5. Compare fills with order reports. Keep different records for these items:
- Fills for only part of the product units sent
- Orders with no fill
- Canceled orders
- Rejected orders.
6. Compare cash and units with the reports. For this step, use only the applicable part of [the product worksheets](../product-worked-sheets.md). The worksheets include settlement, assets that you cannot use, entitlement, conversion, and remaining receivables.
7. Give an explanation of one specified misconception. Tell the learner to give a small revision with text from the learner. Keep the first raw response. Do not replace it with a model response.

The tutor packet for this same step has the numbers, calculation steps, and a misconception prompt. This packet gives no permission to use these assumptions as market rules. Dates, fee conventions, and event rights stay as premises made for this example.

A correct calculation does not show permission, settlement eligibility, or a fill from execution in a market. It does not show knowledge for a new task with these conditions:
- No tutor aid
- No learner access before the task starts. It also does not show a trading method that gives the specified results.

## Indications and aid

Use `support` value `assisted` for each raw response and reveal, also for subsequent attempts. Related index and underlying-stock exposure gives information only. Here, exposure records access to material about related products before this step. This is not financial exposure.

For an empty exposure history, profit, or a four-step loop that is completed, do not give the learner status `independent`.

## Record boundary

Keep records in a directory that is not in the skill package or installed skills directories. Before each step, the CLI examines the record path. After a satisfactory operation result, the CLI puts the new record in the location of the external record. Use one writer for each record. With the in-memory API, the caller must record the data in a file before feedback.

The gate controls the local sequence. It gives no authentication, tamper resistance, or broker connection.
