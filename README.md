# GitHub Trending Scraper

## 📝 Giới thiệu
GitHub Trending Scraper là một công cụ tự động thu thập và phân tích dữ liệu từ trang GitHub Trending. Dự án này giúp theo dõi và phân tích các repository đang thịnh hành trên GitHub, cung cấp thông tin chi tiết về stars, ngôn ngữ lập trình và số lượng người đóng góp.

## ✨ Tính năng chính
- Thu thập dữ liệu tự động từ GitHub Trending
- Lưu trữ dữ liệu vào SQLite database
- Phân tích và trực quan hóa dữ liệu với các biểu đồ
- Dashboard tương tác để xem và phân tích dữ liệu
- Hỗ trợ theo dõi:
  - Tên repository và mô tả
  - Số lượng stars và thay đổi stars
  - Ngôn ngữ lập trình
  - Số lượng người đóng góp

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.8 trở lên
- pip (Python package manager)
- Git (để clone repository)
- Trình duyệt web hiện đại (để xem dashboard)

### Các bước cài đặt

1. Clone repository:
```bash
git clone https://github.com/PhamNhatKhanhs/github-trending-scraper.git
cd github-trending-scraper
```

2. Tạo môi trường ảo:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## 💻 Hướng dẫn sử dụng

### Thu thập dữ liệu
Chạy script scraper để thu thập dữ liệu:
```bash
python scripts/scraper.py
```

Lưu ý:
- Script sẽ tự động thu thập dữ liệu từ trang GitHub Trending
- Quá trình có thể mất vài phút tùy thuộc vào kết nối mạng
- Nếu gặp lỗi timeout, hãy thử chạy lại script

### Xem dashboard phân tích
Khởi động dashboard để xem phân tích dữ liệu:
```bash
python scripts/dashboard.py
```
Sau khi chạy, truy cập dashboard tại: http://127.0.0.1:8050

Dashboard cung cấp các tính năng:
- Biểu đồ phân bố ngôn ngữ lập trình
- Biểu đồ xu hướng stars theo thời gian
- Bảng dữ liệu chi tiết có thể lọc và sắp xếp
- Thống kê về số lượng người đóng góp

### Phân tích dữ liệu
Chạy script phân tích để tạo báo cáo và biểu đồ:
```bash
python scripts/analysis.py
```

## 📊 Kết quả phân tích
Kết quả phân tích được lưu trong thư mục `data/`:
- `github_trending.csv`: Dữ liệu thô từ việc thu thập
- `language_distribution.png`: Biểu đồ phân bố các ngôn ngữ lập trình phổ biến
- `star_changes.png`: Biểu đồ thể hiện sự thay đổi số sao theo thời gian
- `contributor_analysis.png`: Biểu đồ phân tích về số lượng người đóng góp
- `analysis_report.md`: Báo cáo chi tiết với các nhận xét và xu hướng

## 📁 Cấu trúc dự án
```
├── data/                  # Thư mục chứa dữ liệu và kết quả phân tích
├── db/                    # Database SQLite lưu trữ dữ liệu
├── notebooks/             # Jupyter notebooks cho phân tích chuyên sâu
├── scripts/               # Các script chính
│   ├── scraper.py        # Script thu thập dữ liệu từ GitHub
│   ├── analysis.py       # Script phân tích và tạo báo cáo
│   ├── dashboard.py      # Dashboard tương tác Plotly Dash
│   ├── db_utils.py       # Tiện ích thao tác với database
│   └── notifier.py       # Gửi thông báo kết quả
├── requirements.txt      # Danh sách thư viện Python cần thiết
└── README.md            # Tài liệu hướng dẫn
```

## 🔧 Xử lý lỗi thường gặp

1. Lỗi khi cài đặt thư viện:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

2. Lỗi khi chạy dashboard:
- Kiểm tra port 8050 đã được sử dụng chưa
- Đảm bảo đã activate môi trường ảo
- Thử chạy với quyền admin

3. Lỗi khi thu thập dữ liệu:
- Kiểm tra kết nối internet
- Đợi vài phút và thử lại
- Sử dụng VPN nếu bị chặn IP

## 🤝 Đóng góp
Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/TinhNangMoi`)
3. Commit thay đổi (`git commit -m 'Thêm tính năng mới'`)
4. Push lên branch (`git push origin feature/TinhNangMoi`)
5. Tạo Pull Request

## 📝 Giấy phép
Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## 👤 Tác giả
- GitHub: [@PhamNhatKhanhs](https://github.com/PhamNhatKhanhs)

## ⭐️ Hỗ trợ dự án
Nếu dự án này hữu ích với bạn, hãy cho nó một ngôi sao ⭐️ trên GitHub!