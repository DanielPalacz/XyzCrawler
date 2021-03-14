
class FileReader:
    """ ... """

    def __init__(self, name):
        self.filename = name

    def readfile(self) -> set:
        with open(self.filename) as f:
            # return [link.strip() for link in f.readlines() if link.strip()]
            urls = set(filter(bool, map(str.strip, f.readlines())))
            return {"".join(u.split(" ")) for u in urls if u.startswith("http")}


if __name__ == "__main__":
    pass
