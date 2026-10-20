import sys
W, H = 1880, 1160
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'DejaVu Sans Mono', Consolas, monospace"

PH = {  # phase: (fill, label)
    0: ("#64748B", "Foundation"),
    1: ("#2563EB", "GitHub + Jenkins on Azure"),
    2: ("#DC2626", "DevSecOps gates + container"),
    3: ("#7C3AED", "Terraform, ACR, signing"),
    4: ("#0D9488", "AKS, Helm, Argo CD"),
    5: ("#D97706", "Prometheus + Grafana, SLOs"),
    6: ("#16A34A", "Resilience + DR drills"),
}

out = []
def a(s): out.append(s)

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, t, size=14, weight=400, fill="#0F172A", anchor="start", mono=False, italic=False):
    st = ' font-style="italic"' if italic else ""
    a(f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" font-size="{size}" '
      f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}>{esc(t)}</text>')

def rect(x, y, w, h, fill="#FFFFFF", stroke="#CBD5E1", sw=1.5, r=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def badge(x, y, p):
    c = PH[p][0]
    rect(x, y, 30, 18, fill=c, stroke=c, sw=0, r=9)
    text(x + 15, y + 13, f"P{p}", 11, 700, "#FFFFFF", "middle")

def step(x, y, n):
    a(f'<circle cx="{x}" cy="{y}" r="12" fill="#0F172A"/>')
    text(x, y + 4.5, str(n), 12, 700, "#FFFFFF", "middle")

def arrow(pts, color="#334155", dash=None, sw=2):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x},{y}" for x, y in pts)
    a(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
      f'stroke-linejoin="round" marker-end="url(#ah)"/>')

