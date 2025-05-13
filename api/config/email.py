from fastapi_mail import FastMail, ConnectionConfig

# Cấu hình SMTP (dùng Gmail làm ví dụ)
conf = ConnectionConfig(
    MAIL_USERNAME="trinhvinhthuan6@gmail.com",  # Email hợp lệ của bạn
    MAIL_PASSWORD="mife fezv fzfh ywbq",          # App Password của Gmail (16 ký tự)
    MAIL_FROM="trinhvinhthuan6@gmail.com",     # Phải khớp với MAIL_USERNAME
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,  # Sử dụng STARTTLS (bảo mật)
    MAIL_SSL_TLS=False,  # Không sử dụng SSL/TLS (vì đã dùng STARTTLS)
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Tạo instance FastMail
fm = FastMail(conf)