---
id: "wms"
title: "WMS (Warehouse Management System)"
type: entity
status: grounded
sources:
  - ref: "drafts/ch-ng-425_draft.md"
    type: draft
    title: "Chương 425: Tham chiếu hệ thống quản lý kho"
confidence: high
tags: ["warehouse", "logistics", "inventory"]
---

## Definition
**WMS** là hệ thống quản lý kho hàng, được thiết kế để kiểm soát và tối ưu hóa mọi hoạt động diễn ra trong kho, từ việc nhập hàng, lưu kho, đến xuất hàng và kiểm kê.

## How it works
WMS theo dõi vị trí chính xác của từng mặt hàng thông qua mã vạch (Barcode) hoặc RFID. Nó tính toán vị trí lưu kho tối ưu và tạo ra các lộ trình lấy hàng hiệu quả nhất cho nhân viên hoặc robot AGV.

## Components
- **Quản lý tồn kho:** Theo dõi số lượng thực tế.
- **Quản lý vị trí (Location Management):** Bản đồ số của kho.
- **Quản lý đơn hàng:** Xử lý danh sách lấy hàng (Pick list).

## Relations
- **MOM:** Cung cấp thông tin tồn kho nguyên liệu cho sản xuất.
- **AGV:** Gửi lệnh di chuyển đến các vị trí lưu kho để thực hiện việc lấy/cất hàng.
