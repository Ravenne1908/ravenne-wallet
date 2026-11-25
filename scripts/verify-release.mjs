#!/usr/bin/env node
// Verify an Ed25519 release signature.
//
//   node scripts/verify-release.mjs --fingerprint [release-key.pub]
//   node scripts/verify-release.mjs SHA256SUMS [release-key.pub]
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const pubPath = path.resolve(args.includes("--fingerprint")
  ? (args[1] && !args[1].startsWith("--") ? args[1] : "release-key.pub")
  : (args[1] || "release-key.pub"));

if (!fs.existsSync(pubPath)) {
  console.error(`Public key not found: ${pubPath}`);
  process.exit(1);
}
const publicKey = crypto.createPublicKey(fs.readFileSync(pubPath));
const der = publicKey.export({ type: "spki", format: "der" });
const fp = crypto.createHash("sha256").update(der).digest("hex").match(/.{2}/g).join(":");

if (args[0] === "--fingerprint") {
  console.log(fp);
  process.exit(0);
}
if (!args[0]) {
  console.error("Usage: node scripts/verify-release.mjs <file> [release-key.pub]");
  process.exit(1);
}
const file = args[0];
const sigFile = file + ".sig";
if (!fs.existsSync(file) || !fs.existsSync(sigFile)) {
  console.error(`Missing ${file} or ${sigFile}`);
  process.exit(1);
}
let sig;
try { sig = Buffer.from(fs.readFileSync(sigFile, "utf8").trim(), "base64"); }
catch { console.error("Unreadable signature"); process.exit(1); }
const ok = crypto.verify(null, fs.readFileSync(file), publicKey, sig);
console.log(`key  ${fp}`);
console.log(`${ok ? "VALID" : "INVALID"}  ${file}`);
process.exit(ok ? 0 : 1);
