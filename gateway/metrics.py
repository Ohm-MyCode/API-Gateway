from prometheus_client import Histogram,Counter

request_latency = Histogram("req_latency", "Request Latency")
rate_limit_blocks = Counter(
    "rate_limit_blocks_total",
    "Total number of requests blocked by rate limiting",
)