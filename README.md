# simple-spatial-quest-apis

** Instructions to run (Local): **
1. pip install deps (flask, shapely, sqlalchemy etc.) and set DATABASE_URL to your local Postgres url in .env
2. Run init_db.py script that initializes database with mock data
3. 4 tables created. (1) asset_data for storing signals and created assets/content (2) participant_data for storing user data who join the quest (3) quest_data for storing quests (4) geo_fence for storing geo_fences (polygon geometry of campus, downtown locations)
4. Run server via python3 app.py (debug on port 5000)
4. Example curl commands for API testing. Example uses Stanford campus co-ordinates for geofencing. Any co-ordinates within the fence are valid.

GET APIs: 
curl "http://127.0.0.1:5000/quest_discovery?lat=2.5&lon=2.5" (for outside region - returns error)
curl "http://127.0.0.1:5000/quest_discovery?lat=37.4250&lon=-122.1625" (for inside region - valid)


POST APIs:

JOIN:
curl -X POST "http://127.0.0.1:5000/quest_join?questId=1&userId=user1&lat=37.7749&lon=-122.4194" (outside geofence)
curl -X POST "http://127.0.0.1:5000/quest_join?questId=1&userId=user1&lat=37.4260&lon=-122.1650" (inside geofence)

LEAVE:
curl -X POST "http://127.0.0.1:5000/quest_leave?questId=1&userId=user1&lat=37.7749&lon=-122.4194" (outside geofence)
curl -X POST "http://127.0.0.1:5000/quest_leave?questId=1&userId=user1&lat=37.4260&lon=-122.1650" (inside geofence)

COLLECT ASSET:
curl -X POST "http://127.0.0.1:5000/collect_asset?questId=1&userId=user1&assetId=1&lat=37.7749&lon=-122.4194" (outside geofence)
curl -X POST "http://127.0.0.1:5000/collect_asset?questId=1&userId=user1&assetId=1&lat=37.4260&lon=-122.1650" (inside geofence)

CREATE_ASSET:
curl -X POST "http://127.0.0.1:5000/create_asset?assetId=11&asset_name=MyNewAsset&userId=user1&asset_src=https://example.com/treasure10.jpg&user_lat=37.4260&user_lon=-122.1650&dest_lat=37.4255&dest_lon=-122.1640" 



** v1 Release Notes (4/13): **
1. Barebone structure and backend APIs with mocked data (see init_db.py script). No multi-threading/concurrency
2. Docker doesn't work yet. Need to run locally.
3. No full-fledged unit tests


** Incomplete/TODO: **
1. Bugs - Not fully vetted and tested code. Only main flow is tested (somewhat). So you can assume some corner cases not taken care of/bugs to be there
2. No concurrency/synchronization. Will mostly fail or result in invalid states when used for multi-user scenarios. 
3. Better abstractions. Move common check to private methods, better code organization etc. etc.
4. (Bad perf, not scalable) Brute-force implementation. Storing and querying geofences via SQL (Postgres). The problem is similar to proximity server, and there are well known techniques like geo-hashing
5. (Bad perf) No caching. Exploring using memcache is a good logical next step.

