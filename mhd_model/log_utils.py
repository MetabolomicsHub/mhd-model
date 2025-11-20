import logging


class ExcludeLoggerFilter(logging.Filter):
    def __init__(self, excludes: None | dict[str, int]):
        super().__init__()
        self.excludes = excludes

    def filter(self, record):
        if self.excludes:
            for exclude in self.excludes:
                if record.name and record.name.startswith(exclude):
                    if record.levelno < self.excludes[exclude]:
                        return False
        return True


def set_basic_logging_config() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(
        ExcludeLoggerFilter({"fake_useragent": logging.ERROR, "httpx": logging.WARNING})
    )
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        handlers=[handler],
    )
