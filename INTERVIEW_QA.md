# Interview Practice QnA
---

#### Q1. Why does business logic not live in routes (controllers)?
Ans: A route should only deal with HTTP: take the request, call the service, send back the response. The business rules live in a service, which knows nothing about requests or responses. It gets some input, applies the rules, asks the repository to talk to the database, and returns the result.

This way the same logic can be reused from a route, a worker, a script or a websocket, and it can be tested without starting a server. Logic inside a route is stuck with HTTP, hard to test, and makes the route big and messy.

#### Q2. How do you model a many-to-many relationship? Use users and workspaces as the example.
Ans: Many-to-many means one record in A links to many records in B, and the other way round. Example: a workspace has many users, and a user can be in many workspaces.

It cannot be stored in either table, because a column cannot hold a clean list of ids. So a third table sits in the middle, called a junction table. Each row is one pair: a user id and a workspace id, both foreign keys. Together they form the primary key, so the same pair cannot be added twice. The table can also store details about the link itself, like the user's role in that workspace.

For comparison: one-to-many is a foreign key on the "many" side, and one-to-one is a foreign key with a unique constraint.

#### Q3. Why does validation belong at the API boundary?
Ans: The API boundary is where data from outside enters the system, and that data cannot be trusted. So it is checked right there, and a bad request is rejected early with a clear 400 or 422, before any real work starts. The checks are simple: required fields, types, lengths and formats.

This helps in a few ways. Everything inside can trust the data. Bad input never reaches the database. No work is wasted on a request that was going to fail anyway. And the client gets a clear message instead of a confusing 500.

#### Q4. Why is scattered try/catch hard to maintain, and what does central error handling fix?
Ans: With try/catch scattered everywhere, every change has to be repeated in every block, and every new endpoint needs its own block. It is easy to miss one. Errors end up handled in different ways, some get swallowed, and one missed block can leak a stack trace to the client.

Central error handling fixes this. Custom error types live in one file (not found, forbidden, rate limited), each with a status code and message. Business code just raises the right error. One global handler turns it into a response in one fixed format. Unexpected errors get a generic 500 and are logged. To add a new kind of error, add one error type and raise it where needed.

#### Q5. Why are passwords hashed and not encrypted?
Ans: Encryption can be reversed. If the key leaks, every password is exposed. Also, the system never needs the original password. It only needs to know if the entered one matches. Hashing is one way: only the hash is stored, and at login the entered password is hashed and compared.

A hash can still be attacked by guessing, so the type matters. Use a slow password hash like Argon2 or bcrypt, not a fast one like MD5 or SHA-256. Add a random salt for each password, so the same password gives different hashes.

#### Q6. What are the risks of long-lived access tokens?
Ans: If an access token is stolen, the attacker can act as that user until it expires. These tokens are usually stateless, so the server cannot easily cancel them. They keep working even after logout or a password change.

So the access token is kept short-lived, a few minutes, and a separate long-lived refresh token (in an HttpOnly cookie) is used to get new ones.

#### Q7. Where should tokens be stored, in a cookie or in a header? What are the tradeoffs?
Ans: The refresh token goes in an HttpOnly, Secure, SameSite cookie. Scripts cannot read it, so XSS cannot steal it, and SameSite blocks CSRF. The access token goes in the Authorization header and is kept in memory. It is never sent automatically, so there is no CSRF, and it is short-lived, so a leak does limited damage. Each choice covers the weakness of the other.

#### Q8. How do you keep one tenant's data separate from another's?
Ans: Every record that belongs to a tenant has a tenant id, and every query uses it. The tenant comes from the user's verified membership on the server, never from the client. Lookups use the id and the tenant id together, so an id from another tenant finds nothing (404). This is done in one central place so it is not forgotten. Cache keys and live channels are also separated per tenant.

For stronger isolation there are row-level security, or a separate schema or database per tenant, at a higher cost.

#### Q9. Why is authentication alone not enough?
Ans: Authentication only says who the user is. Not every user has the same rights. Authorization checks whether this user may do this action, first by role, then by ownership of the record. Without it, any logged-in user could touch anyone's data.

Not logged in gives 401. Logged in but not allowed gives 403 (or 404, to hide that the record exists).

#### Q10. What is Broken Object Level Authorization (BOLA), and how do you prevent it?
Ans: BOLA is when an API checks that the user is logged in, but not that the requested object belongs to them. The attacker just changes the id in the request and gets someone else's data.

