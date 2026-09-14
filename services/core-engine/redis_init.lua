-- ====================================================================
-- Kişisel Öğrenme Motoru (Personal Learning Engine) Redis 7.2 Lua Script
-- Atomik Hız Sınırlama (Rate Limiting), İdempotent Olay Tekrarı ve Kilit Yönetimi
-- ====================================================================

-- KEYS[1]: Rate limit anahtarı (örn. "ratelimit:session:sess_123")
-- KEYS[2]: İdempotent olay anahtarı (örn. "idempotent:msg:cmsg_456")
-- ARGV[1]: İzin verilen azami istek sayısı (örn. 2)
-- ARGV[2]: Zaman penceresi saniye cinsinden (örn. 1)
-- ARGV[3]: İdempotency TTL saniye cinsinden (örn. 86400 - 24 saat)
-- ARGV[4]: client_msg_id değeri

local rate_key = KEYS[1]
local idemp_key = KEYS[2]

local max_requests = tonumber(ARGV[1]) or 2
local window_seconds = tonumber(ARGV[2]) or 1
local idemp_ttl = tonumber(ARGV[3]) or 86400
local client_msg_id = ARGV[4]

-- 1. İdempotency Kontrolü: Bu mesaj daha önce işlendi mi?
if idemp_key and idemp_key ~= "" then
    local existing = redis.call("GET", idemp_key)
    if existing then
        return { "CACHED", existing }
    end
end

-- 2. Kayar Pencere Hız Sınırlama (Sliding Window Counter)
local current = redis.call("INCR", rate_key)
if current == 1 then
    redis.call("EXPIRE", rate_key, window_seconds)
end

if current > max_requests then
    return { "RATE_LIMITED", tostring(current) }
end

-- 3. İdempotent anahtarı rezerve et
if idemp_key and idemp_key ~= "" then
    redis.call("SETEX", idemp_key, idemp_ttl, "PROCESSING")
end

return { "ALLOWED", tostring(current) }
