// Hosted-only adapter for Ajv 8.20.0; do not execute locally.
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import Ajv2020 from "ajv/dist/2020.js";

const project = process.argv[2] || ".";
const root = path.join(project, "interop", "maintainer-policy-declaration", "compatibility-v1");
const read = (name) => fs.readFileSync(name, "utf8");
const strictParse = (raw) => JSON.parse(raw);
const strictInstanceParse = (raw) => {
  const MAX_RAW_BYTES = 65_536;
  const MAX_DEPTH = 64;
  const MAX_NODES = 4_096;
  if (Buffer.byteLength(raw, "utf8") > MAX_RAW_BYTES) throw new Error("raw JSON exceeds byte limit");
  let index = 0;
  let nodes = 0;
  const whitespace = () => { while (/[\u0009\u000a\u000d\u0020]/.test(raw[index] || "")) index += 1; };
  const stringToken = () => {
    if (raw[index] !== '"') throw new Error("expected JSON string");
    const start = index++;
    while (index < raw.length) {
      const character = raw[index++];
      if (character === '"') return strictParse(raw.slice(start, index));
      if (character.charCodeAt(0) <= 0x1f) throw new Error("unescaped control in JSON string");
      if (character === "\\") {
        if (index >= raw.length) throw new Error("unterminated JSON escape");
        const escape = raw[index++];
        if ('"\\/bfnrt'.includes(escape)) continue;
        if (escape === "u" && /^[0-9a-fA-F]{4}$/.test(raw.slice(index, index + 4))) { index += 4; continue; }
        throw new Error("invalid JSON escape");
      }
    }
    throw new Error("unterminated JSON string");
  };
  const value = (depth) => {
    if (depth > MAX_DEPTH) throw new Error("JSON depth exceeds limit");
    nodes += 1;
    if (nodes > MAX_NODES) throw new Error("JSON node count exceeds limit");
    whitespace();
    if (raw[index] === "{") {
      index += 1; whitespace();
      const keys = new Set();
      if (raw[index] === "}") { index += 1; return; }
      while (true) {
        const key = stringToken();
        if (keys.has(key)) throw new Error("duplicate key in JSON object");
        keys.add(key); whitespace();
        if (raw[index++] !== ":") throw new Error("expected JSON colon");
        value(depth + 1); whitespace();
        const delimiter = raw[index++];
        if (delimiter === "}") return;
        if (delimiter !== ",") throw new Error("expected JSON object delimiter");
        whitespace();
      }
    }
    if (raw[index] === "[") {
      index += 1; whitespace();
      if (raw[index] === "]") { index += 1; return; }
      while (true) {
        value(depth + 1); whitespace();
        const delimiter = raw[index++];
        if (delimiter === "]") return;
        if (delimiter !== ",") throw new Error("expected JSON array delimiter");
        whitespace();
      }
    }
    if (raw[index] === '"') { stringToken(); return; }
    for (const literal of ["true", "false", "null"]) {
      if (raw.startsWith(literal, index)) { index += literal.length; return; }
    }
    const number = raw.slice(index).match(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/);
    if (number) { index += number[0].length; return; }
    throw new Error("invalid JSON value");
  };
  value(1); whitespace();
  if (index !== raw.length) throw new Error("trailing JSON content");
  return strictParse(raw);
};
const preflight = (value) => {
  const allowed = new Set(["#/$defs/policy", "#/$defs/expectation"]);
  const pending = [value];
  while (pending.length) {
    const current = pending.pop();
    if (Array.isArray(current)) pending.push(...current);
    else if (current && typeof current === "object") {
      for (const [key, child] of Object.entries(current)) {
        if (key === "$dynamicRef" || key === "$recursiveRef") throw new Error("dynamic reference rejected");
        if (key === "$ref" && !allowed.has(child)) throw new Error("nonlocal reference rejected");
        pending.push(child);
      }
    }
  }
};
const sorted = (value) => Array.isArray(value) ? value.map(sorted) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, sorted(value[key])])) : value;
const pointer = (value, rawPointer, replacement, remove = false) => {
  const parts = rawPointer.slice(1).split("/");
  let parent = value;
  for (const part of parts.slice(0, -1)) parent = parent[part];
  if (remove) delete parent[parts.at(-1)]; else parent[parts.at(-1)] = replacement;
};
const schema = strictParse(read(path.join(project, "interop/maintainer-policy-declaration/v1/schema.json")));
const base = strictParse(read(path.join(project, "interop/maintainer-policy-declaration/v1/corpus.json")));
const supplemental = strictParse(read(path.join(root, "supplemental-corpus.json")));
const expected = strictParse(read(path.join(root, "expected-results.json")));
const manifestRaw = read(path.join(root, "manifest.json"));
const manifest = strictParse(manifestRaw);
const preparedReceipt = strictParse(read(path.join(root, "prepared-receipt.json")));
const manifestSha256 = crypto.createHash("sha256").update(manifestRaw).digest("hex");
if (preparedReceipt.manifest_sha256 !== manifestSha256) throw new Error("prepared receipt manifest binding differs");
preflight(schema);
const ajv = new Ajv2020({ strict: true, strictTypes: true, allowUnionTypes: true, allErrors: true, validateFormats: false });
const validate = ajv.compile(schema);
const vectors = base.vectors.map((item) => [item.id, item.payload]);
for (const item of supplemental.vectors) {
  const value = structuredClone(supplemental.base_payload);
  for (const operation of item.operations) {
    if (operation.op === "delete") pointer(value, operation.pointer, null, true);
    else if (operation.op === "set") pointer(value, operation.pointer, operation.value);
    else if (operation.op === "repeat") pointer(value, operation.pointer, operation.value.repeat(operation.count));
    else throw new Error("unknown mutation");
  }
  vectors.push([item.id, JSON.stringify(sorted(value))]);
}
const expectedById = new Map(expected.vectors.map((item) => [item.id, item]));
const boundById = new Map(manifest.bindings.vector_contracts.map((item) => [item.id, item]));
const observations = vectors.map(([id, raw]) => {
  let value; let parseResult;
  try { value = strictInstanceParse(raw); parseResult = "accept"; } catch { parseResult = "reject"; }
  const schemaResult = parseResult === "reject" ? "not_run" : (validate(value) ? "accept" : "reject");
  const contract = expectedById.get(id);
  const rawPayloadSha256 = crypto.createHash("sha256").update(raw).digest("hex");
  const bound = boundById.get(id);
  if (rawPayloadSha256 !== bound.raw_payload_sha256) throw new Error(`raw payload binding mismatch: ${id}`);
  if (bound.parse_expected !== contract.parse || bound.schema_expected !== contract.schema || bound.structural_agreement_denominator !== contract.structural_agreement_denominator) throw new Error(`expected outcome binding mismatch: ${id}`);
  if (parseResult !== contract.parse || schemaResult !== contract.schema) throw new Error(`outcome mismatch: ${id}`);
  return { id, raw_payload_sha256: rawPayloadSha256, observed_parse: parseResult, observed_schema: schemaResult, expected_parse: contract.parse, expected_schema: contract.schema, structural_agreement_denominator: contract.structural_agreement_denominator };
});
const inventory = {};
for (const name of ["ajv", "fast-deep-equal", "fast-uri", "json-schema-traverse", "require-from-string"]) inventory[name] = strictParse(read(path.join(root, "node_modules", name, "package.json"))).version;
const required = { ajv:"8.20.0", "fast-deep-equal":"3.1.3", "fast-uri":"3.1.0", "json-schema-traverse":"1.0.0", "require-from-string":"2.0.2" };
if (JSON.stringify(inventory) !== JSON.stringify(required)) throw new Error("installed dependency inventory differs");
console.log(JSON.stringify({ adapter:"node_ajv_8_20_0", manifest_sha256:manifestSha256, configuration:expected.validator_configurations.node_ajv_8_20_0, installed_dependencies:inventory, vectors:observations }, null, 2));
