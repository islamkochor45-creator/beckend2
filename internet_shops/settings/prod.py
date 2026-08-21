from .base import *

DEBUG = False

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

EMAIL_BACKEND = env(
	"EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
