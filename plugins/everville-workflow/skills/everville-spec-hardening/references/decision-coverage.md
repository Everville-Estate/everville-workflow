# Decision Coverage

Use this reference to turn an implementation-bound specification into observable scenarios and owned decisions. Apply only the sections relevant to the scope.

## Build the decision map

For each actor or automated process, identify:

- entry conditions and required authority;
- accepted inputs and validation failures;
- state transitions and durable side effects;
- outputs, notifications, and audit evidence;
- cancellation, timeout, retry, and recovery behavior;
- limits, ordering rules, and idempotency expectations.

Separate facts supported by sources from assumptions introduced for the review. An assumption that changes product policy, money movement, access, legal posture, or irreversible data handling needs an owner rather than an inferred answer.

## Exercise representative scenarios

Cover the smallest useful set:

- expected success;
- invalid or incomplete input;
- unauthorized or stale actor;
- duplicate, delayed, or out-of-order request;
- dependency timeout or partial success;
- cancellation during work;
- restart or recovery after a durable side effect;
- migration or mixed-version operation when rollout is in scope.

Write scenarios as conditions and observable outcomes. Avoid implementation detail unless the specification intentionally fixes that detail.

## Convert gaps into decisions

A useful question names:

1. the unresolved behavior;
2. at least two materially different outcomes when alternatives exist;
3. the components or users affected;
4. the latest point at which the decision can be made safely;
5. the accountable owner.

Do not ask a human to approve obvious consistency repairs. Do not let the reviewer invent a business rule merely to eliminate an open item.

## Exit check

Decision coverage is sufficient when every in-scope state-changing scenario has a defined outcome, an explicit rejection, or a named open decision with implementation impact.
