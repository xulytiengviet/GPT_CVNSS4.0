"""Chuẩn bị dữ liệu huấn luyện và chuyển đổi CVNSS4.0."""
import argparse, json, random, subprocess, unicodedata
from pathlib import Path
SAMPLES = [["Xin chào!","Xin chào! Tôi là GPT CVNSS4.0."],["Bạn là ai?","Tôi là GPT nhỏ dùng để học tập."],["Thủ đô Việt Nam là gì?","Hà Nội là thủ đô Việt Nam."],["Một cộng một bằng mấy?","Một cộng một bằng hai."],["Hai cộng ba bằng mấy?","Hai cộng ba bằng năm."],["Ba nhân ba bằng mấy?","Ba nhân ba bằng chín."],["Mười trừ bốn bằng mấy?","Mười trừ bốn bằng sáu."],["Hình vuông có mấy cạnh?","Hình vuông có bốn cạnh."],["Hình tam giác có mấy cạnh?","Hình tam giác có ba cạnh."],["Một tuần có mấy ngày?","Một tuần có bảy ngày."],["Một năm có mấy tháng?","Một năm có mười hai tháng."],["Một giờ có mấy phút?","Một giờ có sáu mươi phút."],["Mặt Trời là gì?","Mặt Trời là một ngôi sao."],["Trái Đất là gì?","Trái Đất là một hành tinh."],["Nước có công thức gì?","Công thức hóa học của nước là H2O."],["Cây xanh quang hợp cần gì?","Cây xanh cần ánh sáng, nước và khí cacbonic."],["Ngôn ngữ của Việt Nam là gì?","Ngôn ngữ chính là tiếng Việt."],["Chữ Quốc ngữ là gì?","Chữ Quốc ngữ là hệ chữ viết tiếng Việt dựa trên chữ Latinh."],["CVNSS4.0 là gì?","CVNSS4.0 là một hệ biểu diễn chữ viết tiếng Việt."],["Tokenizer là gì?","Tokenizer biến văn bản thành token."],["BPE là gì?","BPE là thuật toán tạo token từ dữ liệu văn bản."],["GPT là gì?","GPT là mô hình Transformer tự hồi quy."],["Transformer là gì?","Transformer là kiến trúc học sâu sử dụng attention."],["Attention là gì?","Attention giúp mô hình chú ý tới các vị trí trong chuỗi."],["Loss là gì?","Loss đo sai lệch giữa dự đoán và mục tiêu."],["Validation là gì?","Validation kiểm tra mô hình trên dữ liệu dành riêng."],["Checkpoint là gì?","Checkpoint lưu trọng số mô hình."],["CPU là gì?","CPU là bộ xử lý trung tâm."],["GPU là gì?","GPU giúp thực hiện tính toán song song."],["JSONL là gì?","JSONL lưu một đối tượng JSON trên mỗi dòng."],["Python là gì?","Python là một ngôn ngữ lập trình."],["PyTorch là gì?","PyTorch là thư viện phát triển mạng nơron."],["Trit là gì?","Trit là chữ số của hệ tam phân."],["Base27 là gì?","Base27 là hệ đếm cơ số hai mươi bảy."],["Ba mũ ba bằng mấy?","Ba mũ ba bằng hai mươi bảy."],["Một phút có mấy giây?","Một phút có sáu mươi giây."],["Tôi muốn học máy học.","Hãy bắt đầu từ dữ liệu và mô hình cơ bản."],["Huấn luyện là gì?","Huấn luyện điều chỉnh tham số mô hình."],["Đánh giá là gì?","Đánh giá đo hiệu quả mô hình trên tập kiểm tra."],["Tạm biệt!","Tạm biệt và hẹn gặp lại."],["Cảm ơn bạn!","Rất vui được giúp bạn."],["Dữ liệu là gì?","Dữ liệu là thông tin được dùng để xử lý."],["Mã hóa là gì?","Mã hóa chuyển thông tin sang một cách biểu diễn khác."],["Giải mã là gì?","Giải mã khôi phục thông tin từ biểu diễn mã."],["Unicode là gì?","Unicode là tiêu chuẩn mã hóa ký tự."],["CPU có huấn luyện GPT được không?","CPU có thể huấn luyện mô hình GPT nhỏ."],["Mô hình nhỏ có thông minh như ChatGPT không?","Không, mô hình giáo dục nhỏ có khả năng hạn chế."],["Học sâu là gì?","Học sâu sử dụng mạng nơron nhiều lớp."],["Câu hỏi là gì?","Câu hỏi dùng để yêu cầu thông tin."],["Câu trả lời là gì?","Câu trả lời cung cấp phản hồi cho câu hỏi."]]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=["unicode","cvnss"],default="unicode")
    ap.add_argument("--input",help="Tập JSONL tiếng Việt tùy chọn")
    args=ap.parse_args()
    rows=[]
    if args.input:
        with open(args.input,encoding="utf-8") as source:
            for line in source:
                if line.strip():
                    row=json.loads(line)
                    rows.append((row["prompt"],row["completion"]))
    else: rows=SAMPLES
    clean=[]; seen=set()
    for p,c in rows:
        p=unicodedata.normalize("NFC",p).strip()
        c=unicodedata.normalize("NFC",c).strip()
        if p and c and p not in seen:
            seen.add(p); clean.append({"prompt":p,"completion":c})
    if len(clean)<10: raise ValueError("Cần ít nhất 10 cặp prompt/completion khác nhau.")
    random.Random(42).shuffle(clean)
    n=len(clean); a=int(n*.8); b=int(n*.9)
    folder=Path("cvnss/data")/args.mode
    folder.mkdir(parents=True,exist_ok=True)
    for name,subset in [("train",clean[:a]),("val",clean[a:b]),("test",clean[b:])]:
        if args.mode=="cvnss":
            payload="\n".join(json.dumps(x,ensure_ascii=False) for x in subset)
            proc=subprocess.run(["node","cvnss/convert.js"],input=payload,text=True,capture_output=True,encoding="utf-8",check=True)
            subset=[json.loads(x) for x in proc.stdout.splitlines() if x.strip()]
        with (folder/(name+".jsonl")).open("w",encoding="utf-8") as f:
            for row in subset: f.write(json.dumps(row,ensure_ascii=False)+"\n")
        print(name,len(subset))
if __name__=="__main__": main()
