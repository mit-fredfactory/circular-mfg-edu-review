# =====================================================================
# PRISMA 2020 flow diagram (Sankey) - REED state-of-the-art review, NAMRC 55
# Paste this whole block into ONE Google Colab code cell and run it.
# Outputs: prisma_flow.pdf (for LaTeX), prisma_flow.png, prisma_flow.html
# =====================================================================

# ---------------------------------------------------------------------
# 0. Setup (pinned versions so the figure renders identically everywhere)
# ---------------------------------------------------------------------
%pip install -q "plotly==5.24.1" "kaleido==0.2.1"

# Liberation Serif is metrically identical to Times New Roman (the paper's font).
# On Google Colab this installs it; elsewhere, skip it if the font is already present.
!apt-get -qq install -y fonts-liberation > /dev/null 2>&1 || echo "fonts-liberation not installed (non-Debian system?)"

# =====================================================================
# PRISMA 2020 flow of records as a horizontal Sankey diagram
# REED state-of-the-art review (NAMRC 55). Web of Science Core Collection,
# all queries run on 11 November 2026.
#
# Every number in the figure comes from the three lists below.
# Edit them, re-run, and the checks at the end of this block will stop
# with an error if any stage does not balance.
# =====================================================================

# ---- 1. Queries: records returned, and records left after the language
#         (English) and document-type filters (article, proceedings paper,
#         review, early access). "stream" is the screening group the query
#         belongs to; queries in the same stream were screened together.
QUERIES = [
    # key    label shown in the figure                     stream       returned  after filters
    ("Q1a", "P1 Q1a: PLA + EVA",            "P1_PLAEVA",   369,      365),
    ("Q1b", "P1 Q1b: EVA hot melts",       "P1_PLAEVA",   354,      332),
    ("Q2",  "P1 Q2: Hardware",             "P1_HW",       126,      124),
    ("Q3",  "P2: Energy",                  "P2",          130,      119),
    ("Q4",  "P2: Multiple cycles",         "P2",           18,       18),
    ("Q5",  "P3: Platforms",               "P3",           39,       39),
    ("Q6",  "P4: Industry 5.0",            "P4",          135,      129),
    ("Q7",  "P5: Education",               "P5",           40,       37),
]

# ---- 2. Screening streams.
#   assessed       : records kept after title/abstract screening AND obtained
#                    in full text (i.e. full texts read)
#   not_retrieved  : records kept after title/abstract screening whose full
#                    text could not be obtained
#   included       : studies cited in the paper and credited to this stream
#                    (each study is credited once, to the first query that
#                    retrieved it, in the order Q1a, Q1b, Q2, Pass 2 ... Pass 5)
STREAMS = [
    # key          label                         colour     assessed  not_retrieved  included
    ("P1_PLAEVA", "P1: PLA + EVA",             "#2E5E8C",   164,      1,             38),  # 21 (Q1a) + 17 (Q1b)
    ("P1_HW",     "P1: Hardware",              "#5B8DB8",    46,      2,             13),
    ("P2",        "P2: Energy",                "#4E8F5E",    34,      0,              7),  # 5 (Q3) + 2 (Q4)
    ("P3",        "P3: Platforms",             "#B9872F",    16,      0,              4),
    ("P4",        "P4: Industry 5.0",          "#7B5EA7",    16,      2,             11),
    ("P5",        "P5: Education",             "#2F8F9D",    10,      1,              3),
]

# ---- 3. Studies retrieved by more than one query. Each is credited to the
#         first query (column "credited_to") and ALSO appears among the full
#         texts read in a later stream ("also_in"), where it is shown leaving
#         through the "counted under an earlier query" branch.
DUPLICATES = [
    # study              credited_to   also_in
    ("Liu 2024",         "P1_PLAEVA",  "P1_HW"),
    ("Aly 2024",         "P1_PLAEVA",  "P1_HW"),
    ("Romani 2024",      "P1_PLAEVA",  "P2"),
    ("Goncalves 2020",   "P1_PLAEVA",  "P2"),
    ("Papa 2025",        "P1_PLAEVA",  "P2"),
    ("Kodra 2026",       "P1_HW",      "P3"),
    ("Sinchai 2024",     "P1_HW",      "P3"),
    ("Petsiuk 2021",     "P1_HW",      "P3"),
    ("Wilkins 2020",     "P1_HW",      "P5"),
]

