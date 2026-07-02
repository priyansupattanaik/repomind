"use client";

import { FormEvent, ReactNode, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock3, FileText, Loader2, Search } from "lucide-react";
import { Button } from "@/components/button";
import { Input } from "@/components/input";

type ScanReport = {
  repository: string;
  file_count: number;
  executive_summary: string;
  security_issues: Array<{ severity: string; file: string; line: number; title: string }>;
  dependency_issues: string[];
  architecture_review: string;
  business_intent: string;
  code_quality: string[];
  recommendations: string[];
  report_path: string;
  scan_duration_seconds?: number;
  timings?: {
    parse_seconds?: number;
    analysis_seconds?: number;
    index_seconds?: number;
    report_seconds?: number;
  };
};

const apiBase = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [report, setReport] = useState<ScanReport | null>(null);
  const [error, setError] = useState("");
  const [scanDuration, setScanDuration] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  async function runScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setReport(null);
    setScanDuration(null);
    setLoading(true);
    const startedAt = performance.now();

    try {
      const response = await fetch(`${apiBase}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(toFriendlyError(data.detail));
      }
      setReport(data);
      setScanDuration(data.scan_duration_seconds ?? (performance.now() - startedAt) / 1000);
    } catch (scanError) {
      setError(scanError instanceof Error ? toFriendlyError(scanError.message) : "Scan failed. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 py-8">
        <header className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal">RepoMind AI</h1>
            <p className="mt-1 text-sm text-subtle">Local repository intelligence for engineering reviews.</p>
          </div>
          <div className="text-sm text-subtle">FastAPI + Next.js</div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[420px_1fr]">
          <form onSubmit={runScan} className="flex flex-col gap-4 rounded-lg border border-border bg-white p-5 shadow-sm">
            <div>
              <label htmlFor="repo-url" className="text-sm font-medium">
                GitHub repository URL
              </label>
              <Input
                id="repo-url"
                value={repoUrl}
                onChange={(event) => setRepoUrl(event.target.value)}
                placeholder="https://github.com/owner/repo"
                required
                className="mt-2"
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Scan repository
            </Button>
            {loading ? (
              <div className="rounded-md border border-border bg-muted p-3 text-sm text-subtle" role="status">
                Cloning and analyzing repository. This can take a moment for larger projects.
              </div>
            ) : null}
            {error ? (
              <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">
                {error}
              </p>
            ) : null}
            {scanDuration !== null && report ? (
              <p className="flex items-center gap-2 text-sm text-subtle">
                <Clock3 className="h-4 w-4" />
                Completed in {formatSeconds(scanDuration)}.
              </p>
            ) : null}
          </form>

          <div className="rounded-lg border border-border bg-white p-5 shadow-sm">
            {!report ? (
              <div className="flex min-h-64 flex-col items-center justify-center gap-3 text-center text-subtle">
                <FileText className="h-8 w-8" />
                <p className="max-w-sm text-sm">Run a scan to see security, dependency, architecture, quality, and timing results.</p>
              </div>
            ) : (
              <ReportView report={report} />
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function ReportView({ report }: { report: ScanReport }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">Scan report</h2>
          <p className="mt-1 break-all text-sm text-subtle">{report.repository}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <div className="rounded-md border border-border px-3 py-2 text-sm">{report.file_count} files</div>
          {report.scan_duration_seconds !== undefined ? (
            <div className="rounded-md border border-border px-3 py-2 text-sm">
              {formatSeconds(report.scan_duration_seconds)}
            </div>
          ) : null}
        </div>
      </div>

      <p className="rounded-md bg-muted p-4 text-sm leading-6">{report.executive_summary}</p>

      <div className="grid gap-4 md:grid-cols-2">
        <Panel title="Security" icon={<AlertTriangle className="h-4 w-4" />}>
          {report.security_issues.length ? (
            report.security_issues.slice(0, 6).map((issue) => (
              <p key={`${issue.file}-${issue.line}-${issue.title}`} className="text-sm">
                {issue.severity.toUpperCase()} {issue.file}:{issue.line} - {issue.title}
              </p>
            ))
          ) : (
            <p className="text-sm text-subtle">No built-in rule findings.</p>
          )}
        </Panel>
        <Panel title="Dependencies" icon={<CheckCircle2 className="h-4 w-4" />}>
          {report.dependency_issues.map((issue) => (
            <p key={issue} className="text-sm">
              {issue}
            </p>
          ))}
        </Panel>
      </div>

      <Panel title="Architecture">
        <p className="text-sm leading-6">{report.architecture_review}</p>
      </Panel>
      <Panel title="Business Intent">
        <p className="text-sm leading-6">{report.business_intent}</p>
      </Panel>
      <Panel title="Recommendations">
        {report.recommendations.map((item) => (
          <p key={item} className="text-sm">
            {item}
          </p>
        ))}
      </Panel>
      <Panel title="Timings">
        <p className="text-sm">Parse: {formatSeconds(report.timings?.parse_seconds ?? 0)}</p>
        <p className="text-sm">Analysis: {formatSeconds(report.timings?.analysis_seconds ?? 0)}</p>
        <p className="text-sm">Index: {formatSeconds(report.timings?.index_seconds ?? 0)}</p>
        <p className="text-sm">Report: {formatSeconds(report.timings?.report_seconds ?? 0)}</p>
      </Panel>
      <p className="text-xs text-subtle">Report written to {report.report_path}</p>
    </div>
  );
}

function formatSeconds(value: number) {
  return `${value.toFixed(value >= 10 ? 1 : 2)}s`;
}

function toFriendlyError(message: string) {
  const normalized = message.toLowerCase();
  if (normalized.includes("failed to fetch")) {
    return "Backend is offline or unreachable. Start the FastAPI server and try again.";
  }
  if (normalized.includes("repository url")) {
    return message;
  }
  if (normalized.includes("not found") || normalized.includes("could not read from remote repository")) {
    return "Repository could not be cloned. Check that the URL is public and reachable.";
  }
  if (normalized.includes("git clone failed")) {
    return "Repository could not be cloned. Check the repository URL and network access.";
  }
  return message || "Scan failed. Check the repository URL and try again.";
}

function Panel({ title, icon, children }: { title: string; icon?: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-border p-4">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
        {icon}
        {title}
      </h3>
      <div className="flex flex-col gap-2">{children}</div>
    </section>
  );
}
