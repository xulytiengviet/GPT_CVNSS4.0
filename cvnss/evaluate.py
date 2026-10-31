"""Đánh giá GPT tiếng Việt riêng trên test.jsonl (không dùng bài kiểm tra tiếng Trung)."""
from __future__ import annotations

import argparse
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from cvnss.runtime import answer, load


def edit_distance(a: str, b: str) -> int:
    """Khoảng cách Levenshtein ký tự; không đánh đồng với BLEU hoặc độ đúng nghĩa."""
    prev = list(range(len(b) + 1))
    for i, char in enumerate(a, 1):
        curr = [i]
        for j, other in enumerate(b, 1):
            curr.append(min(curr[-1] + 1, prev[j] + 1, prev[j - 1] + (char != other)))
        prev = curr
    return prev[-1]


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).strip().split())


def evaluate(mode: str, limit: int | None = None, max_new_tokens: int = 64) -> dict:
    if mode not in ("unicode", "cvnss"):
        raise ValueError("mode phải là unicode hoặc cvnss.")
    model, tok, _, cfg = load(mode)
    path = Path(cfg["data"]["test_path"])
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        raise ValueError("Tập test rỗng.")
    results = []
    total_edits = 0
    total_chars = 0
    exact = 0
    for row in rows:
        prompt, target = row["prompt"], row["completion"]
        # Tập CVNSS đã được mã hóa; đưa trực tiếp vào mô hình để tránh mất thông tin
        # khi giải mã chuẩn tắc rồi mã hóa lại (không bảo đảm song ánh).
        result = answer(prompt, mode, max_new_tokens=max_new_tokens, encoded_input=(mode == "cvnss"))
        predicted = result["raw"]
        target_norm, pred_norm = normalize(target), normalize(predicted)
        ok = target_norm == pred_norm
        exact += int(ok)
        total_edits += edit_distance(target_norm, pred_norm)
        total_chars += len(target_norm)
        results.append({"prompt": prompt, "expected": target, "predicted": predicted,
                        "exact": ok})
    metrics = {
        "mode": mode,
        "source": str(path),
        "samples": len(rows),
        "exact_match": round(exact / len(rows), 6),
        "cer": round(total_edits / max(1, total_chars), 6),
        "model_parameters": sum(p.numel() for p in model.parameters()),
        "vocab_size": tok.vocab_size,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "note": "So khớp văn bản; không đồng nghĩa đúng kiến thức hoặc khả năng suy luận.",
        "results": results
    }
    output = Path(cfg["training"]["save_dir"]) / "metrics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đánh giá {mode}: {exact}/{len(rows)} câu khớp hoàn toàn; CER={metrics['cer']:.4f}")
    print(f"Đã lưu {output}")
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["unicode", "cvnss"], default="unicode")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-new-tokens", type=int, default=64)
    a = ap.parse_args()
    evaluate(a.mode, a.limit, a.max_new_tokens)


if __name__ == "__main__":
    main()
