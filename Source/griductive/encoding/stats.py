from dataclasses import dataclass


@dataclass(frozen=True)
class EncodingStats:
    """Lưu số biến chính, biến phụ và mệnh đề."""
    primary_vars: int = 0
    aux_vars: int = 0
    clauses: int = 0

    @property
    def total_vars(self) -> int:
        return self.primary_vars + self.aux_vars
