from griductive.domain.grid import Coord, coord_to_row_major_index, index_to_coord


class VarMap:

    def __init__(self, size: int) -> None:
        self.size = size
        self.num_primary_vars = size * size
        self._next_aux_var = self.num_primary_vars + 1

    def coord_to_var(self, coord: Coord) -> int:
        return coord_to_row_major_index(coord, self.size)

    def var_to_coord(self, var_id: int) -> Coord:
        return index_to_coord(var_id, self.size)

    def is_primary_var(self, var_id: int) -> bool:
        return 1 <= abs(var_id) <= self.num_primary_vars

    def allocate_aux_var(self) -> int:
        var_id = self._next_aux_var
        self._next_aux_var += 1
        return var_id

    def allocate_aux_vars(self, count: int) -> tuple[int, ...]:
        return tuple(self.allocate_aux_var() for _ in range(count))

    @property
    def num_aux_vars(self) -> int:
        return self._next_aux_var - (self.num_primary_vars + 1)

    @property
    def total_vars(self) -> int:
        return self._next_aux_var - 1
