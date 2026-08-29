from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class LoopDetector:
    seen_patch_hashes: set[str] = field(default_factory=set)
    seen_repo_hashes: set[str] = field(default_factory=set)
    failure_signatures: list[str] = field(default_factory=list)

    def record_patch(self, value: str) -> bool:
        duplicate = value in self.seen_patch_hashes
        self.seen_patch_hashes.add(value)
        return duplicate

    def record_repo_state(self, value: str) -> bool:
        duplicate = value in self.seen_repo_hashes
        self.seen_repo_hashes.add(value)
        return duplicate

    def record_failure(self, value: str) -> bool:
        repeated = bool(self.failure_signatures and self.failure_signatures[-1] == value)
        self.failure_signatures.append(value)
        return repeated

    def has_two_state_oscillation(self) -> bool:
        return (
            len(self.failure_signatures) >= 3
            and self.failure_signatures[-3] == self.failure_signatures[-1]
            and self.failure_signatures[-3] != self.failure_signatures[-2]
        )
