# Griductive Solver Report (Typst)

`main.typ` is the report entry point. The report is split into small files under
`sections/` so each chapter can be edited independently:

| File | Content |
|---|---|
| `01_introduction.typ` | Background, objectives and scope |
| `02_problem_formulation.typ` | Variables, clues, KB and reveal protocol |
| `03_architecture.typ` | Module architecture and data isolation |
| `04_algorithms.typ` | CNF, DPLL, entailment and deduction loop |
| `05_gui_and_gameplay.typ` | GUI, controls and gameplay feedback |
| `06_experiments.typ` | Benchmark table, observations and limitations |
| `07_evaluation.typ` | Requirement checklist and team contribution |
| `08_appendix_ai.typ` | AI disclosure and hand-off structure |

## Compile

Install Typst, then run from the repository root:

```powershell
typst compile typst/main.typ typst/Report.pdf
```

Before submission, update the instructor/class fields if necessary, replace all
`CẬP NHẬT` contribution placeholders with the team's agreed percentages, add the
Google Drive demo link, and verify the rendered PDF visually.
