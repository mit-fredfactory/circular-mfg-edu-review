# =====================================================================
# PRISMA 2020 flow diagram, classic box layout (Page et al. 2021 template,
# as drawn by the PRISMA2020 R package / Shiny app of Haddaway et al. 2022)
# REED state-of-the-art review, NAMRC 55.  Same counts as the Sankey version.
# Paste this whole block into ONE Google Colab code cell and run it.
# Outputs: prisma_classic.pdf (for LaTeX) and prisma_classic.png
# =====================================================================

# ---------------------------------------------------------------------
# 0. Fonts: Liberation Serif is metrically identical to Times New Roman.
#    On Colab this line installs it (delete it when running outside a notebook):
!apt-get -qq install -y fonts-liberation > /dev/null 2>&1
# ---------------------------------------------------------------------
import glob
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle

for f in glob.glob("/usr/share/fonts/truetype/liberation/LiberationSerif*.ttf"):
    fm.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "pdf.fonttype": 42,          # embed fonts as TrueType in the PDF
    "svg.fonttype": "none",
    "mathtext.fontset": "custom",           # bold numbers use the same serif font
    "mathtext.rm": "Liberation Serif",
    "mathtext.bf": "Liberation Serif:bold",
    "mathtext.cal": "Liberation Serif",
    "mathtext.sf": "Liberation Serif",
})

# ---------------------------------------------------------------------
# 1. Counts (identical to the Sankey notebook). Edit here only.
# ---------------------------------------------------------------------
QUERIES = [
    # key    label                     stream       returned  after filters
    ("Q1a", "Pass 1, Query 1a",        "P1_PLAEVA",   369,      365),
    ("Q1b", "Query 1b",                "P1_PLAEVA",   354,      332),
    ("Q2",  "Query 2",                 "P1_HW",       126,      124),
    ("Q3",  "Pass 2, energy",          "P2",          130,      119),
    ("Q4",  "multiple cycles",         "P2",           18,       18),
    ("Q5",  "Pass 3",                  "P3",           39,       39),
    ("Q6",  "Pass 4",                  "P4",          135,      129),
    ("Q7",  "Pass 5",                  "P5",           40,       37),
]
STREAMS = [
    # key          assessed  not_retrieved  included (credited once)
    ("P1_PLAEVA",   164,      1,             38),
    ("P1_HW",        46,      2,             13),
    ("P2",           34,      0,              7),
    ("P3",           16,      0,              4),
    ("P4",           16,      2,             11),
    ("P5",           10,      1,              3),
]
N_ALREADY_INCLUDED = 9         # studies read again in a later query (Liu, Aly, Romani,
                               # Goncalves, Papa, Kodra, Sinchai, Petsiuk, Wilkins)
WOS_UNIQUE_RECORDS = 1126      # WoS union of all filtered queries (search set #18)
EXPECTED_INCLUDED  = 76

# ---------------------------------------------------------------------
# 2. Totals and checks
# ---------------------------------------------------------------------
identified   = sum(q[3] for q in QUERIES)
filtered_out = sum(q[3] - q[4] for q in QUERIES)
screened     = sum(q[4] for q in QUERIES)
sought       = sum(s[1] + s[2] for s in STREAMS)
not_retr     = sum(s[2] for s in STREAMS)
assessed     = sum(s[1] for s in STREAMS)
included     = sum(s[3] for s in STREAMS)
excl_ta      = screened - sought
excl_ft      = assessed - included - N_ALREADY_INCLUDED
overlap      = screened - WOS_UNIQUE_RECORDS

assert identified - filtered_out == screened
assert screened - excl_ta == sought and excl_ta >= 0
assert sought - not_retr == assessed
assert assessed - excl_ft - N_ALREADY_INCLUDED == included and excl_ft >= 0
assert included == EXPECTED_INCLUDED, f"included = {included}, expected {EXPECTED_INCLUDED}"
print(f"identified {identified}, filters {filtered_out}, screened {screened}, "
      f"excluded T/A {excl_ta}, sought {sought}, not retrieved {not_retr}, "
      f"assessed {assessed}, excluded FT {excl_ft}, already included {N_ALREADY_INCLUDED}, "
      f"included {included}; records screened in more than one query: {overlap}")

