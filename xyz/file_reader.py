import logging


class FileReader:
    """..."""

    def __init__(self, name):
        self.filename = name
        self.logger = logging.getLogger()
        self.logger.debug("FileReader object was initiated for the file: %s", name)

    def readfile(self) -> set:
        self.logger.info(f"Reading urls from the file: {self.filename}")
        with open(self.filename) as f:
            urls = set(filter(bool, map(str.strip, f.readlines())))
            results = {"".join(u.split(" ")) for u in urls if u.startswith("http")}
            self.logger.info(f"Returning set of urls: {results}")
            return results


if __name__ == "__main__":
    pass
