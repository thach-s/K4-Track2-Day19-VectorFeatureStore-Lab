# Reflection — Lab 19

**Họ và tên:** Đậu Văn Thạch
**MSSV:** 2A202602592
**Cohort:** A20-K4
**Path đã chạy:** Lite

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set 50 queries, BM25 có lợi thế với nhóm exact vì truy vấn chứa trực tiếp các thuật ngữ xuất hiện trong tài liệu. Semantic search phù hợp hơn với paraphrase vì có thể tìm theo ý nghĩa dù từ ngữ không trùng khớp; tuy nhiên, mô hình bge-small-en trong môi trường Lite còn hạn chế với tiếng Việt. Hybrid RRF hoạt động tốt nhất ở nhóm mixed và đạt kết quả trung bình cao nhất: 78,6%, so với 77,8% của BM25 và 73,2% của semantic. Nguyên nhân là hybrid kết hợp tín hiệu từ khóa chính xác của BM25 với khả năng nhận biết ngữ nghĩa của vector search.

Tôi sẽ không dùng hybrid khi truy vấn chủ yếu là mã sản phẩm, tên riêng hoặc thuật ngữ cần khớp chính xác; khi đó pure BM25 đơn giản, nhanh và dễ giải thích hơn. Ngược lại, nếu người dùng thường diễn đạt lại câu hỏi, dùng nhiều từ đồng nghĩa và hệ thống có mô hình embedding tiếng Việt tốt, pure vector có thể phù hợp hơn. Hybrid cũng không cần thiết khi chi phí tính toán hoặc yêu cầu độ trễ rất nghiêm ngặt.

---

## Điều ngạc nhiên nhất khi làm lab này

Điều ngạc nhiên nhất là môi trường Lite vẫn có thể chạy đầy đủ vector search, hybrid search và Feast mà không cần Docker hay GPU. Phần code cần sửa không nhiều vì scaffold đã khá hoàn chỉnh, nhưng việc chạy end-to-end mới phát hiện lỗi thực tế: API cần hơn 60 giây để index 1.000 tài liệu trên CPU. Sau khi điều chỉnh thời gian chờ, toàn bộ 41 test đều vượt qua và hybrid search vẫn đạt P99 46,2 ms.

---

## Bonus challenge

- [ ] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
