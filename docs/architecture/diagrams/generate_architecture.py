"""Enterprise DevOps Platform reference architecture (v2, dark).

Usage: python3 generate_architecture.py out.svg
"""
import sys

W, H = 1920, 1290
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', Consolas, monospace"

BG = "#0A0F1E"
PANEL = "#111A2E"
PANEL2 = "#0E1628"
LINE = "#24314F"
T1, T2, T3 = "#E6EDF7", "#A3B1C6", "#6B7A93"
C = dict(code="#60A5FA", build="#22D3EE", supply="#A78BFA", deliver="#2DD4BF",
         run="#34D399", observe="#FBBF24", rose="#FB7185", azure="#3B82F6")
PH = {0: "#94A3B8", 1: "#60A5FA", 2: "#FB7185", 3: "#A78BFA", 4: "#2DD4BF", 5: "#FBBF24", 6: "#34D399"}
PHNAME = {0: "Foundation", 1: "GitHub + Jenkins", 2: "DevSecOps gates", 3: "Terraform · ACR · signing",
          4: "AKS · Helm · Argo CD", 5: "Observability · SLOs", 6: "Resilience · DR"}
LIVE = "#22C55E"

out = []
def a(s): out.append(s)
def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, t, size=13, weight=400, fill=T1, anchor="start", mono=False, ls=None, rot=None):
    extra = f' letter-spacing="{ls}"' if ls else ""
    if rot:
        extra += f' transform="rotate({rot} {x} {y})"'
    a(f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" font-size="{size}" '
      f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(t)}</text>')

def rect(x, y, w, h, fill=PANEL, stroke=LINE, sw=1, r=10, dash=None, op=None, filt=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    f = f' filter="url(#{filt})"' if filt else ""
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}{f}/>')

def badge(x, y, p):
    c = PH[p]
    rect(x, y, 30, 17, fill=c, stroke=c, sw=1, r=8.5, op=0.16)
    text(x + 15, y + 12.5, f"P{p}", 10.5, 700, c, "middle")

def tag(x, y, label, color):
    w = 8 + len(label) * 7
    rect(x, y, w, 17, fill="none", stroke=color, sw=1, r=8.5, dash="3 2")
    text(x + w / 2, y + 12.5, label, 9.5, 700, color, "middle", ls=0.8)
    return w

