#!/usr/bin/env python3
"""
log-anomaly-detector — server/application logs → AI flags unusual patterns
Detects: failed auth spikes, error rate changes, unusual request patterns,
data exfiltration signals, performance regressions, infrastructure issues
"""
import anthropic, json, re, sys
from pathlib import Path
from datetime import datetime

SYSTEM = """You are a senior security analyst and SRE with deep expertise in log analysis.
Analyze these logs for anomalies, security events, and operational issues.

Focus on:
1. Security threats (brute force, credential stuffing, injection attempts, data exfiltration)
2. Operational anomalies (error spikes, latency degradation, resource exhaustion)
3. Application issues (crashes, memory leaks, dependency failures)
4. Compliance concerns (unauthorized access attempts, policy violations)

Return ONLY valid JSON — no markdown, no explanation.

{
  "log_source": "nginx|apache|application|auth|syslog|cloudtrail|kubernetes|mixed|unknown",
  "log_period": {
    "start": "YYYY-MM-DD HH:MM:SS or null",
    "end": "YYYY-MM-DD HH:MM:SS or null",
    "duration": "string or null"
  },
  "total_events_analyzed": number,
  "overall_risk": "normal|elevated|high|critical",
  "anomalies": [
    {
      "id": "ANOMALY-001",
      "type": "brute_force|credential_stuffing|sql_injection|xss|path_traversal|data_exfiltration|error_spike|latency_spike|resource_exhaustion|unauthorized_access|config_error|crash|other",
      "severity": "critical|high|medium|low|info",
      "confidence": "high|medium|low",
      "title": "short descriptive title",
      "description": "what happened and why it's suspicious",
      "first_seen": "timestamp or null",
      "last_seen": "timestamp or null",
      "event_count": number_or_null,
      "affected_ips": ["list of IPs involved"],
      "affected_endpoints": ["list of URLs/endpoints affected"],
      "affected_users": ["list of usernames if visible — anonymize if needed"],
      "pattern": "description of the pattern that triggered this",
      "evidence": ["specific log lines that show the anomaly (redact sensitive data)"],
      "recommended_action": "string",
      "ioc": {
        "ips": ["malicious IPs"],
        "user_agents": ["suspicious UAs"],
        "patterns": ["regex or string patterns to block"]
      }
    }
  ],
  "statistics": {
    "error_rate_pct": number_or_null,
    "top_error_codes": [{"code":"string","count":number}],
    "top_source_ips": [{"ip":"string","requests":number,"suspicious":true}],
    "peak_requests_per_minute": number_or_null,
    "avg_response_time_ms": number_or_null,
    "p99_response_time_ms": number_or_null
  },
  "timeline": [
    {"timestamp":"string","event":"key event description","severity":"string"}
  ],
  "baseline_deviations": ["metrics that deviated significantly from normal"],
  "false_positive_notes": ["reasons why flagged events might be legitimate"],
  "recommended_rules": [
    {
      "rule": "detection rule description",
      "format": "nginx|iptables|waf|siem|cloudwatch",
      "rule_text": "actual rule or regex"
    }
  ],
  "immediate_actions": ["actions to take right now"],
  "confidence": 0.0
}"""

