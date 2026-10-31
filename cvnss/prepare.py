"""Chuẩn bị dữ liệu tiếng Việt có thể tái lập, trước khi áp dụng CVNSS4.0."""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import unicodedata
from pathlib import Path

SAMPLES = [["Xin chào!","Xin chào! Tôi là GPT CVNSS4.0."],["Bạn là ai?","Tôi là GPT nhỏ dùng để học tập."],["Thủ đô Việt Nam là gì?","Hà Nội là thủ đô Việt Nam."],["Một cộng một bằng mấy?","Một cộng một bằng hai."],["Hai cộng ba bằng mấy?","Hai cộng ba bằng năm."],["Ba nhân ba bằng mấy?","Ba nhân ba bằng chín."],["Mười trừ bốn bằng mấy?","Mười trừ bốn bằng sáu."],["Hình vuông có mấy cạnh?","Hình vuông có bốn cạnh."],["Hình tam giác có mấy cạnh?","Hình tam giác có ba cạnh."],["Một tuần có mấy ngày?","Một tuần có bảy ngày."],["Một năm có mấy tháng?","Một năm có mười hai tháng."],["Một giờ có mấy phút?","Một giờ có sáu mươi phút."],["Mặt Trời là gì?","Mặt Trời là một ngôi sao."],["Trái Đất là gì?","Trái Đất là một hành tinh."],["Nước có công thức gì?","Công thức hóa học của nước là H2O."],["Cây xanh quang hợp cần gì?","Cây xanh cần ánh sáng, nước và khí cacbonic."],["Ngôn ngữ của Việt Nam là gì?","Ngôn ngữ chính là tiếng Việt."],["Chữ Quốc ngữ là gì?","Chữ Quốc ngữ là hệ chữ viết tiếng Việt dựa trên chữ Latinh."],["CVNSS4.0 là gì?","CVNSS4.0 là một hệ biểu diễn chữ viết tiếng Việt."],["Tokenizer là gì?","Tokenizer biến văn bản thành token."],["BPE là gì?","BPE là thuật toán tạo token từ dữ liệu văn bản."],["GPT là gì?","GPT là mô hình Transformer tự hồi quy."],["Transformer là gì?","Transformer là kiến trúc học sâu sử dụng attention."],["Attention là gì?","Attention giúp mô hình chú ý tới các vị trí trong chuỗi."],["Loss là gì?","Loss đo sai lệch giữa dự đoán và mục tiêu."],["Validation là gì?","Validation kiểm tra mô hình trên dữ liệu dành riêng."],["Checkpoint là gì?","Checkpoint lưu trọng số mô hình."],["CPU là gì?","CPU là bộ xử lý trung tâm."],["GPU là gì?","GPU giúp thực hiện tính toán song song."],["JSONL là gì?","JSONL lưu một đối tượng JSON trên mỗi dòng."],["Python là gì?","Python là một ngôn ngữ lập trình."],["PyTorch là gì?","PyTorch là thư viện phát triển mạng nơron."],["Trit là gì?","Trit là chữ số của hệ tam phân."],["Base27 là gì?","Base27 là hệ đếm cơ số hai mươi bảy."],["Ba mũ ba bằng mấy?","Ba mũ ba bằng hai mươi bảy."],["Một phút có mấy giây?","Một phút có sáu mươi giây."],["Tôi muốn học máy học.","Hãy bắt đầu từ dữ liệu và mô hình cơ bản."],["Huấn luyện là gì?","Huấn luyện điều chỉnh tham số mô hình."],["Đánh giá là gì?","Đánh giá đo hiệu quả mô hình trên tập kiểm tra."],["Tạm biệt!","Tạm biệt và hẹn gặp lại."],["Cảm ơn bạn!","Rất vui được giúp bạn."],["Dữ liệu là gì?","Dữ liệu là thông tin được dùng để xử lý."],["Mã hóa là gì?","Mã hóa chuyển thông tin sang một cách biểu diễn khác."],["Giải mã là gì?","Giải mã khôi phục thông tin từ biểu diễn mã."],["Unicode là gì?","Unicode là tiêu chuẩn mã hóa ký tự."],["CPU có huấn luyện GPT được không?","CPU có thể huấn luyện mô hình GPT nhỏ."],["Mô hình nhỏ có thông minh như ChatGPT không?","Không, mô hình giáo dục nhỏ có khả năng hạn chế."],["Học sâu là gì?","Học sâu sử dụng mạng nơron nhiều lớp."],["Câu hỏi là gì?","Câu hỏi dùng để yêu cầu thông tin."],["Câu trả lời là gì?","Câu trả lời cung cấp phản hồi cho câu hỏi."]]