BOLD_ALL_COUNTS = True     # False: bold counts only in the Identification box

def n(x, bold=None):
    bold = BOLD_ALL_COUNTS if bold is None else bold
    num = f"{x:,}"
    if bold:
        num = r"$\mathbf{" + num.replace(",", "{,}") + "}$"
    return f"(n = {num})"

def nb(x):
    return n(x, bold=True)

q = {k: ret for k, _, _, ret, _ in QUERIES}
BULLET = "\u2022 "
INDENT = "    "                    # aligns wrapped lines with the bullet text
TXT_IDENT = "\n".join([
    f"Records identified from the Web of Science Core Collection,",
    f"eight queries {nb(identified)}:",
    f"{BULLET}Pass 1: Query 1a {nb(q['Q1a'])}; Query 1b {nb(q['Q1b'])}; Query 2 {nb(q['Q2'])}",
    f"{BULLET}Pass 2: energy {nb(q['Q3'])}; multiple cycles {nb(q['Q4'])}",
    f"{BULLET}Pass 3 {nb(q['Q5'])}",
    f"{BULLET}Pass 4 {nb(q['Q6'])}",
    f"{BULLET}Pass 5 {nb(q['Q7'])}",
])
TXT_REMOVED = "\n".join([
    "Records removed before screening:",
    f"{BULLET}Duplicate records removed {n(0)}",
    f"{BULLET}Language and document-type filters {n(filtered_out)}",
])
TXT_SCREENED = f"Records screened {n(screened)}"
TXT_EXCL_TA  = f"Records excluded on title and abstract {n(excl_ta)}"
TXT_SOUGHT   = f"Reports sought for retrieval {n(sought)}"
TXT_NOTRETR  = f"Reports not retrieved {n(not_retr)}"
TXT_ASSESSED = f"Reports assessed for eligibility {n(assessed)}"
TXT_EXCL_FT  = "\n".join([
    "Reports excluded:",
    f"{BULLET}No citable information for the review questions {n(excl_ft)}",
    f"{BULLET}Already included through an earlier query {n(N_ALREADY_INCLUDED)}",
])
TXT_INCLUDED = f"Studies included in review {n(included)}"

# ---------------------------------------------------------------------
# 3. Layout (all dimensions in inches; 7.1 in = Elsevier 5p text width).
#    Every box is sized to its own text, so no box carries empty space;
#    boxes in the same row are centred on each other.
# ---------------------------------------------------------------------
FS          = 8.0                  # body text, pt
LSP         = 1.25                 # line spacing
PAD_X, PAD_Y = 0.08, 0.06          # inner padding, in
GAP         = 0.20                 # vertical gap between rows, in
W_FIG       = 7.1
X_PHASE, W_PHASE = 0.04, 0.30
X_MAIN,  W_MAIN  = 0.46, 3.30
X_SIDE,  W_SIDE  = 4.06, 3.00
HEADER_H    = 0.28
HEADER_FILL = "#FFC000"            # PRISMA 2020 template: amber header
PHASE_FILL  = "#A9C6E8"            # PRISMA 2020 template: light-blue phase labels
EDGE, LW    = "black", 0.8

rows = [  # (phase, main text, side text)
    ("Identification", TXT_IDENT,    TXT_REMOVED),
    ("Screening",      TXT_SCREENED, TXT_EXCL_TA),
    ("Screening",      TXT_SOUGHT,   TXT_NOTRETR),
    ("Screening",      TXT_ASSESSED, TXT_EXCL_FT),
    ("Included",       TXT_INCLUDED, None),
]

fig = plt.figure(figsize=(W_FIG, 10))      # provisional height, fixed below
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
renderer = fig.canvas.get_renderer()

def make_text(text, **kw):
    t = ax.text(0, 0, text, ha="left", va="top", fontsize=FS, linespacing=LSP, **kw)
    bb = t.get_window_extent(renderer)
    return t, bb.width / fig.dpi, bb.height / fig.dpi      # inches

