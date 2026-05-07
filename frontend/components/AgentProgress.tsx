"use client";
import { AGENTS, type AgentName, type AgentStatus } from "@/lib/events";

export interface AgentProgressProps {
  agentStates: Record<AgentName, AgentStatus>;
  elapsedSec: number;
  connectionWarning?: string | null;
}

export function AgentProgress({ agentStates, elapsedSec, connectionWarning }: AgentProgressProps) {
  return (
    <div className="card p-5">
      <div className="flex items-baseline justify-between mb-4">
        <span className="label-mono">running pipeline</span>
        <span className="font-mono text-[13px] text-[var(--muted)]">
          {formatElapsed(elapsedSec)}
        </span>
      </div>
      <ul className="space-y-2">
        {AGENTS.map((agent) => {
          const status = agentStates[agent];
          return (
            <li key={agent} className="flex items-center gap-3 font-mono text-[14px]">
              <span style={{ width: 16, display: "inline-block" }}>{glyph(status)}</span>
              <span
                style={{
                  color:
                    status === "running"
                      ? "var(--accent)"
                      : status === "done"
                      ? "var(--foreground)"
                      : "var(--muted)",
                }}
              >
                {agent}
              </span>
              {status === "running" && (
                <span className="text-[12px] text-[var(--muted)] ml-2">working…</span>
              )}
            </li>
          );
        })}
      </ul>
      {connectionWarning && (
        <p className="mt-4 text-[13px]" style={{ color: "var(--accent)" }}>
          ⚠ {connectionWarning}
        </p>
      )}
    </div>
  );
}

function glyph(s: AgentStatus): string {
  switch (s) {
    case "done":
      return "●";
    case "running":
      return "◐";
    default:
      return "○";
  }
}

function formatElapsed(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
