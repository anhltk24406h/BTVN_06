# Nhật ký nghiên cứu sự kiện — Bài tập 06

## Truy cập và phạm vi

- Ngày tra cứu: 09/10/2026 (Asia/Bangkok), trong phiên lập kế hoạch và xác nhận lại khi triển khai.
- Web search và công cụ mở trang hoạt động. **Không dùng danh sách dự phòng để thay thế nghiên cứu.**
- Dữ liệu giá do người dùng cung cấp: `S&P 500 Historical Data.csv`, nguồn Investing.com theo mô tả người dùng; không tải lại, không tự xác nhận ngày tải ban đầu.
- Đọc trực tiếp tệp bằng Python: 945 dòng; khoảng 2023-01-03–2026-10-08. Các lợi suất bên dưới đều được tính từ cột Price trong tệp này, không lấy số thị trường của báo.
- Nhật ký và bảng sự kiện được lập trước script tiền xử lý. Tập sự kiện chốt trước khi ước lượng hệ số; không thay đổi theo kết quả hồi quy.

## Các truy vấn đã dùng

- `Reuters October 1 2024 Iran missiles Israel attack`
- `Reuters AP Italy surprise windfall tax banks August 8 2023`
- `Reuters AP US Israel strikes Iran February 28 2026`
- `Reuters AP China retaliatory tariffs 34% April 4 2025`
- `Reuters June 24 2023 Wagner seized Rostov Moscow mutiny AP`
- `AP Iran attack Israel April 13 2024 PBS Reuters`
- `Reuters February 28 2026 US Israel attack Iran investing.com`
- `AP China April 4 2025 34 percent tariff PBS`
- `site.pbs.org/newshour June 24 2023 Wagner Rostov AP`
- `site.pbs.org/newshour February 28 2026 Israel US attack Iran AP`
- `site.investing.com Reuters April 13 2024 Iran launches drones Israel`
- `site.cnbc.com/2024/10/01 Iran missile attack Israel`
- `site.cnbc.com/2025/04/04 China 34% tariffs`
- `"China slaps a 34% tax" "apnews.com/article/"`
- `"China" "April 4, 2025" "tariffs" site.apnews.com/article/`

Sau tìm kiếm đã mở các URL nguồn trong bảng dưới; dùng liên kết tham khảo của Wikipedia để tìm URL bài AP đầy đủ. Việc tra cứu trực tiếp một URL không được ghi thành truy vấn tìm kiếm mới.

## Năm sự kiện được chọn

Đơn vị hai cột lợi suất là phần trăm; `100Y = 100 ln(P_t/P_{t-1})`, lợi suất đơn `100(P_t/P_{t-1}-1)`. Giá và thứ tự phiên lấy hoàn toàn từ CSV.

