"""Generate results.tex (all numbers in the paper) and the two data figures.

Every value is read from a repository file; nothing is typed by hand.
Sources:
  N  natural-scope leverage diagnostic (validation split only)
     paper-b-neural-pair-search/outputs/runs/bench_search_benchmark_20261111/ris_leverage_20261112/{summary.json,a*_w*.jsonl}
     paper-b-neural-pair-search/scripts/ris_leverage_summary_20261112.py (aperture constants)
  G  ME-GA reimplementation record paper-a-ris-physics/docs/me-ga-reimplementation.md; pair-neighbourhood sizes
  P  production declaration and site rules
     GeoRIS-Bench/docs/bench-production-full-20261109.md, bench-users-v1-design-20261108.md,
     bench-production-trace-20261109.md, hybrid-gates-v2-20261107.md
GeoRIS-Bench RIS-relevant scope v2 values do not exist yet; they are emitted as \\PENDING{...}.
Run: python make_results.py  (from this folder)
"""
import glob, json, re, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
LD = f"{ROOT}/paper-b-neural-pair-search/outputs/runs/bench_search_benchmark_20261111/ris_leverage_20261112/"
PA = f"{ROOT}/paper-a-ris-physics/"
GB = f"{ROOT}/GeoRIS-Bench/docs/"

M = {}      # key -> formatted string
SRC = {}    # key -> source tag


def put(k, v, src):
    assert re.fullmatch(r"[A-Za-z0-9]+", k), k
    assert k not in M, k
    M[k] = v
    SRC[k] = src


f3 = lambda x: f"{x:.3f}"
f2 = lambda x: f"{x:.2f}"
f1 = lambda x: f"{x:.1f}"
pc = lambda x: f"{100 * x:.1f}"
sg = lambda x: ("+" if x >= 0 else "$-$") + f"{abs(x):.3f}"
db = lambda x: ("$-$" if x < 0 else "+") + f"{abs(x):.1f}"

# ---------------------------------------------------------------- natural scope
S = json.load(open(LD + "summary.json"))
rows = {a: [json.loads(l) for f in sorted(glob.glob(LD + f"a{a}_w*.jsonl")) for l in open(f)] for a in ("64", "128", "256")}
src_script = open(f"{ROOT}/paper-b-neural-pair-search/scripts/ris_leverage_summary_20261112.py").read()
ap = re.search(r"APERTURE = \{64: ([\d.]+) \* ([\d.]+), 128: ([\d.]+) \* ([\d.]+), 256: ([\d.]+) \* ([\d.]+)\}", src_script).groups()
for i, a in enumerate(("64", "128", "256")):
    put(f"natApW{a}", f2(float(ap[2 * i])), "N"); put(f"natApH{a}", f2(float(ap[2 * i + 1])), "N")

