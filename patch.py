import re
import os

def patch_db():
    db_path = r"c:\Akshat\FINDING\DSA-practice\questions_db.py"
    with open(db_path, "r", encoding="utf-8") as f:
        content = f.read()

    lld_append = """            "q05_vending_machine": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/design-vending-machine-lld/", "description": "Vending state pattern machine.", "type": "design" },
            "q06_tic_tac_toe": { "difficulty": "Medium", "type": "design", "description": "Design Tic-Tac-Toe game." },
            "q07_snake_ladder": { "difficulty": "Medium", "type": "design", "description": "Design Snake & Ladder game." },
            "q08_chess_game": { "difficulty": "Hard", "type": "design", "description": "Design Chess Game." },
            "q09_library_management": { "difficulty": "Medium", "type": "design", "description": "Design Library Management System." },
            "q10_hotel_management": { "difficulty": "Medium", "type": "design", "description": "Design Hotel Management System." },
            "q11_coffee_vending": { "difficulty": "Medium", "type": "design", "description": "Design Coffee Vending Machine." },
            "q12_text_editor": { "difficulty": "Hard", "type": "design", "description": "Design Text Editor / Word Processor." },
            "q13_food_ordering": { "difficulty": "Hard", "type": "design", "description": "Design Food Ordering and Ratings (Zomato/Swiggy)." },
            "q14_logger_framework": { "difficulty": "Medium", "type": "design", "description": "Design a Logger Framework (Chain of Responsibility)." },
            "q15_notification_service": { "difficulty": "Medium", "type": "design", "description": "Design Notification Service (Observer Pattern)." },
            "q16_caching_framework": { "difficulty": "Hard", "type": "design", "description": "Design Caching Framework (LRU/LFU, Thread-safe)." },
            "q17_rate_limiter": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Rate Limiter (Token Bucket / Sliding Window)." },
            "q18_kv_store": { "difficulty": "Hard", "type": "design", "description": "Design Key-Value Store like Redis (LLD)." },
            "q19_blocking_queue": { "difficulty": "Medium", "type": "design", "description": "Design Thread-safe Blocking Queue." },
            "q20_rw_lock": { "difficulty": "Medium", "type": "design", "description": "Design Readers-Writers Lock." },
            "q21_pub_sub": { "difficulty": "Hard", "type": "design", "description": "Design Pub-Sub System." },
            "q22_web_crawler": { "difficulty": "Hard", "type": "design", "description": "Design Web Crawler (Extensible design)." },
            "q23_collaborative_editor": { "difficulty": "Hard", "type": "design", "description": "Design Collaborative Document Editor (like Google Docs)." },
            "q24_atm_system": { "difficulty": "Medium", "type": "design", "description": "Design ATM / Banking System." },
            "q25_undo_redo": { "difficulty": "Medium", "type": "design", "description": "Design Undo-Redo Framework (Command Pattern)." },
            "q26_airline_reservation": { "difficulty": "Hard", "type": "design", "description": "Design Airline Reservation System." },
            "q27_spotify_playlist": { "difficulty": "Medium", "type": "design", "description": "Design Spotify Playlist Manager." },
            "q28_url_shortener_lld": { "difficulty": "Medium", "type": "design", "description": "Design URL Shortener (bit.ly) - LLD focus." },
            "q29_elevator_group": { "difficulty": "Hard", "type": "design", "description": "Design Advanced Elevator Group Control." },
            "q30_ticket_resolution": { "difficulty": "Medium", "type": "design", "description": "Design Ticket Resolution System (Support/Tickets)." },
            "q31_file_system": { "difficulty": "Medium", "type": "design", "description": "Design File System (Composite Pattern)." },
            "q32_multiplayer_lobby": { "difficulty": "Hard", "type": "design", "description": "Design Online Multiplayer Game Lobby." }"""
            
    content = content.replace(
        '"q05_vending_machine": { "difficulty": "Medium", "link": "https://www.geeksforgeeks.org/design-vending-machine-lld/", "description": "Vending state pattern machine." }',
        lld_append
    )

    hld_append = """            "q05_video_streaming": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-video-streaming-system-like-netflix-youtube/",
                "description": "Design Netflix transcoding video delivery CDN pipeline.",
                "type": "design"
            },
            "q06_whatsapp": { "difficulty": "Hard", "type": "design", "description": "Design WhatsApp / Messenger - Chat + E2E encryption." },
            "q07_instagram": { "difficulty": "Hard", "type": "design", "description": "Design Instagram - Stories, feed, reels." },
            "q08_swiggy_doordash": { "difficulty": "Hard", "type": "design", "description": "Design Swiggy / DoorDash - Food delivery logistics." },
            "q09_google_docs": { "difficulty": "Hard", "type": "design", "description": "Design Google Docs - Real-time collaboration." },
            "q10_dropbox": { "difficulty": "Hard", "type": "design", "description": "Design Dropbox / Google Drive - File storage/sync." },
            "q11_replit": { "difficulty": "Hard", "type": "design", "description": "Design Replit / Online IDE - Real-time code collaboration." },
            "q12_distributed_cache": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Cache (Redis-like)." },
            "q13_rate_limiter_hld": { "difficulty": "Medium", "type": "design", "description": "Design Distributed Rate Limiter." },
            "q14_search_engine": { "difficulty": "Hard", "type": "design", "description": "Design Search Engine (Google-scale)." },
            "q15_notification_system": { "difficulty": "Medium", "type": "design", "description": "Design Notification System (Push/Email/SMS)." },
            "q16_api_gateway": { "difficulty": "Medium", "type": "design", "description": "Design API Gateway and Load Balancer." },
            "q17_workflow_orchestrator": { "difficulty": "Hard", "type": "design", "description": "Design Workflow Orchestrator (Airflow style)." },
            "q18_distributed_scheduler": { "difficulty": "Hard", "type": "design", "description": "Design Distributed Job Scheduler." },
            "q19_analytics_platform": { "difficulty": "Hard", "type": "design", "description": "Design Analytics Platform (Batch + Real-time)." },
            "q20_cdn": { "difficulty": "Medium", "type": "design", "description": "Design CDN (Content Delivery Network)." },
            "q21_event_streaming": { "difficulty": "Hard", "type": "design", "description": "Design Event Streaming Platform (Kafka style)." },
            "q22_payment_gateway": { "difficulty": "Hard", "type": "design", "description": "Design Payment Gateway (Stripe, Razorpay)." },
            "q23_stock_trading": { "difficulty": "Hard", "type": "design", "description": "Design Stock Trading Platform / Exchange." },
            "q24_rtb_ad_system": { "difficulty": "Hard", "type": "design", "description": "Design Real-Time Bidding Ad System." },
            "q25_monitoring_alerting": { "difficulty": "Medium", "type": "design", "description": "Design Monitoring & Alerting (Prometheus/Grafana)." },
            "q26_recommendation_engine": { "difficulty": "Hard", "type": "design", "description": "Design Recommendation Engine (Netflix-style)." },
            "q27_leaderboard": { "difficulty": "Medium", "type": "design", "description": "Design Leaderboard & Ranking System (Top K Problem)." },
            "q28_chatbot_platform": { "difficulty": "Medium", "type": "design", "description": "Design Chatbot Platform." },
            "q29_ecommerce": { "difficulty": "Hard", "type": "design", "description": "Design E-commerce Platform (Amazon/Flipkart)." },
            "q30_multiplayer_backend": { "difficulty": "Hard", "type": "design", "description": "Design Multiplayer Game Backend." },
            "q31_zoom": { "difficulty": "Hard", "type": "design", "description": "Design Zoom-like Video Conferencing System." }"""

    content = content.replace(
        '''            "q05_video_streaming": {
                "difficulty": "Hard",
                "link": "https://www.geeksforgeeks.org/design-video-streaming-system-like-netflix-youtube/",
                "description": "Design Netflix transcoding video delivery CDN pipeline."
            }''',
        hld_append
    )
    
    # Also fix some stubs that are design type
    content = content.replace('"description": "Design online ticket booker." }', '"description": "Design online ticket booker.", "type": "design" }')
    content = content.replace('"description": "Elevator dispatch constraints." }', '"description": "Elevator dispatch constraints.", "type": "design" }')
    content = content.replace('"description": "Expense share calculations." }', '"description": "Expense share calculations.", "type": "design" }')

    # Fix HLD components
    content = content.replace('"description": "LB routing logic." }', '"description": "LB routing logic.", "type": "design" }')
    content = content.replace('"description": "Cache invalidation write policies." }', '"description": "Cache invalidation write policies.", "type": "design" }')
    content = content.replace('"description": "Topic partition consumer lags." }', '"description": "Topic partition consumer lags.", "type": "design" }')
    content = content.replace('"description": "Static content edge validation." }', '"description": "Static content edge validation.", "type": "design" }')
    content = content.replace('"description": "Horizontal databases partitioning schemes." }', '"description": "Horizontal databases partitioning schemes.", "type": "design" }')
    
    content = content.replace('"description": "Design Twitter feed timeline aggregation."\n            }', '"description": "Design Twitter feed timeline aggregation.",\n                "type": "design"\n            }')
    content = content.replace('"description": "Design Uber dispatch driver passenger matching service.",\n                "starter_code": "",\n                "solutions": "",\n                "test_code": ""\n            }', '"description": "Design Uber dispatch driver passenger matching service.",\n                "type": "design"\n            }')
    content = content.replace('"description": "Design a high-scale TinyURL redirection engine.",\n                "starter_code": "",\n                "solutions": "",\n                "test_code": ""\n            }', '"description": "Design a high-scale TinyURL redirection engine.",\n                "type": "design"\n            }')
    content = content.replace('"description": "Design an Automated Vehicle Damage Auto-Penalty Pipeline.",\n                "starter_code": "class DamageDetectionPipeline:\\n    pass",\n                "solutions": "",\n                "test_code": ""\n            }', '"description": "Design an Automated Vehicle Damage Auto-Penalty Pipeline.",\n                "type": "design"\n            }')
    
    with open(db_path, "w", encoding="utf-8") as f:
        f.write(content)

def patch_generator():
    gen_path = r"c:\Akshat\FINDING\DSA-practice\generator.py"
    with open(gen_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace('if file_type == "code" or not challenge_key.endswith(".md"):', 'if file_type == "code":')
    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    patch_db()
    patch_generator()
    print("Patch applied successfully.")
