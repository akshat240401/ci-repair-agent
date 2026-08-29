# Retry Proof Block

Adds deterministic proof that the repair loop can recover from a bad first attempt.

The integration test forces:
1. first patch applies but fails the targeted test;
2. verification feedback is sent to the retry agent;
3. second patch succeeds;
4. final result is VERIFIED_REPAIR;
5. exactly two attempts are recorded.

Also tests circuit breakers for duplicate patch, no-progress, and A -> B -> A oscillation.

Run:

```powershell
pytest -q tests
```

No API call is required.