EXPECTED_DISTINCT_STUDIES = 76      # studies cited in the paper from the searches
WOS_UNIQUE_RECORDS        = 1126    # WoS union of all filtered queries (search set #18)

# =====================================================================
# Derived counts and consistency checks
# =====================================================================
stream_keys = [s[0] for s in STREAMS]
S = {s[0]: dict(label=s[1], colour=s[2], assessed=s[3],
                not_retrieved=s[4], included=s[5]) for s in STREAMS}

for key, label, stream, returned, kept in QUERIES:
    assert stream in S, f"{key}: unknown stream {stream}"
    assert 0 <= kept <= returned, f"{key}: filters cannot add records"

for k in stream_keys:
    s = S[k]
    s["screened"]   = sum(q[4] for q in QUERIES if q[2] == k)
    s["sought"]     = s["assessed"] + s["not_retrieved"]
    s["excl_ta"]    = s["screened"] - s["sought"]
    s["dups_here"]  = sum(1 for d in DUPLICATES if d[2] == k)
    s["counted"]    = s["included"] + s["dups_here"]       # every study read here and cited
    s["excl_ft"]    = s["assessed"] - s["counted"]
    for f in ("excl_ta", "excl_ft"):
        assert s[f] >= 0, f"{k}: negative count for {f}"

for study, first, later in DUPLICATES:
    assert stream_keys.index(first) < stream_keys.index(later), \
        f"{study}: must be credited to the EARLIER stream"

T = dict(
    returned      = sum(q[3] for q in QUERIES),
    filtered_out  = sum(q[3] - q[4] for q in QUERIES),
    screened      = sum(S[k]["screened"] for k in stream_keys),
    excl_ta       = sum(S[k]["excl_ta"] for k in stream_keys),
    sought        = sum(S[k]["sought"] for k in stream_keys),
    not_retrieved = sum(S[k]["not_retrieved"] for k in stream_keys),
    assessed      = sum(S[k]["assessed"] for k in stream_keys),
    excl_ft       = sum(S[k]["excl_ft"] for k in stream_keys),
    counted       = sum(S[k]["counted"] for k in stream_keys),
    dups          = len(DUPLICATES),
    distinct      = sum(S[k]["included"] for k in stream_keys),
)
assert T["returned"] - T["filtered_out"] == T["screened"]
assert T["screened"] - T["excl_ta"] == T["sought"]
assert T["sought"] - T["not_retrieved"] == T["assessed"]
assert T["assessed"] - T["excl_ft"] == T["counted"]
assert T["counted"] - T["dups"] == T["distinct"]
assert T["distinct"] == EXPECTED_DISTINCT_STUDIES, \
    f"credited studies sum to {T['distinct']}, expected {EXPECTED_DISTINCT_STUDIES}"

print("All stages balance.\n")
print(f"{'Stream':24s}{'screened':>9s}{'excl T/A':>9s}{'sought':>8s}{'no FT':>7s}"
      f"{'read':>6s}{'excl FT':>8s}{'cited':>7s}{'dupl.':>6s}{'credited':>9s}")
for k in stream_keys:
    s = S[k]
    print(f"{s['label']:24s}{s['screened']:9d}{s['excl_ta']:9d}{s['sought']:8d}"
          f"{s['not_retrieved']:7d}{s['assessed']:6d}{s['excl_ft']:8d}"
          f"{s['counted']:7d}{s['dups_here']:6d}{s['included']:9d}")
print(f"\nTotals: {T}")
print(f"The {T['screened']} records screened across queries correspond to "
      f"{WOS_UNIQUE_RECORDS} unique WoS records; records retrieved by more than one "
      f"query were screened in each.")

