# Báo cáo Day 09 — Đinh Quốc Tiến, 2A202603028

## 1. Kết luận trước

Pipeline nhận 202/224 ảnh, loại 22 ảnh ở intake (8 trùng byte, 5 rò rỉ test, 4 trùng gần, 3 ảnh nhỏ và 2 ảnh hỏng). Sau autofix và mô phỏng duyệt 80 ảnh, kết luận là **Hold**: không còn lỗi bắt buộc, nhưng 38/202 ảnh còn cảnh báo (18,81%), cao hơn ngưỡng 10%. Dataset 202 ảnh được xuất ở trạng thái bản nháp Hold, chưa phải bản phát hành.

## 2. Lỗi và phân việc

Số lượng dưới đây là số issue trong báo cáo vòng 1; các nhóm lỗi có thể cùng xuất hiện trên một ảnh.

| Mã lỗi | Số issue | Xử lý | Ghi chú |
|---|---:|---|---|
| POSSIBLE_MISSING | 53 | Người | Cảnh báo model thấy vật thể chưa có box |
| POSSIBLE_FALSE_POS | 29 | Người | Cảnh báo box nhãn không khớp dự đoán |
| POSSIBLE_LOOSE_BOX | 28 | Người | Cảnh báo box có thể lỏng/lệch |
| POSSIBLE_WRONG_CLASS | 18 | Người | Cảnh báo khác lớp cần xem ảnh |
| LEAK_TEST | 5 | Máy loại ảnh | Ảnh gần trùng với tập tham chiếu |
| EMPTY_LABEL | 12 | Người | Cần phân biệt ảnh nền với thiếu nhãn |
| DUP_IMAGE_EXACT | 8 | Máy loại ảnh | Trùng byte |
| BOX_OUT_OF_IMAGE | 8 | Máy cắt | Cắt box vào biên ảnh |
| DUP_IMAGE_NEAR | 4 | Máy loại ảnh | Trùng gần đúng |
| DUP_BOX | 7 | Máy xóa dòng | Dòng box lặp |
| MISSING_LABEL_FILE | 6 | Người | Máy không tự tạo nhãn |
| BAD_CLASS_ID | 6 | Máy xóa dòng | ID ngoài danh sách lớp |
| BOX_TINY | 6 | Người | Cảnh báo box nhỏ |
| BOX_ZERO | 4 | Máy xóa dòng | Box có chiều rộng/cao bằng 0 |
| CLASS_RARE | 4 | Người | Cảnh báo lớp hiếm |
| BAD_SIZE | 3 | Máy loại ảnh | Ảnh nhỏ hơn yêu cầu |
| BAD_FORMAT | 3 | Máy xóa dòng | Dòng nhãn sai định dạng |
| BOX_HUGE | 3 | Người | Box chiếm diện tích lớn |
| CORRUPT_IMAGE | 2 | Máy loại ảnh | Ảnh không mở được |
| BAD_CLASS_NAME | 2 | Máy sửa names | Chuẩn hóa tên lớp |

Autofix ghi 35 thay đổi: 20 drop_line, 8 clip_box, 6 needs_label và 1 rename_classes. Hàng đợi có 121 ảnh, xếp theo điểm ưu tiên cộng dồn từ loại cảnh báo và mức độ nặng; ngân sách 80 ảnh nên còn ảnh chưa được người duyệt.

## 3. Calibration

| Tham số | Giá trị đầu | Đã chọn | Precision / Recall | Lý do |
|---|---:|---:|---|---|
| duplicates.phash_dist | 2 | 14 | near duplicate: 1.00 / 0.50 → 1.00 / 0.67 | Ưu tiên precision vì báo nhầm sẽ loại ảnh tốt. Ảnh raw xác nhận khoảng cách 16 có cặp khác nội dung; ở 20 precision exact duplicate giảm còn 0.33. |
| second_opinion.conf | 0.25 | 0.6 | wrong class: 0.56 / 0.83 → 0.62 / 0.83; missing: 0.50 / 1.00 → 0.57 / 1.00 | Tăng precision mà vẫn giữ recall missing/wrong-class ở mức sweep này. Loose-box giảm recall; cần người xem xét. |

Calibration có thể đánh lừa vì chỉ có 39 ảnh và lỗi được chèn có chủ đích. Kiểm tra trực quan 7 cặp near duplicate raw cho thấy hai cặp khoảng cách 16 khác nội dung (img_0011/img_0008 và img_0177/img_0113); các cặp khoảng cách 0, 6, 10 là cùng cảnh hoặc rất gần. Vì vậy chọn 14 để tránh hai false positive đó, dù recall calib giảm từ 0.83 xuống 0.67.

## 4. Cửa chặn và điểm mù

Ở lần chạy chính, gate báo Hold vì 38/202 ảnh còn cảnh báo (18,81%), vượt ngưỡng 10%. Hàng đợi 125 ảnh vượt ngân sách 80, nên cảnh báo còn lại là lý do cần review thêm.

Ở lần chạy `--budget 0`, gate báo **Rework**, còn 6 lỗi bắt buộc và không xuất dataset (`exported: null`); đây là bằng chứng lỗi bắt buộc chặn xuất. Hai điểm mù đã biết: (1) checker second-opinion phụ thuộc dự đoán model, mà prediction cũng có thể sai; calibration cho wrong-class tại conf 0.6 có precision 0.62, tức còn false positive. (2) bộ calibration nhỏ (39 ảnh) và không bao phủ mọi biến thể trùng ảnh/lỗi tự nhiên, nên recall trên calib không đại diện chắc chắn cho raw.

## 5. Train raw vs clean

Chưa chạy train Colab. Phần so sánh raw/clean chưa có số liệu; cần chạy notebook theo docs/COLAB.md sau khi đẩy repo và export lên GitHub.

## 6. Quyết định và ghi chú AI

Quyết định hiện tại là **Hold**. Để tiến tới Release, cần người duyệt/khắc phục cảnh báo còn lại, chạy lại pipeline và chỉ phát hành nếu gate không còn lỗi bắt buộc và tỷ lệ cảnh báo dưới ngưỡng.

- Prompt chính: yêu cầu triển khai bốn module theo docstring và test của lab, tuân thủ ngưỡng cấu hình và không sửa dữ liệu gốc.
- Cách kiểm: chạy pytest toàn bộ (79 passed), calibration, pipeline chính và pipeline `--budget 0`; kiểm tra summary, danh sách lỗi và log fix.
- Lỗi AI phát hiện và sửa: lỗi cú pháp dấu nháy trong phần ghi `data.yaml` của autofix; pytest bắt lỗi khi import, sau đó đã sửa và toàn bộ test qua.
