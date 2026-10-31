"""Ứng dụng Gradio tiếng Việt dùng checkpoint thực (chạy trên máy cá nhân)."""
from __future__ import annotations
import argparse
import gradio as gr
from cvnss.runtime import answer


def app(initial_mode: str):
    with gr.Blocks(title="GPT CVNSS4.0 - Suy luận thực") as demo:
        gr.Markdown("# GPT CVNSS4.0 — Hỏi đáp tiếng Việt\n"
                    "Suy luận bằng checkpoint đã huấn luyện trên máy tính cá nhân. "
                    "Không có mô hình thì ứng dụng sẽ báo thiếu checkpoint.")
        mode = gr.Radio(["unicode", "cvnss"], value=initial_mode, label="Biểu diễn mô hình")
        prompt = gr.Textbox(value="Xin chào!", lines=3, label="Câu hỏi chữ Quốc ngữ")
        temperature = gr.Slider(0, 1, value=0, step=.1, label="Nhiệt độ sinh (0 = tham lam)")
        tokens = gr.Slider(16, 128, value=64, step=16, label="Số token tối đa")
        go = gr.Button("Gửi câu hỏi", variant="primary")
        raw = gr.Textbox(label="Kết quả sinh theo biểu diễn mô hình", lines=4)
        unicode_output = gr.Textbox(label="Kết quả chữ Quốc ngữ (CVNSS dùng giải mã chuẩn tắc)", lines=4)
        status = gr.Markdown()

        def infer(q, m, t, n):
            try:
                r = answer(q, m, max_new_tokens=int(n), temperature=float(t))
                return r["raw"], r["unicode"], f"Đã suy luận bằng checkpoint **{m}**."
            except Exception as exc:
                return "", "", f"Không thể suy luận: {exc}"

        go.click(infer, [prompt, mode, temperature, tokens], [raw, unicode_output, status])
    return demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["unicode", "cvnss"], default="unicode")
    parser.add_argument("--port", type=int, default=7861)
    args = parser.parse_args()
    app(args.mode).launch(server_name="127.0.0.1", server_port=args.port, share=False)


if __name__ == "__main__":
    main()