To prevent it, check access to the object on every request. Look up by id and owner (or tenant) together, and return 404 if it is not theirs. Do it in one central place so no endpoint forgets. Do not rely on hard-to-guess ids. Random ids (UUIDs) help a little, but they are not a check.

#### Q11. What is the difference between application validation and database constraints, and why do you want both?
Ans: Application validation checks rules in the server code. It gives early, friendly errors and can handle complex rules. But it only covers writes that go through the app.

Database constraints (NOT NULL, UNIQUE, FOREIGN KEY, CHECK) cover every write, whoever makes it: another service, a script, manual SQL, or a bug. They also stop race conditions. Two requests can both pass an "email is free" check, and only a UNIQUE constraint stops the second insert. So both are used: the app for good messages, the database as the last line of defense.

#### Q12. What is the difference between offset and cursor pagination?
Ans: Offset pagination means "skip X rows, return Y". It is simple, and allows jumping to page N and showing the total pages. But if rows are added or deleted while paging, rows shift, so there can be duplicates or missing rows. It is also slow on deep pages, because the skipped rows are still read.

Cursor pagination means "give me Y rows after this row". The cursor marks the last row seen, with a stable unique order like created time plus id. No rows are skipped or repeated, and it stays fast with an index. The downside is that there is no jumping to a page, only next and previous. It suits infinite scroll and big or fast-changing data.

#### Q13. Why does an index speed up reads but slow down writes?
Ans: An index is a separate sorted structure that points to the rows, like the index at the back of a book. The database searches the small sorted index instead of reading every row, so reads are much faster.

Writes are slower because every insert, update or delete also has to update each index and keep it sorted. That costs extra time and storage. So only the columns used to filter, sort or join should be indexed. On very small tables the database may skip the index, because a full scan is cheaper.

#### Q14. What is a transaction, and what breaks without one?
Ans: A transaction groups several steps into one unit: all of them happen or none do. In a bank transfer, the debit and the credit must both succeed. If the debit works and the credit fails, the money disappears. With a transaction, a failure causes a rollback and the debit is undone. If all goes well, it is committed.

