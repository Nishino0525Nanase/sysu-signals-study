# Lecture reading design QA

final result: passed

## Visual truth and evidence

- Selected visual: second displayed concept, `/workspace/scratch/13209b04cbad/generated_images/exec-1482f4fb-8b3c-4e60-b957-a7ea7d32e2da.png` (1487 × 1058 pixels; generated design, no CSS viewport metadata).
- Final browser capture: `docs/lecture-reader-v1.12.jpg` (captured as `/workspace/shared/signals-lecture-final.jpg`) (1363 × 936 pixels, CSS viewport 1363 × 936, 1× density).
- State: light appearance, normal type, 2026 fourth problem, original scan collapsed, complete derivation visible, time-scaling context selected.
- The source and final capture were opened together in one comparison input. Responsive desktop composition was compared proportionally; no claim of pixel-identical reconstruction is made across the different viewport widths.
- Focused checks: actual 17px manuscript paragraphs, 20px large mode, 18px contextual display formulas, original scan availability, triangle support and peak labels, side-column overflow and active-outline placement. These were inspected in the full capture and measured in the rendered DOM; the relevant details were legible without a separate crop.
- The local preview route was unavailable because the environment rejected its network escalation. Verification used the authorized GitHub Pages publication in the cloud browser, rather than claiming a local preview passed.

## Comparison history

1. Initial lecture view retained overly long outline labels and 14px context math (P2). Shortened outline labels, used 18px display math, and split long formulas into equivalent lines.
2. Closing a formula dialog required explicit reading-position restoration. Added stored window position and suppressed progress capture while overlays are open. Actual coordinate-click verification kept the second heading at 95.390625px before and after the overlay.
3. Nested scrolling in the sticky formula column produced incomplete rendering in browser captures (P2). Removed its separate overflow surface on desktop. The final capture shows the complete formula column; computed formula overflow is 0px and page overflow is false.
4. Original scan position restoration now opens the saved disclosure before measuring its anchor. The original stayed expanded and returned to 89.890625px after moving to another problem and back.

## Required fidelity surfaces

- Typography: local system Chinese sans-serif and bundled KaTeX; dark readable body, distinct section headings, restrained smaller metadata. No remote font dependency. Long equations scroll only when their content requires it; short context formulas are split into readable rows.
- Spacing/layout: white horizontal navigation; narrow original/outline column, continuous manuscript, contextual formula column; thin rules instead of nested cards. Persistent bottom tools and responsive mobile step navigation remain available.
- Colors: white surface, dark ink, muted forest green, pale green route explanation, amber check reminder. Dark appearance was exercised without page overflow.
- Images: authentic university crest and original scans retained; new time-scaling plot is a precise matplotlib diagram with Chinese annotations, peak 8 and support [-1/2,1/2]. No generated mathematical assets or fabricated textbook citations were used.
- Copy/content: every existing full solution and original-page mapping retained. The mock's incorrect textbook citation was not copied. Original source and auxiliary paraphrase remain explicitly distinguished.

## Browser interactions

- Step anchors and active directory; original disclosure with both pages of 2026-04.
- Formula drawer opening, closing, reference-card navigation and return position.
- Next problem and previous problem restored the first derivation heading at 95.390625px.
- Original-page continuation restored disclosure and position.
- Large type changed body to 20px; dark mode kept horizontal overflow false.
- Mobile iframe CSS viewport 390 × 844 (375px content width after scrollbar): fixed formula button, step navigation and no horizontal page overflow; 0 KaTeX errors. The second step stayed at 75.953125px before and after the fixed lookup button opened and closed its drawer.
- Browser console checked. Observed errors were browser-extension metadata messages, not errors from the study application.
- Temporary review pages removed from production source and APK.

## Validation and limits

- Content validation: 243 exam groups, 32 drills, 40 textbook groups, 346 original crops, 628 book pages, 175 clear-table rows; 14,464 existing mathematical expressions, 0 errors.
- Contextual notes: 19 notes cover all 315 solution-bearing entries; 62 math fragments render successfully in bundled KaTeX.
- APK v1.12.0, versionCode 14: ZIP CRC passed; 10 core web assets match the final web files byte for byte; original signing certificate preserved.
- Android physical-device interaction was not exercised. Mobile iframe screenshots timed out in the browser backend, so mobile verification relies on rendered DOM and completed interactions, not a claimed mobile screenshot.

## Implementation checklist

- [x] Continuous nonmodal reading page and contextual formula lookup.
- [x] Original question access, full answers, alternate methods, source pages and notes retained.
- [x] Reading position, deep link and Android return handling updated.
- [x] Desktop visual and mobile interaction checks completed.
- [x] Cache fingerprints and offline fallback preserve consistent version loading.
- [x] No remaining actionable P0/P1/P2 findings.

## Follow-up polish

- Physical tablet/phone validation may refine local font metrics and touch spacing.
- Some original scans remain limited by the uploaded source resolution; their pixels are preserved and independently zoomable.
