
LINKS = ["https://wikipedia.org", "https://www.reddit.com", "http://www.ringpolska.pl"]

LOCAL_HTTP_SERVER = "http://0.0.0.0:8000/"

HTTP_HEADERS = {
    "standard":
            {
            "Accept": "application/xhtml+xml, application/xml;q=0.9, text/xml;q=0.7, text/html;q=0.5, text/plain;q=0.3",
            "Accept-Charset": "utf-8, iso-8859-13;q=0.8",
                #
                #
                #
            "User-agent": "Mydownloader"
            },
    "non_standard":
            {
            "Cookie": "ciastko1=wartosc1; ciastko2=wartosc2",
            "Set-Cookie": "ciastko1=wartosc1; ciastko2=wartosc2",
            "Refresh": "czas; url=adres",
            "X-Frame-Options": "deny",
            "Strict-Transport-Security": "max-age=31536000[; includeSubDomains]"
            }
}