# Measure every text and check it fits the column it is going into
cells = []
for ph, main, side in rows:
    tm, wm, hm = make_text(main)
    assert wm + 2 * PAD_X <= W_MAIN, f"text too wide for main column: {main[:40]}..."
    if side:
        ts, ws, hs = make_text(side)
        assert ws + 2 * PAD_X <= W_SIDE, f"text too wide for side column: {side[:40]}..."
    else:
        ts, hs = None, 0
    cells.append((ph, tm, hm + 2 * PAD_Y, ts, hs + 2 * PAD_Y if ts else 0))

# Phase labels must fit inside the rows they span
def label_len(label):
    t = ax.text(0, 0, label, rotation=90, fontsize=FS + 1, fontweight="bold")
    h = t.get_window_extent(renderer).height / fig.dpi
    t.remove()
    return h + 0.10
row_h = [max(hm, hs) for _, _, hm, _, hs in cells]
for ph in dict.fromkeys(r[0] for r in rows):
    idx = [i for i, r in enumerate(rows) if r[0] == ph]
    span = sum(row_h[i] for i in idx) + GAP * (len(idx) - 1)
    if span < label_len(ph):
        row_h[idx[-1]] += label_len(ph) - span

H_FIG = 0.05 + HEADER_H + 0.16 + sum(row_h) + GAP * (len(rows) - 1) + 0.05
fig.set_size_inches(W_FIG, H_FIG)
ax.set_xlim(0, W_FIG); ax.set_ylim(0, H_FIG)

def frame(x, y_top, w, h, fill="white"):
    ax.add_patch(Rectangle((x, y_top - h), w, h, facecolor=fill, edgecolor=EDGE, lw=LW, zorder=1))

def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=LW, color=EDGE,
                                mutation_scale=8, shrinkA=0, shrinkB=0))

# Header bar across the main and side columns
y = H_FIG - 0.05
frame(X_MAIN, y, X_SIDE + W_SIDE - X_MAIN, HEADER_H, fill=HEADER_FILL)
ax.text((X_MAIN + X_SIDE + W_SIDE) / 2, y - HEADER_H / 2,
        "Identification of studies via databases (Web of Science Core Collection)",
        ha="center", va="center", fontsize=FS + 1, fontweight="bold", zorder=2)
y -= HEADER_H + 0.16

main_tops, main_bots, row_tops, row_bots = [], [], [], []
for (ph, tm, hm, ts, hs), h in zip(cells, row_h):
    mid = y - h / 2
    frame(X_MAIN, mid + hm / 2, W_MAIN, hm)
    tm.set_position((X_MAIN + PAD_X, mid + hm / 2 - PAD_Y)); tm.set_zorder(2)
    main_tops.append(mid + hm / 2); main_bots.append(mid - hm / 2)
    if ts:
        frame(X_SIDE, mid + hs / 2, W_SIDE, hs)
        ts.set_position((X_SIDE + PAD_X, mid + hs / 2 - PAD_Y)); ts.set_zorder(2)
        arrow(X_MAIN + W_MAIN, mid, X_SIDE, mid)
    row_tops.append(y); row_bots.append(y - h)
    y -= h + GAP
for i in range(len(rows) - 1):                       # vertical arrows
    arrow(X_MAIN + W_MAIN / 2, main_bots[i], X_MAIN + W_MAIN / 2, main_tops[i + 1])

# Phase labels spanning their rows
spans = {}
for (ph, *_), t, b in zip(cells, row_tops, row_bots):
    t0, b0 = spans.get(ph, (t, b))
    spans[ph] = (max(t0, t), min(b0, b))
for ph, (t, b) in spans.items():
    ax.add_patch(FancyBboxPatch((X_PHASE, b), W_PHASE, t - b,
                                boxstyle="round,pad=0,rounding_size=0.08",
                                facecolor=PHASE_FILL, edgecolor=PHASE_FILL, lw=LW))
    ax.text(X_PHASE + W_PHASE / 2, (t + b) / 2, ph, rotation=90,
            ha="center", va="center", fontsize=FS + 1, fontweight="bold")

fig.savefig("prisma_classic.pdf")
fig.savefig("prisma_classic.png", dpi=300)
print(f"Saved prisma_classic.pdf and prisma_classic.png ({W_FIG} x {H_FIG:.2f} in)")

# On Google Colab, offer the files for download.
try:
    from google.colab import files
    for f in ("prisma_classic.pdf", "prisma_classic.png"):
        files.download(f)
except ImportError:
    pass
