# Title/abstract screening criteria — <topic>

Clinical question: <one sentence PICO question>

## Decision for each record
- `FT` = retrieve full text (P, I, O and design are all plausible from title/abstract; when unsure about one of
  them, prefer FT and add a note saying what to check).
- otherwise one exclusion code:
  - `P` population: <who is out — e.g. mainly type 2 diabetes; children; animals; other diseases>
  - `I` intervention: <what is not the intervention — e.g. other drugs; non-conversational AI>
  - `O` outcome: <no relevant outcome — e.g. weight only; usability only>
  - `D` design: not an RCT or SR/MA of RCTs — narrative review, editorial/letter/news, observational,
    modelling/cost-effectiveness, protocol or design/baseline paper, trial registry record, conference abstract,
    preprint, umbrella review, guideline, case report, animal/in vitro <adjust to the protocol>
  - `L` language other than <English or Chinese>

## Special rules
- <Index trial main report → FT>
- <Secondary analyses of the index trial that report the outcome → FT with "note": "<trial> secondary";
  those that do not → O>
- <Systematic reviews that mix eligible and ineligible populations without separable results → P>
- Conference abstracts → D even if relevant (add a note if it relates to an index trial).
- Chinese records (Airiti) are mostly reviews, theses, newsletters or quasi-experiments → D unless clearly an RCT
  or SR meeting the criteria; off-topic full-text matches → P or I.

## Output
Write a JSON array to the output path, one object per input record, in input order:
`{"uid": "...", "decision": "FT|P|I|O|D|L", "reason": "<= 15 words, English", "note": "optional"}`
Every input uid must appear exactly once.
