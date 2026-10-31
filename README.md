# GPT CVNSS4.0 🇻🇳

**Phòng thí nghiệm GPT tiếng Việt — chữ Quốc ngữ và CVNSS4.0.** Kế thừa [GPT_teacher-3.37M-cn](https://github.com/helloworldtang/GPT_teacher-3.37M-cn), bổ sung đường ống huấn luyện và đánh giá riêng cho tiếng Việt. Mục tiêu là học và đối chứng biểu diễn ngôn ngữ, không tuyên bố đã huấn luyện một chatbot tổng quát.

🌐 **Trang web:** https://xulytiengviet.github.io/GPT_CVNSS4.0/  
📚 **[Hướng dẫn tiếng Việt chi tiết](README_VI.md)** · [README nguyên bản tiếng Trung](README_CN.md) · [README tiếng Anh](README_EN.md)

## Tính năng

- Converter CVNSS4.0 v5.0.0-audit-safe (có `selfTest()`, `audit()`, giữ các ứng viên giải mã).
- Dữ liệu JSONL tiếng Việt; chia train/val/test theo hạt giống cố định trước khi mã hóa CVNSS4.0.
- Tokenizer ByteLevel BPE riêng cho Unicode và CVNSS4.0, nhãn hội thoại `Người dùng:` / `Trợ lý:`.
- Huấn luyện GPT Decoder-only 4 lớp qua lõi gốc, lưu checkpoint riêng cho từng chế độ.
- Suy luận CLI và Gradio cục bộ từ checkpoint thật; đo Exact Match, CER trên tập test riêng.
- Website GitHub Pages tiếng Việt: sơ đồ, chuyển đổi, tạo mẫu JSONL, câu lệnh, nạp và vẽ kết quả thật.

## Bắt đầu nhanh

Yêu cầu Python 3.10–3.12, Node.js, `uv`.

```powershell
git clone https://github.com/xulytiengviet/GPT_CVNSS4.0.git
cd GPT_CVNSS4.0
uv sync
uv run python -m cvnss.cli prepare --mode unicode
uv run python -m cvnss.cli tokenizer --mode unicode
uv run python -m cvnss.cli train --mode unicode --device cpu --max-steps 500
uv run python -m cvnss.cli evaluate --mode unicode
uv run python -m cvnss.cli infer --mode unicode --prompt "Xin chào!"
uv run python -m cvnss.cli web-local --mode unicode
```

Để chạy nhánh CVNSS4.0, thay `unicode` bằng `cvnss` trong các lệnh từ `prepare` tới `web-local`. Để dùng dữ liệu riêng, thêm `--input corpus.jsonl` vào lệnh `prepare` cho **cả hai** chế độ.

## Kết quả và giới hạn

- `cvnss/checkpoints/<mode>/best.pt`: trọng số mô hình sau huấn luyện.
- `cvnss/checkpoints/<mode>/loss_history.json`: lịch sử loss.
- `cvnss/checkpoints/<mode>/metrics.json`: chỉ số đánh giá.
- `http://127.0.0.1:7861`: Gradio với mô hình thực trên máy cá nhân.
- `http://127.0.0.1:7860/docs/`: website tĩnh chạy thử ở máy cá nhân.

Tập 50 cặp ví dụ **chỉ để thử hệ thống**. Không được lấy chỉ số từ tập minh họa để tuyên bố chất lượng GPT. Số tham số của mô hình mới thay đổi theo từ vựng tokenizer. CVNSS4.0 có 56 nhóm nhập nhằng; mặc định giải mã chuẩn tắc không đồng nghĩa khôi phục lossless.

## Giấy phép và ghi công

GPT Teacher gốc: giấy phép MIT, xem [LICENSE](LICENSE) và repository tác giả. Bộ chuyển đổi CVNSS4.0 audit-safe do dự án cung cấp được giữ nguyên header và có nguồn riêng. Nghiên cứu, kiểm thử và công bố kết quả cần ghi rõ dữ liệu, tokenizer, checkpoint và phiên bản converter.
