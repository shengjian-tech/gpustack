from datetime import datetime, timezone
import logging
import os
import sys


# Suppress warnings from transformers
# https://github.com/huggingface/transformers/issues/27214
# Note: This should be set before importing transformers
if "TRANSFORMERS_NO_ADVISORY_WARNINGS" not in os.environ:
    os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

TRACE_LEVEL = 5

# 新增自定义Formatter类（添加位置：在TRACE_LEVEL定义后）
class ReplaceFormatter(logging.Formatter):
    def format(self, record):
        # 替换记录器名称
        record.name = record.name.replace("gpustack", "AITHER")
        # 替换日志消息内容
        if isinstance(record.msg, str):
            record.msg = record.msg.replace("gpustack", "AITHER")
        # 保留原有的时间格式逻辑
        return super().format(record)
    
    # 继承原有时间格式处理（关键：复用原代码的时间格式化逻辑）
    def formatTime(self, record, datefmt=None):
        return datetime.fromtimestamp(record.created, timezone.utc).astimezone().isoformat(timespec="seconds")





def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO


    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logging.addLevelName(TRACE_LEVEL, "TRACE")
    logging.Logger.trace = trace

    logging.Formatter.formatTime = (
        lambda self, record, datefmt=None: datetime.fromtimestamp(
            record.created, timezone.utc
        )
        .astimezone()
        .isoformat(timespec="seconds")
    )
    """

    # 修改点1：替换basicConfig为手动配置（保留原有格式字符串）
    root_logger = logging.getLogger()
    if root_logger.handlers:  # 避免重复初始化
        root_logger.handlers.clear()
    
    handler = logging.StreamHandler()
    # 使用自定义Formatter（保留原有格式字符串）
    handler.setFormatter(ReplaceFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))  # 修改点2
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    logging.addLevelName(TRACE_LEVEL, "TRACE")
    logging.Logger.trace = trace



    # Third-party loggers to disable
    disable_logger_names = [
        "httpcore.connection",
        "httpcore.http11",
        "httpcore.proxy",
        "httpx",
        "asyncio",
        "aiocache.base",
        "aiosqlite",
        "urllib3.connectionpool",
        "multipart.multipart",
        "apscheduler.scheduler",
        "apscheduler.executors.default",
        "tzlocal",
        "alembic.runtime.migration",
        "python_multipart.multipart",
        "filelock",
        "fastapi-cdn-host",
    ]

    for logger_name in disable_logger_names:
        logger = logging.getLogger(logger_name)
        logger.disabled = True

    # Third-party loggers to print on debug
    debug_logger_names = [
        "alembic.runtime.migration",
    ]

    for logger_name in debug_logger_names:
        logger = logging.getLogger(logger_name)
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.disabled = True


def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


class RedirectStdoutStderr:
    def __init__(self, target):
        self.target = target

    def __enter__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.target
        sys.stderr = self.target

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