def chip(x, y, w, title, sub, p, live=False):
    h = 62
    rect(x, y, w, h, fill="#FFFFFF", stroke=PH[p][0], sw=1.6, r=8)
    a(f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2" fill="{PH[p][0]}"/>')
    text(x + 14, y + 25, title, 14, 600)
    text(x + 14, y + 46, sub, 12, 400, "#475569")
    badge(x + w - 38, y + 8, p)
    if live:
        a(f'<circle cx="{x + w - 14}" cy="{y + h - 13}" r="5" fill="#16A34A"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<title>Enterprise DevOps Pipeline target architecture</title>')
a('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
  'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#334155"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#F8FAFC"/>')

# Header
text(40, 58, "Enterprise DevOps Pipeline: target architecture", 30, 700)
text(40, 88, "Java 21 / Spring Boot service delivered by CI, DevSecOps gates and GitOps onto AKS, rebuilt from Git in each 3-hour KodeKloud Azure playground session",
     15, 400, "#475569")

# ---------- Left column: workstation + GitHub ----------
rect(40, 150, 270, 200, fill="#FFFFFF", stroke="#94A3B8")
text(60, 180, "Engineer workstation", 17, 700)
for i, t in enumerate(["git commit, push, open PR", "Browser on localhost:8080", "ssh -L 8080:localhost:8080", "kubectl / argocd CLI", "Terraform plan / apply"]):
    text(60, 210 + i * 26, "• " + t, 13, 400, "#334155")

rect(40, 420, 270, 290, fill="#FFFFFF", stroke=PH[1][0], sw=2)
text(60, 450, "GitHub", 17, 700)
badge(266, 434, 1)
text(60, 474, "enterprise-devops-pipeline", 12, 400, "#475569", mono=True)
for i, t in enumerate(["main protected: PR + Jenkins check", "application/ · ci/Jenkinsfile", "infrastructure/ (Terraform)", "kubernetes/helm/ chart", "Dependabot, CODEOWNERS"]):
    text(60, 502 + i * 24, "• " + t, 13, 400, "#334155")
rect(56, 626, 238, 66, fill="#F0FDFA", stroke=PH[4][0], r=8)
text(70, 651, "gitops/ path", 14, 700, "#0F766E")
text(70, 673, "Helm values: image tag per env", 12, 400, "#0F766E")

# step 1: dev -> GitHub
arrow([(175, 350), (175, 418)])
step(197, 384, 1)
text(215, 389, "push / PR", 12, 600, "#334155")

# ---------- Azure boundary ----------
a('<g transform="translate(80,0)">')
BX, BY, BW, BH = 380, 120, 1390, 820
rect(BX, BY, BW, BH, fill="#EFF6FF", stroke="#2563EB", sw=2, r=16, dash="10 6")
text(BX + 22, BY + 32, "Azure subscription · KodeKloud playground", 18, 700, "#1D4ED8")
text(BX + 22, BY + 54, "One existing resource group (ODL-azure-…) read as a Terraform data source · no role assignments", 13, 400, "#1E40AF")
rect(BX + BW - 380, BY + 16, 360, 46, fill="#FFFFFF", stroke=PH[3][0], r=8)
badge(BX + BW - 368, BY + 30, 3)
text(BX + BW - 328, BY + 37, "Terraform provisions VNet, NSG, VM,", 12.5, 600, "#5B21B6")
text(BX + BW - 328, BY + 54, "ACR, Key Vault, AKS · local state per session", 12.5, 400, "#5B21B6")

# Jenkins VM
JX, JY, JW, JH = 410, 200, 930, 300
rect(JX, JY, JW, JH, fill="#FFFFFF", stroke=PH[1][0], sw=2, r=12)
text(JX + 20, JY + 30, "vm-jenkins-lab · Jenkins CI", 17, 700)
text(JX + 262, JY + 30, "Standard_D2s_v3 · StandardSSD disk · private, reached only through the SSH tunnel", 12.5, 400, "#475569")
badge(JX + JW - 44, JY + 14, 1)

cw1, gap1 = 166, 14
row1 = [("Checkout", "poll SCM, clone", 0, True), ("Maven build", "compile, unit tests", 0, True),
        ("JaCoCo + JUnit", "coverage, reports", 0, True), ("SonarQube", "quality gate", 2, False),
        ("Gitleaks", "secret scan", 2, False)]
x0 = JX + 20
y1 = JY + 52
for i, (t, s, p, live) in enumerate(row1):
    x = x0 + i * (cw1 + gap1)
    chip(x, y1, cw1, t, s, p, live)
    if i < len(row1) - 1:
        arrow([(x + cw1 + 1, y1 + 31), (x + cw1 + gap1 - 1, y1 + 31)], sw=1.5)
# wrap arrow row1 -> row2
lastx = x0 + 4 * (cw1 + gap1) + cw1 / 2
row2 = [("Docker build", "image tag = Git SHA", 2), ("Trivy", "deps + image scan", 2),
        ("Syft", "SBOM (SPDX)", 2), ("Cosign", "sign image digest", 3),
        ("Push to ACR", "by digest", 3)]
y2 = y1 + 106
arrow([(lastx, y1 + 63), (lastx, y1 + 82), (x0 + cw1 / 2, y1 + 82), (x0 + cw1 / 2, y2 - 1)], sw=1.5)
for i, (t, s, p) in enumerate(row2):
    x = x0 + i * (cw1 + gap1)
    chip(x, y2, cw1, t, s, p)
    if i < len(row2) - 1:
        arrow([(x + cw1 + 1, y2 + 31), (x + cw1 + gap1 - 1, y2 + 31)], sw=1.5)
y3 = y2 + 80
text(JX + 20, y3 + 8, "On the same VM: SonarQube container on localhost (heap capped ~2 GB), Docker engine. Credentials only via Jenkins Credentials bindings.", 12, 400, "#475569")
a(f'<circle cx="{JX + 20}" cy="{y3 + 32}" r="5" fill="#16A34A"/>')
text(JX + 32, y3 + 37, "runs in Jenkins today (Phase 0). Every other stage is planned and gets evidence in its phase.", 12, 400, "#166534")


# Right column: Key Vault + ACR
RX, RW = 1370, 380
rect(RX, 200, RW, 104, fill="#FFFFFF", stroke=PH[3][0], sw=2, r=12)
text(RX + 20, 230, "Azure Key Vault", 17, 700)
badge(RX + RW - 44, 214, 3)
text(RX + 20, 256, "Standard, access-policy mode", 13, 400, "#334155")
text(RX + 20, 278, "Cosign key as a secret, read by the Cosign stage", 13, 400, "#334155")

rect(RX, 330, RW, 170, fill="#FFFFFF", stroke=PH[3][0], sw=2, r=12)
text(RX + 20, 360, "Azure Container Registry", 17, 700)
badge(RX + RW - 44, 344, 3)
text(RX + 20, 386, "Standard SKU · enterprise-devops-app", 13, 400, "#334155")
text(RX + 20, 410, "image@sha256 + Cosign signature + SBOM", 13, 400, "#334155")
text(RX + 20, 438, "Scoped ACR tokens instead of AcrPush/AcrPull:", 12.5, 600, "#5B21B6")
text(RX + 20, 460, "push token → Jenkins Credentials", 12.5, 400, "#5B21B6")
text(RX + 20, 480, "pull-only token → K8s imagePullSecret", 12.5, 400, "#5B21B6")

# Cosign <-> KV
cos_x = x0 + 3 * (cw1 + gap1) + cw1 / 2
arrow([(RX - 2, 252), (1355, 252), (1355, 346), (cos_x, 346), (cos_x, y2 - 2)], color="#7C3AED", dash="5 4", sw=1.6)
# push -> ACR
push_x = x0 + 4 * (cw1 + gap1) + cw1
arrow([(push_x + 2, y2 + 31), (RX - 2, y2 + 31)])
step(1355, y2 + 56, 3)


# ---------- AKS ----------
KX, KY, KW, KH = 410, 560, 1340, 350
rect(KX, KY, KW, KH, fill="#FFFFFF", stroke=PH[4][0], sw=2, r=12)
text(KX + 20, KY + 30, "AKS cluster", 17, 700)
text(KX + 134, KY + 30, "1 system node pool · 2 × Standard_D2s_v3 · default networking · monitoring add-ons off · same chart runs on kind/k3d", 12.5, 400, "#475569")
badge(KX + KW - 44, KY + 14, 4)

NY, NH = KY + 50, 280
def ns(x, w, name, color, p):
    rect(x, NY, w, NH, fill="#F8FAFC", stroke=color, sw=1.4, r=10, dash="4 3")
    text(x + 14, NY + 24, f"namespace: {name}", 13, 700, color, mono=False)
    badge(x + w - 40, NY + 10, p)

def card(x, y, w, h, title, lines, color):
    rect(x, y, w, h, fill="#FFFFFF", stroke=color, sw=1.4, r=8)
    text(x + 12, y + 22, title, 14, 700)
    for i, t in enumerate(lines):
        text(x + 12, y + 44 + i * 19, t, 12, 400, "#475569")

# argocd
ns(430, 300, "argocd", "#0F766E", 4)
card(446, NY + 40, 268, 150, "Argo CD", ["watches gitops/ in GitHub", "dev: auto-sync on main", "prod: promoted by pull request", "drift detection, self-heal", "rollback = git revert / history"], "#0D9488")
card(446, NY + 202, 268, 64, "Helm chart", ["enterprise-devops-app, values per env"], "#0D9488")
# dev
ns(760, 290, "dev", "#0F766E", 4)
card(776, NY + 40, 258, 172, "enterprise-devops-app", ["Deployment, rolling update", "probes: /actuator/health/", "  liveness · readiness", "runAsNonRoot, read-only FS", "requests and limits set", "imagePullSecret: acr-pull"], "#0D9488")
card(776, NY + 222, 258, 44, "Service · ClusterIP :8080", [], "#0D9488")
# prod
ns(1080, 260, "prod", "#0F766E", 4)
card(1096, NY + 40, 228, 130, "enterprise-devops-app", ["same chart, prod values", "manual approval via PR", "post-deploy smoke test", "graceful shutdown 20 s"], "#0D9488")
card(1096, NY + 182, 228, 84, "Service", ["a separate cluster in a", "real enterprise"], "#0D9488")
# monitoring
ns(1370, 360, "monitoring", "#B45309", 5)
card(1386, NY + 40, 328, 74, "Prometheus", ["ServiceMonitor scrapes /actuator/prometheus", "trimmed kube-prometheus-stack"], "#D97706")
card(1386, NY + 124, 328, 66, "Grafana", ["RED + JVM dashboards, SLO and error budget"], "#D97706")
card(1386, NY + 200, 328, 66, "Alertmanager", ["error rate, latency, restarts → runbook, RCA"], "#D97706")

# argo -> dev, argo -> prod
arrow([(716, NY + 90), (774, NY + 90)], color="#0D9488")
step(745, NY + 72, 6)
arrow([(580, NY + 267), (580, NY + 290), (1210, NY + 290), (1210, NY + 268)], color="#0D9488", dash="6 4")
rect(830, NY + 281, 170, 18, fill="#FFFFFF", stroke="#FFFFFF", sw=0, r=4)
text(915, NY + 294, "promotion to prod by PR", 11.5, 600, "#0F766E", "middle")
# ACR -> AKS pull
arrow([(1440, 502), (1440, 530), (905, 530), (905, NY + 38)], color="#7C3AED")
arrow([(1250, 530), (1250, NY + 38)], color="#7C3AED")
step(1462, 530, 7)
text(1480, 535, "kubelet pulls image@digest with pull-only token", 11.5, 600, "#5B21B6")
# prometheus scrape
arrow([(1384, NY + 78), (1326, NY + 78)], color="#D97706")
step(1355, NY + 110, 8)
text(1386, NY + 296, "Prometheus scrapes dev and prod", 11.5, 600, "#B45309")

a("</g>")
# crossing arrows (canvas coordinates, right side shifted by 80)
arrow([(312, 260), (488, 260)], color="#475569", dash="6 4")
text(330, 250, "SSH tunnel", 11.5, 600, "#475569")
text(330, 280, "port 22 only", 11.5, 400, "#475569")
arrow([(312, 450), (488, 450)])
step(338, 432, 2)
text(356, 437, "poll + clone", 11.5, 600, "#334155")
text(320, 470, "outbound HTTPS", 11, 400, "#475569")
arrow([(488, 480), (420, 480), (420, 655), (312, 655)], color="#0D9488")
step(420, 560, 4)
text(330, 600, "bump", 11.5, 600, "#0F766E")
text(330, 615, "image tag", 11.5, 600, "#0F766E")
arrow([(296, 692), (296, 740), (508, 740)], color="#0D9488")
step(400, 740, 5)
text(318, 766, "Argo CD pulls", 11.5, 600, "#0F766E")
text(318, 781, "desired state", 11.5, 600, "#0F766E")

# ---------- Bottom: phases legend + DR ----------
LY = 970
text(40, LY, "Build phases", 16, 700)
pw, pg = 248, 12
for i in range(7):
    x = 40 + i * (pw + pg)
    rect(x, LY + 14, pw, 56, fill="#FFFFFF", stroke=PH[i][0], sw=1.5, r=8)
    badge(x + 12, LY + 33, i)
    text(x + 52, LY + 47, PH[i][1], 13, 600)
rect(40, LY + 86, 1808, 84, fill="#F0FDF4", stroke=PH[6][0], sw=1.5, r=10)
badge(56, LY + 103, 6)
text(98, LY + 117, "Resilience and DR: every playground session is wiped after 3 hours, so each session is a full rebuild from this repository.", 14, 600, "#14532D")
text(98, LY + 141, "Terraform recreates Azure, JCasC and job definitions in Git restore Jenkins, Argo CD resyncs the apps. Rebuild time is recorded as the RTO; chaos drills end in RCAs.", 13, 400, "#166534")
text(98, LY + 160, "Numbered arrows: 1 push · 2 poll + CI · 3 push signed image · 4 bump tag in Git · 5 Argo CD pulls · 6 sync · 7 pull image · 8 scrape metrics", 12, 400, "#475569")

a("</svg>")
open(sys.argv[1], "w").write("\n".join(out))
