# log-anomaly-detector

> **Server or application logs → AI anomaly detection.** Brute force attacks, error spikes, data exfiltration patterns, latency regressions — with detection rules to block them.

[![PyPI](https://img.shields.io/pypi/v/log-anomaly-detector?style=flat)](https://pypi.org/project/log-anomaly-detector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install log-anomaly-detector
python -m log_anomaly_detector access.log --type nginx
python -m log_anomaly_detector auth.log --type auth --json
tail -n 5000 /var/log/nginx/access.log | python -m log_anomaly_detector -
```

Detects: brute force · credential stuffing · SQL injection · path traversal ·
data exfiltration · error spikes · latency degradation · unauthorized access

Outputs: detection rules (nginx/iptables/WAF), suspicious IPs to block,
immediate actions, IOC summary
