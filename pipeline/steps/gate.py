"""BƯỚC 4 — Cửa chặn: quyết định Release / Hold / Rework.   ★

Test:  pytest tests/test_gate.py -q

Cây quyết định Day 07 (slide Day 09: "Lỗi bắt buộc chặn pipeline; lỗi cảnh báo chuyển người xem"):

  còn ≥ 1 lỗi bắt buộc (severity ERROR)                          -> "Rework"
  không còn lỗi bắt buộc, nhưng tỉ lệ ẢNH còn cảnh báo
      >= cfg["gate"]["warn_ratio_hold"]                          -> "Hold"
  còn lại                                                        -> "Release"

Tỉ lệ cảnh báo = (số ẢNH khác nhau có ≥ 1 cảnh báo) / (tổng số ảnh).  Chú ý:
- chỉ đếm issue có `image` nằm trong `image_stems` (bỏ "<dataset>", "data.yaml");
- bỏ qua ảnh nằm trong `reviewed` (người đã xem, cảnh báo của ảnh đó coi như đã xử lý) — nhưng LỖI BẮT BUỘC thì không bao giờ được bỏ qua;
- mẫu số là số ảnh, không phải số issue.

Trả về dict: decision, n_errors, n_warn_images, n_images, warn_ratio (làm tròn 4 chữ số), reasons (list[str], giải thích bằng tiếng Việt, có số liệu).
"""
from ..common import ERROR, WARN  # noqa: F401


def decide(issues, image_stems, cfg, reviewed=frozenset()):
    images = set(image_stems); errors = sum(i.severity == ERROR for i in issues)
    warns = {i.image for i in issues if i.severity == WARN and i.image in images and i.image not in reviewed}
    n = len(images); ratio = round(len(warns) / n, 4) if n else 0
    decision = "Rework" if errors else "Hold" if ratio >= cfg["gate"]["warn_ratio_hold"] else "Release"
    reasons = ([f"Còn {errors} lỗi bắt buộc; cần làm lại."] if errors else [f"Còn cảnh báo ở {len(warns)}/{n} ảnh (tỷ lệ {ratio:.4f}); quyết định {decision}."])
    return dict(decision=decision, n_errors=errors, n_warn_images=len(warns), n_images=n, warn_ratio=ratio, reasons=reasons)