def analyze(log_text: str, log_type: str = "auto") -> dict:
    client = anthropic.Anthropic()
    if len(log_text) > 40000:
        lines = log_text.split("\n")
        # Keep first and last portions
        half = 15000
        sample = "\n".join(lines[:200]) + "\n...[middle truncated]...\n" + "\n".join(lines[-200:])
        log_text = sample[:40000]

    prompt = f"Log type: {log_type}\n\nAnalyze these logs for anomalies:\n\n{log_text}"
    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=4096, system=SYSTEM,
        messages=[{"role":"user","content":prompt}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

def analyze_file(path: str, log_type: str = "auto") -> dict:
    return analyze(Path(path).read_text(encoding="utf-8",errors="replace"), log_type)

RISK_C = {"normal":"\033[92m","elevated":"\033[93m","high":"\033[91m","critical":"\033[91m"}
SEV_ICON = {"critical":"🚨","high":"🔴","medium":"🟠","low":"🔵","info":"⚪"}
R = "\033[0m"

def print_report(r: dict):
    risk = r.get("overall_risk","normal")
    anomalies = r.get("anomalies",[])
    stats = r.get("statistics",{})
    period = r.get("log_period",{})

    print(f"\n{'═'*60}")
    print(f"  LOG ANOMALY DETECTOR — {r.get('log_source','?').upper()}")
    print(f"  Risk: {RISK_C.get(risk,'')}{risk.upper()}{R}")
    if period.get("start"): print(f"  Period: {period['start']} → {period.get('end','?')}")
    print(f"  Events analyzed: {r.get('total_events_analyzed',0):,}")
    print(f"{'═'*60}")

    if anomalies:
        sorted_a = sorted(anomalies, key=lambda x: ["critical","high","medium","low","info"].index(x.get("severity","info")))
        print(f"\n  ANOMALIES DETECTED ({len(anomalies)})")
        for a in sorted_a:
            conf_bar = {"high":"●●●","medium":"●●○","low":"●○○"}.get(a.get("confidence","low"),"○○○")
            print(f"\n  {SEV_ICON.get(a.get('severity','info'),'')} [{a.get('id','')}] {a.get('title','')}")
            print(f"     {a.get('description','')}")
            print(f"     Confidence: {conf_bar} | Events: {a.get('event_count','?')}")
            if a.get("affected_ips"): print(f"     IPs: {', '.join(a['affected_ips'][:4])}")
            if a.get("affected_endpoints"): print(f"     Endpoints: {', '.join(a['affected_endpoints'][:3])}")
            evidence = a.get("evidence",[])
            if evidence: print(f"     Evidence: {evidence[0][:100]}")
            print(f"     Action: {a.get('recommended_action','')}")

            rules = a.get("ioc",{}).get("patterns",[])
            if rules:
                print(f"     Block pattern: {rules[0][:60]}")

    if stats.get("error_rate_pct") is not None:
        print(f"\n  STATS")
        print(f"  Error rate: {stats.get('error_rate_pct',0):.1f}%")
        if stats.get("avg_response_time_ms"): print(f"  Avg response: {stats.get('avg_response_time_ms','?')}ms | P99: {stats.get('p99_response_time_ms','?')}ms")
        top_errors = stats.get("top_error_codes",[])
        if top_errors:
            print(f"  Top errors: {', '.join(f\"{e.get('code','?')}({e.get('count',0)})\" for e in top_errors[:5])}")
        suspect_ips = [ip for ip in stats.get("top_source_ips",[]) if ip.get("suspicious")]
        if suspect_ips:
            print(f"  Suspicious IPs: {', '.join(ip.get('ip','?') for ip in suspect_ips[:4])}")

    rules = r.get("recommended_rules",[])
    if rules:
        print(f"\n  RECOMMENDED DETECTION RULES")
        for rule in rules[:3]:
            print(f"  [{rule.get('format','').upper()}] {rule.get('rule','')}")
            if rule.get("rule_text"): print(f"     {rule['rule_text'][:80]}")

    immediate = r.get("immediate_actions",[])
    if immediate:
        print(f"\n  IMMEDIATE ACTIONS")
        for action in immediate: print(f"  ⚡ {action}")

    fp_notes = r.get("false_positive_notes",[])
    if fp_notes: print(f"\n  Note: {fp_notes[0]}")
    print(f"\n  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Detect anomalies in server and application logs")
    p.add_argument("source", help="Log file path or '-' for stdin")
    p.add_argument("--type","-t",default="auto",help="Log type: nginx|apache|auth|syslog|application|kubernetes")
    p.add_argument("--json",action="store_true")
    a = p.parse_args()
    src = sys.stdin.read() if a.source=="-" else a.source
    r = analyze_file(src, a.type) if Path(src).exists() else analyze(src, a.type)
    if a.json: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_report(r)
