/* Preview one ghost splash frame without starting the wallet.
 * Usage: node scripts/preview-ghost.mjs [frame] [cols] [rows] [--ansi]
 */
import { _internals } from "../ravenne.js";

const args = process.argv.slice(2);
const ansi = args.includes("--ansi");
const nums = args.filter(a => !a.startsWith("--")).map(Number);
const frame = Number.isFinite(nums[0]) ? nums[0] : 120;
const cols = Number.isFinite(nums[1]) ? nums[1] : 80;
const rows = Number.isFinite(nums[2]) ? nums[2] : 30;

const { ghostData, ghostLayout, ghostScale, ghostPaint } = _internals;
const g = ghostData();
const lay = ghostLayout(cols, rows, g.w, g.h);
if (!lay) {
  console.log("terminal too small for the ghost");
  process.exit(0);
}
const scaled = ghostScale(g.raw[((frame % g.raw.length) + g.raw.length) % g.raw.length], g.w, g.h, lay.w, lay.h);
const lines = ghostPaint(scaled, { scroll: 6, fade: 1 });
const pad = " ".repeat(Math.max(0, Math.floor((cols - lay.w) / 2)));
for (const line of lines) console.log(pad + (ansi ? line : line.replace(/\x1b\[[0-9;]*m/g, "")));
