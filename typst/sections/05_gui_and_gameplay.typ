#import "../components.typ": styled_table, callout_tip

#pagebreak()

= Giao diện và trải nghiệm chơi

== Bàn cờ

`BoardView` dựng grid $N times N$ với header cột `A, B, ...` và header hàng `1, 2, ...`. `CharacterCardWidget` hiển thị avatar, tọa độ, tên, nghề nghiệp và trạng thái khi đã biết. Card úp không lộ status hoặc clue. Click card úp mở `VerdictDialog`; click card đã lật kích hoạt spotlight clue.

== Điều khiển

#styled_table(
  (1.25fr, 2.2fr, 2.15fr),
  ([Điều khiển], [Hành vi], [Kết quả]),
  (
    ([Level selector], [Chọn preset puzzle trong `Source/puzzles/`], [Load lại KB_0 của level]),
    ([Restart], [Khôi phục puzzle hiện tại], [Chỉ còn initially revealed]),
    ([Hint], [Chọn ô forced đầu tiên], [Hiển thị status và clue liên quan]),
    ([Auto Solve], [Chạy agent theo QTimer], [Lật từng bước và cập nhật trace]),
    ([Click revealed card], [Xem clue và vùng tham chiếu], [Highlight subject/targets]),
  ),
  caption: [Các thao tác chính trên GUI],
)


== Verdict và phản hồi

Verdict đúng và được entailment chứng minh sẽ lật card, lưu status và hiển thị clue. Verdict chưa đủ dữ kiện trả `NOT_PROVABLE`; verdict ngược với status forced trả `CONTRADICTED`; ô đã lật trả `ALREADY_REVEALED`. Nếu public KB mâu thuẫn, engine hiển thị trạng thái `INCONSISTENT` riêng thay vì đánh đồng với một verdict sai.

== Thông báo hoàn tất

Khi tất cả ô đã lật, GUI chỉ mở một thông báo trong game:

#callout_tip[
  *VỤ ÁN HOÀN TẤT!*\
  Đã giải xong trong `k` bước suy luận.
]

Với chơi thủ công, `k` là số verdict được chấp nhận. Với Auto Solve, `k` là số `TraceStep` trong deduction trace. Các đồ họa khác của bàn cờ không bị thay đổi bởi thông báo này.
