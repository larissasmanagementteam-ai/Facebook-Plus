Facebook System Design — Python Simulation
A complete, runnable simulation of Facebook's core backend architecture, implemented in pure Python. No external dependencies — just the standard library.
Overview
This project breaks down how Facebook (Meta) actually works at scale — from the social graph to the ads auction — and implements each system as a standalone Python module you can run and study.
It covers the same systems that power billions of daily users: TAO, News Feed ranking, Unicorn search, Messenger, GraphQL, and more.
Modules
Module
File
What it covers
1
1_tao_graph.py
TAO Social Graph — nodes, edges, associations
2
2_news_feed.py
News Feed — candidate generation, ML ranking, re-rank
3
3_cache_and_cdn.py
Memcached look-aside cache + CDN edge nodes
4
4_notifications.py
Fan-out notification system (celebrity problem)
5
5_search.py
Unicorn Search Engine — inverted index, TF-IDF, social boost
6
6_auth_sessions.py
Authentication — password hashing, sessions, access tokens
7
7_graphql_api.py
GraphQL API — resolvers, mutations, scope-based auth
8
8_realtime_messaging.py
Messenger — WebSocket, message queue, presence, read receipts
9
9_ads_engine.py
Ads Engine — auction, targeting, budget pacing, frequency cap
10
10_microservices.py
Production Security — API gateway, risk fusion, feedback loop
11
11_production_deploy.py
Kubernetes + CI/CD + multi-region failover + Prometheus
Quick Start
# Run the full system (all 11 modules)
python main.py

# Run any individual module
python 1_tao_graph.py
python 7_graphql_api.py
python 9_ads_engine.py
Requirements: Python 3.10 or higher. No pip installs needed.
Architecture Highlights
1. TAO — The Social Graph
Facebook's custom graph database. Stores every relationship as nodes (users, posts, pages) and edges (friends, likes, follows). Designed for high-read, low-latency graph traversal at 1 billion+ nodes.
2. News Feed Ranking
A 3-stage ML pipeline:
Candidate generation — fetch posts from friends/followed pages
Scoring — rank by engagement signals, freshness, author affinity
Re-ranking — apply diversity rules, ad insertion, content policies
3. Cache + CDN
Facebook serves ~500TB of media per day using:
Memcached — look-aside caching with 99%+ hit rate
Haystack — blob storage for photos/videos
CDN edge nodes — serve static content from 200+ PoPs worldwide
4. Notifications — Fan-out
The "celebrity problem": when Cristiano Ronaldo posts, 600M followers need to be notified. Facebook solves this with a hybrid push/pull fan-out strategy based on follower count thresholds.
5. Unicorn Search
Facebook's internal search engine. Combines:
Inverted index (TF-IDF relevance)
Social graph boosting (friends' interactions)
Typeahead completion
Entity-type ranking (users > posts > events)
6. Auth & Sessions
SHA-256 + salt + pepper password hashing
Session management with per-device revocation
Short-lived access tokens with scope-based permissions
Multi-device logout
7. GraphQL API
Facebook invented GraphQL in 2012 to solve REST's over-fetching problem. Key concepts:
Schema-defined types (User, Post, Comment)
Resolver functions per field
DataLoader pattern (N+1 query prevention)
Scope-based field-level authorization
8. Real-time Messaging (Messenger)
WebSocket connection manager (one per tab/device)
Async message queue with exponential backoff retry
Typing indicators and read receipts
Presence system (online/offline/away)
Group chat fan-out
9. Ads Engine
Facebook's ad system is the revenue core of Meta (~$120B/year).
Vickrey auction — second-price, incentivizes honest bidding
Targeting — demographics, interests, lookalike audiences
Predicted CTR — XGBoost-style weighted scoring
Budget pacing — spreads daily spend evenly
Frequency capping — prevents ad fatigue (max 3 impressions/day)
10. Production Security System
API Gateway with rate limiting (per IP, per device)
Risk fusion engine: XGBoost + LSTM + SVM parallel inference
Kafka event streaming backbone
Redis real-time caching
OTP step-up authentication
ML feedback loop (label → retrain → deploy)
11. Production Deploy
Kubernetes cluster management (pods, deployments, services)
Rolling updates (zero-downtime deploys)
Canary deployments (10% traffic split)
Horizontal Pod Autoscaler (CPU-based scale up/down)
CI/CD pipeline (build → test → security scan → deploy → verify)
Prometheus metrics + alert rules
Multi-region failover (us-east + eu-west)
HashiCorp Vault secret rotation
Design Patterns Used
Look-aside caching (Cache + CDN)
Fan-out on write vs read (Notifications)
Second-price auction (Ads Engine)
DataLoader / request batching (GraphQL)
Event sourcing (Kafka backbone)
Hash chain integrity (Audit log)
Weighted ensemble scoring (Risk fusion)
Rolling + canary deployments (Kubernetes)
Key Concepts Demonstrated
How Facebook handles the N+1 query problem in GraphQL
Why Facebook uses second-price auctions for ads
How the celebrity problem is solved in notifications
Why look-aside caching (not write-through) dominates at scale
How LSTM sequences detect fraudulent login patterns
What zero-downtime deploys actually look like in Kubernetes
Project Structure
facebook_system_design/
├── README.md
├── main.py                    ← Run everything
├── 1_tao_graph.py
├── 2_news_feed.py
├── 3_cache_and_cdn.py
├── 4_notifications.py
├── 5_search.py
├── 6_auth_sessions.py
├── 7_graphql_api.py
├── 8_realtime_messaging.py
├── 9_ads_engine.py
├── 10_microservices.py
└── 11_production_deploy.py
Learning Path
If you're studying system design, go through the modules in order:
Start with 1_tao_graph.py — understand the data model
Then 6_auth_sessions.py — how users authenticate
Then 2_news_feed.py — how content is ranked
Then 8_realtime_messaging.py — how real-time works
Then 9_ads_engine.py — how the business model works
Finally 11_production_deploy.py — how it all runs in production
Author
Built as a technical system design breakdown — a complete, working simulation of Facebook's architecture in Python.
Each module is self-contained and runnable independently. The main.py file orchestrates all modules together as one unified system demo.