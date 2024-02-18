# RateLimiter
https://codingchallenges.fyi/challenges/challenge-rate-limiter

# Good Read
https://systemsdesign.cloud/SystemDesign/RateLimiter

# Learnings

## Token Bucket 
The Token Bucket throttling algorithm works as follows: A token bucket is a container that has pre-defined capacity. Tokens are put in the bucket at preset rates periodically. Once the bucket is full, no more tokens are added.

**Pros**
1. Memory efficient
2. Token Bucket technique allows spike in traffic or burst of traffic. A request goes through as long as there are tokens left. This is super important since traffic burst is not uncommon. One example is events like Amazon Prime Day when traffic spikes for a certain time period.

**Cons**
1. Despite the token bucket algorithm’s elegance and tiny memory footprint, its Redis operations aren’t atomic. In a distributed environment, the “read-and-then-write” behavior creates a race condition, which means the rate limiter can at times be too lenient
If only a single token remains and two servers’ Redis operations interleave, both requests would be let through.

Imagine if there was only one available token for a user and that user issued multiple requests. If two separate processes served each of these requests and concurrently read the available token count before either of them updated it, each process would think the user had a single token left and that they had not hit the rate limit.

Our token bucket implementation could achieve atomicity if each process were to fetch a Redis lock for the duration of its Redis operations. This, however, would come at the expense of slowing down concurrent requests from the same user and introducing another layer of complexity. Alternatively, we could make the token bucket’s Redis operations atomic via Lua scripting.

## Fixed Window Counter
You have a user, window length, requests count.
In a particular window a user can only have limited requests count.

**Pros**
1. Memory Efficient:= Keys can be just the user_id:current_window and value can be the counter
2. Best for use cases where quota is reset only at the end of the unit time window. For example: if the limit is 10 requests / min, it allows 10 requests in every unit minute window say from 10:00:00 AM to 10:00:59 AM, and the quota resets at 10:01:00 AM. It does not matter if 20 requests were allowed in between 10:00:30 AM and 10:01:29 AM, since 10:00:00 AM to 10:00:59 AM is one slot and 10:01:00 AM to 10:01:59 AM is another slot, even though 20 requests we allowed in last one minute at 10:01:30 AM. This is why this algorithm is called Fixed Window and not Sliding Window

**Cons**
1. Spike in traffic at the edge of a window makes this algorithm unsuitable for use cases where time window needs to be tracked real-time at all given time.
Example 1: if we set a maximum of 10 message per minute, we don’t want a user to be able to receive 10 messages at 0:59 and 10 more messages at 1:01.
Example 2: if the limit is 10 requests / min and 10 requests were sent starting from 10:00:30 AM to 10:00:59 AM, then no requests will be allowed till 10:01:29 AM and quota will be reset only at 10:01:29 AM since 10 requests were already sent in last 1 min starting at 10:00:30 AM.

## Sliding Window Logs
1. The algorithm keeps track of request timestamps. Timestamp data is usually kept in cache, such as sorted sets of Redis .
2. When a new request comes in, remove all the outdated timestamps. Outdated timestamps are defined as those older than the start of the current time window.
3. Storing the timestamps in sorted order in sorted set enables us to effieciently find the outdated timestamps.
4. Add timestamp of the new request to the log.
5. If the log size is the same or lower than the allowed count, a request is accepted. Otherwise, it is rejected.

**Pros**
1. The advantage of this algorithm is that it does not suffer from the boundary conditions of fixed windows. The limit will be enforced precisely and because the sliding log is tracked for each consumer, you don’t have the issue that every use can suddenly surge in requests each time a fixed window boundary passes.

**Cons**
1. Memory Limit: Depending on the size of the sliding window and the granularity of the data being logged, the algorithm may require a significant amount of memory to store the logged data points. This can become a limitation, especially when dealing with large-scale data streams
2. Processing Overhead: As new data points are added to the sliding window and old ones are removed, there is a constant need for processing to maintain the window. This overhead can impact the overall performance of the system, especially if the window size is large or if there are frequent updates to the data.

## Sliding Window Counter
The Sliding Window Counter algorithm is a hybrid approach that combines the Fixed Window Counter algorithm and Sliding Window Logs algorithm.
`Current Request rate = Requests in current window + (Requests in the previous window * overlap percentage of the rolling window and previous window)`

**Pros**
1. Memory efficient.
2. It smoothes out spikes in the traffic because the rate is based on the average rate of the previous window.

**Cons**
1. It only works for not-so-strict look back window. It is an approximation of the actual rate because it assumes requests in the previous window are evenly distributed.
However, this problem may not be as bad as it seems. According to experiments done by Cloudflare, only 0.003% of requests are wrongly allowed or rate limited among 400 million requests.
