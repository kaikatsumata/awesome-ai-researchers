#!/usr/bin/env python3
"""Check researcher homepage / scholar / DBLP links.

The script intentionally skips Google Scholar URLs because automated checks are
often blocked and the result is not a reliable signal for link rot.
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
from collections import Counter
import datetime as dt
import json
import os
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "researchers.json")
REPORT = os.path.join(ROOT, "docs", "link-check-report.md")

FIELDS = ("homepage", "scholar", "dblp")
MAX_WORKERS = 16
TIMEOUT = 10
USER_AGENT = (
    "awesome-ai-researchers-link-check/1.0 "
    "(https://github.com/; contact via repository issues)"
)


@dataclasses.dataclass(frozen=True)
class Link:
    researcher: str
    kind: str
    url: str


@dataclasses.dataclass(frozen=True)
class Result:
    link: Link
    outcome: str
    status: str
    status_code: int | None = None
    reason: str = ""


def load_rows() -> list[dict]:
    with open(DATA, encoding="utf-8") as f:
        rows = json.load(f)
    if isinstance(rows, dict) and "researchers" in rows:
        rows = rows["researchers"]
    if not isinstance(rows, list):
        raise ValueError("data/researchers.json must be a list or contain researchers")
    return rows


def iter_links(rows: list[dict]) -> list[Link]:
    links: list[Link] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "(unknown)").strip() or "(unknown)"
        for kind in FIELDS:
            value = row.get(kind)
            if isinstance(value, str) and value.strip():
                links.append(Link(name, kind, value.strip()))
    return links


def is_google_scholar(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.netloc or "").lower()
    return host == "scholar.google.com" or host.endswith(".scholar.google.com")


def validate_url(link: Link) -> Result | None:
    parsed = urllib.parse.urlparse(link.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return Result(link, "dead", "不正なURL", reason="invalid-url")
    return None


def request_once(url: str, method: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        return int(response.getcode() or 0), response.geturl()


def format_error(exc: BaseException) -> tuple[int | None, str, str]:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code, f"HTTP {exc.code}", "http-error"
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", exc)
        # DNS解決失敗(ドメイン消滅)はリンク切れとみなす。それ以外の接続不可は一時的/bot対策の可能性。
        if isinstance(reason, socket.gaierror) or any(
            k in str(reason) for k in ("Name or service not known", "nodename nor servname", "getaddrinfo")
        ):
            return None, f"DNS解決失敗: {reason}", "dns"
        return None, f"接続不可: {reason}", "url-error"
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return None, "接続不可: timeout", "timeout"
    return None, f"接続不可: {type(exc).__name__}: {exc}", "error"


# 「壊れている可能性が高い」とみなすHTTPステータス(恒久的). 403/429/5xx等はbot対策・一時的の可能性が高く手動確認に回す。
BROKEN_HTTP = {404, 410}


def check_link(link: Link) -> Result:
    invalid = validate_url(link)
    if invalid:
        return invalid

    if is_google_scholar(link.url):
        return Result(
            link,
            "manual",
            "要手動確認: Google Scholarは自動判定をスキップ",
            reason="google-scholar",
        )

    last_error: tuple[int | None, str, str] | None = None
    for method in ("HEAD", "GET"):
        try:
            status_code, _final_url = request_once(link.url, method)
            if status_code in BROKEN_HTTP:
                return Result(link, "dead", f"HTTP {status_code}", status_code, "http-error")
            if 400 <= status_code <= 599:
                # 403/429/5xx等: bot対策・一時的の可能性 → 手動確認
                return Result(link, "manual", f"要手動確認: HTTP {status_code}", status_code, "http-other")
            return Result(link, "alive", f"HTTP {status_code}", status_code)
        except Exception as exc:  # noqa: BLE001 - retain precise network failure in report
            last_error = format_error(exc)

    status_code, status, reason = last_error or (None, "接続不可", "error")
    # 恒久的に壊れていると判断できるのは 404/410 と DNS解決失敗のみ。
    if reason == "dns" or status_code in BROKEN_HTTP:
        return Result(link, "dead", status, status_code, reason)
    # それ以外(timeout/接続リセット/SSL/403/429/5xx)は環境・bot対策・一時障害の可能性 → 手動確認
    return Result(link, "manual", f"要手動確認: {status}", status_code, reason)


def md_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def shorten(value: str, limit: int = 180) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def render_report(rows: list[dict], links: list[Link], results: list[Result]) -> str:
    checked_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    dead = sorted(
        (r for r in results if r.outcome == "dead"),
        key=lambda r: (r.link.researcher.lower(), r.link.kind, r.link.url),
    )
    manual = [r for r in results if r.outcome == "manual"]
    alive_count = sum(1 for r in results if r.outcome == "alive")

    lines: list[str] = []
    lines.append("# Link Check Report")
    lines.append("")
    lines.append(f"- チェック日(UTC): {checked_at}")
    lines.append(f"- 研究者数: {len(rows)}")
    lines.append(f"- 総URL数: {len(links)}")
    lines.append(f"- 自動チェック成功数: {alive_count}")
    lines.append(f"- 壊れている可能性が高いリンク数 (HTTP 404/410・DNS解決失敗): {len(dead)}")
    lines.append(f"- 要手動確認/スキップ数 (403/429/5xx・タイムアウト・SSL・接続リセット・Google Scholar等): {len(manual)}")
    lines.append("")
    lines.append("> 注: 403/429/タイムアウト/SSL/接続リセットは、サイト側のbot対策・一時的な障害・チェッカー環境(証明書/レート制限)に起因することが多く、リンク切れとは限りません。**恒久的に壊れていると判断できる 404/410 と DNS解決失敗のみ**を「壊れている可能性が高い」に分類しています。")
    lines.append("")
    lines.append("## 壊れている可能性が高いリンク (要修正候補)")
    lines.append("")
    if dead:
        lines.append("| 研究者 | 種別 | URL | ステータス |")
        lines.append("|:--|:--|:--|:--|")
        for result in dead:
            lines.append(
                "| {name} | {kind} | <{url}> | {status} |".format(
                    name=md_escape(result.link.researcher),
                    kind=md_escape(result.link.kind),
                    url=result.link.url.replace(">", "%3E"),
                    status=md_escape(shorten(result.status)),
                )
            )
    else:
        lines.append("404/410・DNS解決失敗のリンクは検出されませんでした。")
    lines.append("")
    lines.append("## 要手動確認/スキップ")
    lines.append("")
    reason_label = {
        "google-scholar": "Google Scholar (bot対策が強いため自動判定対象外)",
        "http-other": "HTTP 403/429/5xx (bot対策・一時的の可能性)",
        "timeout": "タイムアウト (一時的・低速サーバの可能性)",
        "url-error": "接続不可/SSL証明書 (一時的・チェッカー環境の可能性)",
        "error": "その他の接続エラー",
    }
    counts = Counter(r.reason or "error" for r in manual)
    lines.append("| 理由 | 件数 |")
    lines.append("|:--|--:|")
    for reason, n in counts.most_common():
        lines.append(f"| {reason_label.get(reason, reason)} | {n} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    rows = load_rows()
    links = iter_links(rows)
    results: list[Result] = []

    manual_results = [check_link(link) for link in links if is_google_scholar(link.url)]
    checked_links = [link for link in links if not is_google_scholar(link.url)]
    results.extend(manual_results)

    total_to_check = len(checked_links)
    if total_to_check:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_link, link): link for link in checked_links}
            for completed, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                results.append(future.result())
                if completed % 100 == 0 or completed == total_to_check:
                    print(
                        f"checked {completed}/{total_to_check} "
                        f"(skipped/manual {len(manual_results)})",
                        file=sys.stderr,
                    )

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(render_report(rows, links, results))

    dead_count = sum(1 for result in results if result.outcome == "dead")
    manual_count = sum(1 for result in results if result.outcome == "manual")
    print(
        f"総URL数: {len(links)} / 死亡リンク数: {dead_count} / "
        f"要手動確認・スキップ数: {manual_count}"
    )
    print(f"Report: {os.path.relpath(REPORT, ROOT)}")
    return 1 if dead_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