def live(x, y):
    a(f'<circle cx="{x}" cy="{y}" r="7" fill="{LIVE}" fill-opacity="0.25"/>')
    a(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{LIVE}"/>')

def step(x, y, n, color=T1):
    a(f'<circle cx="{x}" cy="{y}" r="10.5" fill="{BG}" stroke="{color}" stroke-width="1.6"/>')
    text(x, y + 4.2, str(n), 11.5, 700, color, "middle")

def arrow(pts, color=T2, dash=None, sw=1.8, marker="ah"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x},{y}" for x, y in pts)
    a(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
      f'stroke-linejoin="round" stroke-linecap="round" marker-end="url(#{marker})"/>')

def card(x, y, w, h, title, lines=(), accent=T2, phase=None, status="planned", lsz=12.5, sub=None):
    """status: live | planned | later"""
    dash = "5 4" if status == "later" else None
    rect(x, y, w, h, fill=PANEL, stroke=accent if status == "later" else LINE, sw=1.2, r=10, dash=dash, filt="sh")
    if status != "later":
        a(f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="3" rx="1.5" fill="{accent}"/>')
    text(x + 14, y + 25, title, 14.5, 700, T1)
    right = x + w - 12
    if phase is not None:
        badge(right - 30, y + 11, phase)
        right -= 38
    if status == "later":
        tw = 8 + 5 * 7
        tag(right - tw, y + 11, "LATER", accent)
    if status == "live":
        live(right - 8, y + 19.5)
    yy = y + 25 + (18 if sub else 0)
    if sub:
        text(x + 14, y + 43, sub, 11.5, 500, accent, mono=True)
    for i, t in enumerate(lines):
        text(x + 14, yy + 21 + i * 19.5, t, lsz, 400, T2)

def stage_list(x, y, w, title, rows, accent, footer=None):
    """rows: (title, sub, phase, status)"""
    RH = 46
    h = 40 + RH * len(rows) + (30 if footer else 6)
    rect(x, y, w, h, fill=PANEL, stroke=LINE, sw=1.2, r=10, filt="sh")
    a(f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="3" rx="1.5" fill="{accent}"/>')
    text(x + 14, y + 25, title, 14.5, 700, T1)
    for i, (t, s, p, st) in enumerate(rows):
        ry = y + 38 + i * RH
        dash = "4 3" if st == "later" else None
        rect(x + 10, ry, w - 20, RH - 6, fill=PANEL2, stroke=accent if st == "later" else LINE, sw=1, r=7, dash=dash)
        a(f'<rect x="{x + 10}" y="{ry + 8}" width="3" height="{RH - 22}" rx="1.5" fill="{PH[p]}"/>')
        text(x + 22, ry + 17, t, 13, 600, T1)
        text(x + 22, ry + 33, s, 11.5, 400, T3)
        badge(x + w - 50, ry + 6, p)
        if st == "live":
            live(x + w - 64, ry + 14.5)
    if footer:
        text(x + 14, y + h - 12, footer, 11.5, 600, C["rose"])
    return h

# ---------------------------------------------------------------- canvas
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<title>Enterprise DevOps Platform reference architecture</title>')
a('<defs>')
for mid, col in [("ah", T2), ("ahc", C["code"]), ("ahb", C["build"]), ("ahs", C["supply"]),
                 ("ahd", C["deliver"]), ("ahr", C["run"]), ("aho", C["observe"])]:
    a(f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
      f'orient="auto-start-reverse"><path d="M0,0.5 L10,5 L0,9.5 z" fill="{col}"/></marker>')
a('<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
  '<circle cx="1" cy="1" r="1" fill="#1A2440"/></pattern>')
a('<linearGradient id="hdr" x1="0" x2="1"><stop offset="0" stop-color="#60A5FA"/>'
  '<stop offset="0.5" stop-color="#A78BFA"/><stop offset="1" stop-color="#2DD4BF"/></linearGradient>')
a('<radialGradient id="glow" cx="0.5" cy="0" r="0.8"><stop offset="0" stop-color="#1E3A8A" stop-opacity="0.35"/>'
  '<stop offset="1" stop-color="#0A0F1E" stop-opacity="0"/></radialGradient>')
a('<filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="4" stdDeviation="6" '
  'flood-color="#000000" flood-opacity="0.35"/></filter>')
a('</defs>')
a(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
a(f'<rect width="{W}" height="520" fill="url(#glow)"/>')

# ---------------------------------------------------------------- header
text(40, 56, "Enterprise DevOps Platform", 32, 800, T1)
text(522, 56, "reference architecture", 32, 300, T2)
a(f'<rect x="40" y="70" width="230" height="3" rx="1.5" fill="url(#hdr)"/>')
text(40, 100, "Commit to production on Azure: CI with DevSecOps gates, a signed software supply chain, GitOps delivery to AKS and SLO-driven operations.",
     14.5, 400, T2)
text(40, 121, "Built and rebuilt from Git in every 3-hour KodeKloud Azure playground session.", 14.5, 400, T3)
# legend
lx = 1380
rect(lx, 28, 500, 96, fill=PANEL2, stroke=LINE, r=10)
live(lx + 22, 52); text(lx + 36, 56.5, "Running today", 12.5, 500, T2)
rect(lx + 150, 44, 26, 16, fill=PANEL, stroke=T2, r=4); text(lx + 184, 56.5, "Planned, by phase", 12.5, 500, T2)
rect(lx + 14, 78, 26, 16, fill="none", stroke=T2, r=4, dash="4 3"); text(lx + 48, 90.5, "Later option", 12.5, 500, T2)
badge(lx + 150, 77, 3); text(lx + 188, 90.5, "Roadmap phase", 12.5, 500, T2)
step(lx + 352, 52, 1); text(lx + 370, 56.5, "Flow step", 12.5, 500, T2)
a(f'<line x1="{lx + 342}" y1="86" x2="{lx + 362}" y2="86" stroke="{C["rose"]}" stroke-width="2" stroke-dasharray="4 3"/>')
text(lx + 370, 90.5, "Trust boundary", 12.5, 500, T2)

# ---------------------------------------------------------------- columns
CW, CG = 290, 20
X = [40 + i * (CW + CG) for i in range(6)]
STAGES = [("01", "CODE", "GitHub", C["code"]), ("02", "BUILD & VERIFY", "Jenkins CI", C["build"]),
          ("03", "SECURE SUPPLY CHAIN", "Docker · Cosign · ACR", C["supply"]),
          ("04", "DELIVER", "GitOps · Argo CD · Helm", C["deliver"]),
          ("05", "RUN", "AKS", C["run"]), ("06", "OBSERVE & LEARN", "Prometheus · Grafana", C["observe"])]

# plane labels
def plane(x1, x2, y, label, color):
    a(f'<path d="M{x1},{y + 8} V{y} H{x2} V{y + 8}" fill="none" stroke="{color}" stroke-width="1.2" stroke-opacity="0.7"/>')
    tw = len(label) * 7.4 + 20
    rect((x1 + x2) / 2 - tw / 2, y - 9, tw, 18, fill=BG, stroke=BG, r=4)
    text((x1 + x2) / 2, y + 4.5, label, 11, 700, color, "middle", ls=1.2)

plane(X[0], X[0] + CW, 152, "OUTSIDE AZURE", T3)
plane(X[1], X[2] + CW, 152, "CI PLANE · PUSH", C["build"])
plane(X[3], X[4] + CW, 152, "CD PLANE · PULL (GITOPS)", C["deliver"])
plane(X[5], X[5] + CW, 152, "OBSERVABILITY PLANE", C["observe"])

HY = 170
for i, (n, name, sub, col) in enumerate(STAGES):
    x = X[i]
    rect(x, HY, CW, 46, fill=col, stroke=col, r=10, op=0.10)
    a(f'<rect x="{x}" y="{HY}" width="{CW}" height="46" rx="10" fill="none" stroke="{col}" stroke-opacity="0.55"/>')
    text(x + 16, HY + 29, n, 15, 800, col, mono=True)
    text(x + 46, HY + 21, name, 13, 800, T1, ls=1)
    text(x + 46, HY + 37, sub, 11.5, 500, T2)
    if i < 5:
        text(x + CW + CG / 2, HY + 29, "›", 20, 700, T3, "middle")

# Azure boundary
BX1, BY1, BX2, BY2 = X[1] - 10, 232, X[5] + CW + 10, 764
rect(BX1, BY1, BX2 - BX1, BY2 - BY1, fill=C["azure"], stroke=C["azure"], sw=1.4, r=16, dash="8 6", op=0.04)
lbl = "AZURE · KODEKLOUD PLAYGROUND · ONE EXISTING RESOURCE GROUP · NO ROLE ASSIGNMENTS"
tw = len(lbl) * 7.1 + 24
rect(BX1 + 20, BY1 - 10, tw, 20, fill=BG, stroke=C["azure"], sw=1, r=10)
text(BX1 + 32, BY1 + 4.5, lbl, 10.5, 700, "#93C5FD", ls=1)

TOP = 252

# ---- col 1: code
x = X[0]
card(x, TOP, CW, 106, "Developer", ["Short-lived branches, one PR per change", "Local: JDK 21, Docker, kubectl, Terraform"], C["code"], 0, "live")
card(x, TOP + 128, CW, 236, "GitHub monorepo", [
    "application/ · Spring Boot 4, Java 21",
    "ci/ · Jenkinsfile, scanner config",
    "infrastructure/ · Terraform",
    "kubernetes/ · Helm chart",
    "gitops/ · desired state per env",
    "main: review + Jenkins check required",
    "Dependabot · CODEOWNERS · secret scan",
], C["code"], 1, sub="enterprise-devops-pipeline", lsz=12)
card(x, TOP + 386, CW, 126, "Private access path", ["Jenkins UI only through an SSH tunnel", "No inbound webhook: Jenkins polls Git", "Argo CD, Grafana via port-forward"], C["rose"], 1)
arrow([(x + CW / 2, TOP + 107), (x + CW / 2, TOP + 126)], C["code"], marker="ahc")
step(x + CW / 2 + 22, TOP + 117, 1, C["code"])

# ---- col 2: build & verify
x = X[1]
card(x, TOP, CW, 106, "Jenkins controller", ["vm-jenkins-lab · D2s_v3 · StandardSSD", "Config as code (JCasC), jobs in Git", "SonarQube + Docker on the same VM"], C["build"], 1)
h2 = stage_list(x, TOP + 128, CW, "Quality and security gates", [
    ("Checkout", "SCM poll every 5 min", 0, "live"),
    ("Compile + 12 tests", "unit, web layer, integration", 0, "live"),
    ("JaCoCo + JUnit reports", "coverage published per build", 0, "live"),
    ("SonarQube quality gate", "bugs, smells, coverage threshold", 2, "planned"),
    ("Gitleaks", "secrets in tree and full history", 2, "planned"),
    ("Trivy filesystem", "dependency CVEs + IaC misconfig", 2, "planned"),
], C["build"], footer="Any red gate stops the build: no image")
arrow([(X[0] + CW + 2, TOP + 200), (x - 3, TOP + 200)], C["code"], marker="ahc")
step(X[0] + CW + CG / 2, TOP + 178, 2, C["code"])

# ---- col 3: supply chain
x = X[2]
h3 = stage_list(x, TOP, CW, "Build once, sign, publish", [
    ("Docker build", "from the tested JAR · tag = Git SHA", 2, "planned"),
    ("Trivy image scan", "HIGH / CRITICAL fails the build", 2, "planned"),
    ("Syft SBOM", "SPDX, attached to the image", 2, "planned"),
    ("Cosign sign", "signs the digest, key in Key Vault", 3, "planned"),
    ("Push by digest", "repo-scoped push token", 3, "planned"),
], C["supply"])
card(x, TOP + h3 + 18, CW, 128, "Azure Container Registry", ["image@sha256 + signature + SBOM", "push token → Jenkins credentials", "pull-only token → AKS imagePullSecret"], C["supply"], 3, sub="Standard SKU · no ACR Tasks")
card(x, TOP + h3 + 164, CW, 76, "Azure Key Vault", ["access-policy mode · Cosign key"], C["supply"], 3)
arrow([(X[1] + CW + 2, TOP + 360), (x - 3, TOP + 360)], C["build"], marker="ahb")
step(X[1] + CW + CG / 2, TOP + 338, 3, C["build"])
arrow([(x + CW / 2, TOP + h3 + 1), (x + CW / 2, TOP + h3 + 16)], C["supply"], marker="ahs")
step(x + CW / 2 + 22, TOP + h3 + 9, 4, C["supply"])

# trust boundary between CI and CD planes
tx = X[2] + CW + CG / 2
a(f'<line x1="{tx}" y1="{BY1 + 14}" x2="{tx}" y2="{BY2 - 14}" stroke="{C["rose"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
rect(tx - 9, 370, 18, 320, fill=BG, stroke=BG, r=6)
text(tx + 4, 530, "CI HOLDS NO CLUSTER CREDENTIALS", 10.5, 800, C["rose"], "middle", ls=1.4, rot=-90)

# ---- col 4: deliver
x = X[3]
card(x, TOP, CW, 106, "Desired state in Git", ["gitops/ path, same GitHub repo", "CI commits the new digest for dev", "prod changes only by pull request"], C["deliver"], 4)
card(x, TOP + 128, CW, 150, "Argo CD", ["Pulls Git and syncs the cluster", "dev auto-sync · prod gated by PR", "Drift detection and self-heal", "Rollback = git revert"], C["deliver"], 4)
card(x, TOP + 304, CW, 90, "Helm chart", ["one chart, values per environment", "imagePullSecrets set from values"], C["deliver"], 4)
card(x, TOP + 412, CW, 100, "Admission policy", ["Kyverno verifies Cosign signatures", "blocks unsigned and :latest images"], C["rose"], None, "later")
arrow([(X[2] + CW + 2, TOP + 50), (x - 3, TOP + 50)], C["supply"], marker="ahs")
step(X[2] + CW + CG / 2, TOP + 28, 5, C["supply"])
arrow([(x + CW / 2, TOP + 107), (x + CW / 2, TOP + 126)], C["deliver"], marker="ahd")

# ---- col 5: run
x = X[4]
rect(x, TOP, CW, 400, fill=PANEL, stroke=LINE, sw=1.2, r=10, filt="sh")
a(f'<rect x="{x + 1}" y="{TOP + 1}" width="{CW - 2}" height="3" rx="1.5" fill="{C["run"]}"/>')
text(x + 14, TOP + 25, "AKS cluster", 14.5, 700, T1)
badge(x + CW - 42, TOP + 11, 4)
text(x + 14, TOP + 43, "1 pool · 2 × D2s_v3 · default CNI", 11.5, 500, C["run"], mono=True)
for j, (ns, l1, l2) in enumerate([("dev", "Deployment + Service :8080", "auto-synced from main"),
                                  ("prod", "same digest as dev", "smoke test after each sync")]):
    ny = TOP + 58 + j * 96
    rect(x + 12, ny, CW - 24, 84, fill=PANEL2, stroke=C["run"], sw=1, r=8, dash="4 3")
    text(x + 26, ny + 22, f"namespace  {ns}", 12.5, 700, C["run"], mono=True)
    text(x + 26, ny + 44, l1, 12.5, 400, T2)
    text(x + 26, ny + 64, l2, 12.5, 400, T2)
text(x + 14, TOP + 274, "Every pod", 12.5, 700, T1)
for i, t in enumerate(["runAsNonRoot · read-only root FS", "liveness + readiness probes", "requests and limits · 20 s drain", "pulls with pull-only ACR token"]):
    text(x + 14, TOP + 296 + i * 22, "▸ " + t, 12.5, 400, T2)
card(x, TOP + 420, CW, 92, "Portable fallback", ["same chart and Argo CD apps", "run on kind / k3d when AKS can't"], C["run"], 4)
arrow([(X[3] + CW + 2, TOP + 200), (x - 3, TOP + 200)], C["deliver"], marker="ahd")
step(X[3] + CW + CG / 2, TOP + 178, 6, C["deliver"])
# ACR -> AKS pull, threaded under Argo CD and the Helm chart
ay = TOP + 291
acr_y = TOP + h3 + 18
arrow([(X[2] + CW + 2, acr_y + 40), (X[3] - 4, acr_y + 40), (X[3] - 4, ay), (x - 3, ay)], C["supply"], marker="ahs")
step(X[3] + CW / 2, ay, 7, C["supply"])

# ---- col 6: observe & learn
x = X[5]
card(x, TOP, CW, 96, "Prometheus", ["ServiceMonitor → /actuator/prometheus", "trimmed kube-prometheus-stack"], C["observe"], 5)
card(x, TOP + 112, CW, 96, "Grafana", ["RED + JVM dashboards", "SLO and error-budget burn"], C["observe"], 5)
card(x, TOP + 224, CW, 96, "Alertmanager", ["burn rate, latency, restarts", "every alert links a runbook"], C["observe"], 5)
card(x, TOP + 336, CW, 82, "Chaos and RCA", ["kill pods, drain a node, write the RCA"], C["run"], 6)
card(x, TOP + 432, CW, 80, "DORA metrics", ["lead time, deploy frequency, CFR, MTTR"], C["observe"], None, "later")
arrow([(X[4] + CW + 2, TOP + 48), (x - 3, TOP + 48)], C["observe"], marker="aho")
step(X[4] + CW + CG / 2, TOP + 26, 8, C["observe"])

# feedback loop
fy = 790
fx2 = X[5] + CW / 2
a(f'<polyline points="{fx2},{TOP + 513} {fx2},{fy} {24},{fy} {24},{TOP + 53} {X[0] - 3},{TOP + 53}" fill="none" '
  f'stroke="{C["observe"]}" stroke-width="1.8" stroke-dasharray="7 5" stroke-linejoin="round" marker-end="url(#aho)"/>')
msg = "FEEDBACK LOOP · SLO burn, alerts, RCAs and DORA trends go back into the backlog"
tw = len(msg) * 7.2 + 28
rect(960 - tw / 2, fy - 11, tw, 22, fill=BG, stroke=C["observe"], sw=1, r=11)
text(960, fy + 4.5, msg, 11.5, 700, C["observe"], "middle", ls=0.6)
step(960 + tw / 2 + 22, fy, 9, C["observe"])

# ---------------------------------------------------------------- foundation band
FY = 822
rect(40, FY, 1840, 112, fill=PANEL2, stroke=LINE, r=12)
text(60, FY + 27, "FOUNDATION · EVERYTHING AS CODE · THE ENVIRONMENT IS DISPOSABLE", 12, 800, T1, ls=1.2)
chips = [("Terraform", "RG as data source · VNet, NSG, VM, ACR, KV, AKS", 3),
         ("Jenkins bootstrap", "cloud-init VM build inside one session", 1),
         ("JCasC + jobs in Git", "Jenkins rebuilt, never restored by hand", 6),
         ("Helm + Argo CD apps", "the whole cluster state lives in Git", 4),
         ("Rebuild drill", "every 3-hour wipe is a DR test · RTO logged", 6)]
cw = (1800 - 4 * 12) / 5
for i, (t, s, p) in enumerate(chips):
    cx = 60 + i * (cw + 12)
    rect(cx, FY + 40, cw, 56, fill=PANEL, stroke=LINE, r=8)
    a(f'<rect x="{cx}" y="{FY + 48}" width="3" height="40" rx="1.5" fill="{PH[p]}"/>')
    text(cx + 14, FY + 63, t, 13.5, 700, T1)
    text(cx + 14, FY + 83, s, 11.5, 400, T3)
    badge(cx + cw - 42, FY + 49, p)

# ---------------------------------------------------------------- principles + constraints
PY = 952
PHH = 262
rect(40, PY, 910, PHH, fill=PANEL2, stroke=LINE, r=12)
text(60, PY + 28, "ARCHITECTURE PRINCIPLES", 12, 800, T1, ls=1.2)
principles = [
    ("Build once, promote the digest", "dev and prod run the identical image; only Helm values differ"),
    ("Pull-based delivery", "CI writes to Git, Argo CD pulls; no kubeconfig in Jenkins"),
    ("Verifiable supply chain", "commit SHA → image digest → SBOM + Cosign signature"),
    ("Everything as code", "infra, CI, deploy state in Git; any session rebuilds from zero"),
    ("SLO-driven operations", "page on error-budget burn, each alert with a runbook and RCA"),
]
for i, (t, s) in enumerate(principles):
    yy = PY + 48 + i * 42
    text(60, yy + 18, f"0{i + 1}", 14, 800, "#60A5FA", mono=True)
    text(96, yy + 12, t, 13.5, 700, T1)
    text(96, yy + 30, s, 12, 400, T3)

rx = 970
rect(rx, PY, 910, PHH, fill=PANEL2, stroke=LINE, r=12)
text(rx + 20, PY + 28, "PLAYGROUND CONSTRAINT", 12, 800, T1, ls=1.2)
text(rx + 330, PY + 28, "DESIGN ADAPTATION", 12, 800, T1, ls=1.2)
cons = [
    ("No Azure role assignments", "repo-scoped ACR tokens + imagePullSecret (ADR-0007)"),
    ("One fixed resource group", "Terraform reads it as a data source"),
    ("3-hour session, then wiped", "scripted rebuild from Git doubles as the DR drill"),
    ("No inbound path to Jenkins", "SCM polling + SSH tunnel, no public admin UI"),
    ("2 small nodes, no Container Insights", "trimmed Prometheus stack, kind/k3d fallback"),
]
for i, (c1, c2) in enumerate(cons):
    yy = PY + 50 + i * 34
    a(f'<line x1="{rx + 20}" y1="{yy - 8}" x2="{rx + 890}" y2="{yy - 8}" stroke="{LINE}"/>')
    text(rx + 20, yy + 12, c1, 12.5, 600, T2)
    text(rx + 300, yy + 12, "→", 13, 700, C["rose"])
    text(rx + 330, yy + 12, c2, 12.5, 400, T1)
text(rx + 20, PY + PHH - 22, "Production equivalent: managed identity + AcrPull, GitHub webhooks via a private agent, private endpoints, Container Insights.",
     11.5, 400, T3)

# ---------------------------------------------------------------- roadmap strip
RY = 1232
text(40, RY + 20, "ROADMAP", 11.5, 800, T3, ls=1.2)
px = 120
for p in range(7):
    w = 26 + len(PHNAME[p]) * 6.6 + 28
    rect(px, RY + 4, w, 26, fill=PH[p], stroke=PH[p], r=13, op=0.10)
    a(f'<rect x="{px}" y="{RY + 4}" width="{w}" height="26" rx="13" fill="none" stroke="{PH[p]}" stroke-opacity="0.6"/>')
    text(px + 12, RY + 21.5, f"P{p}", 11.5, 800, PH[p])
    text(px + 38, RY + 21.5, PHNAME[p], 12, 500, T2)
    if p < 6:
        text(px + w + 9, RY + 22, "›", 15, 700, T3, "middle")
    px += w + 18
text(1880, RY + 21.5, "github.com/gunasekar89/enterprise-devops-pipeline", 12, 500, T3, "end", mono=True)

a("</svg>")
open(sys.argv[1], "w").write("\n".join(out))
