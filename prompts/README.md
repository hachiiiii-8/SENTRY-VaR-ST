# Financial-news semantic prompts

The semantic pipeline processes each news title in two steps.

## 1. Atomic event decomposition

[atomic_decomposition.txt](atomic_decomposition.txt) identifies independent risk-bearing propositions in a masked title. It preserves negation and numerical qualifiers, retains source order, and returns a structured list of mentions. Each mention is classified separately.

## 2. Repeated semantic readings

[semantic_reading_1.txt](semantic_reading_1.txt), [semantic_reading_2.txt](semantic_reading_2.txt), and [semantic_reading_3.txt](semantic_reading_3.txt) contain three readings with shared financial-event definitions and distinct instruction wording and category order.

All three readings use the same ten event categories: earnings/guidance, analyst rating, legal/regulatory, liquidity/financing, operations/supply chain, macro exposure, M&A/restructuring, management change, positive corporate event, and neutral/low-information news.

The backbone scores the **ten fixed category completions** conditional on each reading's context. The resulting scores are normalized to category probabilities and calibrated before the mention-level uncertainty and transport calculations.

Company names, ticker symbols, and exact dates are replaced by fixed placeholders in the input. The semantic templates are used with Qwen3-14B in non-thinking mode.
