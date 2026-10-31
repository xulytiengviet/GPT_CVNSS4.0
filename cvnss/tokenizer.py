"""Tokenizer BPE sử dụng nhãn hội thoại tiếng Việt."""
import argparse,json
from pathlib import Path
from tokenizers import Tokenizer,models,trainers,decoders,pre_tokenizers,processors
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=["unicode","cvnss"],default="unicode")
    ap.add_argument("--vocab-size",type=int,default=2048)
    a=ap.parse_args()
    src=Path("cvnss/data")/a.mode/"train.jsonl"
    dst=Path("cvnss")/("tokenizer_"+a.mode+".json")
    t=Tokenizer(models.BPE(unk_token="<unk>"))
    t.pre_tokenizer=pre_tokenizers.ByteLevel(add_prefix_space=False)
    t.decoder=decoders.ByteLevel()
    trainer=trainers.BpeTrainer(vocab_size=a.vocab_size,initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),special_tokens=["<bos>","<eos>","<pad>","<unk>"])
    def corpus():
        with src.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d=json.loads(line)
                    yield "Người dùng:"+d["prompt"]+"\nTrợ lý:"+d["completion"]
    t.train_from_iterator(corpus(),trainer=trainer)
    t.post_processor=processors.TemplateProcessing(single="<bos> $A <eos>",special_tokens=[("<bos>",t.token_to_id("<bos>")),("<eos>",t.token_to_id("<eos>"))])
    t.save(str(dst))
    print(f"Đã lưu {dst}, vocab={t.get_vocab_size()}")
if __name__=="__main__": main()
