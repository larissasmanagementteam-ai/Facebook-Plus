"""
Facebook System Design — Full App Orchestrator
================================================
Ties together all 9 modules into a single unified simulation.

Modules:
  1. TAO Social Graph
  2. News Feed Ranking Pipeline
  3. Cache + CDN
  4. Notification Fan-out
  5. Search Engine (Unicorn)
  6. Authentication & Sessions
  7. GraphQL API
  8. Real-time Messaging
  9. Ads Engine
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import importlib.util

def load(filename, alias):
    """Dynamically load a module from file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(alias, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

m1 = load("1_tao_graph.py", "tao")
m2 = load("2_news_feed.py", "feed")
m3 = load("3_cache_and_cdn.py", "cache")
m4 = load("4_notifications.py", "notif")
m5 = load("5_search.py", "search")
m6 = load("6_auth_sessions.py", "auth")
m7 = load("7_graphql_api.py", "gql")
m8 = load("8_realtime_messaging.py", "msg")
m9 = load("9_ads_engine.py", "ads")


def divider(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


if __name__ == "__main__":

    # ── 1. AUTH ──────────────────────────────
    divider("1. Authentication & Sessions")
    auth = m6.AuthService()
    auth.register("alice@meta.com", "Pass123!")
    auth.register("bob@meta.com",   "Pass456!")
    auth.register("carol@meta.com", "Pass789!")
    user_alice, session_alice, token_alice = auth.login(
        "alice@meta.com", "Pass123!", device="iPhone", ip="10.0.0.1")
    user_bob, session_bob, token_bob = auth.login(
        "bob@meta.com", "Pass456!", device="Android", ip="10.0.0.2")
    print(f"  Alice logged in  | token: {token_alice.token[:16]}...")
    print(f"  Bob logged in    | token: {token_bob.token[:16]}...")
    print(f"  Scopes: {token_alice.scopes}")


    # ── 2. SOCIAL GRAPH (TAO) ────────────────
    divider("2. TAO Social Graph")
    tao = m1.TAOStore()
    alice = tao.create_node("user", {"name": "Alice", "user_id": user_alice.id})
    bob   = tao.create_node("user", {"name": "Bob",   "user_id": user_bob.id})
    carol = tao.create_node("user", {"name": "Carol"})
    post1 = tao.create_node("post", {"text": "Hello from Alice!", "author": alice.id})
    post2 = tao.create_node("post", {"text": "Bob's big news 🎉", "author": bob.id})
    tao.create_edge(alice.id, bob.id,   "friend")
    tao.create_edge(bob.id,   alice.id, "friend")
    tao.create_edge(alice.id, carol.id, "friend")
    tao.create_edge(bob.id,   post2.id, "posted")
    tao.create_edge(alice.id, post2.id, "liked")
    tao.create_edge(carol.id, post2.id, "liked")
    friends = tao.get_edges(alice.id, "friend")
    print(f"  Alice's friends: {[tao.get_node(e.to_id).data['name'] for e in friends]}")
    print(f"  Alice liked Bob's post: {tao.edge_exists(alice.id, post2.id, 'liked')}")


    # ── 3. CACHE ─────────────────────────────
    divider("3. Cache + CDN")
    cache_sim = m3.MemcachedSimulator()
    db_sim    = m3.DatabaseSimulator()
    layer     = m3.CacheLayer(cache_sim, db_sim)
    db_sim.write("user:alice", {"name": "Alice", "followers": 320})
    v, src = layer.get("user:alice"); print(f"  1st read: {src}")
    v, src = layer.get("user:alice"); print(f"  2nd read: {src}")
    print(f"  Hit rate: {layer.hit_rate():.0%}")
    cdn = m3.CDNEdgeNode("us-east")
    origin = lambda mid, res: f"[blob:{mid}@{res}]".encode()
    r = cdn.fetch("photo_alice_001", "1080p", origin_fn=origin)
    print(f"  CDN 1st fetch: {r['source']}")
    r = cdn.fetch("photo_alice_001", "1080p", origin_fn=origin)
    print(f"  CDN 2nd fetch: {r['source']}")


    # ── 4. NEWS FEED ─────────────────────────
    divider("4. News Feed Ranking")
    posts = [
        m2.Post("p1","bob",   "Bob's big news 🎉",       "text",  time.time()-1800, likes=80,  comments=12),
        m2.Post("p2","carol", "Carol's travel photo 🌴", "photo", time.time()-900,  likes=200, comments=60),
        m2.Post("p3","bob",   "Morning run ✅",          "text",  time.time()-3600, likes=15,  comments=3),
        m2.Post("p4","dave",  "Stranger's post",         "link",  time.time()-600,  likes=5,   comments=1),
    ]
    signals = m2.UserSignals(
        user_id="alice",
        friend_interactions={"bob": 0.9, "carol": 0.7},
        content_preferences={"photo": 0.9, "text": 0.5, "link": 0.2},
        active_hours=list(range(7, 23)),
    )
    feed_svc = m2.NewsFeedService()
    feed = feed_svc.get_feed("alice", ["bob","carol"], posts, signals)
    print(f"  Alice's feed ({len(feed)} items):")
    for i, item in enumerate(feed, 1):
        if isinstance(item, dict):
            print(f"    [{i}] AD")
        else:
            print(f"    [{i}] @{item.post.author_id}: {item.post.text} | score={item.score:.3f}")


    # ── 5. NOTIFICATIONS ─────────────────────
    divider("5. Notifications & Fan-out")
    notif_store = m4.NotificationStore()
    fan_out     = m4.FanOutService(notif_store)
    fan_out.notify_like("bob",   "alice", "p1", "Bob")
    fan_out.notify_comment("carol", "alice", "p1", "Carol", "Love this post!")
    fan_out.notify_friend_request("dave", "alice", "Dave")
    fan_out.fan_out_post("alice", "p_new", "Alice", ["bob","carol"], 2)
    print(f"  Alice's unread: {notif_store.unread_count('alice')}")


    # ── 6. SEARCH ────────────────────────────
    divider("6. Search (Unicorn)")
    engine = m5.UnicornSearchEngine()
    search_docs = [
        m5.SearchDocument("u1","user","Alice Johnson","Engineer at Meta","u1",["#tech"],0.8),
        m5.SearchDocument("u2","user","Bob Smith",    "PM and traveler",  "u2",["#travel"],0.5),
        m5.SearchDocument("p1","post","Meta AI News", "AI developments",  "u1",["#AI"],0.7),
        m5.SearchDocument("e1","event","Meta Tech Talk","Annual dev conf","u3",["#meta"],0.9),
    ]
    for d in search_docs: engine.add_document(d)
    results = engine.search("meta tech", "alice", friend_ids=["u2"])
    print(f"  Search 'meta tech': {len(results)} results")
    for r in results:
        print(f"    [{r.document.entity_type}] {r.document.title} | score={r.score:.3f}")
    tips = engine.typeahead("ali", "alice", ["u2"])
    print(f"  Typeahead 'ali': {tips}")


    # ── 7. GRAPHQL ───────────────────────────
    divider("7. GraphQL API")
    db = m7.DataStore()
    db.seed()
    gql = m7.GraphQLEngine(db)
    q = gql.execute(
        {"user": {"id": "u1", "fields": ["name","email","followers","posts"]}},
        viewer_id="u1", scopes=["read","read_email","write"]
    )
    print(f"  User query: {q['data']['user']['name']} | {q['data']['user']['followers']} followers")
    print(f"  Posts: {len(q['data']['user']['posts'])}")
    m = gql.mutate({"createPost": {"text": "Posted via GraphQL!"}}, "u2", ["read","write"])
    print(f"  New post: \"{m['data']['createPost']['text']}\"")


    # ── 8. MESSAGING ─────────────────────────
    divider("8. Real-time Messaging")
    messenger = m8.MessengerService()
    messenger.ws.connect("alice", "iPhone")
    messenger.ws.connect("bob",   "Android")
    msg1 = messenger.send_message("alice", "bob",   "Hey Bob!")
    msg2 = messenger.send_message("bob",   "alice", "Hey Alice!")
    msg3 = messenger.send_message("alice", "carol", "Carol, you around?")  # carol offline
    stats = messenger.process_queue()
    print(f"  Queue stats: {stats}")
    group = messenger.store.create_conversation(
        ["alice","bob","carol"], is_group=True, name="Dev Team 🚀")
    messenger.send_group_message("alice", group.id, "Team standup in 5!")
    print(f"  Active online users: {messenger.ws.active_users()}")


    # ── 9. ADS ───────────────────────────────
    divider("9. Ads Engine")
    ads_engine = m9.AdsEngine()
    ads_list = [
        m9.Ad("a1","adv1","Learn Python","Master Python in 30 days","Start Now",
              m9.AdTargeting((18,45),["US","UK"],["tech","coding"],None,[]),
              bid_amount=5.0, bid_type="CPM", daily_budget=100.0, lifetime_budget=1000.0),
        m9.Ad("a2","adv2","Book Travel","Flights from $199","Book Now",
              m9.AdTargeting((25,55),["US"],["travel"],None,[]),
              bid_amount=3.5, bid_type="CPC", daily_budget=200.0, lifetime_budget=5000.0),
        m9.Ad("a3","adv3","iPhone 17 Pro","Pre-order now","Pre-order",
              m9.AdTargeting((18,65),["US","UK"],["tech"],None,[]),
              bid_amount=8.0, bid_type="CPM", daily_budget=500.0, lifetime_budget=50000.0),
    ]
    for ad in ads_list: ads_engine.register_ad(ad)
    ad_users = [
        m9.UserProfile("alice", 28, "F", "US", ["tech","coding","travel"], {}),
        m9.UserProfile("bob",   35, "M", "UK", ["tech","fitness"],         {}),
    ]
    for u in ad_users:
        result = ads_engine.serve(u)
        if result:
            print(f"  {u.user_id}: \"{result.winning_ad.title}\" | CTR={result.predicted_ctr:.2%} | price=${result.clearing_price:.4f}")

    divider("System Summary")
    print("  ✅ Auth & Sessions      — login, tokens, multi-device")
    print("  ✅ TAO Social Graph     — nodes, edges, associations")
    print("  ✅ Cache + CDN          — memcached, look-aside, edge nodes")
    print("  ✅ News Feed            — candidate gen, ML ranking, re-rank")
    print("  ✅ Notifications        — fan-out, push/pull model")
    print("  ✅ Search (Unicorn)     — inverted index, TF-IDF, social boost")
    print("  ✅ GraphQL API          — resolvers, mutations, scope auth")
    print("  ✅ Real-time Messaging  — WebSocket, queue, presence, receipts")
    print("  ✅ Ads Engine           — auction, targeting, budget, freq cap")
    print()
    print("  All 9 modules running. Facebook decoded. 🚀")
