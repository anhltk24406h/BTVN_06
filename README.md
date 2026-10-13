# Bài tập 06 — Sự kiện địa chính trị và lợi suất S&P 500

Mở **[notebook/bai06.ipynb](notebook/bai06.ipynb)** để đọc tiểu luận tiếng Việt, bảng nguồn, các biểu đồ và kết quả thống kê đã thực thi.

## Dữ liệu và đầu ra

- `data/sp500.csv`: bản sao nguyên nội dung tệp Investing.com do người dùng cung cấp; tệp gốc được giữ lại, không tải dữ liệu giá mới.
- `data/events.csv`: ngày thực tế, tên/mô tả, hai URL Reuters/AP đã mở và đọc, cùng `date_assigned` do tiền xử lý bổ sung.
- `data/events_research.md`: nhật ký truy vấn, đối chiếu nguồn, ứng viên chọn/loại, lý do điều chỉnh mốc ngày và thiên lệch chọn mẫu.
- `script/preprocessing.py`: làm sạch dữ liệu, kiểm tra và gán sự kiện; in báo cáo bằng tiếng Việt.
- `data/processed.csv`: đúng các cột `date, price, Y, Y_lag1, D, event`. Đơn vị `Y` là lợi suất log gốc, không phải phần trăm. Missing do tạo lợi suất và độ trễ được giữ trong CSV.
- `notebook/bai06.ipynb`: kết hợp nghiên cứu định tính và phân tích chuỗi thời gian; kết quả và diễn giải số được tạo từ code.

## Chạy lại trên Windows / PowerShell

Từ thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe script\preprocessing.py
.\.venv\Scripts\python.exe -m unittest discover -s script -p test_preprocessing.py -v
.\.venv\Scripts\python.exe script\run_notebook.py
```

`requirements-lock.txt` ghi chính xác các phiên bản đã chạy; `requirements.txt` ghi khoảng phiên bản phụ thuộc. Khi mở trong IDE, chọn interpreter/kernel `.venv\Scripts\python.exe` và chạy các cell từ đầu. Script `run_notebook.py` tạo kernel sạch bằng đúng Python đang chạy, lưu output vào notebook sau khi thành công và giữ cache trong `.cache` của dự án; không cần đăng ký kernel toàn hệ thống.

Tiền xử lý mặc định tìm dữ liệu theo vị trí script nên có thể gọi từ thư mục khác; có thể chỉ định một bản dự án bằng `--root`. Gán ngày dùng lịch quan sát trong CSV, không dùng lịch ngày làm việc thông thường. Một phiên thực tế bị thiếu trong CSV có thể ảnh hưởng việc gán ngày; không nội suy giá để che vấn đề đó.

## Cách đọc kết quả

Mô hình chính là `Y ~ const + Y_lag1 + D`, ước lượng OLS. Suy luận và khoảng tin cậy dùng Newey–West, kernel Bartlett, độ trễ đã chốt, hiệu chỉnh hữu hạn và phân phối chuẩn. Notebook so sánh độ khớp hồi cứu với AR(1), đồng thời dự báo AR(1) cuốn chiếu chỉ dùng quá khứ. Cửa sổ `[0,+1]` mở rộng dummy sang phiên kế tiếp; hệ số của nó là chênh lệch mỗi phiên thuộc cửa sổ, không phải tổng tác động hai phiên.

Sự kiện được chọn hồi cứu, ưu tiên phiên giảm; một số cú sốc đã có cảnh báo. Sự kiện năm 2026 có lợi suất dương vẫn được giữ theo yêu cầu trải đều các năm. Kết quả là liên hệ thống kê của mẫu đã chọn, không nhận diện tác động nhân quả; không thay đổi sự kiện theo dấu hoặc p-value của hệ số.
