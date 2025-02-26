# GitHub Trending Scraper

## 📝 Giới thiệu
GitHub Trending Scraper là một công cụ tự động thu thập và phân tích dữ liệu từ trang GitHub Trending. Dự án này giúp theo dõi và phân tích các repository đang thịnh hành trên GitHub, cung cấp thông tin chi tiết về stars, ngôn ngữ lập trình, chủ đề và số lượng người đóng góp.

## ✨ Tính năng chính
- Thu thập dữ liệu tự động từ GitHub Trending
- Lưu trữ dữ liệu vào SQLite database
- Phân tích và trực quan hóa dữ liệu với các biểu đồ
- Dashboard tương tác để xem và phân tích dữ liệu
- Hỗ trợ theo dõi:
  - Tên repository và mô tả
  - Số lượng stars và thay đổi stars
  - Ngôn ngữ lập trình
  - Chủ đề (topics)
  - Số lượng người đóng góp

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.8 trở lên
- pip (Python package manager)

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

### Xem dashboard phân tích
Khởi động dashboard để xem phân tích dữ liệu:
```bash
python scripts/dashboard.py
```
Sau khi chạy, truy cập dashboard tại: http://127.0.0.1:8050

### Phân tích dữ liệu
Chạy script phân tích để tạo báo cáo và biểu đồ:
```bash
python scripts/analysis.py
```

## 📊 Kết quả phân tích
Kết quả phân tích được lưu trong thư mục `data/`:
- `github_trending.csv`: Dữ liệu thô
- `language_distribution.png`: Biểu đồ phân bố ngôn ngữ
- `star_changes.png`: Biểu đồ thay đổi số sao
- `topic_distribution.png`: Biểu đồ phân bố chủ đề
- `contributor_analysis.png`: Biểu đồ phân tích người đóng góp
- `analysis_report.md`: Báo cáo phân tích chi tiết

## 📁 Cấu trúc dự án
```
├── data/                  # Thư mục chứa dữ liệu và kết quả phân tích
├── db/                    # Database SQLite
├── notebooks/             # Jupyter notebooks cho phân tích
├── scripts/               # Các script chính
│   ├── scraper.py        # Script thu thập dữ liệu
│   ├── analysis.py       # Script phân tích dữ liệu
│   ├── dashboard.py      # Dashboard Plotly Dash
│   ├── db_utils.py       # Tiện ích thao tác database
│   └── notifier.py       # Thông báo kết quả
├── requirements.txt      # Danh sách thư viện cần thiết
└── README.md            # Tài liệu hướng dẫn
```

## 🤝 Đóng góp
Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 Giấy phép
Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## 👤 Tác giả
- GitHub: [@PhamNhatKhanhs](https://github.com/PhamNhatKhanhs)

## ⭐️ Hỗ trợ dự án
Nếu dự án này hữu ích với bạn, hãy cho nó một ngôi sao ⭐️ trên GitHub!