frames_total = 0
fig_gain = {}
for a in ("64", "128", "256"):
    s = S[a]; R = rows[a]
    assert s["frames"] == len(R)
    frames_total += len(R)
    rz = np.array([r["rate_alloff"] for r in R]); rb = np.array([r["rate_best"] for r in R])
    zero = rz < 1e-9                       # same threshold as the summary script
    g = rb - rz
    traj = {}
    for r in R:
        traj.setdefault("/".join(r["key"].split("/")[:3]), []).append(r["rate_alloff"])
    put(f"natFrames{a}", str(s["frames"]), "N")
    put(f"natZeroShare{a}", pc(s["share_worst_rate_zero_alloff"]), "N")
    put(f"natZeroBoth{a}", str(s["why_zero"]["bs=blocked,ris=blocked,direct0=True,ris0=True"]), "N")
    put(f"natZeroTraj{a}", str(sum(1 for v in traj.values() if max(v) < 1e-9)), "N")
    put(f"natTraj{a}", str(len(traj)), "N")
    put(f"natOffMinusNoRis{a}", sg(s["alloff_minus_noris_storedw"]["mean"]), "N")
    put(f"natGainAllMean{a}", f3(s["best_minus_alloff_all"]["mean"]), "N")
    put(f"natGainAllMedian{a}", f3(s["best_minus_alloff_all"]["median"]), "N")
    nz = s["best_minus_alloff_nonzero_frames"]
    put(f"natGainNzMean{a}", f3(nz["mean"]), "N"); put(f"natGainNzMedian{a}", f3(nz["median"]), "N")
    put(f"natGainNzPninety{a}", f3(nz["p90"]), "N"); put(f"natGainNzMax{a}", f3(nz["max"]), "N")
    put(f"natGainGtOne{a}", pc(float(np.mean(g > 0.1))), "N")
    put(f"natGainGtFive{a}", pc(float(np.mean(g > 0.5))), "N")
    put(f"natRateOffMean{a}", f3(s["rate"]["alloff"]["mean"]), "N")
    put(f"natRateNoRisMean{a}", f3(s["rate"]["noris_storedw"]["mean"]), "N")
    put(f"natRateBestMean{a}", f3(s["rate"]["best"]["mean"]), "N")
    put(f"natRateOnMean{a}", f3(s["rate"]["allon"]["mean"]), "N")
    put(f"natRateBestOwnMean{a}", f3(s["rate"]["best_ownrzf"]["mean"]), "N")
    put(f"natIN{a}", db(s["worst_user_intf_over_noise_db_median_nonzero"]), "N")
    put(f"natPrecErr{a}", f"{s['precoder_relerr_vs_alloff_max']:.0f}", "N")
    for cls, tag in (("bs=blocked,ris=los", "BlkLos"), ("bs=reflection_only,ris=los", "RefLos"), ("bs=los,ris=los", "LosLos"),
                     ("bs=blocked,ris=reflection_only", "BlkRef")):
        c = s["by_user_class"][cls]
        put(f"natRisDir{tag}{a}", db(c["risbest_minus_direct_db_median"]), "N")
        put(f"natBound{tag}{a}", db(c["bound_ris_vs_los_db_median"]), "N")
        put(f"natUF{tag}{a}", str(c["user_frames"]), "N")
    # headroom by the worst user's class (worst user = min per-user rate at all OFF), non-zero frames
    cl = {}
    for r, gi, z in zip(R, g, zero):
        if z: continue
        u = r["users"][int(np.argmin(r["peruser_rate_alloff"]))]
        cl.setdefault((u["bs_user"], u["ris_user"]), []).append(gi)
    for key, tag in ((("los", "los"), "LosLos"), (("blocked", "los"), "BlkLos")):
        v = np.array(cl[key]); put(f"natHrN{tag}{a}", str(len(v)), "N")
        put(f"natHrMed{tag}{a}", f3(float(np.median(v))), "N"); put(f"natHrGt{tag}{a}", f"{100 * np.mean(v > 0.1):.0f}", "N")
    for mp in ("munich", "rotterdam", "maastricht"):
        put(f"natZero{mp.capitalize()}{a}", f"{100 * s['per_map'][mp]['zero_share']:.0f}", "N")
    fig_gain[a] = (g[~zero], zero.mean())
put("natFramesTotal", f"{frames_total:,}", "N")
FREQ = float(re.search(r"The Sionna run is fixed at ([\d.]+) GHz", open(GB + "bench-production-trace-20261109.md").read()).group(1)) * 1e9
lam = 299792458.0 / FREQ
put("freqGHz", f"{FREQ / 1e9:.2f}", "N")
A256 = float(ap[4]) * float(ap[5])
put("lambdaMm", f"{1000 * lam:.1f}", "N")
put("boundXtenDb", f"{A256 / (lam * 10 ** (-10 / 20)):.0f}", "N")   # d1*d2/d giving -10 dB of LOS at 256 el.
d = S["64"]["d_bs_ris_m"]
put("natDbsrisMedian", f"{d['median']:.0f}", "N"); put("natDbsrisMax", f"{d['max']:.0f}", "N")
# user-to-RIS median distance range over RIS-visible classes (64-element geometry)
dr = [S["64"]["by_user_class"][c]["d_ris_user_median"] for c in ("bs=blocked,ris=los", "bs=los,ris=los", "bs=reflection_only,ris=los")]
put("natDrisUserLo", f"{min(dr):.0f}", "N"); put("natDrisUserHi", f"{max(dr):.0f}", "N")

