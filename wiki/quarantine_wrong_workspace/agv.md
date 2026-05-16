---
id: "agv"
title: "AGV (Automated Guided Vehicle)"
type: entity
status: grounded
sources:
  - ref: "drafts/ch-ng-397_draft.md"
    type: draft
    title: "Chương 397: Tinh thạch an toàn (Tham chiếu cơ chế tự động)"
confidence: high
tags: ["automation", "robotics", "logistics"]
---

## Definition
**AGV** là phương tiện tự động dẫn đường, được sử dụng để vận chuyển hàng hóa, nguyên vật liệu trong kho bãi hoặc nhà máy mà không cần sự can thiệp trực tiếp của con người.

## How it works
AGV di chuyển theo các tuyến đường được lập trình sẵn thông qua các công nghệ dẫn đường như băng từ, laser, hoặc định vị bản đồ (SLAM). Trong bối cảnh mạt thế, các thiết bị này có thể được tích hợp với "Tinh thạch an toàn" để vận hành trong các vùng bảo vệ.

## Components
- **Hệ thống dẫn đường:** Cảm biến laser/từ tính.
- **Bộ điều khiển trung tâm:** Xử lý lộ trình.
- **Cơ cấu chấp hành:** Động cơ di chuyển và nâng hạ.
- **Pin/Năng lượng:** Nguồn cấp điện.

## Relations
- **WMS:** Nhận lệnh xuất nhập kho từ hệ thống quản lý kho.
- **MOM:** Báo cáo trạng thái vận hành cho hệ thống quản lý sản xuất.