| Ngày thực tế | Ngày gán | Sự kiện | 100Y (%) | Lợi suất đơn (%) | Hai nguồn đã mở và đọc |
|---|---|---|---:|---:|---|
| 2023-06-24 | 2023-06-26 | Wagner chiếm sở chỉ huy quân sự tại Rostov-on-Don và tiến về Moskva | -0.449688 | -0.448678 | [Reuters](https://www.investing.com/news/world-news/mutinous-russian-mercenary-chief-says-he-and-his-men-wont-turn-themselves-in-3112399); [AP](https://apnews.com/article/russia-ukraine-wagner-prigozhin-9acbdf1eda849692ca0423a4116058d1) |
| 2024-04-13 | 2024-04-15 | Iran mở cuộc tấn công trực tiếp bằng drone và tên lửa vào Israel | -1.209413 | -1.202129 | [Reuters](https://www.investing.com/news/world-news/sirens-blasts-sound-across-israel-after-iran-launches-retaliatory-attack-3377350); [AP](https://apnews.com/article/strait-of-hormuz-vessel-33fcffde2d867380e98c89403776a8ac) |
| 2024-10-01 | 2024-10-01 | Iran phóng tên lửa đạn đạo vào Israel | -0.936785 | -0.932411 | [Reuters](https://www.investing.com/news/world-news/us-condemns-irans-attack-as-significant-escalation-3643691); [AP](https://apnews.com/article/israel-lebanon-hezbollah-gaza-news-10-01-2024-eb175dff6e46906caea8b9e43dfbd3da) |
| 2025-04-04 | 2025-04-04 | Trung Quốc công bố thuế trả đũa 34% đối với hàng Mỹ | -6.160907 | -5.974962 | [Reuters](https://www.investing.com/news/economy-news/china-to-impose-tariffs-of-34-on-all-us-goods-from-april-10-3967314); [AP](https://apnews.com/article/china-tariff-trade-trump-earths-02cd23e913649f32985f075058e787c4) |
| 2026-02-28 | 2026-03-02 | Mỹ và Israel mở cuộc tấn công vào Iran | 0.039824 | 0.039832 | [Reuters](https://www.investing.com/news/world-news/israel-us-launched-strikes-as-iranian-leader-met-with-inner-circle-sources-say-4533450); [AP](https://apnews.com/article/iran-us-explosion-tehran-c2f11247d8a66e36929266f2c557a54c) |

### Đối chiếu ngày và loại cú sốc

1. **Wagner, 24/06/2023:** Reuters mô tả lực lượng đã chiếm một thành phố phía nam; AP xác nhận kiểm soát sở chỉ huy Rostov vào sáng thứ Bảy. Chọn mốc chiếm sở chỉ huy và tiến về Moskva, không gọi 24/06 là ngày khởi đầu toàn bộ nổi loạn (khởi đầu 23/06). Đây là leo thang vũ trang; tuy nhiên AP ghi nhận tình báo Mỹ đã theo dõi việc tập hợp lực lượng từ trước.
2. **Iran–Israel, 13/04/2024:** Reuters xác định bắt đầu tối thứ Bảy; AP mô tả hành động tấn công tối thứ Bảy, với đánh chặn sang Chủ Nhật. Chọn ngày bắt đầu 13/04, không chọn ngày bài được cập nhật 14/04. Nguy cơ trả đũa đã được cảnh báo: tính bất ngờ được hiểu là thời điểm, hình thức và mức độ leo thang, không phải hoàn toàn không có thông tin trước.
3. **Iran–Israel, 01/10/2024:** hai hãng tin xác nhận tấn công ngày thứ Ba 01/10. Là một đợt tấn công riêng, cách xa đợt tháng Tư. Tin cảnh báo trong ngày có thể đã khiến thị trường phản ứng trước lúc tên lửa phóng.
4. **Trung Quốc, 04/04/2025:** cả Reuters và AP xác nhận **công bố** thuế trả đũa bổ sung 34% vào thứ Sáu 04/04; hiệu lực 10/04. Đây là bước leo thang chính sách thương mại; không lấy ngày hiệu lực thay ngày công bố. Trả đũa có thể được dự đoán một phần; mức thuế và gói biện pháp cụ thể là thông tin mới.
5. **Mỹ–Israel–Iran, 28/02/2026:** Reuters xác nhận mở cuộc tấn công thứ Bảy 28/02; AP cùng xác nhận ngày thứ Bảy, ảnh và tường thuật ghi ngày 28/02. Ngày 01/03 ở danh sách dự phòng là ngày tin tiếp diễn/xác nhận, không phải ngày bắt đầu. Phiên gán có lợi suất dương; vẫn giữ để phủ năm 2026 theo lựa chọn người dùng. Căng thẳng và đe dọa đã có trước.

Reuters được đọc qua bản đăng lại tại Investing.com, có byline Reuters; nguồn thứ hai là AP News. Hai trang đăng lại cùng Reuters **không** được coi là hai nguồn độc lập. Không thấy mâu thuẫn về ngày của các mốc cụ thể được chọn; các khác biệt 23/24, 13/14 và 28/01 phản ánh giai đoạn sự kiện hoặc thời điểm cập nhật.

## Ứng viên không chọn

| Ngày ứng viên | Phiên đối chiếu | Ứng viên | 100Y (%) từ CSV | Lý do |
|---|---|---|---:|---|
| 2023-06-23 | 2023-06-23 | Khởi đầu nổi loạn Wagner | -0.768827 | Không thêm vào cùng mẫu: chọn riêng mốc kiểm soát Rostov ngày 24/06 và không đếm hai giai đoạn của cùng một cuộc nổi loạn thành hai sự kiện. |
| 2023-10-07 | 2023-10-09 | Hamas tấn công Israel | 0.628403 | Ứng viên lớn nhưng phiên gán có lợi suất dương; ưu tiên Wagner cho năm 2023. Ngày được đối chiếu với Wikipedia có trích dẫn; chưa hoàn tất hai nguồn độc lập nên không đưa vào events.csv. |
| 2024-04-12 | 2024-04-12 | Tin lo ngại Iran sắp tấn công Israel | -1.465761 | Lo ngại đã xuất hiện trước cuộc tấn công; không đồng nhất tin dự báo ngày 12/04 với hành động quân sự ngày 13/04; hai mốc sẽ trùng cụm sự kiện. |
| 2025-04-02 | 2025-04-02 | Công bố thuế "Liberation Day" | 0.670559 | Ngày công bố thực tế là 02/04, không phải phiên giảm 03/04. Phiên công bố có lợi suất dương; đồng thời quá gần sự kiện trả đũa 04/04. |
| 2025-04-03 | 2025-04-03 | Phiên giảm sau "Liberation Day" | -4.960588 | Đây là ngày phản ứng thị trường, không phải ngày công bố; không đổi ngày sự kiện nhằm chọn phiên giảm mạnh. |
| 2026-03-01 | 2026-03-02 | Ngày xuất hiện tin tiếp diễn sau đợt tấn công Iran | 0.039824 | Không dùng làm ngày bắt đầu cuộc tấn công: Reuters/AP xác nhận bắt đầu ngày 28/02; hai mốc cùng gán 02/03. |

- Chính sách thuế lợi nhuận ngân hàng Italy cũng được tìm bằng truy vấn trên. Tin Reuters cho thấy thông báo ban đầu vào tối thứ Hai, khác ngày bài báo/phiên thị trường thứ Ba. Không hoàn tất hai nguồn độc lập và không cần thêm ứng viên cùng năm 2023; loại, không coi là sự kiện đã đạt tiêu chí. [Bài Reuters được phát hiện trong kết quả tìm kiếm](https://www.marketscreener.com/quote/stock/UNICREDIT-S-P-A-33364083/news/Italian-government-s-raid-on-banks-undermined-by-confusion-44565819/); không dùng URL này trong events.csv.
- [Wikipedia về cuộc tấn công Hamas](https://en.wikipedia.org/wiki/2023_Hamas-led_attack_on_Israel) và [Wikipedia về biến động thị trường 2025](https://en.wikipedia.org/wiki/2025_stock_market_crash) đã được mở; chỉ dùng bổ trợ và tìm liên kết nguồn gốc, không dùng các tỷ suất thị trường trên đó.
- Không tuyên bố đã rà soát toàn bộ mọi cú sốc trong giai đoạn; đây là tập ứng viên từ các truy vấn được ghi lại.

## Nguồn không truy cập được và cách xử lý

Một số URL rút gọn của AP và các trang PBS đăng lại AP trả lỗi khi mở, dù kết quả tìm kiếm hiện được. Ví dụ:

- https://apnews.com/article/9960adc7091bbc363c0daf60fd15aba7
- https://apnews.com/article/02cd23e913649f32985f075058e787c4
- https://www.pbs.org/newshour/world/leader-of-wagner-mercenaries-says-forces-entered-russian-city-of-rostov-facing-no-resistance
- https://www.pbs.org/newshour/politics/china-hits-back-with-34-percent-tariff-on-u-s-imports-as-world-weighs-how-to-deal-with-trumps-hikes
- https://www.marshallindependent.com/news/national-news-apwire/2024/10/wall-street-retreats-from-records-and-oil-prices-jump-after-irans-missile-attack-on-israel

Không đưa các URL chỉ hiện snippet hoặc mở lỗi vào events.csv. Dùng URL bài AP đầy đủ tìm qua các liên kết đã đọc và mở thành công. Có internet nhưng một trang lỗi không đồng nghĩa mất quyền truy cập internet.

## Gán ngày và kiểm tra khoảng cách

- Ngày thực tế lưu dạng ISO; ngày giao dịch giữ nguyên nếu có trong CSV. Cuối tuần/lễ chuyển sang **ngày quan sát giao dịch kế tiếp** trong CSV; không tạo lịch bằng ngày làm việc thông thường.
- Ba mốc cuối tuần gán lần lượt theo bảng. Không thay đổi ngày thực tế để chọn phiên giảm. Script bổ sung `date_assigned` vào events.csv.
- Chênh lệch chỉ số phiên giữa các sự kiện liên tiếp: 202, 117, 127, 226; nhỏ nhất 117 phiên, đạt quy định ít nhất 5 phiên. Không cần ngoại lệ dùng sự kiện liền kề.
- Không tự dịch sự kiện xảy ra sau đóng cửa nếu ngày thực tế đã là phiên giao dịch; đây là quy tắc của đề. Cửa sổ [0,+1] giúp khảo sát phản ứng trễ.
- Lịch ngày quan sát là lịch làm việc thực nghiệm của tệp; thiếu một phiên trong tệp có thể bị nhầm thành ngày không giao dịch. Không tải bộ giá khác để thay thế.

## Thiên lệch và giới hạn diễn giải

Ưu tiên sự kiện sau khi biết lợi suất giảm là **thiên lệch chọn mẫu theo biến kết quả**, làm β₂ có xu hướng âm. Giữ sự kiện 2026 dương không xóa thiên lệch này. Tập sự kiện vẫn được chọn hồi cứu; đánh giá cuốn chiếu tránh dùng giá tương lai để ước lượng ở từng phiên, nhưng không biến việc chọn sự kiện hồi cứu thành thiết kế tiền nghiệm.

Chỉ có năm phiên D=1; sự kiện không đồng nhất, có tin khác cùng ngày, một số cú sốc có dấu hiệu báo trước. OLS và HAC mô tả liên hệ, không xác định tác động nhân quả riêng của từng tin. Phiên cuối tuần có thể gộp nhiều diễn biến (bao gồm kết thúc nổi loạn Wagner). Giảm RMSE trong mẫu khi thêm D có thể chỉ do thêm tham số; D của tin bất ngờ không biết ở thời điểm dự báo trước phiên. Không thay đổi sự kiện hoặc loại lợi suất cực đoan hợp lệ nhằm ép β₂ âm hay có ý nghĩa.