# ---------------------------------------------------------------- production / site rules
prod = open(GB + "bench-production-full-20261109.md").read()
put("prodTrajPerMap", re.search(r"\*\*Trajectories:\*\* (\d+) natural trajectories per development map", prod).group(1), "P")
put("prodTraj", re.search(r"= (\d+) trajectories total", prod).group(1), "P")
put("prodFramesPerTraj", re.search(r"\*\*Selected frames:\*\* (\d+) approximately", prod).group(1), "P")
put("prodFrames", re.search(r"([\d,]+) frames across all 3 maps", prod).group(1), "P")
put("prodArrayFrames", re.search(r"([\d,]+) array-frames across all 3 maps", prod).group(1), "P")
put("prodValTraj", re.search(r"\*\*Validation \(15%\):\*\* 18 trajectories per map \(indices `0084`–`0101`, (\d+) total", prod).group(1), "P")
usr = open(GB + "bench-users-v1-design-20261108.md").read()
lo, hi = re.search(r"distance of \*\*(\d+)-(\d+) m\*\*", usr).groups()
put("siteDminNat", lo, "P"); put("siteDmaxNat", hi, "P")
put("negSlotProb", re.search(r"probability \*\*([\d.]+)\*\*", usr).group(1), "P")
tr = open(GB + "bench-production-trace-20261109.md").read()
put("rtSamples", re.search(r"([\d,]+) samples per source", tr).group(1), "P")
put("rtDepth", re.search(r"maximum interaction depth (\d+)", tr).group(1), "P")
gates = open(GB + "hybrid-gates-v2-20261107.md").read()
put("openGapPct", re.search(r"change the BS-UE direct channel by ([\d.]+)%", gates).group(1), "P")

# ---------------------------------------------------------------- ME-GA reimplementation record (documentation only)
mg = open(PA + "docs/me-ga-reimplementation.md").read()
mm = re.search(r"\(Gamma = (\d+), V = (\d+), W = (\d+)", mg)
put("megaPop", mm.group(1), "G"); put("megaIter", mm.group(2), "G")
put("megaDecisions", str(len(re.findall(r"^\| \d+ \|", mg, re.M))), "G")
put("megaSensItems", str(len(re.findall(r"\| \*\*Y\*\*", mg))), "G")
for nm, nn in (("nPairsSixtyFour", 64), ("nPairsOneTwentyEight", 128), ("nPairsTwoFiftySix", 256)):
    put(nm, f"{nn * (nn - 1) // 2:,}", "G")   # size of the exact pair neighbourhood N(N-1)/2

# ---------------------------------------------------------------- baseline settings (code and docs)
mesrc = open(f"{ROOT}/GeoRIS-Bench/src/atomwise_ris/optimization/me_ga.py").read()
put("megaWoodM", re.search(r"woodbury_max_m: int = (\d+)", mesrc).group(1), "G")
put("megaWoodMin", re.search(r"woodbury_min_children: int = (\d+)", mesrc).group(1), "G")
nsrc = open(f"{ROOT}/GeoRIS-Bench/src/atomwise_ris/optimization/nsga2.py").read()
m = re.search(r"CHOSEN_PARAMS = NSGA2Params\(population=(\d+), crossover_prob=([\d.]+)\)", nsrc)
put("nsgaPop", m.group(1), "G"); put("nsgaPc", m.group(2), "G")
ndoc = open(GB + "nsga2-baseline-20261113.md").read()
g = re.search(r"Grid: P ∈ \{([\d, ]+)\} × pc ∈ \{([\d., ]+)\} \((\d+) configs\)", ndoc)
put("nsgaGridP", g.group(1).replace(", ", "/"), "G"); put("nsgaGridPc", g.group(2).replace(", ", "/"), "G"); put("nsgaGridN", g.group(3), "G")

