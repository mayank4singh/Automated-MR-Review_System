import secrets
webhook_secret = secrets.token_urlsafe(32)
print(webhook_secret)