Atomicity is one part of ACID. The others are consistency (data stays valid), isolation (transactions do not see each other's half-done work) and durability (committed data survives a crash). Without transactions there are half-done states after failures, and race conditions like two transfers reading the same balance and both succeeding.

#### Q15. What is cache-aside, and what are its risks?
Ans: In cache-aside, the application manages the cache. It checks the cache first. On a hit, it returns the value. On a miss, it reads the database, stores the result in the cache with a TTL, and returns it.

Risks: stale data, because the cache can differ from the database after a write (reduced with a TTL and by deleting the key when data changes). A cache stampede, when a popular key expires and many requests hit the database at once (fixed with TTL jitter or letting only one request rebuild it). And a cold or unavailable cache sends all traffic to the database, so the app should fall back safely.

#### Q16. How do you keep a cache consistent with the database?
Ans: One way is write-through: update the database and the cache together on every write. The risks are that the two writes are not atomic, so one can fail and they disagree, and concurrent writers can leave an old value in the cache.

A better way is to invalidate on write: after the database commit succeeds, delete the cache key. The next read loads fresh data and refills the cache. The delete must happen after the commit, not before. A TTL is kept as a safety net. A cache is never perfectly in sync, so the goal is to keep the staleness small.

#### Q17. How do you rate limit an API, and what do you count?
Ans: Rate limiting means allowing a maximum number of requests in a time window. A counter is kept in a shared fast store like Redis, keyed by who is calling and which route, and it expires with the window. When the count passes the limit, the API returns 429 with a Retry-After header.

Requests are counted per user id when logged in, per IP for anonymous routes like login, and per API key for outside clients. Sensitive routes get stricter limits to slow down brute force. IP has limits: many users can share one, and behind a proxy the real IP must be read safely. Common methods are fixed window, sliding window and token bucket.

#### Q18. When do you use a background job, and what can go wrong?
Ans: A background job is used for work that is slow or heavy, may need retries, and does not have to finish before the user gets a response, like sending an email after sign-up. The request stays fast and a worker does the job separately.

What can go wrong: most queues deliver at least once, so a job can run twice, which means jobs must be idempotent. A job must be queued only after the database commit, or the worker may run before the data exists. Failures need retries with backoff, a timeout, and a dead-letter queue. If workers are down, jobs pile up. The user does not see failures, so logging and alerts are needed.

#### Q19. What can go wrong with user uploads, and how do you protect against it?
Ans: Risks: malicious files, huge uploads and unsupported types. Protection: allow only listed file types, checked by the real file content and not by the extension or header, because the client controls those. Enforce a maximum size while reading, so a huge upload cannot fill the memory. Save the file under a random name, never the user's name, which stops path traversal and overwriting server files. The original name is kept separately as metadata.

Store files where they cannot be executed, check permission on every download, and serve them with attachment and nosniff headers so a browser cannot run them as a page. For higher-risk systems, add virus scanning and use object storage.

#### Q20. How do you scale WebSockets across several servers?
Ans: A WebSocket is a long-lived connection held by one server. With several servers, users in the same room can be on different servers, and each server only knows its own connections. The fix is a shared message bus between the servers, like Redis Pub/Sub. When an event happens, the server publishes it to the bus. Every server is subscribed, receives it, and sends it to its own clients.

No important state should be kept in server memory. Clients reconnect automatically, maybe to another server, and fetch the data again, because Pub/Sub does not store messages. Also watch the connection limit per server, use heartbeats to find dead connections, and drain servers gracefully on deploy.

#### Q21. How is an API secured, layer by layer?
Ans: Security is built in layers, so if one fails, the next one still protects the system. This is called defence in depth.

- Network: use HTTPS everywhere, and keep the database and cache private, not reachable from the internet. 
- Edge: rate limiting, a CORS allowlist and security headers.
- Authentication: passwords stored as slow hashes, short-lived access tokens, refresh tokens in secure cookies.
- Authorization: role checks, plus object-level checks so users only reach their own tenant's data.
- Input: validate at the boundary, use parameterized queries against SQL injection, and check uploads.
- Data: database constraints, and secrets in environment variables or a secrets manager, never in code.
- Errors and logs: generic error messages to clients, details only in logs, and no passwords or tokens in logs.
- Operations: least privilege (like non-root containers), updated dependencies, and monitoring with alerts.


#### Q22. What do you unit test, what do you leave for integration tests?
Ans: Unit tests check small pieces of logic, like business rules and validation, with no HTTP, database or network. They are fast, and there are many of them, covering edge cases. Integration tests send a full request and check everything on its way, so they show that routes, dependencies, the database and responses fit together. They are slower, so there are fewer.

#### Q23. Why do API tests catch issues that mocked unit tests cannot? And how do you keep tests isolated from each other and from real data?
Ans: A mocked unit test only checks one piece, with fake versions of everything around it. It passes as long as the fakes behave the way the author assumed. An API test sends a real request through the whole path: routing, auth, validation, the service, real database queries and the response shape. So it catches problems that appear only when the pieces are joined, like a wrong route, a missing dependency, a bad query, or a response that does not match the schema.

Isolation between tests: every test starts clean, usually by emptying the tables after each test, and never depends on what another test left behind. Isolation from real data: tests use a separate test database, and refuse to run if its name is not clearly a test database. Outside services like Redis or the job queue are replaced with small fakes, so tests have no real side effects.

#### Q24. How do request IDs help debug distributed systems?
Ans: A request ID is a unique ID created when a request first enters the system, or taken from the incoming header. It is added to every log line, passed on to each service the request calls (usually in a header, and also into background jobs), and returned in the response. In a distributed system one request touches many services, and their logs are mixed with thousands of others. Searching the central logs for that one ID gives the full journey of the request: what happened, in which service, when, and where it failed or slowed down. Users and support can also quote the ID from a response when reporting a problem.

#### Q25. Why do containers improve environment consistency?
Ans: A container image packages the app together with its exact runtime, dependencies and the OS files it needs. The same image is built once and runs the same way on a laptop, in CI and in production, which removes the “it works on my machine” problem. Containers share the host’s kernel instead of running a full OS, so they are light and start fast. They are also isolated from each other, so apps with different versions of the same library do not clash. The setup is written in a Dockerfile, so it is reproducible, versioned and easy to roll back, and settings are passed in through environment variables.CI automatically runs checks on every push or pull request, on a clean machine. It finds problems early, before the code is merged, so the main branch stays working. It also removes “it works on my machine”, because nothing depends on one person’s laptop setup. The result is a clear pass or fail on every change, and a failing check can block the merge.

#### Q26. What does CI give a team?
Ans: CI automatically runs checks on every push or pull request, on a clean machine. It finds problems early, before the code is merged, so the main branch stays working. It also removes “it works on my machine”, because nothing depends on one person’s laptop setup. The result is a clear pass or fail on every change, and a failing check blocks the merge.