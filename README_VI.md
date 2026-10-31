# Hướng dẫn huấn luyện GPT CVNSS4.0 bằng tiếng Việt

**Phiên bản phòng thí nghiệm:** học tập và đối chứng chữ Quốc ngữ ↔ CVNSS4.0 trên GPT Teacher. Toàn bộ thao tác dưới đây chạy tại thư mục gốc dự án.

## 1. Mô hình và công cụ

Khung GPT gốc là Decoder-only Transformer 4 lớp, GQA, SwiGLU, RMSNorm, RoPE và chia sẻ trọng số. Kích thước mô hình thực tế phụ thuộc vocab; 3,37M là mốc mô tả mô hình gốc tiếng Trung, **không** phải kết quả đo mới. Yêu cầu Python 3.10–3.12, Node.js và `uv`; các thiết bị CPU, NVIDIA CUDA hoặc Apple MPS.

```powershell
git clone https://github.com/xulytiengviet/GPT_CVNSS4.0.git
cd GPT_CVNSS4.0
uv sync
node -e "console.log(require('./cvnss/vendor/converter.js').selfTest())"
```

## 2. Chuẩn bị tập JSONL

Mỗi dòng phải có hai chuỗi UTF-8; ví dụ:

```json
{"prompt":"Thủ đô Việt Nam là gì?","completion":"Hà Nội là thủ đô của Việt Nam."}
```

Tạo dữ liệu ví dụ có sẵn (50 cặp câu hỏi–trả lời):

```powershell
uv run python -m cvnss.cli prepare --mode unicode
uv run python -m cvnss.cli prepare --mode cvnss
```

Hoặc thay bằng tập của bạn:

```powershell
uv run python -m cvnss.cli prepare --mode unicode --input corpus.jsonl
uv run python -m cvnss.cli prepare --mode cvnss --input corpus.jsonl
```

Dữ liệu được chuẩn hóa Unicode NFC, loại dòng trùng hoàn toàn, xáo theo seed 42 và chia train/val/test 80/10/10 trước khi chuyển đổi. Tập có nhiều câu gần nghĩa hoặc cùng tài liệu cần được phân nhóm theo nguồn trước để hạn chế rò rỉ; chia theo dòng đơn lẻ chưa đủ cho đánh giá khoa học.

## 3. Huấn luyện tokenizer độc lập

```powershell
uv run python -m cvnss.cli tokenizer --mode unicode --vocab-size 2048
uv run python -m cvnss.cli tokenizer --mode cvnss --vocab-size 2048
```

Có thể thử 4096, 8000, 16000 nhưng với dữ liệu mẫu nhỏ số token học thực tế thường nhỏ hơn mục tiêu. Các tệp `cvnss/tokenizer_unicode.json` và `cvnss/tokenizer_cvnss.json` là **hai từ vựng khác nhau**, không thể hoán đổi với nhau hoặc dùng lại với checkpoint cũ.

## 4. Huấn luyện GPT

```powershell
uv run python -m cvnss.cli train --mode unicode --device cpu --max-steps 500
uv run python -m cvnss.cli train --mode cvnss --device cpu --max-steps 500
```

Cấu hình ở `cvnss/config_unicode.yml`, `cvnss/config_cvnss.yml`. Tập dữ liệu, tokenizer và checkpoint của hai nhánh hoàn toàn độc lập. Trên máy có NVIDIA, đổi `--device cpu` thành `--device cuda`; `auto` tự chọn thiết bị có sẵn. Loss giảm chỉ cho biết mô hình khớp tập dữ liệu tốt hơn; không đảm bảo đúng kiến thức hoặc đối thoại tổng quát.

## 5. Đánh giá đúng chế độ

```powershell
uv run python -m cvnss.cli evaluate --mode unicode
uv run python -m cvnss.cli evaluate --mode cvnss
```

Bộ đánh giá tiếng Việt sử dụng `cvnss/data/<mode>/test.jsonl` và tính Exact Match (khớp chuỗi sau chuẩn hóa khoảng trắng) và CER (tổng khoảng cách Levenshtein / tổng ký tự tham chiếu). Với chế độ CVNSS, đầu vào trong test.jsonl được truyền nguyên dạng mã hóa vào mô hình, không giải mã rồi mã hóa lại gây thất thoát. Kết quả có thể chứa dự đoán kèm `model_parameters`, `vocab_size`; lưu tại `cvnss/checkpoints/<mode>/metrics.json`.

Các chỉ số này chỉ đo **độ giống chuỗi**, không đo sự hiểu biết, sự thật hoặc năng lực suy luận.

## 6. Suy luận GPT từ checkpoint

```powershell
uv run python -m cvnss.cli infer --mode unicode --prompt "Bạn là ai?"
uv run python -m cvnss.cli infer --mode cvnss --prompt "Xin chào!"
uv run python -m cvnss.cli web-local --mode unicode
```

Mở **http://127.0.0.1:7861** để hỏi đáp với mô hình đã học. Nếu chưa có `best.pt`, giao diện báo lỗi thay vì tạo câu trả lời giả. Dùng `web-local --mode cvnss` để chạy mô hình CVNSS4.0; phần chữ Quốc ngữ hiển thị là giải mã chuẩn tắc, không bảo đảm khôi phục nguyên bản trong các trường hợp nhập nhằng.

## 7. Trang minh họa công khai

Trang [GitHub Pages](https://xulytiengviet.github.io/GPT_CVNSS4.0/) thể hiện từng công đoạn, cho phép chuyển đổi CVNSS4.0 theo quy tắc, tạo JSONL và đọc kết quả đánh giá từ tệp cục bộ. **Không có máy chủ GPT trên GitHub Pages**.

```powershell
uv run python -m cvnss.cli web
```

Mở **http://127.0.0.1:7860/docs/**. Trên GitHub Pages, hỗ trợ cả chế độ xuất bản từ `main:/docs` và từ `main:/` (trang ở root tự chuyển đến `/docs/`).

## 8. Kiểm chứng và công bố kết quả

Cần lưu phiên bản mã nguồn, dữ liệu (hoặc fingerprint), tokenizer, seed, tham số mô hình, số bước, biểu đồ train/validation loss, kết quả test và giới hạn CVNSS4.0. Dữ liệu ví dụ 50 cặp chỉ để smoke test. Khi thay tokenizer hoặc dữ liệu, cần huấn luyện checkpoint mới. Các bài test tiếng Trung của GPT Teacher gốc chỉ có ý nghĩa hồi quy cho nhánh gốc, không đại diện chất lượng tiếng Việt.

Nguồn: [GPT_teacher-3.37M-cn](https://github.com/helloworldtang/GPT_teacher-3.37M-cn). Tôn trọng giấy phép MIT của thành phần nguồn và nguồn gốc bản converter CVNSS4.0.