# ---------------------------------------------------------------- dataset: GeoRIS-Bench RIS-relevant v3 (declaration + appended results)
V3 = open(GB + "bench-ris-relevant-scope-v3-20261113.md").read()
put("vMap", re.search(r"\*\*Map:\*\* (\w+)", V3).group(1), "V")
m = re.search(r"\*\*Size:\*\* \*\*(\d+) trajectories\*\* × (\d+) frames", V3)
put("vTraj", m.group(1), "V"); put("vFrames", m.group(2), "V")
m = re.search(r"train 0000–0083 \((\d+)\), validation 0084–0101 \((\d+)\), \*\*test 0102–0119 \((\d+), SEALED\)", V3)
put("vTrainTraj", m.group(1), "V"); put("vValTraj", m.group(2), "V"); put("vTestTraj", m.group(3), "V")
m = re.search(r"\| G3 \| 0 violations of (\d+)–(\d+) m; d1 ([\d.]+) / ([\d.]+) / ([\d.]+) m \(min / median / max\); (\d+) sites", V3)
put("vDmin", m.group(1), "V"); put("vDmax", m.group(2), "V"); put("vDOneMin", m.group(3), "V"); put("vDOneMed", m.group(4), "V")
put("vDOneMax", m.group(5), "V"); put("vSites", m.group(6), "V")
m = re.search(r"d2: ([\d.]+) / ([\d.]+) / ([\d.]+) m \(q10 / median / q90\)", V3)
put("vDTwoLo", m.group(1), "V"); put("vDTwoMed", m.group(2), "V"); put("vDTwoHi", m.group(3), "V")
_rad = float(re.search(r"RIS_RELEVANT_V3_RADIUS_M = ([\d.]+)", V3).group(1))
put("vRadius", f"{_rad:.0f}", "V")
put("vAngle", re.search(r"angle between \(user − RIS\) and the panel normal ≤ (\d+)°", V3).group(1), "V")
put("vServedUF", re.search(r"\| G2 \| ([\d,]+) served user-frames", V3).group(1), "V")
put("vSamples", "10^{6}" if "`samples_per_src = 1e6`" in V3 else None, "V")
put("vPathCap", "2\\times10^{6}" if "`max_num_paths_per_src = 2e6`" in V3 else None, "V")
put("vDepth", re.search(r"seed 7, max_depth (\d+)", V3).group(1), "V")
m = re.search(r"\*\*Channels:\*\* (\d+) / (\d+) units", V3)
put("vUnitsOk", m.group(1), "V"); put("vUnits", m.group(2), "V")
put("vIncluded", re.search(r"(\d+) / 120 included", V3).group(1), "V")
for row, key in (("L2 median \\(best − all OFF\\), bit/s/Hz", "vGainMed"),):
    vals = re.search(r"\| " + row + r" \| \*\*([\d.]+) ✓\*\* \| \*\*([\d.]+) ✓\*\* \| \*\*([\d.]+) ✓\*\*", V3).groups()
    for arr, v in zip(("64", "128", "256"), vals): put(f"{key}{arr}", f3(float(v)), "V")
vals = re.search(r"\| Best − all OFF, mean / p90 \| ([\d.]+) / ([\d.]+) \| ([\d.]+) / ([\d.]+) \| ([\d.]+) / ([\d.]+) \|", V3).groups()
for i, arr in enumerate(("64", "128", "256")):
    put(f"vGainMean{arr}", vals[2 * i], "V"); put(f"vGainPninety{arr}", vals[2 * i + 1], "V")
put("vPathless", re.search(r"\| L1a pathless served user-frames \| ([\d.]+)% ✓", V3).group(1), "V")

# ---------------------------------------------------------------- protocol (frozen v3 search declaration)
SD = open(f"{ROOT}/paper-b-neural-pair-search/docs/bench-ris-relevant-v3-search-declaration-20261113.md").read()
put("vSeeds", str(len(re.search(r"test: ([\d, ]+) \(10 seeds\)", SD).group(1).split(","))), "S")
put("vBoot", re.search(r"Paired trajectory bootstrap, ([\d,]+) resamples", SD).group(1), "S")
put("vFamily", re.search(r"\*\*Bonferroni over (\w+) contrasts\*\*", SD).group(1), "S")
put("vMaxMiss", re.search(r"\*\*([\d.]+)% rule:\*\*", SD).group(1), "S")

