# Channel-observation records

The observation normalizer turns a manually recorded, minimal GitHub channel record into
deterministic JSON and Markdown. It does not access GitHub, verify the operator's assertions, read
issue text, accept screenshots, or infer people, attribution, buyers, customers, or revenue.

The registered experiment file is SHA-256 pinned by the validator and binds the exact public
release, user-owned repository namespace, commit, entry path, hashes, 14-day UTC window,
two-day final-capture deadline, repository description, and topics. The cumulative observation
file repeats those directly observed configuration fields, plus only owner-preview events,
controlled traffic-row facts, and minimal public issue metadata. The validator derives whether
the observed configuration matches; a caller cannot submit a bare "unchanged" boolean. Unknown
fields are rejected, so issue titles, bodies, comments, excerpts, screenshots, customer data, and
payment data cannot enter through this schema.

Every checked traffic row binds its capture to one exact 14-day retained window. For a `present`
exact-path row, qualified views are `max(0, raw views - logged owner previews inside that retained
window)`. Snapshots are never added together. An `absent` retained row produces `null` and
`unobservable`, never zero or "under ten". `not-checked` remains `not-observed`. Missing the
post-window final checkpoint is `incomplete`, and a day-14 capture after the registered two-day
deadline is rejected. A sensitive or uncertain issue accepts only its URL, timestamps, and
controlled disposition, halts the channel, and emits no author or submitted content.

Qualifying interest remains an operator-recorded, unverified account-level signal. It requires a
clear in-window issue, the frozen form hash, a non-owner user, the public boundary acknowledgement,
a generic in-scope outcome, and the first record for that account. The report never emits author
logins. Every result sets `checkout_authorized` to false and cannot supersede the charter gate.

When both report formats are requested, the tool stages both files before replacing each
destination. Each replacement is atomic, but the filesystem does not provide a portable two-file
transaction. A failed command means both outputs must be regenerated. The Markdown report embeds
the canonical JSON SHA-256 so a consumer can detect a stale or mixed pair.

From `support-eval-lab/`:

```sh
python -m support_eval_lab.observation \
  experiments/sel-gh-001.json observations/sel-gh-001-window.json \
  --as-of 2026-08-09T00:50:13Z \
  --json-out samples/channel-observation.json \
  --markdown-out samples/channel-observation.md
```

The activation record currently says only that its repeated configuration fields match the
registered frozen configuration, no owner browser entry preview was made, no labeled interest
issue was present at the recorded checkpoint, and traffic had not been checked. Its view result is
therefore unobserved, not zero. These are operator-recorded assertions; the offline normalizer does
not independently query GitHub.

## Source-limited platform captures

The current checked-row contract is stronger than GitHub's Popular content response. GitHub
describes the endpoint as returning up to ten popular content paths over the last 14 days, but the
response does not expose an exact window start, end, or cutoff. Capture time must not be substituted
for that undisclosed boundary. A capture without exact source bounds therefore stays outside the
normalizer and cannot update the cumulative observation. The current normalized report remains
unchanged with `null` raw and qualified views and a `not-observed` state; the ad hoc receipt does
not validate those values.

The `2026-08-10` source check is recorded separately in
`observations/sel-gh-001-source-check-2026-08-10.json`. Its absent exact-path result means only that
the target was not among the returned top paths at capture time. It does not mean zero views, fewer
than ten views, a unique-person count, or an exact day-one bucket. Any broader source schema must be
introduced prospectively and must not reinterpret historical normalizer records.
