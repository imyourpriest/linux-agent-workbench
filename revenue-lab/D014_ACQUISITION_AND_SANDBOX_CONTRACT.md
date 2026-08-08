# D-014 acquisition and sandbox contract

- Status: contract scaffold validated with project-owned synthetic records only
- Gate status: **blocked; no real acquisition or isolation platform exists**
- Applies to: every future public-repository report or review
- Does not apply to: the explicitly unverified, project-owned synthetic demo

This document defines the minimum hostile-source boundary required by D-014. It is a
design and acceptance contract, not evidence that the boundary currently exists. The
current Python scaffold validates strict synthetic records and always returns
`real_repository_eligible: false`.

## Security objective

Obtain content associated by an approved source host with an operator-requested commit,
independently verify the acquired Git object graph, convert it to a bounded content capsule,
and analyze that capsule in a second disposable environment with no network or target-code
execution path.

The result may be described as **source-host-attested commit content** only when the source
host binding and object verification both pass. It is not author-signed provenance unless a
separate maintainer signature is verified under a reviewed signature policy.

## Assets and trust boundaries

Protected assets are:

- host files, credentials, wallets, homelab access, identities, and network position;
- the integrity of repository identity, requested commit, analyzed bytes, and report labels;
- availability of the worker, controller, and output channel;
- the no-execution, no-egress, and resource-limit guarantees.

Trusted computing base:

- the operator-controlled request and approved source-host identity policy;
- the controller, hypervisor, immutable acquisition and analysis images, fixed binaries,
  trust store, verifier, syscall policy, and receipt-signing key;
- independently observed process, resource, mount, and egress telemetry.

Everything else is untrusted, including the URL and commit until validated, DNS and remote
responses, redirects, advertised refs, packs, every Git object and tree mode, filenames,
file content, repository configuration, hooks, attributes, submodules, LFS metadata, local
Git state, environment variables, analyzer input, and reportable strings.

## Adversary capabilities and required controls

| Attack | Required fail-closed control | Required future platform evidence |
|---|---|---|
| Poisoned local object, alternate, cache, or reference repository | Fresh per-job VM and empty volume; no host checkout, object cache, alternates, bundles, shared/reference clone, or inherited `GIT_*` value | Volume identity plus a planted-sentinel test proving the local object is inaccessible |
| Spoofed `.git/config`, origin, refs, replacement object, or promisor metadata | Create all acquisition metadata from the immutable image; never open a supplied `.git` directory or use its identity claims | Trace showing only controller-created configuration and storage were opened |
| Target-selected helper, hook, filter, submodule, LFS process, or target program | Fixed HTTPS transport only; fixed executable path; no checkout; hooks, filters, submodules, LFS, alternates, and non-HTTPS protocols forbidden | Zero unexpected child processes and marker-file tests for each execution vector |
| Wrong repository or commit | Bind canonical repository identity and requested object ID through an approved source-host adapter, then independently hash the commit, tree, and analyzed blobs | Signed receipt binding repository ID, URL, requested/resolved object ID, verifier, policy, and capsule hashes |
| Redirect or protocol confusion | Canonical HTTPS URL only; no credentials, query, fragment, default port, encoded path, cross-authority redirect, `file`, `ssh`, `git`, or `ext` transport | Adapter trace and rejection tests for every disallowed form |
| Pack, object, path, decompression, CPU, memory, process, disk, time, or output exhaustion | External hard limits and bounded parser; reject rather than partially report | Supervisor kill/rejection evidence at every stated boundary |
| Link, device, FIFO, socket, gitlink, duplicate path, absolute path, or traversal escape | Capsule contains normalized unique regular files and directories only; no `.git` tree | Hostile tree fixtures rejected before analysis |
| Analysis egress or lateral movement | Separate analysis VM with no virtual NIC, routes, DNS, host shares, home mount, secrets, or Docker socket | Hypervisor configuration plus an egress canary with zero packets |
| Target code or tool execution during analysis | Fixed analyzer entrypoint; no Git, shell, package manager, compiler, build tool, target interpreter invocation, or child process; deny process creation after startup | Process telemetry, syscall-policy evidence, and marker payloads showing zero execution |
| Capsule or receipt tampering | Controller-signed canonical manifest; read-only capsule; verify manifest and file digests immediately before analysis | Mutation tests fail before collector input is opened |
| Forged or excessive diagnostics | Controller-generated error codes and hard stdout/stderr/report caps; never echo untrusted secrets or arbitrary paths | Output-bomb tests and byte counts |

## Phase A: acquisition contract

1. The controller accepts only an operator-supplied canonical HTTPS repository URL, an
   explicit object format, and a full lowercase nonzero object ID. Target files cannot
   supply or override any request field.
