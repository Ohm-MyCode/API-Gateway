local bucket_key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2]) -- tokens per second
local current_time = tonumber(ARGV[3]) -- milliseconds

local bucket = redis.call(
    "HMGET",
    bucket_key,
    "tokens",
    "last_refill"
)

local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if not tokens then
    tokens = capacity
    last_refill = current_time
end

-- elapsed time in milliseconds
local elapsed_ms = current_time - last_refill

-- convert milliseconds to seconds
local refill = (elapsed_ms / 1000) * refill_rate

tokens = math.min(
    capacity,
    tokens + refill
)

last_refill = current_time

if tokens < 1 then
    return 0
end

tokens = tokens - 1

redis.call(
    "HSET",
    bucket_key,
    "tokens",
    tokens,
    "last_refill",
    last_refill
)

redis.call(
    "EXPIRE",
    bucket_key,
    3600
)

return 1