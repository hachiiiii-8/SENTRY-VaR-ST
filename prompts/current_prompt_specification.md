# Current prompt specification

This file records the prompt information that is currently verified from the manuscript and the existing revision archive. It is not yet the verbatim prompt release.

## Atomic decomposition

- Input: one masked financial-news title.
- Return the smallest independent risk-bearing propositions in source order.
- Preserve negation, numerical qualifiers, and fixed company, ticker, and date placeholders.
- Do not add facts.
- Return the complete title when no independent split is warranted.

## Semantic reading instructions

The three readings share the same event definitions and output slot. They vary instruction wording and category order.

1. Classify the risk-relevant meaning of the following financial-news mention.
2. Which defined financial event category best describes this masked mention?
3. Select the closest risk-relevant event meaning for the statement below.

## Fixed label completions

1. Earnings or guidance
2. Analyst rating
3. Legal or regulatory
4. Liquidity or financing
5. Operation or supply chain
6. Macro exposure
7. M&A or restructuring
8. Management change
9. Positive corporate event
10. Neutral or low-information news

## Pending verbatim release

The exact system messages, full category definitions, category order for each reading, input wrapper, fixed output schema, parser constraints, and fallback text must still be exported from the authoritative experiment workspace.
