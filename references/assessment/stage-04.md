# Stage 04 tutor guide

1. B has a higher high and a higher low than A and C at this cutoff. B is a candidate top with the specified convention for local fractals. C is not completed. Thus, its last relation is unknown. If C completes with these values, the three-bar pattern after containment agrees with this convention. This without other data does not show a stroke endpoint, trend reversal, or trade.
2. Get the end times of the initial bars, containment convention, signal confirmation, order submission, fill records, and subsequent revisions. Position time and information-availability time are different times for different events.
3. The intersection is [max(20,22,21), min(25,26,24)] = [22,24]. These premises are necessary:
- Subordinate trend types that are completed and occur one after the other
- The same target level.
The interval arithmetic without other data does not show these premises.
4. Three bars give at most their specified interval relation. For a recursive center result, data for the specified level and type are necessary. Do not accept an equivalence without indications that show it is correct between daily interval and analytical level.
5. MACD is a proxy. A structural context that agrees with the specified comparison conditions is necessary. For third-class points, find these items:
   - The center and related level
   - The departure and subsequent return as completed subordinate structures as applicable
   - The boundary relation and confirmation.
Give an explanation of the sell conditions in the opposite direction. Do not use one three-stroke method as sufficient for all contexts.
6. First, compare the clear definitions and the input and cutoff. A different software configuration without other data does not show that the theory is incorrect. Keep segments without confirmation, source differences, and alternatives for which the result is not known.

If the packet does not show that only one segmentation is correct, do not make this segmentation mandatory. Items 7–10 give conventions and data applicable only to these items. Give an assessment of these operations. Do not give an assessment of a software implementation for which the packet gives no data. Keep this guide in a different document from the learner packet. After a hint, record the answer as a response with tutor aid, not as a response without tutor aid.

## 7. Directional containment and the specified stroke

The first pair A1, A2 has no containment and sets downward processing. A3 is in A2. Thus, use the lower low and lower high:

```text
A2 + A3 → [min(70,70.5), min(73,72.5)] = [70,72.5]
```

A4 has a higher low and a higher high than this result. It stays as a different group and sets upward processing. A5, A6 and A7 also stay as different groups. A8 is in A7. Thus, use upward processing:

```text
A7 + A8 → [max(75,75.5), max(78,77.5)] = [75.5,78]
```

A9 has a lower low and a lower high than this result. Thus, keep it as a different interval. The full sequence after containment is:

| Group after containment | Raw sources | Interval |
| --- | --- | --- |
| P1 | A1 | [72,75] |
| P2 | A2, A3 | [70,72.5] |
| P3 | A4 | [70.8,73.2] |
| P4 | A5 | [71.5,74] |
| P5 | A6 | [73,76] |
| P6 | A7, A8 | [75.5,78] |
| P7 | A9 | [74.5,77] |

P1–P3 are a bottom at P2. Its low 70 is less than 72 and 70.8. Its high 72.5 is less than 75 and 73.2. P5–P7 are a top at P6. Its low 75.5 is more than 73 and 74.5. Its high 78 is more than 76 and 77.

No group in the first triple is in the second triple. P4 is between these triples. It is not in the first triple or the second triple. The endpoint prices also include the related extremes. Thus, the specified upward stroke at 70→78 agrees with the M11 strict convention at this cutoff.

The low is from raw A2 and the high is from raw A7. The supplied data do not give their intrabar times. The bottom has its necessary right group at a4. The top has its necessary right group at a9. Thus, a9 is the first possible cutoff from the supplied data for this stroke decision.

The right group is not available at a7 or a8. This qualification is applicable only at this cutoff. Do not write that a trade occurred or that the last endpoint is permanently set.

## 8. Containment used independently for a different example and a stroke that does not agree with the conditions

Use the same operations with the new data. B1→B2 sets downward processing. B3 is in B2:

```text
B2 + B3 → [min(89,89.4), min(92,91.5)] = [89,91.5]
```

B4 has no containment with the other bar and increases the two bounds. Use the procedure for the direction of higher prices at B6+B7:

```text
B6 + B7 → [max(94,94.6), max(97,96.4)] = [94.6,97]
```

The six groups after containment are [91,94], [89,91.5], [90,93], [92,95], [94.6,97], [93,96]. Their sources are B1, B2+B3, B4, B5, B6+B7, and B8.

Groups 1–3 are a bottom at 89. The two bounds of group 2 are less than those of the adjacent groups. Groups 4–6 are a top at 97. The two bounds of group 5 are more than those of the adjacent groups. No group in the first triple is in the second triple. There are zero groups between them that are not in the first triple and are not in the second triple.

