"""Abstract Base Class for Clues.

Tác dụng:
    Định nghĩa hợp đồng trừu tượng (Interface/ABC) cho tất cả các loại manh mối (Clue)
    trong Griductive Solver mà không phụ thuộc vào triển khai cụ thể của từng loại clue.

Input:
    Các thuộc tính cơ bản của clue: id, owner (tọa độ ô sở hữu), clue_type (chuỗi định danh loại clue).

Output:
    Lớp trừu tượng Clue với 2 phương thức trừu tượng bắt buộc:
    - cells() -> tuple[Coord, ...]: trả về các ô liên quan (cho GUI highlight).
    - evaluate(assign: Mapping[Coord, bool]) -> bool: đánh giá ngữ nghĩa chân trị độc lập.
    Được kế thừa bởi clues/core.py và clues/extensions.py, được re-export bởi clues/base.py.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from griductive.domain.grid import Coord


class Clue(ABC):
    """Lớp cơ sở trừu tượng cho mọi manh mối trong bài toán.

    Attributes:
        id: Mã định danh duy nhất của manh mối (VD: "c01", "clue-A1").
        owner: Tọa độ ô sở hữu manh mối này (VD: "A1").
        clue_type: Loại manh mối dạng chuỗi (VD: "FACT", "SAME", "EXACTLY", "PARITY").
                   Lưu ý: Không lưu trường 'text' tĩnh; GUI sẽ tự động sinh văn bản mô tả.
    """

    def __init__(self, id: str, owner: Coord, clue_type: str) -> None:
        self.id = id
        self.owner = owner
        self.clue_type = clue_type

    @abstractmethod
    def cells(self) -> tuple[Coord, ...]:
        """Trả về tuple các tọa độ ô chịu sự tác động hoặc được đề cập trong clue.

        Phương thức này được GUI dùng để highlight các ô liên quan khi người dùng click xem clue.
        """
        pass

    @abstractmethod
    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        """Đánh giá ngữ nghĩa chân lý của clue trên một phép gán giá trị cụ thể.

        Quy ước: True = Criminal, False = Innocent.
        Hàm này là semantic evaluator độc lập, dùng để:
        - Kiểm tra tính hợp lệ của solution khi loader nạp puzzle.
        - Dùng làm Ground Truth Oracle để test_encoder_vs_eval.py kiểm tra chéo với CNF.

        Args:
            assign: Ánh xạ từ Coord sang bool (True nếu là Criminal, False nếu là Innocent).

        Returns:
            bool: True nếu phép gán thỏa mãn ngữ nghĩa của manh mối, ngược lại False.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, owner={self.owner!r}, type={self.clue_type!r})"
