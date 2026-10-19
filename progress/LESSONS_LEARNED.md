# Lessons Learned

Short, reusable lessons. Each says what happened, why it matters, and what to do next time.

| # | Lesson | Source |
|---|---|---|
| 1 | **Assume the playground forbids things a normal subscription allows.** Resource groups and Premium disks were refused. Design IaC to take the resource group as input and keep SKUs configurable. | Manual exercises, known-issues #1-2 |
| 2 | **Generate SSH keys locally; give the cloud only the public key.** Avoids lost one-time downloads and keeps the private key off third-party systems. | known-issues #3 |
| 3 | **Check the port before installing a service.** `sudo ss -ltnp 'sport = :8080'` takes one second and explains a failed start immediately. | known-issues #4 |
| 4 | **One user per workload.** Building the same project as `azureuser`, `jenkins` and `root` creates ownership problems. Let Jenkins build from Git in its own workspace. | known-issues #5 |
| 5 | **Anything not in Git is gone when the sandbox expires.** Record commands and results while working, not afterwards. | Manual exercises |
| 6 | **`JAVA_HOME` beats `PATH`.** Check the JDK the build tool will use, not the one your shell finds. Let the build enforce its own requirements (Maven Enforcer). | Phase 0, known-issues #7 |
| 7 | **"Latest framework version" does not mean "no known CVEs".** Scan even a brand-new project; Spring Boot 4.1.1 shipped with critical Tomcat CVEs at the time of the scan. | Phase 0, known-issues #8 |
| 8 | **A stage that cannot run must fail, not pass.** Opt-in stages call `require-tool.sh`; the unimplemented ACR stage errors out. Fake green builds destroy trust in CI. | Phase 0 |
| 9 | **Test the pipeline itself, not just the code.** Running the Jenkinsfile in Jenkinsfile Runner found the `JAVA_HOME` problem before it reached the VM. | Phase 0 |
