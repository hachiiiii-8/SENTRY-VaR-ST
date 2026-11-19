# Main-experiment prompt protocol summary

## Atomic decomposition

- Input: one masked financial-news title.
- Extract the smallest independent risk-bearing propositions in source order.
- Preserve negation, numerical qualifiers, and company, ticker, and date placeholders.
- Use the complete title when a single proposition is present.

## Semantic reading

Three semantic readings use common event definitions and label completions, with varied instruction wording and category order. The instruction themes are:

1. Classify the risk-relevant meaning of a financial-news mention.
2. Select the defined financial event category that best describes a masked mention.
3. Select the closest risk-relevant event meaning for the input statement.

## Event categories

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
