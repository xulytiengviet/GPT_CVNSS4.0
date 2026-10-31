"""CLI huấn luyện, đánh giá và suy luận tiếng Việt / CVNSS4.0."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
import yaml


def run(*arguments: str) -> None:
    subprocess.run([sys.executable, *arguments], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Phòng thí nghiệm GPT CVNSS4.0")
    ap.add_argument("action", choices=["prepare", "tokenizer", "train", "infer", "evaluate", "web", "web-local"])
    ap.add_argument("--mode", choices=["unicode", "cvnss"], default="unicode")
    ap.add_argument("--input", help="Đường dẫn JSONL nguồn Unicode")
    ap.add_argument("--prompt", default="Xin chào!")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    ap.add_argument("--max-steps", type=int, default=500)
    ap.add_argument("--vocab-size", type=int, default=2048)
    args = ap.parse_args()
    cfg_path = Path("cvnss") / f"config_{args.mode}.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))

    if args.action == "prepare":
        cmd = ["-m", "cvnss.prepare", "--mode", args.mode]
        if args.input:
            cmd += ["--input", args.input]
        run(*cmd)
    elif args.action == "tokenizer":
        run("-m", "cvnss.tokenizer", "--mode", args.mode, "--vocab-size", str(args.vocab_size))
    elif args.action == "train":
        if not Path(cfg["tokenizer"]["path"]).is_file():
            raise SystemExit("Chưa có tokenizer. Hãy chuẩn bị dữ liệu và huấn luyện tokenizer trước.")
        if args.max_steps < int(cfg["training"]["eval_interval"]):
            raise SystemExit("Số bước quá ít: max-steps phải >= eval_interval để ghi best.pt.")
        run("-m", "train.train", "--config", str(cfg_path), "--device", args.device,
            "--max_steps", str(args.max_steps), "--no-acceptance")
    elif args.action == "infer":
        # Dùng chung phương pháp chuyển đổi và prompt với giao diện Gradio.
        from cvnss.runtime import answer
        result = answer(args.prompt, args.mode)
        print("Câu hỏi:", args.prompt)
        print("Biểu diễn:", args.mode)
        print("Câu trả lời dạng mô hình:", result["raw"])
        if args.mode == "cvnss":
            print("Đọc ngược chữ Quốc ngữ (chuẩn tắc):", result["unicode"])
    elif args.action == "evaluate":
        run("-m", "cvnss.evaluate", "--mode", args.mode)
    elif args.action == "web":
        print("Giao diện tài liệu: http://127.0.0.1:7860/docs/")
        run("-m", "http.server", "7860")
    elif args.action == "web-local":
        run("-m", "cvnss.web_demo", "--mode", args.mode)


if __name__ == "__main__":
    main()
