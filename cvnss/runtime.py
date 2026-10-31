"""Tiện ích suy luận thống nhất cho CLI và Gradio, không giả lập checkpoint."""
from __future__ import annotations
import json
import subprocess
from functools import lru_cache
from pathlib import Path
import yaml


@lru_cache(maxsize=2)
def load(mode: str):
    from core.infer import load_model_and_tokenizer
    cfg = yaml.safe_load(Path(f"cvnss/config_{mode}.yml").read_text(encoding="utf-8"))
    ckpt = Path(cfg["training"]["save_dir"]) / "best.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"Chưa có {ckpt}. Hãy huấn luyện trước.")
    model, tok, _, device = load_model_and_tokenizer(str(ckpt))
    return model, tok, device, cfg


def convert(text: str, direction: str) -> str:
    path = str((Path(__file__).resolve().parent / "vendor" / "converter.js").resolve())
    program = (
        'const c=require(process.argv[1]);'
        'const v=require("node:fs").readFileSync(0,"utf8");'
        'process.stdout.write((process.argv[2]=="encode"?c.fromCqn(v).cvss:c.fromCvss(v).cqn));'
    )
    proc = subprocess.run(["node", "-e", program, path, direction],
                          input=text, text=True, encoding="utf-8", capture_output=True, check=True)
    return proc.stdout


def answer(question: str, mode: str, max_new_tokens: int = 64, temperature: float = 0.0, encoded_input: bool = False) -> dict[str, str]:
    if mode not in ("unicode", "cvnss"):
        raise ValueError("Chế độ không hợp lệ.")
    if not question.strip():
        raise ValueError("Vui lòng nhập câu hỏi.")
    from core.infer import generate
    model, tok, device, cfg = load(mode)
    prompt = convert(question.strip(), "encode") if mode == "cvnss" and not encoded_input else question.strip()
    user_prefix = cfg["data"]["user_prefix"]
    assistant_prefix = cfg["data"]["assistant_prefix"]
    context = user_prefix + prompt + "\n" + assistant_prefix
    output = generate(model, tok, context, temperature=temperature,
                      max_new_tokens=max_new_tokens, wrap_prompt=False,
                      stop_strings=["\n" + user_prefix, "\n" + assistant_prefix],
                      device=device)
    return {"raw": output, "unicode": convert(output, "decode") if mode == "cvnss" else output,
            "encoded_question": prompt}