2. The controller launches a newly created disposable acquisition VM from a pinned image
   with a newly provisioned empty volume. It mounts no checkout, cache, home directory,
   credential, secret, wallet, Docker socket, or host path.
3. Network policy permits only the approved source-host authority needed by the selected
   identity adapter and acquisition transport. URL IP literals and DNS results in loopback,
   link-local, private, reserved, or otherwise disallowed ranges are rejected and guarded
   against rebinding. Redirects to another authority and every non-HTTPS transport fail
   closed. No reusable credentials are present.
4. A pinned project-controlled client uses sterile controller-created configuration and a
   fixed executable directory. It may use only its pinned built-in HTTPS transport
   component. It performs no checkout and does not enable hooks, filters, submodules, LFS,
   partial/shallow fetching, promisor objects, alternates, bundles, or target-selected
   helpers. Target-controlled Git metadata is never read or trusted.
5. The approved source-host adapter establishes a canonical repository identifier and a
   source-host assertion that the requested commit belongs to that repository. The object
   bytes must be acquired from the same canonical authority under the identity policy. A
   redirect, missing/unadvertised commit, repository mismatch, or unverifiable binding
   blocks the job.
6. A project-owned bounded verifier, independent of target configuration, recomputes each
   Git object identifier from its type, length, and bytes; parses the requested commit;
   verifies its tree linkage; and verifies every tree and analyzed blob identifier. Unknown
   algorithms, malformed objects, missing links, duplicate normalized paths, symlinks,
   gitlinks, and non-regular entries fail closed. SHA-1 verification must use a
   Git-compatible collision-detecting implementation and reject a collision alarm.
7. The verifier creates a normalized content capsule with no `.git` directory or acquisition
   metadata. A canonical manifest binds every path and digest to the canonical repository,
   requested commit, source-host assertion, image, verifier, and identity-policy hashes.
8. The controller signs the receipt and manifest, seals the capsule read-only, destroys the
   acquisition VM, and transfers only the capsule, manifest, and receipt to Phase B.

The acquisition supervisor enforces no more than one CPU, 60 CPU seconds, 90 wall seconds,
1 GiB memory, 64 processes, 512 MiB combined acquisition storage and sealed analysis input,
and 1 MiB combined diagnostics. The sealed input size includes the capsule, manifest, and
receipt. A tighter source-adapter bound may apply.

The source-host adapter and independent object parser are unresolved implementation choices.
Git's own object store, repository configuration, `origin`, refs, or worktree state are not
acceptable substitutes for this proof.

## Phase B: analysis sandbox contract

The analysis phase uses a second disposable VM, not the acquisition VM. Before the capsule
is opened, the trusted supervisor must establish and attest all of these properties:

- no virtual NIC, DNS, route, shared filesystem, host/home mount, secret, credential,
  wallet, production access, or Docker socket;
- a fresh work directory, read-only input capsule, bounded output volume, empty home, fixed
  environment, dedicated unprivileged user, and no capabilities or privilege escalation;
- a fixed analyzer image and entrypoint that do not derive commands, imports, configuration,
  plugins, or executable paths from target content;
- no Git command, Git helper, hook, shell, package manager, build command, target interpreter,
  or child process; process-creation and network syscalls denied after the fixed analyzer
  starts;
- hypervisor/supervisor-enforced limits no greater than one CPU, 60 CPU seconds, 90 wall
  seconds, 1 GiB memory, one analysis workload process, 512 MiB input, 64 MiB writable work
  storage, 1 MiB combined stdout/stderr, and 2 MiB report output;
- kill and discard on any limit, policy, manifest, signature, or digest failure; no partial
  report is eligible.

The collector's existing entry, file, path, depth, per-file, aggregate-text, evidence, and
cooperative time bounds remain defense in depth. They do not replace the external limits.

## Signed envelopes and state contract

Every real envelope requires a controller signature from a key unavailable to both VMs. The
controller must issue a unique job nonce and store identifier, persist their one-time binding to
the request, and reject reuse. Three immutable, cross-hashed envelopes are required:

1. The **acquisition receipt**, signed before Phase B, binds the job nonce, request digest,
   canonical source URL and repository ID, requested and resolved commit, source-host identity
   assertion and policy digest, fresh-store identity and no-local-reuse result, target metadata
   and execution-vector results, object-graph verification results, acquisition image, verifier,
   capsule manifest, and capsule digests.
2. The **analysis authorization**, signed before Phase B starts, binds the job nonce, acquisition
   receipt digest, capsule digests, analysis image, syscall policy, required network/mount/identity
   state, and every hard limit. It is an instruction boundary, not evidence that enforcement
   occurred.
