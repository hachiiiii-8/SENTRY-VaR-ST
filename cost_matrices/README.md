# Semantic transport-cost matrix

[final_semantic_transport_cost.csv](final_semantic_transport_cost.csv) contains the 10 × 10 ground-cost matrix for the main FNSPID semantic transport model.

The row and column order matches the financial-event categories used in the semantic readings. Each entry represents the cost of moving probability mass from one event interpretation to another. The diagonal is zero, the values are non-negative, and the matrix is symmetric.

The financial-event geometry combines normalized event-ontology distances, event-description embedding distances, and symmetrized calibrated-confusion costs with equal weights. This final matrix is used to construct mention-level transport sets and reweight risk-channel probabilities during robust VaR inference.
