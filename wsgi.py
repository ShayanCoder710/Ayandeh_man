import logging


class _QuietSocketIoLogFilter(logging.Filter):
    def filter(self, record):
        return "/socket.io" not in record.getMessage()


logging.getLogger("werkzeug").addFilter(_QuietSocketIoLogFilter())
from app import app
if __name__ == '__main__':
    app.run()
