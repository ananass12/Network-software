#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


ROOT = Path(__file__).resolve().parents[2]
WEEK16 = ROOT / "weeks" / "week-16"
SERVICE_DIR = WEEK16 / "Service"


@dataclass(frozen=True)
class CheckResult:
    id: str
    title: str
    ok: bool
    details: str = ""


def _load_variant_project_code() -> Optional[str]:
    variants_dir = ROOT / "variants"
    if not variants_dir.exists():
        return None
    candidates = list(variants_dir.glob("**/week-16.json"))
    if not candidates:
        return None
    data = json.loads(candidates[0].read_text(encoding="utf-8"))
    return data.get("project_code")


def _load_app(disable_docs: bool) -> object:
    """
    Load FastAPI app from Service/main.py without requiring it to be importable as a package.
    """
    main_py = SERVICE_DIR / "main.py"
    if not main_py.exists():
        raise RuntimeError(f"Not found: {main_py}")

    # Ensure imports like `from schemas import ...` resolve.
    sys.path.insert(0, str(SERVICE_DIR))
    try:
        if disable_docs:
            os.environ["INVENTORY_DISABLE_DOCS"] = "1"
        else:
            os.environ.pop("INVENTORY_DISABLE_DOCS", None)

        import importlib.util

        spec = importlib.util.spec_from_file_location("week16_service_main", str(main_py))
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to create module spec for main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[assignment]
        app = getattr(module, "app", None)
        if app is None:
            raise RuntimeError("main.py does not expose `app`")
        return app
    finally:
        # Best-effort cleanup. Keep sys.path stable for subsequent checks.
        if sys.path and sys.path[0] == str(SERVICE_DIR):
            sys.path.pop(0)

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _static_file_exists() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(
        CheckResult(
            id="DOC-1",
            title="checklist.md exists",
            ok=(WEEK16 / "checklist.md").exists(),
            details=str(WEEK16 / "checklist.md"),
        )
    )
    results.append(
        CheckResult(
            id="DOC-2",
            title="audit.md exists",
            ok=(WEEK16 / "audit.md").exists(),
            details=str(WEEK16 / "audit.md"),
        )
    )

    code = _load_variant_project_code()
    if code:
        text = (WEEK16 / "audit.md").read_text(encoding="utf-8") if (WEEK16 / "audit.md").exists() else ""
        results.append(
            CheckResult(
                id="DOC-3",
                title="audit.md contains project_code",
                ok=(code in text),
                details=f"expected: {code}",
            )
        )
    else:
        results.append(
            CheckResult(
                id="DOC-3",
                title="audit.md contains project_code",
                ok=False,
                details="variant week-16.json not found",
            )
        )
    return results


