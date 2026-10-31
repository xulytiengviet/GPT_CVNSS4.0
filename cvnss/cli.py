"""CLI tiếng Việt: dữ liệu → BPE → GPT → suy luận."""
import argparse, json, subprocess, sys
from pathlib import Path
import yaml
from core.infer import generate,load_model_and_tokenizer
def run(*a): subprocess.run([sys.executable,*a],check=True)
def main():
    ap=argparse.ArgumentParser(description="GPT CVNSS4.0 - công cụ tiếng Việt")
    ap.add_argument("action",choices=["prepare","tokenizer","train","infer","web"])
    ap.add_argument("--mode",choices=["unicode","cvnss"],default="unicode")
    ap.add_argument("--input",help="JSONL đầu vào")
    ap.add_argument("--prompt",default="Xin chào!")
    ap.add_argument("--device",choices=["auto","cpu","cuda","mps"],default="auto")
    ap.add_argument("--max-steps",type=int,default=500)
    a=ap.parse_args()
    config="cvnss/config_"+a.mode+".yml"
    cfg=yaml.safe_load(Path(config).read_text(encoding="utf-8"))
    if a.action=="prepare":
        cmd=["-m","cvnss.prepare","--mode",a.mode]
        if a.input: cmd+=["--input",a.input]
        run(*cmd)
    elif a.action=="tokenizer":
        run("-m","cvnss.tokenizer","--mode",a.mode)
    elif a.action=="train":
        if not Path(cfg["tokenizer"]["path"]).exists():
            raise SystemExit("Thiếu tokenizer. Hãy tạo dữ liệu và tokenizer trước.")
        run("-m","train.train","--config",config,"--device",a.device,
            "--max_steps",str(a.max_steps),"--no-acceptance")
    elif a.action=="infer":
        ckpt=Path(cfg["training"]["save_dir"])/"best.pt"
        if not ckpt.exists():
            raise SystemExit("Thiếu checkpoint best.pt; cần huấn luyện mô hình trước.")
        p=a.prompt
        if a.mode=="cvnss":
            js=subprocess.run(["node","cvnss/convert.js"],input=json.dumps({"prompt":p,"completion":""},ensure_ascii=False),capture_output=True,text=True,encoding="utf-8",check=True)
            p=json.loads(js.stdout)["prompt"]
        model,tok,_,device=load_model_and_tokenizer(str(ckpt))
        prefix=cfg["data"]["user_prefix"]+p+"\n"+cfg["data"]["assistant_prefix"]
        answer=generate(model,tok,prefix,temperature=0.0,max_new_tokens=64,
                        wrap_prompt=False,device=device,stop_strings=["\n"+cfg["data"]["user_prefix"]])
        print("Câu hỏi:",a.prompt)
        print("Đáp án",a.mode+":",answer)
        if a.mode=="cvnss":
            code='const c=require(process.argv[1]);process.stdout.write(c.fromCvss(require("node:fs").readFileSync(0,"utf8")).cqn)'
            o=subprocess.run(["node","-e",code,str(Path("cvnss/vendor/converter.js").resolve())],
                input=answer,text=True,capture_output=True,encoding="utf-8",check=True)
            print("Unicode theo chính sách chuẩn tắc:",o.stdout)
    elif a.action=="web":
        print("Truy cập http://127.0.0.1:7860")
        run("-m","http.server","7860")
if __name__=="__main__": main()