# ---------------------------------------------------------------- benchmark results: one rerun with --bench TEST_SUMMARY.json
# TEST_SUMMARY.json = output of paper-b-neural-pair-search/scripts/collect_rr3_results_20261113.py on the sealed test pass.
import argparse
ap_ = argparse.ArgumentParser(); ap_.add_argument("--bench", default=os.environ.get("PAPER_A_BENCH"))
args_, _ = ap_.parse_known_args()
BENCH = json.load(open(args_.bench)) if args_.bench else None
PEND = []
def pend(k, label):
    put(k, None, "PENDING"); PEND.append((k, label))
METH = {"greedy": "Greedy", "pair": "Pair", "pair_plus_b3": "Bthree", "pair_plus_b5": "Bfive", "pair_plus_b35": "Bts",
        "me_ga": "Mega", "nsga2": "Nsga"}
BUDN = {5: "Five", 10: "Ten", 50: "Fifty", 100: "Hundred"}
HYP = {"H1": "HOne", "H2": "HTwo", "H5": "HFive"}
FIG = {}
for arr in ("64", "128", "256"):
    blk = (BENCH or {}).get("arrays", {}).get(arr)
    cells = {(c["method"], int(round(float(c["budget_ms"])))): c for c in (blk["metrics"] if blk else [])}
    for mkey, mt in METH.items():
        for bud, bn in BUDN.items():
            c = cells.get((mkey, bud))
            if c: put(f"vRate{mt}{bn}{arr}", f3(c["M1_rate_mean"]), "B")
            else: pend(f"vRate{mt}{bn}{arr}", f"M1 {mkey} {bud} ms {arr}")
            if c: FIG.setdefault((arr, mkey), []).append((c["M2_latency_ms_mean"], c["M1_rate_mean"]))
        c = cells.get((mkey, 50))
        if c:
            put(f"vLat{mt}{arr}", f2(c["M2_latency_ms_mean"]), "B"); put(f"vLatP{mt}{arr}", f2(c["M2_latency_ms_p95"]), "B")
            put(f"vEvals{mt}{arr}", f"{c['M3_evaluations_mean']:,.0f}", "B"); put(f"vMiss{mt}{arr}", f"{100 * c['miss_fraction_search_clock']:.2f}", "B")
        else:
            for k, lab in (("vLat", "M2 mean"), ("vLatP", "M2 p95"), ("vEvals", "M3 evals"), ("vMiss", "miss %")):
                pend(f"{k}{mt}{arr}", f"{lab} {mkey} 50 ms {arr}")
    ver = [v for v in (blk["verdicts"] if blk else []) if v.get("primary")]
    for h, hn in HYP.items():
        v = ver[0].get(h) if ver else None
        if v and "diff" in v:
            put(f"v{hn}{arr}", f"{sg(v['diff'])} [{sg(v['ci'][0])}, {sg(v['ci'][1])}]", "B"); put(f"v{hn}Verdict{arr}", v["verdict"], "B")
        else:
            pend(f"v{hn}{arr}", f"{h} diff [CI] {arr}"); pend(f"v{hn}Verdict{arr}", f"{h} verdict {arr}")
put("vBenchLoaded", "yes" if BENCH else "no", "B")

# ---------------------------------------------------------------- write results.tex
with open(os.path.join(HERE, "results.tex"), "w") as fh:
    fh.write("% AUTO-GENERATED by make_results.py -- do not edit by hand.\n")
    fh.write("% Sources: N=natural-scope leverage diagnostic (validation), G=ME-GA record / pair counts,\n")
    fh.write("% P=production docs, V=v3 scope declaration, S=v3 search declaration, B=benchmark summary (--bench), PENDING=not yet produced.\n")
    fh.write("\\providecommand{\\PENDING}[1]{\\textcolor{red}{\\textbf{[#1]}}}\n")
    fh.write("\\makeatletter\n\\newcommand{\\res}[1]{\\ifcsname res@#1\\endcsname\\csname res@#1\\endcsname\\else\\PENDING{undefined:#1}\\fi}\n")
    for k in M:
        v = M[k]
        if v is None:
            v = "\\PENDING{" + k + "}"
        fh.write(f"\\expandafter\\def\\csname res@{k}\\endcsname{{{v}}}% {SRC[k]}\n")
    fh.write("\\makeatother\n")
