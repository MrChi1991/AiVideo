@echo off
color 0A
echo Bắt đầu cài đặt AI Video Production System...

REM Kiểm tra và cài đặt Docker Desktop
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker chưa được cài đặt. Vui lòng cài Docker Desktop thủ công từ https://www.docker.com/products/docker-desktop
    echo Sau khi cài đặt, chạy lại script này.
    pause
    exit /b 1
) else (
    echo Docker đã được cài đặt.
)

REM Kiểm tra Docker Compose (thường đi kèm Docker Desktop)
docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker Compose chưa được cài đặt. Đang cố gắng cài đặt qua Docker...
    docker pull docker/compose
) else (
    echo Docker Compose đã được cài đặt.
)

REM Kiểm tra và cài đặt Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python chưa được cài đặt. Vui lòng cài Python từ https://www.python.org/downloads/
    echo Sau khi cài đặt, chạy lại script này.
    pause
    exit /b 1
) else (
    echo Python đã được cài đặt.
)

REM Cài đặt thư viện Python
echo Cài đặt các thư viện Python từ requirements.txt...
pip install -r central_controller\requirements.txt

REM Kiểm tra file .env
if not exist .env (
    echo File .env không tồn tại. Tạo từ .env.example...
    copy .env.example .env
    echo Vui lòng mở file .env và thêm các API keys cần thiết trước khi tiếp tục!
    pause
    exit /b 1
)

REM Khởi động dự án với Docker Compose
echo Khởi động dự án...
docker-compose up -d

echo Cài đặt hoàn tất! Truy cập Grafana tại http://localhost:3000 (admin/admin) và Prometheus tại http://localhost:9090.
echo Kiểm tra trạng thái với: docker-compose ps
echo Xem logs với: docker-compose logs
pause