# =====================================================================
# Figure: horizontal Sankey, sized for a full-width (figure*) float.
# At W = 1100 px a 16 px label prints at about 7.4 pt when the figure is
# scaled to the 7.1 in text width of the Elsevier 5p layout.
# =====================================================================
import plotly.graph_objects as go

FONT       = "Times New Roman, Liberation Serif, Times, serif"
FONT_PX    = 16
EXIT_RED   = "#A8433A"
FINAL_GREY = "#3A3A3A"
W, H       = 1100, 650
MARGIN     = dict(l=6, r=6, t=78, b=34)
PAD_PX     = 12                                  # minimum vertical gap between nodes
COLS_X     = [0.001, 0.20, 0.40, 0.60, 0.80, 0.999]
HEADERS    = ["Records<br>identified", "Records<br>screened", "Reports sought<br>for retrieval",
              "Reports assessed<br>in full text", "Included<br>per query", "Distinct<br>studies"]

def rgba(hex_colour, a):
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"

labels, colours, values, xs, cols, is_exit = [], [], [], [], [], []
def node(label, colour, value, col, exit_=False):
    labels.append(label); colours.append(colour); values.append(value)
    xs.append(COLS_X[col]); cols.append(col); is_exit.append(exit_)
    return len(labels) - 1

src, tgt, val, lcol = [], [], [], []
def link(a, b, v, colour, alpha=0.38):
    if v > 0:
        src.append(a); tgt.append(b); val.append(v); lcol.append(rgba(colour, alpha))

# ---- Nodes (column by column)
q_node = {q[0]: node(f"{q[1]} ({q[3]})", S[q[2]]["colour"], q[3], 0) for q in QUERIES}
# Streams screened together show where their records came from (e.g. 365 + 332).
SPLIT_TAGS = {"Q1a": "Q1a", "Q1b": "Q1b", "Q3": "Energy", "Q4": "Cycles"}
def screened_label(k):
    parts = [q for q in QUERIES if q[2] == k]
    text = f"{S[k]['label']} ({S[k]['screened']})"
    if len(parts) > 1:
        text += "<br>" + " + ".join(f"{SPLIT_TAGS.get(q[0], q[0])} {q[4]}" for q in parts)
    return text
c1 = {k: node(screened_label(k), S[k]["colour"], S[k]["screened"], 1) for k in stream_keys}
x1 = node(f"Removed by language and<br>document-type filters ({T['filtered_out']})", EXIT_RED, T["filtered_out"], 1, True)
c2 = {k: node(f"{S[k]['sought']}", S[k]["colour"], S[k]["sought"], 2) for k in stream_keys}
x2 = node(f"Excluded on title<br>and abstract ({T['excl_ta']})", EXIT_RED, T["excl_ta"], 2, True)
c3 = {k: node(f"{S[k]['assessed']}", S[k]["colour"], S[k]["assessed"], 3) for k in stream_keys}
x3 = node(f"Full text not<br>obtained ({T['not_retrieved']})", EXIT_RED, T["not_retrieved"], 3, True)
c4 = {k: node(f"{S[k]['counted']}", S[k]["colour"], S[k]["counted"], 4) for k in stream_keys}
x4 = node(f"Excluded after<br>full-text reading ({T['excl_ft']})", EXIT_RED, T["excl_ft"], 4, True)
c5 = node(f"Distinct studies<br>included ({T['distinct']})", FINAL_GREY, T["distinct"], 5)
x5 = node(f"Already counted under<br>an earlier query ({T['dups']})", EXIT_RED, T["dups"], 5, True)

# ---- Links
for key, label, stream, returned, kept in QUERIES:
    link(q_node[key], c1[stream], kept, S[stream]["colour"])
    link(q_node[key], x1, returned - kept, EXIT_RED, 0.30)
