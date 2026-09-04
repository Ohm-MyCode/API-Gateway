from prometheus_client import Counter, Histogram

request_latency = Histogram("request_latency", "Request Latency")
rate_limit_blocks = Counter(
    "rate_limit_blocks_total",
    "Total number of requests blocked by rate limiting",
)