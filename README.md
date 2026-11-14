# circular-mfg-edu-review

# REED state-of-the-art review: search, screening and PRISMA figures

Supporting material for *State of the Art: Low-Cost Circular Remanufacturing Platforms
and Energy Monitoring in Engineering Education* (NAMRC 55, Manufacturing Letters, 2027).

## Contents
- `NAMRC55-Queries-CircularMfg.txt` – full Web of Science Core Collection query strings for all eight queries,
  and the search history export (searches rerun on November 11, 2026)
- `PRISMA-Query_filtration_diagram.py` – PRISMA 2020 flow diagram (Fig. 1 in the paper)
- `Sankey_diagram-PRISMA-Query.py` – Pass-by-pass Sankey version of the same flow

## Reproducing the figures
Open Google Colab, paste the whole contents of `prisma_classic_colab.py` into one code
cell, and run it. The Sankey notebook can be opened directly in Colab and run top to
bottom. All counts are defined at the top of each file; the scripts stop with an error
if any stage of the flow does not balance.
