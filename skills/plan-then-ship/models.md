# Model roles and handoff

Use the current capable parent for planning and review. For implementation, choose a less costly model from the models the current harness actually exposes, honoring the user's explicit choice. Do not infer model availability, prices, or capability from an old name table. A missing preferred model is not a reason to abandon a reviewable spec.

If named-model delegation is available, state the selected roles and pass the implementer the complete spec, its absolute worktree path, branch, allowed files, tests, and explicit ownership. Tell it other agents may be working and to preserve their changes. Keep concurrent writers in separate worktrees. Reviewers are read-only and use scratch space.

If delegation is unavailable, explain that limitation and perform implementation followed by a separate review pass locally unless the user specifically requires a different-model handoff. Do not call sequential passes independent review. For a required handoff, finish the spec and provide the exact continuation prompt before yielding.

A cloud or standalone user-visible task is created only when the user asks for one. Tool availability alone is not permission to create new sidebar tasks or send work to another service.

For a defect that survives the repair budget, use one stronger investigation pass only if it fits the authorized budget and the spec remains coherent. Diagnose before rewriting. If the contract itself is wrong, present the concrete decision that must change.
