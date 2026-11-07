# Hardware and always-on execution

## What machine must run continuously?

### Takeaway
An always-on, internet-connected mini PC can coordinate scheduled work while the MacBook is off. Jobs that require the Ryzen workstation must wait while that workstation is powered off, unless an independently configured and tested wake mechanism brings it online.

### Cited Findings
- n8n’s current Docker Compose guide, including its AI-code sandbox stack, lists 4 GB RAM and 2 vCPUs as its minimum, with Docker Engine and Compose v2; on Windows the guide requires WSL. These are for that setup, not a guarantee for heavy video or multiple jobs. [n8n Compose setup](https://docs.n8n.io/deploy/host-n8n/install-options/install-using-docker-compose/)
- Docker Desktop for Windows lists 8 GB RAM and BIOS/UEFI virtualization among prerequisites, plus supported Windows/WSL versions. [Docker requirements](https://docs.docker.com/desktop/setup/install/windows-install/)
- Docker Engine and Compose can run on Linux; n8n uses a persisted data volume for credentials and workflows. [n8n Docker installation](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-docker/)
- The 3060 Ti has 8 GB VRAM and NVIDIA encoder hardware. [NVIDIA specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3060-3060ti/)
- FFmpeg supports NVIDIA hardware encoding, but available options depend on the GPU, driver, and FFmpeg build; NVENC accelerates encoding rather than providing unlimited local generation. [FFmpeg NVENC](https://ffmpeg.org/ffmpeg-all.html)

### Inferences
- Recommend a modest Linux mini-PC with 8 GB RAM, SSD and 2+ cores as a practical choice, not as a formal universal requirement. 4 GB may suffice for light n8n workloads, but retain headroom and measure before buying. 120 GB SSD is a convenience, not a documented minimum.
- 5800X/16GB/3060Ti workstation can reasonably serve as FFmpeg worker and for some local AI experiments, but GPU video model compatibility, speed, resolution, and concurrent desktop performance must be benchmarked for the exact model and OS. 8 GB VRAM is a real constraint and no quality or turnaround guarantee can be made.
- Do not add a second n8n instance, Redis, Postgres, complex wake-on-LAN, and remote GPU protocol as mandatory for a pilot. A single coordinator and a dedicated bounded job worker that checks in, retrieves jobs, and reports state is a smaller initial architecture. The specific integration must be built and tested.

### Gaps
- Actual make, OS, RAM, storage, electricity and cost of the user's prospective always-on device, workstation operating system, network, and workload are unknown. Wake-on-LAN requires hardware, sleep settings, network support, and testing.

## How should the systems communicate and recover?

### Takeaway
Use an authenticated private connection and durable job state; do not assume the coordinator or desktop is always healthy. Back up data and encryption material, and reconcile uncertain post submissions before retrying.

### Cited Findings
- n8n's queue mode has a main process, Redis broker and worker instances. Persistent binary data on local filesystem is not supported in queue mode; the documentation points to external object storage for persisted binaries. SQLite isn't recommended for queue mode. Encryption key must be shared by the main and worker instances. [n8n queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode/)
- n8n identifies TLS, security policies, restriction of public API/nodes and security auditing as measures for self-hosted instances. [n8n security](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/)
- Tailscale says most deployments do not need inbound firewall ports and may fall back to encrypted relays when direct connectivity fails. [Tailscale firewall ports](https://tailscale.com/docs/reference/faq/firewall-ports)
- n8n's data directory stores important settings such as encryption keys even with PostgreSQL. [n8n Docker data persistence](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-docker/)

### Inferences
- Keep server UI private on home network or authenticated VPN, avoid exposing an unauthenticated admin dashboard, use least-privilege credentials, protect the database and key, back up both and test restoration. Credentials are not stored in the public media repo.
- Reliable automatic posting requires unique job IDs, deduplication, retries with limits, polling provider status, timestamps, alerting and durable media retention. If the workstation is off, the pipeline must queue work or use a separately costed cloud path; cloud video does not become free because the server is local.
- Existing Codex/Buffer/GitHub connections on the Mac do not automatically migrate to n8n on a different machine. They need separate approved service credentials and a verified publishing path.

### Gaps
- Exact runtime setup and log retention remain design decisions; no end-to-end autonomous production has been demonstrated on the second server.

## How much electricity does an always-on server use?

### Takeaway
Actual electricity costs depend on power at the wall, time, and marginal utility charges; device wattage is not known until measured. Use estimates only as scenarios.

### Cited Findings
- EPCOR lists Edmonton's residential Rate of Last Resort energy charge as 12.01 Canadian cents/kWh through 2026, with daily administrative charges; delivery charges and other fees may also apply. The user's actual contract may differ. [EPCOR Edmonton rates](https://www.epcor.com/ca/en/ab/edmonton/start-services/home/compare-electricity-rates/rate-of-last-resort.html)

### Inferences
- Assuming 30 days on 24/7, 10 W average draws 7.2 kWh/month; 30 W draws 21.6 kWh/month. At the illustrative 12.01 cents/kWh energy-only rate, those amount to approximately CAD $0.86 and $2.59, respectively, excluding incremental variable delivery, taxes, and any other applicable charges. These are not measured device figures or the user's all-in electricity cost. Use a plug-in meter and their utility bill to obtain a real estimate.

### Gaps
- No actual wall-power measurement, local plan, tariff allocation or device has been confirmed; realistic standby/active power is unknown.