def _static_requirements_pinned() -> CheckResult:
    req = SERVICE_DIR / "requirements.txt"
    if not req.exists():
        return CheckResult(id="A06-1", title="requirements are pinned (==)", ok=False, details="requirements.txt missing")
    lines = [ln.strip() for ln in req.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    unpinned = [ln for ln in lines if "==" not in ln]
    return CheckResult(
        id="A06-1",
        title="requirements are pinned (==)",
        ok=(len(unpinned) == 0),
        details=("unpinned: " + ", ".join(unpinned)) if unpinned else "ok",
    )


def _static_docker_non_root() -> CheckResult:
    dockerfile = SERVICE_DIR / "Dockerfile"
    if not dockerfile.exists():
        return CheckResult(id="A08-1", title="Docker runs as non-root (USER ...)", ok=False, details="Dockerfile missing")
    text = dockerfile.read_text(encoding="utf-8")
    ok = bool(re.search(r"(?mi)^\s*USER\s+\S+", text)) and ("USER appuser" in text)
    return CheckResult(id="A08-1", title="Docker runs as non-root (USER appuser)", ok=ok, details="USER appuser expected")


def _static_authz_protection() -> list[CheckResult]:
    main_py = SERVICE_DIR / "main.py"
    text = _read_text(main_py) if main_py.exists() else ""

    def has_depends_on(endpoint_def: str) -> bool:
        # rough but effective for this educational project
        return endpoint_def in text and "Depends(require_api_key)" in text[text.find(endpoint_def) : text.find(endpoint_def) + 300]

    res: list[CheckResult] = []
    res.append(
        CheckResult(
            id="A01-1",
            title="POST /products protected by API key",
            ok=has_depends_on("async def create_product"),
            details="expects Depends(require_api_key)",
        )
    )
    res.append(
        CheckResult(
            id="A01-2",
            title="PUT /products/{id} protected by API key",
            ok=has_depends_on("async def update_product"),
            details="expects Depends(require_api_key)",
        )
    )
    res.append(
        CheckResult(
            id="A01-3",
            title="DELETE /products/{id} protected by API key",
            ok=has_depends_on("async def delete_product"),
            details="expects Depends(require_api_key)",
        )
    )
    res.append(
        CheckResult(
            id="A01-4",
            title="GET /products/{id} protected by API key (IDOR mitigation)",
            ok=has_depends_on("async def get_product"),
            details="expects Depends(require_api_key)",
        )
    )

    res.append(
        CheckResult(
            id="A07-1",
            title="API key verified with secrets.compare_digest",
            ok=("secrets.compare_digest" in text),
            details="constant-time compare",
        )
    )
    res.append(
        CheckResult(
            id="A07-2",
            title="API key loaded from environment (no hardcode)",
            ok=("INVENTORY_API_KEY" in text and "os.getenv" in text),
            details="INVENTORY_API_KEY env var",
        )
    )
    return res


def _static_validation_rules() -> list[CheckResult]:
    schemas_py = SERVICE_DIR / "schemas.py"
    text = _read_text(schemas_py) if schemas_py.exists() else ""

    checks = [
        ("A03-1", "Name has length limits", bool(re.search(r"name:\s*str\s*=\s*Field\([^)]*min_length\s*=\s*1[^)]*max_length\s*=\s*80", text))),
        ("A03-2", "Description has max_length", "description:" in text and "max_length=500" in text),
        ("A03-3", "Quantity has bounds (ge/le)", "quantity:" in text and "ge=0" in text and "le=" in text),
        ("A03-4", "Quality is allowlisted (Literal/enum)", "Quality = Literal[" in text),
        ("A03-5", "Pattern used for text fields", "SAFE_TEXT_PATTERN" in text and "pattern=SAFE_TEXT_PATTERN" in text),
        ("A03-6", "Whitespace is stripped (str_strip_whitespace)", "str_strip_whitespace=True" in text),
    ]
    return [CheckResult(id=i, title=t, ok=ok, details="schemas.py") for i, t, ok in checks]


def _static_limits_and_dos() -> list[CheckResult]:
    main_py = SERVICE_DIR / "main.py"
    text = _read_text(main_py) if main_py.exists() else ""

    checks = [
        ("A04-1", "Max body size configured via env", "INVENTORY_MAX_BODY_BYTES" in text and "MAX_BODY_BYTES" in text),
        ("A04-2", "Body size enforced when Content-Length present", "content-length" in text and "Request body too large" in text and "413" in text),
        ("A04-3", "Body size enforced even when Content-Length missing", "await request.body()" in text),
        ("A04-4", "Rate limit configured via env", "INVENTORY_RATE_LIMIT_WINDOW_S" in text and "INVENTORY_RATE_LIMIT_MAX_REQUESTS" in text),
        ("A04-5", "Rate limit returns 429", "429" in text and "Too Many Requests" in text),
    ]
    return [CheckResult(id=i, title=t, ok=ok, details="main.py") for i, t, ok in checks]


def _static_security_headers_and_config() -> list[CheckResult]:
    main_py = SERVICE_DIR / "main.py"
    text = _read_text(main_py) if main_py.exists() else ""

    headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Content-Security-Policy",
        "Cache-Control",
        "X-Request-Id",
    ]
    missing = [h for h in headers if h not in text]
    res: list[CheckResult] = []
    res.append(
        CheckResult(
            id="A05-1",
            title="Security headers set",
            ok=(len(missing) == 0),
            details=("missing: " + ", ".join(missing)) if missing else "ok",
        )
    )
    res.append(
        CheckResult(
            id="A05-2",
            title="CORS origins are allowlisted (not '*')",
            ok=("INVENTORY_CORS_ORIGINS" in text and "allow_origins=cors_origins" in text and "allow_origins=[\"*\"]" not in text),
            details="main.py",
        )
    )
    res.append(
        CheckResult(
            id="A05-3",
            title="Docs/OpenAPI can be disabled via env",
            ok=("INVENTORY_DISABLE_DOCS" in text and "docs_url=None" in text and "openapi_url=None" in text),
            details="INVENTORY_DISABLE_DOCS",
        )
    )
    res.append(
        CheckResult(
            id="A09-1",
            title="Request logging present (A09)",
            ok=("logger.info" in text and "request_id" in text),
            details="request_id logging",
        )
    )
    return res


def run_checks() -> list[CheckResult]:
    checks: list[Callable[[], list[CheckResult] | CheckResult]] = [
        _static_file_exists,
        _static_requirements_pinned,
        _static_docker_non_root,
        _static_authz_protection,
        _static_validation_rules,
        _static_limits_and_dos,
        _static_security_headers_and_config,
    ]

    results: list[CheckResult] = []
    for fn in checks:
        try:
            r = fn()
            if isinstance(r, list):
                results.extend(r)
            else:
                results.append(r)
        except Exception as e:  # noqa: BLE001
            results.append(CheckResult(id="ERR", title=getattr(fn, "__name__", "check"), ok=False, details=str(e)))
    return results


def main() -> int:
    results = run_checks()
    passed = sum(1 for r in results if r.ok)
    total = len(results)

    print(f"Security checklist checks: {passed}/{total} passed")
    for r in results:
        status = "OK" if r.ok else "FAIL"
        details = f" — {r.details}" if r.details else ""
        print(f"[{status}] {r.id} {r.title}{details}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

