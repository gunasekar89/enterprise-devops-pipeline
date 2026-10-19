# LinkedIn Project Entry

Copy into LinkedIn → Profile → Add section → Projects. Update the "Status" line as phases complete; do not describe planned work as done.

**Title:** Enterprise DevOps Pipeline (Azure, Jenkins, DevSecOps, Kubernetes)

**Associated with:** Personal project / KodeKloud Azure labs

**Project URL:** https://github.com/gunasekar89/enterprise-devops-pipeline *(after publishing)*

**Description (Phase 0 version, about 1,300 characters):**

> Building a reproducible, end-to-end delivery pipeline for a Java 21 / Spring Boot service on Microsoft Azure, designed the way an enterprise platform team would: pipeline-as-code, security gates in every stage, immutable artifacts, GitOps deployment and SRE-grade observability.
>
> Delivered so far:
> • Spring Boot 4.1 REST API with health probes and Prometheus metrics, 12 automated tests across unit, web and integration layers
> • Declarative Jenkins pipeline (build, test reporting, fingerprinted artifacts, SCM polling for a private Jenkins behind an SSH tunnel), with security stages that fail loudly instead of faking success
> • Non-root, layered Docker image built from the CI-tested artifact
> • Baseline security scans: Gitleaks found no secrets; Trivy found 3 critical and 5 high CVEs in framework-managed dependencies, which I remediated and verified with a clean rescan
> • Jenkins on an Ubuntu 24.04 Azure VM in a restricted KodeKloud sandbox, working around policy limits on resource groups and disk SKUs
> • Architecture decision records, runbooks and a rebuild guide so anyone can reproduce the setup
>
> Next: SonarQube quality gates, SBOM and image signing, Terraform for ACR and AKS, Helm and Argo CD, Prometheus and Grafana alerting with incident runbooks.

**Skills:** Jenkins · CI/CD · DevSecOps · Docker · Microsoft Azure · Spring Boot · Maven · Trivy · Gitleaks · Site Reliability Engineering · Technical Documentation

## Post template (when publishing the repository)

> I'm building an end-to-end enterprise DevOps pipeline in public, one verified phase at a time. Phase 0 is done: a tested Spring Boot service, a Jenkins pipeline-as-code, a non-root container, and documentation good enough that anyone can rebuild it.
>
> Most useful lesson so far: even a brand-new project on the latest Spring Boot release had critical CVEs in its embedded Tomcat. Scan from day one.
>
> Repo: <link> · Next up: Jenkins on Azure with SonarQube and Trivy gates.
>
> #DevOps #Azure #Jenkins #DevSecOps #Kubernetes #SRE