Thus, the specified strict stroke at 89→97 does not agree with the M11 spacing condition. Eight raw bars do not make this stroke agree with the spacing condition. At b8, there are the two local patterns with the cutoff convention. But no confirmation time for this specified strict stroke is known. With new data and a new decision record, accept a subsequent extension only.

Tell the learner to do the two merges. Tell the learner to find the condition that did not agree with the requirements. A correct yes/no response without the interval calculations does not sufficiently show that the learner can use this method for a different example.

## 9. Feature-sequence gap branches

This packet supplies strokes with qualification, not raw bars. With only these endpoints, do not make raw lower-level proof necessary. The ranges of the first three strokes are [120,127], [123,127], [123,135]. Their intersection is [123,127]. This agrees with the supplied starting-overlap check.

For the upward candidate segment, select downward strokes 2, 4 and 6:

```text
E1 = [123,127]
E2 = [130,135]
E3 = [129,133]
```

For these elements, no containment merge is necessary. E1→E2 increases the two bounds. E2→E3 decreases the two bounds. The middle element is a top because 130 is more than 123 and 129, and 135 is more than 127 and 133. E1∩E2 is empty: max(123,130)=130 is more than min(127,135)=127. The open gap is (127,130).

At h13, stroke 6 has confirmation and there is the first feature top. Use the M11 gap branch. The candidate price is 135 at p3, with observation time h6. But the upward segment has no completion confirmation at this time. Only the first feature element in the feature sequence in the opposite direction is available. If the price decreases to 129, this price is not a replacement for the second feature fractal.

### Branch A

From p3=135, the reverse sequence starts with downward stroke 4. Its feature elements are upward strokes 5, 7 and 9:

| Element | Stroke and endpoints | Range | First possible confirmation of each stroke |
| --- | --- | --- | --- |
| R1 | stroke 5: 130→133 | [130,133] | h11 |
| R2 | stroke 7: 129→132 | [129,132] | h15 |
| R3 | stroke 9: 130→132.5 | [130,132.5] | h19 |

Each adjacent pair has the two bounds in the same direction. Thus, there is no containment. R2 is a bottom: 129<130 on the two sides, 132<133 and 132<132.5. The first three-stroke overlap of the sequence in the opposite direction, from strokes 4–6, is [130,133]. The completed R3 supplies the missing second feature fractal with the M11 convention.

At h17, strokes thru 8 have confirmation. But the reverse feature sequence has only R1 and R2. At h18, you can see p9=132.5, but stroke 9 has no confirmation at this time. R3 stays without confirmation.

At h19, all three elements agree with the conditions. Thus, the initial upward segment has its end at price 135. Its position time is h6, and its first possible time for confirmation is h19. The subsequent price 132.5 is confirmation data. It is not the initial segment endpoint.