for k in stream_keys:
    c = S[k]["colour"]
    link(c1[k], c2[k], S[k]["sought"],    c); link(c1[k], x2, S[k]["excl_ta"],       EXIT_RED, 0.30)
    link(c2[k], c3[k], S[k]["assessed"],  c); link(c2[k], x3, S[k]["not_retrieved"], EXIT_RED, 0.30)
    link(c3[k], c4[k], S[k]["counted"],   c); link(c3[k], x4, S[k]["excl_ft"],       EXIT_RED, 0.30)
    link(c4[k], c5,    S[k]["included"],  c); link(c4[k], x5, S[k]["dups_here"],     EXIT_RED, 0.30)

# ---- Fixed vertical layout (Plotly reads node y as the node centre, 0 = top).
#      Streams are stacked from the top in pass order and exclusions sit at the
#      bottom of each column. Node heights use one common scale (px per record).
plot_h = H - MARGIN["t"] - MARGIN["b"]
n_col  = [cols.count(c) for c in range(6)]
tot    = [sum(v for v, cc in zip(values, cols) if cc == c) for c in range(6)]
ky     = min((plot_h - (n_col[c] - 1) * PAD_PX) / tot[c] for c in range(6))
ys = [0.0] * len(labels)
for c in range(5):
    members = [i for i in range(len(labels)) if cols[i] == c]
    streams = [i for i in members if not is_exit[i]]
    exits   = [i for i in members if is_exit[i]]
    free = plot_h - sum(values[i] * ky for i in members)
    gap  = max(PAD_PX, min(30, free / len(members)))  # small columns get room for labels
    y = 0.0
    for i in streams:
        h = values[i] * ky; ys[i] = y + h / 2; y += h + gap
    yb = plot_h
    for i in reversed(exits):
        h = values[i] * ky; ys[i] = yb - h / 2; yb -= h + gap
# Last column: the distinct-studies node level with the middle of the per-query
# column, and the duplicate branch below it, clear of the ribbons and of the
# column-4 exit label.
mid = sum(ys[c4[k]] for k in stream_keys) / len(stream_keys)
ys[c5] = mid
ys[x5] = mid + values[c5] * ky / 2 + 105
ys = [min(max(v / plot_h, 0.001), 0.999) for v in ys]

fig = go.Figure(go.Sankey(
    arrangement="fixed",
    node=dict(label=labels, color=colours, x=xs, y=ys, pad=PAD_PX, thickness=12,
              line=dict(width=0),
              hovertemplate="%{label}<extra></extra>"),
    link=dict(source=src, target=tgt, value=val, color=lcol),
    textfont=dict(family=FONT, size=FONT_PX, color="#1A1A1A"),
))
for i, (x, h) in enumerate(zip(COLS_X, HEADERS)):
    fig.add_annotation(x=x, y=1.0, xref="paper", yref="paper", yanchor="bottom",
                       xanchor="right" if i == len(COLS_X) - 1 else "left", align="right" if i == len(COLS_X) - 1 else "left",
                       yshift=10, text=f"<b>{h}</b>", showarrow=False,
                       font=dict(family=FONT, size=FONT_PX + 1, color="#1A1A1A"))
fig.update_layout(width=W, height=H, margin=MARGIN, paper_bgcolor="white",
                  plot_bgcolor="white", font=dict(family=FONT))

fig.show()

import plotly.io as pio
pio.kaleido.scope.mathjax = None   # stops a stray "Loading [MathJax]" box appearing in the PDF

# Vector PDF for LaTeX (\includegraphics) and a high-resolution PNG preview.
fig.write_image("prisma_flow.pdf")
fig.write_image("prisma_flow.png", scale=2)
fig.write_html("prisma_flow.html", include_plotlyjs="cdn")   # interactive version
print("Saved prisma_flow.pdf, prisma_flow.png and prisma_flow.html")

# On Google Colab, offer the files for download.
try:
    from google.colab import files
    for f in ("prisma_flow.pdf", "prisma_flow.png"):
        files.download(f)
except ImportError:
    pass
