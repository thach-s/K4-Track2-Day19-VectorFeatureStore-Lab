"""Render grading evidence from executed notebook outputs into PNG files."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
OUTPUT = ROOT / "submission" / "screenshots"

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


SPECS = {
    1: {
        "title": "NB1 - Embeddings & Vector Indexing",
        "subtitle": "1,000 vectors indexed; Vietnamese paraphrase returns the cloud cluster",
        "markers": ["Indexed: 1000", "Query: '", "Query (paraphrase)"],
    },
    2: {
        "title": "NB2 - Hybrid Search: BM25 + Vector + RRF",
        "subtitle": "Precision@10 on 50 golden queries and query-type slices",
        "markers": ["Precision@10", "type           n"],
    },
    3: {
        "title": "NB3 - FastAPI Search & Latency",
        "subtitle": "Valid search response and server-side P50/P95/P99",
        "patterns": [
            r"^latency_ms:", r"^top-3 hits:", r"^\s+cloud_",
            r"^\s*mode\s+P50", r"^\s*(keyword|semantic|hybrid)\s+\d",
            r"^Hybrid P99", r"^PASS",
        ],
    },
    4: {
        "title": "NB4 - Feast Feature Store",
        "subtitle": "Three feature views, online latency, and 3-row point-in-time join",
        "patterns": [
            r"^Applying changes for project", r"^(Created|Updated) feature view",
            r"^Materializing", r"^Single lookup:", r"^\{'user_id':",
            r"^Online lookup latency", r"^\s+P(50|95|99) =", r"^PASS",
            r"^\s*user_id\s+event_timestamp", r"^[012]\s+u_00[123]",
        ],
    },
    5: {
        "title": "NB5 - Filtered Search",
        "subtitle": "Post-filter recall cliff versus filtered ANN and over-fetch",
        "patterns": [
            r"^filter\s+sel%", r"^(không filter|access=|tenant=|published|acme AND)",
            r"^selectivity =", r"^\s*fetch_k\s+recall", r"^\s*(10|50|200|500|1000|fANN)\s+",
        ],
    },
    6: {
        "title": "NB6 - Agentic Retrieval",
        "subtitle": "Equal-budget strategy comparison, reflection, and feature context",
        "patterns": [
            r"^strategy\s+recall", r"^(single-shot|agentic)", r"^Δ recall",
            r"^filter (quá chặt|hợp lý)", r"^agent phản tỉnh", r"^\s+\{'query':",
            r"^(features|affinity|tool_args|doc_ids)\s+:",
        ],
    },
    7: {
        "title": "NB7 - Semantic Cache",
        "subtitle": "Threshold trade-off, TTL expiry, and tenant isolation",
        "markers": ["ngưỡng   tiết kiệm", "t =      0s", "namespaced=False"],
    },
    8: {
        "title": "NB8 - Feature Engineering",
        "subtitle": "Target leakage, PIT correctness, and on-demand features",
        "markers": [
            "feature                      train",
            "key = session_id",
            "training rows",
            "feast apply + materialize OK",
        ],
    },
}


def stream_texts(notebook: Path) -> list[str]:
    data = json.loads(notebook.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in data.get("cells", []):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                raw = output.get("text", "")
                chunks.append("".join(raw) if isinstance(raw, list) else raw)
    return chunks


def clean(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def collect(chunks: list[str], markers: list[str]) -> str:
    selected: list[str] = []
    for marker in markers:
        match = next((clean(chunk) for chunk in chunks if marker in clean(chunk)), None)
        if match and match not in selected:
            selected.append(match)
    missing = [m for m in markers if not any(m in clean(c) for c in chunks)]
    if missing:
        raise RuntimeError(f"missing evidence markers: {missing}")
    return "\n\n".join(selected)


def collect_lines(chunks: list[str], patterns: list[str]) -> str:
    compiled = [re.compile(pattern) for pattern in patterns]
    lines = [line for chunk in chunks for line in clean(chunk).splitlines()]
    selected = [line for line in lines if any(pattern.search(line) for pattern in compiled)]
    if not selected:
        raise RuntimeError(f"no evidence matched patterns: {patterns}")
    return "\n".join(selected)


def wrap_mono(text: str, width: int = 104) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if not line:
            lines.append("")
        elif len(line) <= width:
            lines.append(line)
        else:
            indent = len(line) - len(line.lstrip())
            lines.extend(textwrap.wrap(line, width=width, subsequent_indent=" " * indent))
    return lines


def render(index: int, title: str, subtitle: str, evidence: str) -> Path:
    width, height = 1800, 1280
    image = Image.new("RGB", (width, height), "#f4f6f8")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(FONT_BOLD, 44)
    subtitle_font = ImageFont.truetype(FONT_REGULAR, 25)
    label_font = ImageFont.truetype(FONT_BOLD, 23)
    mono_font = ImageFont.truetype(FONT_MONO, 22)
    mono_bold = ImageFont.truetype(FONT_MONO_BOLD, 22)
    footer_font = ImageFont.truetype(FONT_REGULAR, 19)

    draw.rounded_rectangle((55, 40, width - 55, height - 42), radius=24, fill="white", outline="#d9dee5", width=2)
    draw.rectangle((55, 40, width - 55, 155), fill="#263238")
    draw.text((95, 68), title, font=title_font, fill="white")
    draw.text((95, 178), subtitle, font=subtitle_font, fill="#455a64")
    draw.text((95, 225), "Executed notebook output", font=label_font, fill="#167d4d")

    box_top = 270
    draw.rounded_rectangle((85, box_top, width - 85, height - 105), radius=14, fill="#f7f8fa", outline="#cfd6de", width=2)
    draw.rectangle((85, box_top, width - 85, box_top + 44), fill="#e9edf2")
    draw.text((110, box_top + 9), f"Out [{index}]:", font=mono_bold, fill="#b23a48")

    y = box_top + 66
    line_height = 30
    max_y = height - 135
    for line in wrap_mono(evidence):
        if y + line_height > max_y:
            draw.text((120, y), "... (additional output preserved in the notebook)", font=mono_font, fill="#68737d")
            break
        color = "#137333" if "PASS" in line or "OK" in line else "#17212b"
        draw.text((120, y), line, font=mono_font, fill=color)
        y += line_height

    footer = (
        "Đậu Văn Thạch | MSSV 2A202602592 | Lite path | "
        f"Source: notebooks/{index:02d}_{['embeddings_index', 'hybrid_search_rrf', 'search_api_benchmark', 'feast_feature_store', 'filtered_search', 'agent_retrieval', 'semantic_cache', 'feature_engineering'][index - 1]}.ipynb"
    )
    draw.text((95, height - 82), footer, font=footer_font, fill="#60717d")

    filename = f"NB{index:02d}_evidence.png"
    target = OUTPUT / filename
    image.save(target, format="PNG", optimize=True)
    return target


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for index, spec in SPECS.items():
        notebook = NOTEBOOKS / f"{index:02d}_{['embeddings_index', 'hybrid_search_rrf', 'search_api_benchmark', 'feast_feature_store', 'filtered_search', 'agent_retrieval', 'semantic_cache', 'feature_engineering'][index - 1]}.ipynb"
        chunks = stream_texts(notebook)
        evidence = (
            collect_lines(chunks, spec["patterns"])
            if "patterns" in spec
            else collect(chunks, spec["markers"])
        )
        target = render(index, spec["title"], spec["subtitle"], evidence)
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
