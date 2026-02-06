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
    


def generate_svg_sprite(sprite_string: str):
    if not sprite_string or len(sprite_string) != 256:
        return ""

    char_map = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
    colors_64 = [
    "#211d25",
    "#413d42",
    "#5c5b63",
    "#7c808b",
    "#a5b0b6",
    "#d6dede",
    "#ffffff",
    "#dcded1",
    "#aab1a1",
    "#7b8375",
    "#585f57",
    "#3c3c3c",
    "#635d5a",
    "#8d837d",
    "#b4aea4",
    "#dedcd1",
    "#eadedf",
    "#bcacb1",
    "#8f8189",
    "#685d66",
    "#643747",
    "#b2434d",
    "#e55858",
    "#fa8971",
    "#ffb999",
    "#ffe0b7",
    "#ffbdc1",
    "#ef93b5",
    "#c971a2",
    "#944e89",
    "#4c3d57",
    "#5d558f",
    "#777dc4",
    "#96b1e7",
    "#bedef6",
    "#aae3db",
    "#5ac5ce",
    "#4694a8",
    "#2a69b0",
    "#2a3b4a",
    "#29684a",
    "#379648",
    "#79b547",
    "#b8cf61",
    "#f3db6f",
    "#f4ba7a",
    "#e79055",
    "#ce6442",
    "#944940",
    "#91555d",
    "#b76f6b",
    "#cd9383",
    "#e1ba9e",
    "#facafb",
    "#d49ce5",
    "#9f76b8",
    "#725689",
    "#edb762",
    "#fcfbc9",
    "#de9463",
    "#b66a4d",
    "#333f29",
    "#4e5c2c",
    "#708939"
]
    svg_parts = ['<svg width="40" height="40" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" style="image-rendering: pixelated; shape-rendering: crispEdges;">']
    
    for i, char in enumerate(sprite_string):
        color_idx = char_map.find(char)
        if color_idx == -1: continue
        
        color = colors_64[color_idx]
        x = i % 16
        y = i // 16
        svg_parts.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{color}" />')
    
    svg_parts.append('</svg>')
    return "".join(svg_parts)