import structlog

structlog.configure(processors=[structlog.processors.add_log_level,
                                structlog.processors.TimeStamper(fmt="iso"),
                                structlog.processors.JSONRenderer(),],
                                wrapper_class=structlog.stdlib.BoundLogger,
                                logger_factory=structlog.stdlib.LoggerFactory(),)

log = structlog.get_logger()