Calculate the sequence in the opposite direction on its side of the candidate boundary. If the learner also extends the previous downward-element list, its stroke-8 interval [130,132] is in E3=[129,133]. This does not replace the necessary calculation for the reverse sequence R1–R3. For the second fractal, no more gap classification or closure of (127,130) is necessary. These branches use the definitions in [lesson 67](https://blog.sina.com.cn/s/blog_486e105c01000c16.html), with the M11 conditions.

### Branch B

The new stroke 7 extends from 129 to 136 in the upward direction. Its reverse feature interval [129,136] contains R1=[130,133]. There are only two feature elements from the raw reverse sequence. This new feature sequence has no previous pair without containment. Thus, its initial containment direction is unknown.

Keep this calculation without a decision result. Do not use subsequent data to give a direction at this cutoff. There is no bottom fractal with confirmation in the opposite direction.

The price 136 is more than the candidate high 135. It shows at h14. The supplied stroke-7 confirmation is available at h15. Before or at the specified h15 cutoff, cancel the segment-end candidate at 135. Then, continue the tests of the initial upward segment.

Do not keep a completed segment at 135. Do not write that 136 is a new end with confirmation. This branch has sufficient data for withdrawal. But it does not have data for a new segment end.

## 10. B0-to-L1 completion transfer with C12-F

Tell the learner to give the name **C12-F**, the finite classroom partition from M12-U02-P01. C12-F gives qualification to an L1 teaching block with one center for L2 exercises with the same convention. This qualification does not show Chan trend-type completion from the source theory or only one possible decomposition. It also does not show a larger trend reversal, a buy/sell classification, or profitability. Three B0 inputs that make a center do not complete an L1 block without other conditions.

The raw B0 ranges are [160,171], [165,171], [165,173], [166,173], [166,170], [158,170], [158,163], [157,163]. The previous core from H1–H3 is:

```text
Z = [max(160,165,165), min(171,171,173)] = [165,171]
```

For completeness, the rolling three-B0 intersections available for the first time at this cutoff are:

| Window | Calculation | Intersection |
| --- | --- | --- |
| H2–H4 | [max(165,165,166), min(171,173,173)] | [166,171] |
| H3–H5 | [max(165,166,166), min(173,173,170)] | [166,170] |
| H4–H6 | [max(166,166,158), min(173,170,170)] | [166,170] |
| H5–H7 | Minimum 166 is more than maximum 163 | Empty |
| H6–H8 | [max(158,158,157), min(170,163,163)] | [158,163] |

Only windows fully in the candidate initial block are its internal-center checks. H4–H6 and H5–H7 extend across the candidate boundary. These windows do not let you count H6 and H7 two times or change the initial Z.

The internal rolling intersections are H2–H4 and H3–H5. Each of these intersections has a width more than zero. Their intersections with Z are not empty. With this classroom partition, these intersections do not give different centers without overlap.

The candidate boundary is the end of H5 at 170. H6 has confirmation and a departure in the direction of lower prices to 158<165. H7 has confirmation and a return only to 163<165. H8 makes a subsequent low 157<158. The witness intersection [158,163] has width 5. All its prices are less than the initial core, with a gap (163,165).

| Cutoff | Available B0 with confirmation | Qualification specified for this exercise |
| --- | --- | --- |
| u7 | H1–H3 | There is core [165,171]. The L1 block has no C12-F completion confirmation. |
| u11 | H1–H5 | The extension with the same initial core is permitted. The boundary at 170 is a candidate. |
| u15 | H1–H7 | Departure and return agree with their inequalities. The third witness with confirmation is missing. |
| u16 | H1–H7, plus the end of H8 shown at this cutoff without confirmation | The block stays without C12-F completion confirmation. Observation of 157 does not give H8 confirmation. |
| u17 | H1–H8 | The data agree with all C12-F conditions. Record completion of the initial block at the previous H5 boundary. |

The possible cut after H3 does not agree with the conditions. The next downward H4 has the value 166, which is in [165,171] and is not less than ZD. This gives no indication that the first center is completed at this cutoff.

The necessary record of the sealed block is:

| Field | Specified value |
| --- | --- |
| Convention and status | C12-F qualification: L1 teaching block for consolidation in the sealed state |
| Members | H1–H5 |
| Time boundary | u0–u10 |
| Endpoint prices | 160→170 |
| Initial core | [165,171] |
| Full range | [160,173], with the high 173 from an observation in the block |
| Witnesses | H6–H8, not in the previous block |
| First possible availability for L2 with C12-F | u17 |

The full range has width 13. If you use only endpoints, the range [160,170] incorrectly does not include the high in the block. The witness time is u17, not u10. The same endpoint at u10 does not make H6 a member of the two blocks.

H6–H8 have a core with overlap but do not have closing witnesses for these blocks. Do not accept them as a second L1 block that is completed. This packet has only one sealed block. Thus, it cannot supply three L1 inputs with qualification and no other L1 input between them or show an L2 center.

### Example without completion and alternative decomposition

With H7=158→165 and H8=165→157, the witness ranges become [158,170], [158,165], [157,165]. Their intersection is [158,165], which has the same boundary 165 as Z. The return high is equal to ZD. With C12-F, the return high must be less than ZD, and equality is not permitted. Thus, the candidate C12-F completion does not agree with the conditions at u17, although all eight B0 have confirmation.

Record this candidate as without C12-F completion confirmation. Examine continuation or regrouping. Do not use an inclusive boundary convention as a replacement.

Accept a clear alternative interpretation with these conditions:
- H1–H8 stay in a longer observation without a completion decision
- The interpretation uses a different specified partition. This packet has only the supplied observations. For this alternative, do not make only one trend type from the source theory necessary.

For the branch that agrees with the conditions, the specified result stays C12-F completion at u17 with this qualification. A learner who gives the scope of the convention correctly but does not give its correct arithmetic does not complete the transfer task.

Give different assessments for interval operations, pattern conditions, membership, and timing. Correct arithmetic without other data does not show mastery of all decompositions from the source Chan theory.

This teacher key shows if the specified examples are correct or not. It does not show teaching effectiveness or trading performance.
