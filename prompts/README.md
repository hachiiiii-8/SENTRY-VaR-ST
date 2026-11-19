# Main-experiment prompt materials

The four text files provide complete, reviewer-editable drafts for the FNSPID semantic stage:

- `atomic_decomposition.txt`: decomposition of masked news titles into independent event mentions.
- `semantic_reading_1.txt`, `semantic_reading_2.txt`, and `semantic_reading_3.txt`: three event-category readings with the same ten classes and distinct instruction wording and category order.

Each file specifies system and user messages, the input slot, and the completion format. The current prompt protocol summary is in `current_prompt_specification.md`.

**Author verification:** The files are reconstructed from the manuscript protocol and proposed for review. Their final wording, prompt ordering, input masking, output grammar, and category definitions should be checked against the prompts actually used to produce the paper's cached posteriors.