json.dump({"pending": PEND, "n_values": sum(v is not None for v in M.values())}, open(os.path.join(HERE, "results_manifest.json"), "w"), indent=1)

# ---------------------------------------------------------------- figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02})
cols = {"64": "#4C72B0", "128": "#DD8452", "256": "#55A868"}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.8 * 1.0, 1.95), gridspec_kw={"width_ratios": [1.1, 1]})
for a in ("64", "128", "256"):
    g, z = fig_gain[a]
    x = np.sort(np.maximum(g, 1e-4)); y = np.arange(1, len(x) + 1) / len(x)
    ax1.step(x, y, where="post", color=cols[a], lw=1.1, label=f"{a} el.")
ax1.set_xscale("log"); ax1.set_xlim(1e-4, 1.0)
ax1.axvline(0.1, color="0.5", lw=0.6, ls="--")
ax1.set_xlabel("best $-$ all-OFF worst-user rate\n(bit/s/Hz, non-zero frames)"); ax1.set_ylabel("ECDF")
ax1.legend(frameon=False, loc="upper left", fontsize=7)
ax1.set_title("(a) configuration headroom", fontsize=8)
classes = (("bs=blocked,ris=los", "BS blk./\nRIS LOS"), ("bs=reflection_only,ris=los", "BS refl./\nRIS LOS"), ("bs=los,ris=los", "BS LOS/\nRIS LOS"))
w = 0.26
for i, a in enumerate(("64", "128", "256")):
    vals = [S[a]["by_user_class"][c]["risbest_minus_direct_db_median"] for c, _ in classes]
    ax2.bar(np.arange(3) + (i - 1) * w, vals, w, color=cols[a])
    bnd = [S[a]["by_user_class"][c]["bound_ris_vs_los_db_median"] for c, _ in classes]
    ax2.scatter(np.arange(3) + (i - 1) * w, bnd, marker="_", s=40, color="k", zorder=3, lw=1.2)
ax2.scatter([], [], marker="_", color="k", label="ideal plate vs LOS")
ax2.set_xticks(range(3)); ax2.set_xticklabels([l for _, l in classes], fontsize=6.5)
ax2.set_ylabel("median RIS $-$ direct (dB)"); ax2.axhline(0, color="0.3", lw=0.5)
ax2.set_title("(b) RIS path vs BS paths", fontsize=8); ax2.legend(frameon=False, fontsize=6.5, loc="lower center", ncol=1)
ax2.set_ylim(-80, 2)
fig.tight_layout(w_pad=1.0)
fig.savefig(os.path.join(HERE, "figures", "natural_leverage.pdf"))
fig.savefig(os.path.join(HERE, "figures", "natural_leverage.png"), dpi=200)


if FIG:
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.1), sharey=False)
    sty = {"pair_plus_b35": ("b35", "#C44E52", "o"), "pair_plus_b5": ("b5", "#8172B2", "s"), "pair_plus_b3": ("b3", "#937860", "^"),
           "pair": ("pair", "#4C72B0", "D"), "greedy": ("greedy", "#55A868", "v"), "me_ga": ("ME-GA", "#DD8452", "x"), "nsga2": ("NSGA-II", "#8C8C8C", "+")}
    for ax, arr in zip(axs, ("64", "128", "256")):
        for mkey, (lab, c, mk) in sty.items():
            pts = sorted(FIG.get((arr, mkey), []))
            if pts: ax.plot([x for x, _ in pts], [y for _, y in pts], marker=mk, ms=3, lw=1, color=c, label=lab)
        ax.set_xscale("log"); ax.set_xticks([5, 10, 50, 100]); ax.set_xticklabels(["5", "10", "50", "100"])
        ax.set_title(f"{arr} elements", fontsize=8); ax.set_xlabel("M2 mean latency (ms)")
    axs[0].set_ylabel("M1 worst-user SE (bit/s/Hz)"); axs[-1].legend(frameon=False, fontsize=6, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "headline.pdf"))
if BENCH:
    with open(os.path.join(HERE, "results.tex"), "a") as fh:
        fh.write("\\benchtrue% headline figure drawn from the loaded benchmark summary\n")
print("values:", sum(v is not None for v in M.values()), "pending:", len(PEND))
