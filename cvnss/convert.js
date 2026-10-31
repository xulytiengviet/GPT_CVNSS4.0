"use strict";
const fs=require("node:fs");
const c=require("./vendor/converter.js");
for(const line of fs.readFileSync(0,"utf8").split(/\r?\n/)){
 if(!line.trim())continue;
 const x=JSON.parse(line);
 process.stdout.write(JSON.stringify({prompt:c.fromCqn(x.prompt).cvss,completion:c.fromCqn(x.completion).cvss})+"\n");
}