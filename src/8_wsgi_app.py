import re
from urllib import request
from wsgiref.simple_server import make_server


def app(environ, start_response):
    path = environ["PATH_INFO"]
    currency = path.lstrip("/").upper()

    if not re.fullmatch(r"[A-Z]{3}", currency):
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Path example: USD"]

    # url = f"https://v6.exchangerate-api.com/v6/fbdc86fe0727eb06009ff5d5/latest/{currency}"
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    try:
        with request.urlopen(url, timeout=10) as response:
            data = response.read()
            content_type = response.getheader("Content-Type")
            start_response("200 OK", [("Content-Type", content_type)])
            return [data]

    except Exception:
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Internal server error"]


if __name__ == "__main__":
    server = make_server("localhost", 8000, app)
    # http://localhost:8000/USD
    server.serve_forever()