def read_pairs(input_path: str | None) -> list[dict[str, str]]:
    """Đọc JSONL tiếng Việt; không tự ý dịch hoặc suy diễn nội dung."""
    if input_path is None:
        source = [{"prompt": p, "completion": c} for p, c in SAMPLES]
    else:
        source = []
        with open(input_path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict) or not isinstance(item.get("prompt"), str) or not isinstance(item.get("completion"), str):
                    raise ValueError(f"Dòng {number}: cần prompt và completion là chuỗi.")
                source.append({"prompt": item["prompt"], "completion": item["completion"]})
    seen = set()
    cleaned = []
    for item in source:
        p = unicodedata.normalize("NFC", item["prompt"]).strip()
        c = unicodedata.normalize("NFC", item["completion"]).strip()
        key = (p, c)
        if p and c and key not in seen:
            cleaned.append({"prompt": p, "completion": c})
            seen.add(key)
    if len(cleaned) < 10:
        raise ValueError("Cần tối thiểu 10 cặp dữ liệu hợp lệ để chia train/val/test.")
    return cleaned


def encode_cvnss(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Dùng đúng converter v5 đi kèm, không dùng phép thay dấu đơn giản."""
    if not rows:
        return []
    path = Path(__file__).resolve().parent / "convert.js"
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    proc = subprocess.run(["node", str(path)], input=payload, text=True, capture_output=True, encoding="utf-8", check=True)
    output = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    if len(output) != len(rows):
        raise RuntimeError("Converter trả về số bản ghi không khớp.")
    return output


def prepare(mode: str, input_path: str | None = None, out_dir: str | None = None, seed: int = 42) -> dict[str, int]:
    rows = read_pairs(input_path)
    # Chia bộ dữ liệu gốc TRƯỚC KHI biến đổi biểu diễn; hai nhánh dùng cùng chỉ số nguồn.
    random.Random(seed).shuffle(rows)
    a = max(1, int(len(rows) * 0.8))
    b = max(a + 1, int(len(rows) * 0.9))
    partitions = {"train": rows[:a], "val": rows[a:b], "test": rows[b:]}
    output_dir = Path(out_dir) if out_dir else Path("cvnss/data") / mode
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, subset in partitions.items():
        converted = encode_cvnss(subset) if mode == "cvnss" else subset
        path = output_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for item in converted:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        counts[name] = len(converted)
        print(f"  {name:<5} {counts[name]:>5} mẫu -> {path}")
    meta = {"mode": mode, "seed": seed, "count": len(rows), "counts": counts,
            "input": input_path or "50 câu hỏi đáp minh họa",
            "note": "Mẫu giáo dục; chưa phải bộ dữ liệu huấn luyện GPT có ý nghĩa thống kê."}
    (output_dir / "manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description="Chuẩn bị dữ liệu tiếng Việt cho GPT CVNSS4.0.")
    ap.add_argument("--mode", choices=["unicode", "cvnss"], default="unicode")
    ap.add_argument("--input", help="JSONL Unicode gốc có prompt/completion")
    ap.add_argument("--out-dir", help="Thư mục kết quả, mặc định cvnss/data/<mode>")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    print(f"Chuẩn bị dữ liệu ({args.mode})")
    prepare(args.mode, args.input, args.out_dir, args.seed)


if __name__ == "__main__":
    main()
