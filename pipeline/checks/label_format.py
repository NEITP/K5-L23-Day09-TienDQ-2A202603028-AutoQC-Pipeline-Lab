"""CHECK 2 — Dòng nhãn YOLO: sai định dạng, ID lớp lạ, box tràn ảnh, box rỗng, box lặp.   (Script 2 trong slide)   ★★

Test:  pytest tests/test_label_format.py -q

Mỗi dòng nhãn: `id cx cy w h` (5 số, toạ độ 0–1). Trả về list[Issue]; `Issue.line` = số dòng (đếm từ 1).

| code             | severity | khi nào                                                                  |
|------------------|----------|--------------------------------------------------------------------------|
| BAD_FORMAT       | ERROR    | không đúng 5 cột số (dùng `parse_yolo_line`, bắt `ValueError`)           |
| BAD_CLASS_ID     | ERROR    | id lớp ngoài 0..len(ds.classes)-1                                        |
| BOX_ZERO         | ERROR    | w <= 0 hoặc h <= 0                                                       |
| BOX_OUT_OF_IMAGE | ERROR    | mép box vượt [0,1] quá `cfg["label_format"]["overflow_tol"]`; extra={"overflow": mức tràn} |
| DUP_BOX          | ERROR    | cùng lớp với một dòng TRƯỚC ĐÓ và IoU > `dup_box_iou`; báo ở dòng SAU    |
| BOX_TINY         | WARN     | cạnh ngắn của box (px) < `min_box_px`  (cần `ds.image_size(stem)`)       |
| BOX_HUGE         | WARN     | w*h > `max_box_frac`                                                     |

Gợi ý
- Mép trái = x - w/2, mép phải = x + w/2 (xem câu hỏi "dòng YOLO nào lỗi?" trong slide).
- Một dòng hỏng (BAD_FORMAT, BAD_CLASS_ID, BOX_ZERO) thì `continue`, đừng kiểm tiếp hình học của dòng đó.
- Dòng thiếu cột làm script của slide dừng giữa chừng: đây là lý do phải `try/except`.
- `iou_xywh(a, b)` có sẵn trong common.py.
- Ngưỡng nằm trong `cfg["label_format"]` — đừng viết cứng số vào code.
"""
from ..common import ERROR, WARN, Issue, iou_xywh, parse_yolo_line  # noqa: F401


def run(ds, cfg):
    out = []
    t = cfg["label_format"]
    for p in ds.image_files():
        stem, prior = p.stem, []
        size = ds.image_size(stem)
        for line, raw in ds.read_label_lines(stem) or []:
            try:
                c, x, y, w, h = parse_yolo_line(raw)
            except ValueError as e:
                out.append(Issue("label_format", ERROR, "BAD_FORMAT", stem, str(e), line)); continue
            if not 0 <= c < len(ds.classes):
                out.append(Issue("label_format", ERROR, "BAD_CLASS_ID", stem, f"class id {c} không hợp lệ", line)); continue
            if w <= 0 or h <= 0:
                out.append(Issue("label_format", ERROR, "BOX_ZERO", stem, "width/height phải dương", line)); continue
            overflow = max(0, -(x-w/2), -(y-h/2), x+w/2-1, y+h/2-1)
            if overflow > t["overflow_tol"]: out.append(Issue("label_format", ERROR, "BOX_OUT_OF_IMAGE", stem, "box tràn ảnh", line, {"overflow": overflow}))
            box = (x, y, w, h)
            if any(pc == c and iou_xywh(box, pb) > t["dup_box_iou"] for pc, pb in prior): out.append(Issue("label_format", ERROR, "DUP_BOX", stem, "box trùng cùng lớp", line))
            prior.append((c, box))
            if size and min(w*size[0], h*size[1]) < t["min_box_px"]: out.append(Issue("label_format", WARN, "BOX_TINY", stem, "box nhỏ", line))
            if w*h > t["max_box_frac"]: out.append(Issue("label_format", WARN, "BOX_HUGE", stem, "box quá lớn", line))
    return out
