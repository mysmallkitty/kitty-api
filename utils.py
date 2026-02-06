from datetime import datetime, timezone



class TimeUtil:
    @staticmethod
    def format_last_active(last_login_at: datetime) -> str:
        if not last_login_at:
            return ""

        now = datetime.now(timezone.utc) if last_login_at.tzinfo else datetime.now()
        delta = now - last_login_at
        seconds = int(delta.total_seconds())

        if seconds < 3600:
            minutes = seconds // 60
            return "Just now" if minutes < 1 else f"{minutes} minutes ago"

        if seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hours ago"

        days = seconds // 86400
        return f"{days} days ago"