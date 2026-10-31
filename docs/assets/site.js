"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const cvnss = window.CVNSSConverter;
  let direction = "cqn";
  let lastJson = "";
  const reference = "Xin chào Việt Nam. Tôi đang học mô hình GPT và CVNSS4.0.";
  const toast = text => { const el=$("toast"); el.textContent=text; el.classList.add("shown"); clearTimeout(toast.timer); toast.timer=setTimeout(()=>el.classList.remove("shown"),2200); };
  const safeConvert = (input, mode) => {
    if (!cvnss) return {cqn:"Chưa tải được converter",cvss:"Chưa tải được converter"};
    return mode==="cqn" ? cvnss.fromCqn(input) : cvnss.fromCvss(input);
  };
  function renderConverter() {
    if (!cvnss) { $("converter-status").textContent="Converter chưa sẵn sàng"; return; }
    try {
      const input=$("input-text").value.normalize("NFC");
      const out=safeConvert(input,direction);
      const main=direction==="cqn" ? out.cvss : out.cqn;
      const reverse=direction==="cqn" ? cvnss.fromCvss(out.cvss).cqn : cvnss.fromCqn(out.cqn).cvss;
      $("output-code").textContent=main;
      $("reverse-code").textContent=reverse;
      $("source-chars").textContent=Array.from(input).length.toLocaleString("vi-VN");
      $("output-chars").textContent=Array.from(main).length.toLocaleString("vi-VN");
      $("output-bytes").textContent=new TextEncoder().encode(main).length.toLocaleString("vi-VN");
      if(direction==="cqn"){
        const codes=out.cvss.match(/[\p{L}]+/gu)||[];
        const ambiguous=codes.map(w=>cvnss.inspectWord(w,"cvss")).filter(i=>i.ambiguous);
        const samples=ambiguous.slice(0,3).map(i=>i.input+" → "+i.candidates.join(" / "));
        $("ambiguous").textContent=ambiguous.length
          ? "Phát hiện "+ambiguous.length+" mã có nhiều ứng viên khôi phục trong văn bản: "+samples.join("; ")+". Bản đọc ngược chỉ theo chính sách chuẩn tắc."
          : "Chưa phát hiện mã nhập nhằng trong đoạn này. Kết quả giải mã vẫn không là cam kết lossless cho mọi văn bản.";
      }else{
        const codes=input.match(/[\p{L}]+/gu)||[];
        const ambiguous=codes.map(w=>cvnss.inspectWord(w,"cvss")).filter(i=>i.ambiguous);
        $("ambiguous").textContent=ambiguous.length
          ? "Có "+ambiguous.length+" mã nhập nhằng; bộ giải mã hiển thị một ứng viên chuẩn tắc.": "Giải mã dựa trên bộ quy tắc CVNSS4.0 v5.";
      }
    }catch(err){$("converter-status").textContent="Lỗi chuyển đổi: "+err.message;}
  }
  function setDirection(value){
    direction=value;
    $("tab-cqn").classList.toggle("active",value==="cqn");
    $("tab-cvss").classList.toggle("active",value==="cvss");
    $("tab-cqn").setAttribute("aria-pressed",String(value==="cqn"));
    $("tab-cvss").setAttribute("aria-pressed",String(value==="cvss"));
    $("input-label").textContent=value==="cqn"?"Văn bản chữ Quốc ngữ":"Văn bản CVNSS4.0";
    $("output-title").textContent=value==="cqn"?"Kết quả CVNSS4.0":"Kết quả chữ Quốc ngữ";
    $("reverse-title").textContent=value==="cqn"?"Giải mã chuẩn tắc về Quốc ngữ":"Mã hóa lại CVNSS4.0";
    $("input-text").value=value==="cqn"?reference:cvnss?cvnss.fromCqn(reference).cvss:reference;
    renderConverter();
  }
  function makeJSONL(){
    const prompt=$("example-prompt").value.normalize("NFC").trim();
    const completion=$("example-completion").value.normalize("NFC").trim();
    if(!prompt||!completion){toast("Cần nhập câu hỏi và câu trả lời.");return;}
    const source={prompt,completion};
    lastJson=JSON.stringify(source);
    $("jsonl-cqn").textContent=lastJson;
    $("jsonl-cvnss").textContent=cvnss?JSON.stringify({prompt:cvnss.fromCqn(prompt).cvss,completion:cvnss.fromCqn(completion).cvss}):"Không có converter.js";
  }
  function commands(){
    const m=$("training-mode").value, device=$("device").value, vocab=$("vocab-size").value;
    const lines=[
      "# Cài đặt từ repository GPT_CVNSS4.0",
      "git clone https://github.com/xulytiengviet/GPT_CVNSS4.0.git",
      "cd GPT_CVNSS4.0",
      "uv sync",
      "",
      "# Kiểm tra bộ quy tắc",
      "node -e \"console.log(require('./cvnss/vendor/converter.js').selfTest())\"",
      "",
      "# Chuẩn bị dữ liệu và huấn luyện tokenizer",
      "uv run python -m cvnss.cli prepare --mode "+m,
      "uv run python -m cvnss.cli tokenizer --mode "+m+" --vocab-size "+vocab,
      "",
      "# Huấn luyện GPT và đánh giá trên test.jsonl",
      "uv run python -m cvnss.cli train --mode "+m+" --device "+device+" --max-steps 500",
      "uv run python -m cvnss.cli evaluate --mode "+m,
      "",
      "# Suy luận với checkpoint đã huấn luyện",
      'uv run python -m cvnss.cli infer --mode '+m+' --prompt "Xin chào!"',
      "uv run python -m cvnss.cli web-local --mode "+m
    ];
    $("train-commands").textContent=lines.join("\n");
  }
  async function clipboard(text){
    try{await navigator.clipboard.writeText(text);toast("Đã sao chép.");}
    catch(e){toast("Không thể sao chép tự động; hãy chọn văn bản thủ công.");}
  }
  $("tab-cqn").addEventListener("click",()=>setDirection("cqn"));
  $("tab-cvss").addEventListener("click",()=>setDirection("cvss"));
  $("convert-btn").addEventListener("click",renderConverter);
  $("reset-btn").addEventListener("click",()=>{$("input-text").value=direction==="cqn"?reference:cvnss.fromCqn(reference).cvss;renderConverter();});
  $("input-text").addEventListener("input",renderConverter);
  $("make-jsonl").addEventListener("click",makeJSONL);
  $("download-jsonl").addEventListener("click",()=>{
    makeJSONL();
    if(!lastJson)return;
    const url=URL.createObjectURL(new Blob([lastJson+"\n"],{type:"application/x-ndjson;charset=utf-8"}));
    const link=document.createElement("a");link.href=url;link.download="mau_tieng_viet.jsonl";link.click();URL.revokeObjectURL(url);
  });
  document.querySelectorAll("[data-copy]").forEach(button=>button.addEventListener("click",()=>clipboard($(button.dataset.copy).textContent)));
  ["training-mode","device","vocab-size"].forEach(id=>$(id).addEventListener("change",commands));
  $("metrics-file").addEventListener("change",async event=>{
    try{
      const file=event.target.files[0];if(!file)return;
      const data=JSON.parse(await file.text());
      if(!Number.isFinite(data.exact_match)||!Number.isFinite(data.cer)||!Number.isFinite(data.samples)||data.samples<1)throw Error("Thiếu exact_match, cer hoặc samples hợp lệ.");
      $("metric-em").textContent=(data.exact_match*100).toFixed(1)+"%";
      $("metric-cer").textContent=(data.cer*100).toFixed(1)+"%";
      $("metric-samples").textContent=String(data.samples);
      $("metric-params").textContent=Number.isFinite(data.model_parameters)?data.model_parameters.toLocaleString("vi-VN"):"—";
      $("metrics-message").textContent="Đã nạp kết quả "+(data.mode||"")+" từ "+file.name+". Tệp chỉ được đọc cục bộ.";
    }catch(e){$("metrics-message").textContent="Không đọc được kết quả: "+e.message;}
  });
  function drawLoss(data){
    const train=data.train_losses, val=data.val_losses||[];
    if(!Array.isArray(train)||!train.length||train.some(x=>!Number.isFinite(x)))throw Error("Không có train_losses hợp lệ.");
    if(!Array.isArray(val)||val.some(x=>!Number.isFinite(x)))throw Error("val_losses phải là mảng số.");
    const el=$("loss-chart"),ctx=el.getContext("2d"),W=el.width,H=el.height,pad={left:48,right:15,top:20,bottom:34};
    const values=[...train,...val],lo=Math.min(...values),hi=Math.max(...values),range=Math.max(hi-lo,.01);
    ctx.clearRect(0,0,W,H);ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);
    ctx.strokeStyle="#dce5f1";ctx.lineWidth=1;ctx.font="12px Segoe UI";ctx.fillStyle="#65738d";
    for(let j=0;j<=4;j++){const y=pad.top+(H-pad.top-pad.bottom)*j/4;ctx.beginPath();ctx.moveTo(pad.left,y);ctx.lineTo(W-pad.right,y);ctx.stroke();ctx.fillText((hi-range*j/4).toFixed(2),4,y+4);}
    const X=t=>pad.left+(W-pad.left-pad.right)*(t-1)/Math.max(1,train.length-1);
    const Y=v=>pad.top+(H-pad.top-pad.bottom)*(hi-v)/range;
    function plot(arr,interval,color){
      if(!arr.length)return;
      ctx.strokeStyle=color;ctx.lineWidth=2.1;ctx.beginPath();
      arr.forEach((v,i)=>{const x=X(interval===1?i+1:(i+1)*interval),y=Y(v);if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);});
      ctx.stroke();
    }
    plot(train,1,"#3868da");plot(val,Math.max(1,Number(data.eval_interval)||25),"#ec9c42");
    ctx.fillStyle="#3c5989";ctx.fillText("Bước học →",W-95,H-9);
    ctx.fillStyle="#3868da";ctx.fillRect(pad.left+7,8,12,3);ctx.fillText("train",pad.left+23,14);
    ctx.fillStyle="#ec9c42";ctx.fillRect(pad.left+76,8,12,3);ctx.fillText("validation",pad.left+93,14);
  }
  $("loss-file").addEventListener("change",async event=>{
    try{const file=event.target.files[0];if(!file)return;const data=JSON.parse(await file.text());drawLoss(data);$("loss-message").textContent="Đồ thị từ "+file.name+"; không sử dụng số liệu giả lập.";}
    catch(e){$("loss-message").textContent="Không đọc được loss: "+e.message;}
  });
  makeJSONL();commands();
  if(cvnss){
    const test=cvnss.selfTest(),audit=cvnss.audit();
    $("converter-status").textContent=test.ok?"Converter sẵn sàng · "+test.tests+"/"+test.tests+" kiểm thử":"Converter có lỗi tự kiểm tra";
    $("audit-count").textContent=audit.ambiguityGroups;
    renderConverter();
  }else{
    $("converter-status").textContent="Không tải được converter.js";
    $("output-code").textContent="Thiếu converter";
    $("reverse-code").textContent="Thiếu converter";
  }
})();