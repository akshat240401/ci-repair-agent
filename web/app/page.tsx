"use client";

import { FormEvent, useMemo, useState } from "react";

type Event = {
  type: "progress" | "result" | "error";
  stage?: string;
  message?: string;
  data?: unknown;
  result?: RepairResult;
  sequence?: number;
  emitted_at?: string;
};

type RepairResult = {
  final_status: string;
  stopped_reason?: string;
  root_cause?: string;
  target_files?: string[];
  attempts?: unknown[];
  attempt_count?: number;
  files_modified?: number;
  syntax_passed?: boolean;
  targeted_test_passed?: boolean;
  full_suite_passed?: boolean;
  diff?: string;
  repaired_zip_b64?: string | null;
  latency_seconds?: number;
};

type Sample = {
  filename: string;
  targeted_test: string;
  failing_log: string;
  repository_zip_b64: string;
  title: string;
};

const stages = ["triage", "investigate", "plan", "patch", "verify", "done"];

export default function Home() {
  const [repo, setRepo] = useState<File | null>(null);
  const [log, setLog] = useState("");
  const [target, setTarget] = useState("");
  const [events, setEvents] = useState<Event[]>([]);
  const [result, setResult] = useState<RepairResult | null>(null);
  const [running, setRunning] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const reached = useMemo(() => new Set(events.map((e) => e.stage).filter(Boolean)), [events]);

  async function loadSample() {
    setError("");
    setLoadingSample(true);
    try {
      const response = await fetch(`${api}/api/sample/case-013`);
      if (!response.ok) throw new Error(`Could not load sample (HTTP ${response.status})`);
      const sample = (await response.json()) as Sample;
      const bytes = Uint8Array.from(atob(sample.repository_zip_b64), (c) => c.charCodeAt(0));
      const file = new File([bytes], sample.filename, { type: "application/zip" });
      setRepo(file);
      setTarget(sample.targeted_test);
      setLog(sample.failing_log);
      setEvents([]);
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load the sample case.");
    } finally {
      setLoadingSample(false);
    }
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!repo) return setError("Choose a repository ZIP first.");
    if (!target.trim()) return setError("Enter the targeted failing pytest node id.");
    if (!log.trim()) return setError("Paste the failing CI / pytest log.");
    setError("");
    setEvents([]);
    setResult(null);
    setExpanded(new Set());
    setRunning(true);

    const form = new FormData();
    form.set("repository", repo);
    form.set("failing_log", log);
    form.set("targeted_test", target);

    try {
      const response = await fetch(`${api}/api/repair/stream`, { method: "POST", body: form });
      if (!response.ok || !response.body) throw new Error(`Backend returned HTTP ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          const evt = JSON.parse(line) as Event;
          setEvents((prev) => [...prev, evt]);
          if (evt.type === "result" && evt.result) setResult(evt.result);
          if (evt.type === "error") setError(evt.message || "Repair failed.");
        }
        if (done) break;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setRunning(false);
    }
  }

  function toggleEvent(index: number) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function downloadRepaired() {
    if (!result?.repaired_zip_b64) return;
    const bytes = Uint8Array.from(atob(result.repaired_zip_b64), (c) => c.charCodeAt(0));
    const blob = new Blob([bytes], { type: "application/zip" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "verified-repair.zip";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main>
      <header className="nav">
        <div className="brand"><span className="mark">CI</span> Agentic Repair</div>
        <a href="https://github.com/akshat240401/ci-repair-agent" target="_blank">GitHub ↗</a>
      </header>

      <section className="hero">
        <div>
          <div className="eyebrow">AGENTIC CI FAILURE INVESTIGATOR</div>
          <h1>From failing CI logs to <span>verified repairs.</span></h1>
          <p>Upload a small Python repository, provide the failing pytest log, and let the agent investigate, repair, and prove the result.</p>
        </div>
        <div className="metric">
          <strong>86.7% → 100%</strong>
          <span>Verified Repair Rate on the frozen benchmark</span>
        </div>
      </section>

      <section className="workspace">
        <form className="panel inputPanel" onSubmit={submit}>
          <div className="panelHeader">
            <div className="panelTitle"><span>01</span> Repair input</div>
            <button className="sampleButton" type="button" disabled={running || loadingSample} onClick={loadSample}>
              {loadingSample ? "Loading…" : "Try sample case"}
            </button>
          </div>

          <label>Repository ZIP <small>Python 3.11 / pytest, max 5 MB</small></label>
          <div className="fileBox">
            <input id="repo" type="file" accept=".zip,application/zip" onChange={(e) => setRepo(e.target.files?.[0] || null)} />
            <label htmlFor="repo">
              <span>{repo ? repo.name : "Choose repository .zip"}</span>
              {repo && <small>{formatBytes(repo.size)}</small>}
            </label>
          </div>

          <label>Targeted failing test <small>pytest node id</small></label>
          <input value={target} onChange={(e) => setTarget(e.target.value)} placeholder="tests/test_api.py::test_payload_contract" />

          <label>Failing CI / pytest log</label>
          <textarea value={log} onChange={(e) => setLog(e.target.value)} placeholder="$ python -m pytest -q ...\nFAILED ..." rows={12} />

          <button disabled={running}>{running ? "Investigating…" : "Investigate & Repair"}</button>
          <p className="notice">Trusted-repository demo: uploaded code is executed by the verifier. Public arbitrary-code execution should use a dedicated sandbox worker.</p>
          {error && <div className="error">{error}</div>}
        </form>

        <div className="panel outputPanel">
          <div className="panelTitle"><span>02</span> Agent run</div>
          <div className="pipeline">
            {stages.map((stage) => (
              <div key={stage} className={`stage ${reached.has(stage) ? "active" : ""}`}>
                <i />
                <b>{stage === "investigate" ? "Investigate" : stage[0].toUpperCase() + stage.slice(1)}</b>
              </div>
            ))}
          </div>

          <div className="timeline">
            {events.filter((e) => e.type === "progress").map((e, i) => {
              const hasData = e.data !== undefined && e.data !== null;
              return (
                <div className="event" key={`${e.sequence ?? i}-${i}`}>
                  <div className="eventMeta">
                    <span>{e.stage}</span>
                    <time>{formatTime(e.emitted_at)}</time>
                  </div>
                  <div className="eventBody">
                    <p>{e.message}</p>
                    {hasData && (
                      <button type="button" className="detailButton" onClick={() => toggleEvent(i)}>
                        {expanded.has(i) ? "Hide details" : "View details"}
                      </button>
                    )}
                    {hasData && expanded.has(i) && <pre className="traceDetail">{JSON.stringify(e.data, null, 2)}</pre>}
                  </div>
                </div>
              );
            })}
            {!events.length && <div className="empty">Agent activity will appear here.</div>}
          </div>

          {result && (
            <div className="result">
              <div className={`status ${result.final_status === "VERIFIED_REPAIR" ? "verified" : "unresolved"}`}>
                {result.final_status}
              </div>
              {result.root_cause && <><h3>Root cause</h3><p>{result.root_cause}</p></>}
              {result.target_files && result.target_files.length > 0 && (
                <div className="fileChips">{result.target_files.map((file) => <span key={file}>{file}</span>)}</div>
              )}
              <div className="checks">
                <Check label="Syntax" ok={result.syntax_passed} />
                <Check label="Targeted test" ok={result.targeted_test_passed} />
                <Check label="Full suite" ok={result.full_suite_passed} />
              </div>
              <div className="stats">
                <span><b>{result.files_modified ?? 0}</b> files modified</span>
                <span><b>{result.attempt_count ?? 0}</b> attempts</span>
                <span><b>{result.latency_seconds?.toFixed(1) ?? "—"}s</b> runtime</span>
              </div>
              {result.diff && <><h3>Verified diff</h3><pre>{result.diff}</pre></>}
              {result.repaired_zip_b64 && <button className="secondary" onClick={downloadRepaired}>Download verified repair</button>}
            </div>
          )}
        </div>
      </section>

      <footer>Model judgment for ambiguity. Deterministic software for mechanics and proof.</footer>
    </main>
  );
}

function Check({ label, ok }: { label: string; ok?: boolean }) {
  return <div className={ok ? "check ok" : "check"}><span>{ok ? "✓" : "–"}</span>{label}</div>;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatTime(value?: string) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
