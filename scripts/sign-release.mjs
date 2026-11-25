#!/usr/bin/env node
// Ed25519 release signing. The private key NEVER goes into the repository.
//
//   node scripts/sign-release.mjs --init       create ~/.ravenne/release-key.pem
//   node scripts/sign-release.mjs SHA256SUMS   sign files → SHA256SUMS.sig
//
// Override the key location with RAVENNE_SIGNING_KEY.
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const keyPath = process.env.RAVENNE_SIGNING_KEY
  || path.join(os.homedir(), ".ravenne", "release-key.pem");
const pubPath = path.resolve("release-key.pub");
const args = process.argv.slice(2);

const fingerprint = (spkiDer) =>
  crypto.createHash("sha256").update(spkiDer).digest("hex").match(/.{2}/g).join(":");

if (args[0] === "--init") {
  const force = args.includes("--force");
  if (fs.existsSync(keyPath) && !force) {
    console.error(`Key already exists: ${keyPath}`);
    console.error("Use --init --force to replace it (this breaks old signatures).");
    process.exit(1);
  }
  fs.mkdirSync(path.dirname(keyPath), { recursive: true });
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const privPem = privateKey.export({ type: "pkcs8", format: "pem" });
  const pubPem = publicKey.export({ type: "spki", format: "pem" });
  fs.writeFileSync(keyPath, privPem, { mode: 0o600 });
  fs.writeFileSync(pubPath, pubPem);
  try { fs.chmodSync(keyPath, 0o600); } catch {}
  const fp = fingerprint(publicKey.export({ type: "spki", format: "der" }));
  console.log(`Private key : ${keyPath}  (BACK THIS UP — losing it means no more signed releases)`);
  console.log(`Public key  : ${pubPath}`);
  console.log(`Fingerprint : ${fp}`);
  process.exit(0);
}

if (!args.length) {
  console.error("Usage: node scripts/sign-release.mjs <file> [file...]");
  process.exit(1);
}
if (!fs.existsSync(keyPath)) {
  console.error(`No signing key at ${keyPath}. Run: node scripts/sign-release.mjs --init`);
  process.exit(1);
}
const privateKey = crypto.createPrivateKey(fs.readFileSync(keyPath));
for (const file of args) {
  if (!fs.existsSync(file)) { console.error(`Missing: ${file}`); process.exit(1); }
  const sig = crypto.sign(null, fs.readFileSync(file), privateKey).toString("base64");
  fs.writeFileSync(file + ".sig", sig + "\n");
  console.log(`signed ${file} → ${file}.sig`);
}
