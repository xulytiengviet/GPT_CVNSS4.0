"""Xây dựng ByteLevel BPE tiếng Việt/CVNSS4.0 từ tập huấn luyện riêng."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, processors, trainers


def build(mode: str, vocab_size: int = 2048) -> tuple[str, int]:
    if vocab_size < 260:
        raise ValueError("Vocab tối thiểu phải đủ chứa bảng ByteLevel cùng token đặc biệt.")
    src = Path("cvnss/data") / mode / "train.jsonl"
    dst = Path("cvnss") / f"tokenizer_{mode}.json"
    if not src.is_file():
        raise FileNotFoundError(f"Chưa có {src}; hãy chạy prepare --mode {mode}.")
    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        special_tokens=["<bos>", "<eos>", "<pad>", "<unk>"],
    )

    def corpus():
        with src.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    yield "Người dùng:" + item["prompt"] + "\nTrợ lý:" + item["completion"]

    tokenizer.train_from_iterator(corpus(), trainer=trainer)
    tokenizer.post_processor = processors.TemplateProcessing(
        single="<bos> $A <eos>",
        special_tokens=[
            ("<bos>", tokenizer.token_to_id("<bos>")),
            ("<eos>", tokenizer.token_to_id("<eos>")),
        ],
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(dst))
    count = tokenizer.get_vocab_size()
    print(f"Tokenizer: {dst} | kích thước từ vựng thực tế: {count}")
    return str(dst), count


def main():
    ap = argparse.ArgumentParser(description="Huấn luyện tokenizer BPE riêng cho mỗi biểu diễn.")
    ap.add_argument("--mode", choices=["unicode", "cvnss"], default="unicode")
    ap.add_argument("--vocab-size", type=int, default=2048)
    a = ap.parse_args()
    build(a.mode, a.vocab_size)


if __name__ == "__main__":
    main()
