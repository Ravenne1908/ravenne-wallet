// Ravenne — unit tests for the pure helpers and the crypto plumbing.
// Run: npm test   (node --test)
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import * as bitcoin from "bitcoinjs-lib";

import {
  _internals, encryptVault, decryptVault, loadVaultResilient, stripUsb,
  btcAddressFromPhrase, btcChangeFromPhrase, buildBtcTx, mergeChainTx,
} from "../ravenne.js";

const { fmtUnits, fmtBtc, fmtXmr, parseXmr, parseDuration, totpCode, b32encode, b32decode, liveUtxos, atomicWriteFile, readJsonResilient } = _internals;

const tmp = () => path.join(os.tmpdir(), `ravenne-test-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);

test("fmtUnits: wei → ETH, negative and zero", () => {
  assert.equal(fmtUnits(0n), "0");
  assert.equal(fmtUnits(10n ** 18n), "1");
  assert.equal(fmtUnits(1_500_000_000_000_000_000n), "1.5");
  assert.equal(fmtUnits(-2n * 10n ** 18n), "-2");
  assert.equal(fmtUnits(1_234_567n, 6), "1.234567");
});

test("fmtBtc: satoshi formatting", () => {
  assert.equal(fmtBtc(0n), "0");
  assert.equal(fmtBtc(100_000_000n), "1");
  assert.equal(fmtBtc(123_456n), "0.00123456");
  assert.equal(fmtBtc(-50_000_000n), "-0.5");
});

test("xmr helpers round-trip", () => {
  assert.equal(fmtXmr(0n), "0");
  assert.equal(fmtXmr(1_000_000_000_000n), "1");
  assert.equal(fmtXmr(1_500_000_000_000n), "1.5");
  assert.equal(parseXmr("1.5").toString(), "1500000000000");
  assert.equal(parseXmr("0.000000000001").toString(), "1");
});

test("parseDuration accepts m/h/d and rejects junk", () => {
  assert.equal(parseDuration("30m"), 30 * 60000);
  assert.equal(parseDuration("2h"), 2 * 3600000);
  assert.equal(parseDuration("3d"), 3 * 86400000);
  assert.equal(parseDuration("1"), 3600000); // default unit = hours
  assert.equal(parseDuration("nope"), null);
});

test("vault encrypt/decrypt round-trip and wrong password fails", () => {
  const file = tmp();
  const payload = { profiles: { default: { wallets: [{ label: "w1" }] } }, active: "default" };
  encryptVault(payload, "correct horse battery", file);
  assert.deepEqual(decryptVault("correct horse battery", file), payload);
  assert.throws(() => decryptVault("wrong password", file));
  const raw = JSON.parse(fs.readFileSync(file, "utf8"));
  assert.match(raw.tag, /^[0-9a-f]{32}$/);         // real GCM tag
  assert.equal(raw.kdf, "argon2id");                // new default
  const bytes = Buffer.from(raw.data, "base64").length;
  assert.equal(bytes % 4096, 0, "ciphertext padded to 4 KiB buckets");
  fs.unlinkSync(file);
});

test("atomic write keeps a .bak and leaves no temp file", () => {
  const file = tmp();
  fs.writeFileSync(file, "one");
  atomicWriteFile(file, "two");
  assert.equal(fs.readFileSync(file, "utf8"), "two");
  assert.equal(fs.readFileSync(file + ".bak", "utf8"), "one");
  const leftovers = fs.readdirSync(path.dirname(file)).filter(n => n.startsWith("." + path.basename(file)) && n.endsWith(".tmp"));
  assert.equal(leftovers.length, 0);
  fs.rmSync(file); fs.rmSync(file + ".bak");
});

test("corrupted vault recovers from its .bak", () => {
  const file = tmp();
  const pass = "pw12345678";
  const p1 = { profiles: { default: { wallets: [], btcWallets: [], xmrWallets: [], history: [], chainTx: [] } }, active: "default" };
  const p2 = { ...p1, active: "other" };
  encryptVault(p1, pass, file);          // no .bak yet
  encryptVault(p2, pass, file);          // .bak = p1
  fs.writeFileSync(file, "{broken");     // simulate a truncated write
  assert.throws(() => decryptVault(pass, file));
  const r = loadVaultResilient(pass, file);
  assert.equal(r.recovered, true);
  assert.deepEqual(r.payload, p1);
  fs.rmSync(file); fs.rmSync(file + ".bak");
});

test("legacy scrypt vaults still decrypt and keep working", () => {  const file = tmp();
  const pass = "legacy-password";
  const salt = crypto.randomBytes(16), iv = crypto.randomBytes(12);
  const key = crypto.scryptSync(pass, salt, 32, { N: 16384, r: 8, p: 1 });
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const data = Buffer.concat([cipher.update(JSON.stringify({ legacy: true }), "utf8"), cipher.final()]);
  fs.writeFileSync(file, JSON.stringify({
    app: "ravenne", v: 7,
    salt: salt.toString("hex"), iv: iv.toString("hex"),
    tag: cipher.getAuthTag().toString("hex"), data: data.toString("base64"),
  }));
  assert.deepEqual(decryptVault(pass, file), { legacy: true });
  fs.unlinkSync(file);
});

test("stripUsb removes USB wallets on every chain", () => {
  const p = {
    profiles: {
      a: {
        wallets: [{ usb: true }, { usb: false }],
        btcWallets: [{ usb: true }],
        xmrWallets: [{ usb: true }, {}],
      },
    },
  };
  const s = stripUsb(p);
  assert.equal(s.profiles.a.wallets.length, 1);
  assert.equal(s.profiles.a.btcWallets.length, 0);
  assert.equal(s.profiles.a.xmrWallets.length, 1);
});

test("BTC receiver derivation is deterministic (BIP84 testnet)", () => {
  const phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";
  const a = btcAddressFromPhrase(phrase, 0, true).address;
  const b = btcAddressFromPhrase(phrase, 0, true).address;
  assert.equal(a, b);
  assert.match(a, /^tb1q/);
  assert.notEqual(a, btcAddressFromPhrase(phrase, 1, true).address);
});

test("BTC change address uses the INTERNAL chain (never the source)", () => {
  const phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";
  const source = btcAddressFromPhrase(phrase, 0, true).address;
  const ch0 = btcChangeFromPhrase(phrase, 0, true);
  const ch1 = btcChangeFromPhrase(phrase, 1, true);
  assert.equal(ch0.path, "m/84'/1'/1'/0/0");
  assert.equal(ch1.path, "m/84'/1'/1'/0/1");
  assert.notEqual(ch0.address, source);
  assert.notEqual(ch0.address, ch1.address);
  assert.match(ch0.address, /^tb1q/);
});

test("buildBtcTx signs a valid transaction and routes change to a fresh address", async () => {
  const phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";
  const entry = { phrase, index: 0 };
  const change0 = btcChangeFromPhrase(phrase, 0, true).address;
  const recipient = btcAddressFromPhrase(phrase, 9, true).address;
  const utxos = [{ txid: "11".repeat(32), vout: 0, value: 100_000 }];
  const r = await buildBtcTx(entry, utxos, recipient, 50_000, 2, true, 0);
  assert.match(r.hex, /^[0-9a-f]+$/);
  assert.equal(r.inputs, 1);
  assert.ok(r.fee > 0n);
  assert.equal(r.changePath, "m/84'/1'/1'/0/0");
  assert.equal(BigInt(50_000) + r.fee + (r.change ?? 0n), 100_000n);
  /* decode the tx: change must pay the internal-chain address, not the sender */
  const tx = bitcoin.Transaction.fromHex(r.hex);
  const outs = tx.outs.map(o => bitcoin.address.fromOutputScript(o.script, bitcoin.networks.testnet));
  assert.ok(outs.includes(recipient), "recipient output");
  assert.ok(outs.includes(change0), "fresh change output");
  assert.ok(!outs.includes(btcAddressFromPhrase(phrase, 0, true).address), "sender not reused");
});

test("mergeChainTx dedupes by hash and caps history", () => {
  const p = { chainTx: [] };
  const items = [
    { hash: "0xaa", value: "1000", timestamp: "2026-01-01T00:00:00.000Z", from: "0x1", to: "0x2" },
    { hash: "0xaa", value: "1000", timestamp: "2026-01-01T00:00:00.000Z", from: "0x1", to: "0x2" },
    { hash: "0xbb", value: "2000", timestamp: "2026-01-02T00:00:00.000Z", from: "0x1", to: "0x2" },
  ];
  assert.equal(mergeChainTx(p, items, "eth"), 2);
  assert.equal(mergeChainTx(p, items, "eth"), 0);
  assert.equal(p.chainTx.length, 2);
  assert.equal(p.chainTx[0].hash, "0xbb");
});

test("BTC coin control filters frozen UTXOs", () => {
  const e = { frozenUtxos: ["aa:0"] };
  const list = [{ txid: "aa", vout: 0, value: 1 }, { txid: "bb", vout: 1, value: 2 }];
  const live = liveUtxos(e, list);
  assert.equal(live.length, 1);
  assert.equal(live[0].txid, "bb");
  assert.equal(liveUtxos({}, list).length, 2);
});

test("TOTP base32 round-trip and stable codes", () => {
  const buf = Buffer.from("ravenne-test-secret");
  assert.deepEqual(b32decode(b32encode(buf)), buf);
  const secret = b32encode(buf);
  const a = totpCode(secret, 0);
  assert.equal(a.length, 6);
  assert.match(a, /^\d{6}$/);
  assert.equal(totpCode(secret, -1).length, 6);   // window support used by the gate
});
