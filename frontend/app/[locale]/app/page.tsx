"use client";
/**
 * Outlier — main app page.
 *
 * Lives at /app (and also /ru/app, /pl/app — copy is intentionally
 * EN-only at this stage; locale only switches the surrounding chrome).
 *
 * State machine:
 *   idle → key_valid → uploaded → running → done | error | cancelled
 *
 * The Gemini api_key lives ONLY in React state. It is sent with each
 * backend call and never persisted to localStorage / sessionStorage / cookies.
 * Refreshing the page wipes the key — the user has to paste it again.
 *
 * `?run=<run_id>` query param survives refreshes for the run state itself
 * (file is on the server, report can be re-fetched). On mount we probe
 * /api/state to decide where to drop the user back into the flow.
 */

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Link } from "@/i18n/routing";
import { KeyInput, type KeyStatus } from "@/components/KeyInput";
import { FileUpload } from "@/components/FileUpload";
import { AgentProgress } from "@/components/AgentProgress";
import { ReportViewer } from "@/components/ReportViewer";
import {
  cancelRun,
  eventsUrl,
  fetchReport,
  getState,
  startRun,
  uploadFile,
  type RunStatus,
} from "@/lib/api";
import {
  AGENTS,
  type AgentName,
  type AgentStatus,
  type PipelineEvent,
} from "@/lib/events";

type Phase =
  | "idle"
  | "uploading"
  | "uploaded"
  | "running"
  | "done"
  | "error"
  | "cancelled";

const initialAgentStates: Record<AgentName, AgentStatus> = AGENTS.reduce(
  (acc, a) => ({ ...acc, [a]: "pending" }),
  {} as Record<AgentName, AgentStatus>,
);

function AppPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlRunId = searchParams.get("run");

  const [apiKey, setApiKey] = useState("");
  const [keyStatus, setKeyStatus] = useState<KeyStatus>("idle");

  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);

  const [runId, setRunId] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [agentStates, setAgentStates] = useState(initialAgentStates);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [connectionWarning, setConnectionWarning] = useState<string | null>(null);

  const startTimeRef = useRef<number | null>(null);
  const [elapsedSec, setElapsedSec] = useState(0);

  // Tick elapsed timer while running.
  useEffect(() => {
    if (phase !== "running" || startTimeRef.current === null) return;
    const id = setInterval(() => {
      setElapsedSec((Date.now() - (startTimeRef.current ?? Date.now())) / 1000);
    }, 250);
    return () => clearInterval(id);
  }, [phase]);

  // SSE attach: open EventSource whenever we move into "running" with a runId.
  // Reconnects via /api/state if connection drops mid-run.
  useEffect(() => {
    if (phase !== "running" || !runId) return;
    let closed = false;
    const es = new EventSource(eventsUrl(runId));

    const handle = (raw: string) => {
      try {
        const ev = JSON.parse(raw) as PipelineEvent;
        switch (ev.type) {
          case "pipeline.start":
            startTimeRef.current = Date.now();
            break;
          case "agent.start":
            setAgentStates((s) => ({ ...s, [ev.data.agent]: "running" }));
            break;
          case "agent.end":
            setAgentStates((s) => ({ ...s, [ev.data.agent]: "done" }));
            break;
          case "pipeline.end":
            setPhase("done");
            break;
          case "error":
            setPhase("error");
            setErrorMessage(ev.data.message || "Pipeline failed");
            break;
        }
      } catch {
        // ignore malformed events
      }
    };

    const types: PipelineEvent["type"][] = [
      "pipeline.start",
      "agent.start",
      "agent.end",
      "pipeline.end",
      "error",
    ];
    types.forEach((t) =>
      es.addEventListener(t, (e) => handle((e as MessageEvent).data)),
    );

    es.onerror = async () => {
      if (closed) return;
      // Connection dropped. Probe /api/state — if still running, signal a
      // soft warning to the user (the browser will auto-retry the SSE).
      // If the run has finished while we were disconnected, clean up.
      try {
        const s = await getState(runId);
        if (!s) return;
        if (s.status === "done") {
          es.close();
          setPhase("done");
        } else if (s.status === "error") {
          es.close();
          setPhase("error");
          setErrorMessage(s.error || "Pipeline failed");
        } else {
          setConnectionWarning("connection issue, retrying…");
        }
      } catch {
        setConnectionWarning("connection issue, retrying…");
      }
    };

    es.onopen = () => setConnectionWarning(null);

    return () => {
      closed = true;
      es.close();
    };
  }, [phase, runId]);

  // Fetch report when we move to "done".
  useEffect(() => {
    if (phase !== "done" || !runId || reportHtml) return;
    fetchReport(runId)
      .then(setReportHtml)
      .catch((e) => setErrorMessage(e instanceof Error ? e.message : String(e)));
  }, [phase, runId, reportHtml]);

  // Refresh recovery: if URL has ?run=, probe /api/state on mount.
  useEffect(() => {
    if (!urlRunId) return;
    let cancelled = false;
    (async () => {
      try {
        const s = await getState(urlRunId);
        if (cancelled || !s) return;
        setRunId(urlRunId);
        if (s.status === "running" || s.status === "queued") {
          startTimeRef.current = Date.now();
          setPhase("running");
          // SSE will be opened by the [phase, runId] effect above.
        } else if (s.status === "done") {
          setPhase("done");
        } else if (s.status === "error") {
          setPhase("error");
          setErrorMessage(s.error || "Pipeline failed earlier");
        } else if (s.status === "cancelled") {
          setPhase("cancelled");
        }
      } catch {
        // run not found or network issue — ignore, user can start fresh
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [urlRunId]);

  const handleKeyChange = useCallback(
    (key: string, status: KeyStatus, message?: string) => {
      setApiKey(key);
      setKeyStatus(status);
      if (status === "valid") setErrorMessage(null);
      else if (message) setErrorMessage(message);
    },
    [],
  );

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setPhase("uploading");
    setFileError(null);
    setErrorMessage(null);
    try {
      const r = await uploadFile(file);
      setRunId(r.run_id);
      setPhase("uploaded");
      router.replace(`/app?run=${r.run_id}`);
    } catch (e) {
      setPhase("idle");
      setFileError(e instanceof Error ? e.message : String(e));
    }
  }, [file, router]);

  const handleRun = useCallback(async () => {
    if (!runId || !apiKey) return;
    setPhase("running");
    setAgentStates(initialAgentStates);
    setErrorMessage(null);
    setReportHtml(null);
    startTimeRef.current = Date.now();
    setElapsedSec(0);
    try {
      await startRun(runId, apiKey);
    } catch (e) {
      setPhase("error");
      setErrorMessage(e instanceof Error ? e.message : String(e));
    }
  }, [runId, apiKey]);

  const handleCancel = useCallback(async () => {
    if (!runId) return;
    try {
      await cancelRun(runId);
      setPhase("cancelled");
    } catch {
      // best-effort, ignore
    }
  }, [runId]);

  const handleReset = useCallback(() => {
    setFile(null);
    setRunId(null);
    setPhase("idle");
    setAgentStates(initialAgentStates);
    setErrorMessage(null);
    setReportHtml(null);
    startTimeRef.current = null;
    setElapsedSec(0);
    setConnectionWarning(null);
    router.replace("/app");
  }, [router]);

  const canUpload = keyStatus === "valid" || keyStatus === "rate_limited";
  const canRun = phase === "uploaded" && !!runId && !!apiKey;

  return (
    <main className="min-h-screen px-[6vw] py-12 max-w-5xl mx-auto w-full">
      <header className="mb-10 flex items-baseline justify-between">
        <Link href="/" className="font-mono text-[11px] uppercase tracking-[0.15em] text-[var(--muted)] hover:text-[var(--foreground)]">
          ← outlier
        </Link>
        {runId && (
          <span className="font-mono text-[11px] uppercase tracking-[0.15em] text-[var(--muted)]">
            run · {runId.slice(0, 8)}
          </span>
        )}
      </header>

      <h1 className="font-medium leading-[1.2] mb-10" style={{ fontSize: "clamp(28px, 4vw, 40px)" }}>
        Run analysis
      </h1>

      <div className="space-y-5">
        <KeyInput status={keyStatus} onChange={handleKeyChange} />

        <div data-disabled={!canUpload}>
          <FileUpload
            disabled={!canUpload || phase === "running"}
            selected={file}
            onSelect={(f, err) => {
              setFile(f);
              setFileError(err ?? null);
              if (f) setPhase("idle");
            }}
          />
          {fileError && (
            <p className="mt-2 text-[13px]" style={{ color: "var(--error)" }}>
              {fileError}
            </p>
          )}
          {file && phase === "idle" && (
            <button
              type="button"
              className="btn-ghost mt-3"
              onClick={handleUpload}
              disabled={!canUpload}
            >
              Upload to backend
            </button>
          )}
          {phase === "uploading" && (
            <p className="mt-2 text-[13px] text-[var(--muted)]">Uploading…</p>
          )}
        </div>

        {phase === "uploaded" && (
          <div className="card p-5 flex items-center justify-between">
            <div>
              <p className="label-mono mb-1">step 3 · run pipeline</p>
              <p className="text-[14px] text-[var(--muted)]">
                Five agents · ~50 seconds on a paid Gemini tier · longer on free tier.
              </p>
            </div>
            <button type="button" className="btn-accent" onClick={handleRun} disabled={!canRun}>
              Run analysis
            </button>
          </div>
        )}

        {(phase === "running" || phase === "done" || phase === "error" || phase === "cancelled") && (
          <AgentProgress
            agentStates={agentStates}
            elapsedSec={elapsedSec}
            connectionWarning={connectionWarning}
          />
        )}

        {phase === "running" && (
          <button type="button" className="btn-ghost" onClick={handleCancel}>
            Cancel
          </button>
        )}

        {phase === "done" && reportHtml && runId && (
          <ReportViewer runId={runId} html={reportHtml} elapsedSec={elapsedSec} />
        )}

        {phase === "error" && (
          <div className="card p-5">
            <p className="label-mono mb-2" style={{ color: "var(--error)" }}>error</p>
            <p className="text-[14px]">{errorMessage || "Something went wrong."}</p>
            <button type="button" className="btn-ghost mt-4" onClick={handleReset}>
              Start over
            </button>
          </div>
        )}

        {phase === "cancelled" && (
          <div className="card p-5">
            <p className="label-mono mb-2" style={{ color: "var(--accent)" }}>cancelled</p>
            <p className="text-[14px] text-[var(--muted)]">
              Cancellation is best-effort — if the pipeline is mid-LLM-call, it may still finish.
            </p>
            <button type="button" className="btn-ghost mt-4" onClick={handleReset}>
              Start over
            </button>
          </div>
        )}

        {phase === "done" && (
          <button type="button" className="btn-ghost" onClick={handleReset}>
            Run another file
          </button>
        )}
      </div>
    </main>
  );
}

export default function AppPage() {
  return (
    <Suspense fallback={null}>
      <AppPageInner />
    </Suspense>
  );
}
