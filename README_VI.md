# GPT CVNSS4.0 — Hướng dẫn tiếng Việt

Đây là bản Việt hóa và mở rộng mô hình giáo dục từ [GPT_teacher-3.37M-cn](https://github.com/helloworldtang/GPT_teacher-3.37M-cn).

**Quy trình:** dữ liệu tiếng Việt Unicode JSONL → tách train/val/test → (tùy chọn) chuyển CVNSS4.0 → huấn luyện ByteLevel BPE → Transformer GPT → checkpoint → suy luận.

## Cài đặt

Yêu cầu Python 3.10–3.12, Node.js và uv.

```powershell
git clone https://github.com/xulytiengviet/GPT_CVNSS4.0.git
cd GPT_CVNSS4.0
uv sync
node -e "console.log(require('./cvnss/vendor/converter.js').selfTest())"
```

## Chạy thí nghiệm

```powershell
uv run python -m cvnss.cli prepare --mode unicode
uv run python -m cvnss.cli prepare --mode cvnss
uv run python -m cvnss.cli tokenizer --mode unicode
uv run python -m cvnss.cli tokenizer --mode cvnss
uv run python -m cvnss.cli train --mode unicode --device cpu --max-steps 500
uv run python -m cvnss.cli train --mode cvnss --device cpu --max-steps 500
uv run python -m cvnss.cli infer --mode unicode --prompt "Xin chào!"
uv run python -m cvnss.cli infer --mode cvnss --prompt "Xin chào!"
```

Để thay dữ liệu ví dụ bằng dữ liệu thật, chuẩn bị tệp JSONL có hai trường chuỗi `prompt` và `completion`, sau đó chạy `uv run python -m cvnss.cli prepare --mode unicode --input corpus.jsonl` (lặp lại với chế độ cvnss). Tập 50 cặp mẫu chỉ dùng để thử đường ống, không chứng minh chất lượng mô hình.

Để xem giao diện tĩnh, chạy `uv run python -m cvnss.cli web` và truy cập http://127.0.0.1:7860/docs/. Để xuất bản, chọn GitHub Pages từ branch `main`, thư mục `/docs` sau khi merge. GitHub Pages không hỗ trợ inference PyTorch tự động.

**Giới hạn:** kích thước vocab ảnh hưởng số tham số, vì vậy nhãn 3.37M của bản gốc không được coi là số đo hiện tại. Converter v5 có 56 nhóm nhập nhằng và chính sách chuẩn tắc, không đảm bảo khôi phục lossless tuyệt đối. Khi thay tokenizer, không thể sử dụng checkpoint từ tokenizer cũ. Bộ kiểm tra tiếng Trung gốc không phản ánh chất lượng tiếng Việt. Thí nghiệm chạy riêng và không thay dữ liệu gốc.

**Ghi công:** GPT Teacher của helloworldtang được phát hành theo MIT trong repository nguồn; converter CVNSS4.0 phiên bản audit-safe do người dùng cung cấp và giữ nguyên phần khai báo tác giả, phiên bản trong tệp nguồn.
