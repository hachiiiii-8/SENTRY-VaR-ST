# Remaining main-experiment reproducibility items

Only materials required to reproduce the headline FNSPID experiment and its temporal diagnostics are in scope.

## Required before public release

- [ ] complete 986-date daily breach series for all twelve headline models and three confidence levels;
- [ ] complete 986-date daily mean pinball-loss series for the same model-level combinations;
- [ ] one script that regenerates the headline pooled rates, DM-HAC results, Table 18, Table 19, and the COVID-window extraction;
- [ ] exact verbatim atomic-decomposition prompt used by the main experiment;
- [ ] exact verbatim three semantic-reading prompts used by the main experiment, including taxonomy definitions, category orders, and output format;
- [ ] confirmation of the bootstrap seed and exact DQ regression specification;
- [ ] a clean-environment validation run;
- [ ] repository access changed to public after the release files are checked for restricted or identifying content.

## Already available

- [x] 986-date eligible forecast-origin index;
- [x] COVID-window daily 95% breach table;
- [x] COVID-window realized-loss summary;
- [x] manuscript-facing DM-HAC, Table 18, and Table 19 summaries;
- [x] final main-experiment semantic transport-cost matrix;
- [x] evaluation helpers and automated consistency checks.

## Explicitly out of scope

- ablation experiments;
- sensitivity analyses over horizons, windows, or targets;
- semantic-backbone controls;
- Astock external-market results;
- mechanism-only tables and case studies;
- model checkpoints, training logs, and complete training code;
- copyrighted news text, original market data, or identifiable company-day records;
- per-origin predictions and thresholds;
- intermediate ontology, embedding, and confusion matrices when the final matrix used by the main experiment is already released.