3. The **final analysis attestation**, signed only after Phase B is destroyed and trusted
   controller telemetry is validated, binds the job nonce, acquisition receipt and authorization
   digests, reverified capsule digests, observed network/mount/identity/process/resource state,
   telemetry reference, start/end time, result or controlled failure code, and either the final
   report digest or an explicit no-report disposition.

The synthetic validator has no signing key or trusted state, cannot establish freshness or detect
replay, and does not implement these real envelopes.

The allowed state sequence is:

1. request validated;
2. fresh acquisition environment attested;
3. source-host identity and requested commit proved;
4. object graph verified and capsule sealed;
5. acquisition receipt and manifest signed, then acquisition environment destroyed;
6. analysis authorization signed and separate no-network analysis environment attested;
7. capsule and acquisition receipt reverified;
8. bounded analysis completed or the job failed closed;
9. analysis environment destroyed and trusted telemetry validated;
10. final analysis attestation signed, with a report digest only for an eligible result.

Any missing, reordered, mismatched, unsigned, or policy-relaxed state makes the report
ineligible. An acquisition receipt cannot be overwritten with post-analysis claims, and a
self-declared receipt or sandbox record is not an attestation.

## Executable scaffold in this work unit

`release_readiness.acquisition_contract` exposes a bounded serialized-JSON entrypoint that
strictly validates the synthetic request, receipt, and sandbox records. Duplicate keys,
non-standard numbers, excessive bytes, nesting, and node counts fail closed before record
validation. It:

- accepts only two pinned, non-routable project-owned contract fixture identities and exact
  fixture URL/object-ID tuples;
- rejects missing and unknown fields, noncanonical URLs/object IDs, local-object reuse,
  target metadata trust, execution indicators, network-enabled or privileged analysis,
  missing isolation controls, mismatched declared capsule-to-analysis input digests, and
  absent, excessive, or combined acquisition/sealed-input hard limits;
- computes deterministic SHA-256 record fingerprints; these are not signatures and can be
  recomputed by a caller;
- performs no acquisition, filesystem scan, network call, subprocess launch, Git command,
  or analysis;
- always emits `synthetic_policy_shape_checked_no_platform_evidence`,
  `platform_evidence_status: absent`, and `real_repository_eligible: false`.

Every `fixture_asserts_*` field and every `declared_*` digest or byte count is untrusted test
input. The scaffold checks shape, exact bindings, and safe policy values only. It does not
verify a signature, inspect a capsule, prove freshness, or establish the truth of an
assertion. A future real implementation requires a different signed-envelope schema and a
trusted controller verifier; this synthetic schema must not be promoted into that role.
Only the fixture identities and their URL/object-ID/source-ID tuples are pinned; receipt and
sandbox values are deliberately variable hostile record-shape inputs for negative tests.

The unit tests exercise only project-owned dictionaries and JSON strings. Passing them proves
the validator's fail-closed policy behavior, not the truth of a receipt, upstream identity,
VM disposal, network isolation, privilege state, resource enforcement, or no-execution
telemetry.

## Future acceptance tests before the gate can pass

Use only project-owned hostile repositories and infrastructure fixtures until independent
review completes:

1. Serve a synthetic commit graph from an approved test source adapter; accept the exact
   repository/commit pair and reject wrong repository IDs, wrong commits, redirects,
   malformed or missing objects, and an unavailable identity assertion.
2. Plant unique objects in a host checkout, cache, alternate, bundle, and reference store;
   prove none is visible in the fresh acquisition volume or final capsule.
3. Include hostile config, `fsmonitor`, hooks, custom helpers, attributes, filters,
   submodules, LFS/promisor data, executable marker files, and command-shaped filenames;
   observe no target-controlled child process and no marker.
4. Reject symlink, gitlink, device/FIFO/socket, absolute/traversal, case/Unicode-colliding,
   duplicate, oversized, deeply nested, decompression-bomb, and malformed-pack fixtures.
5. Tamper with each request, receipt, manifest, and capsule binding; every mutation must stop
   before analysis.
6. Attempt DNS, TCP, UDP, and local-socket egress from the analysis fixture; independently
   observe no NIC and zero packets.
7. Exercise CPU, memory, process, disk, blocking-I/O, wall-time, stdout/stderr, and report
   bombs; the supervisor must kill or reject at the exact bound and emit capped diagnostics.
8. Verify the fixed unprivileged identity, empty capabilities, mount table, process tree,
   syscall denials, read-only input, and destruction of both VMs and job volumes.

## Stop point

The next step requires choosing and operating a real disposable VM/isolation platform,
building pinned images and source-host adapters, and independently observing enforcement.
That exceeds this bounded work unit and is intentionally not attempted. Until those platform
requirements pass adversarial tests, no customer or third-party checkout may enter either
the demo collector or a purported D-014 path, and the revenue gate remains blocked.
