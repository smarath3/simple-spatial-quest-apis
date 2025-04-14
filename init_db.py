# Script to init database with mock data
# create a bunch of geofences
# create a bunch of quests
# create a bunch of participants

from shapely import to_wkt
from shapely.geometry import Polygon
from server.models.asset_data import AssetData, store_asset
from server.models.geo_fence import store_geofence
from server.models.geo_fence import GeoFence
from server.models.quest_data import QuestData, store_quest
from server.models.participant_data import ParticipantData, store_participant
from server.models.quest_data import QuestState
from datetime import datetime
import random


# Create 3 geofences with polygon coordinates, place bunch of quests in them
# and place a bunch of participants in them

# Create a polygon for Stanford Campus
polygon1 = Polygon([(37.4277, -122.1700), (37.4277, -122.1600), 
                (37.4240, -122.1600), (37.4240, -122.1700), (37.4277, -122.1700)])
    
fence1 = GeoFence(
    name="Stanford Campus",
    polygon = to_wkt(polygon1)
)

# Create a polygon for Downtown Palo Alto
polygon2 = Polygon([(37.4419, -122.1649), (37.4419, -122.1549),
                (37.4379, -122.1549), (37.4379, -122.1649), (37.4419, -122.1649)])

fence2 = GeoFence(
    name="Downtown Palo Alto",
    polygon = to_wkt(polygon2)
)


# Create a polygon for Google Campus
polygon3 = Polygon([(37.4220, -122.0841), (37.4220, -122.0741),
                (37.4180, -122.0741), (37.4180, -122.0841), (37.4220, -122.0841)])
    
fence3 = GeoFence(
    name="Google Campus",
    polygon = to_wkt(polygon3)
)

id1 = store_geofence(fence1.name, fence1.polygon) # for Stanford Campus
id2 = store_geofence(fence2.name, fence2.polygon)
id3 = store_geofence(fence3.name, fence3.polygon)

# # Example points within Stanford Campus polygon
# stanford_points = [
#     (37.4260, -122.1650),  # Center-ish
#     (37.4250, -122.1625),  # Southeast
#     (37.4265, -122.1675),  # Northwest
#     (37.4255, -122.1640),  # South-central
#     (37.4270, -122.1635),  # Northeast

#create a bunch of assets in each geofence with mocked co-orindates
# Mock asset data creation

# Sample asset types and names
asset_types = ['quest', 'location']
asset_names = ['Treasure', 'Artifact', 'Collectible', 'Trophy', 'Medal']
asset_sources = ['https://example.com/treasure1.jpg', 'https://example.com/treasure2.jpg', 'https://example.com/treasure3.jpg']
asset_owners = ['user1', 'user2']

# Stanford Campus assets (id1)
stanford_assets = [
    AssetData(
        asset_id=i+1,
        asset_name=f"{random.choice(asset_names)} {i}",
        asset_source=random.choice(asset_sources),
        asset_desc=f"Asset description {i}",
        asset_status='active',
        asset_owner=random.choice(asset_owners),
        asset_location=f"{37.426 + random.uniform(-0.001, 0.001)},{-122.165 + random.uniform(-0.002, 0.002)}",
        asset_timestamp=datetime.now().isoformat(),
        asset_type=random.choice(asset_types),
        geofence_id=1,  # geofence_id 1 is for Stanford Campus
    ) for i in range(5)
]

quest1assetlist= []
user1owned_assets = []
user2owned_assets = []

print(f"Stanford assets: {stanford_assets}")

for asset in stanford_assets:
    # Store each asset in the database
    # Store result 
    asset_id = store_asset(asset, False)
    if asset.asset_owner == 'user1':
        user1owned_assets.append(str(asset.asset_id))
    elif asset.asset_owner == 'user2':
        user2owned_assets.append(str(asset.asset_id))
    quest1assetlist.append(str(asset_id))


# Create a quest in the Stanford Campus geofence

#for 1st geofence
quest1 = QuestData(
    quest_name="Quest 1", 
    quest_assetids=",".join(quest1assetlist), # Asset IDs from stored assets
    quest_desc="Description of Quest 1",
    active_participant_list="",
    quest_state=QuestState.INACTIVE,
    quest_start_time="2023-10-01T00:00:00Z",
    quest_end_time="2023-10-31T23:59:59Z",
    latitude=37.4267,
    longitude=-122.1697,  # Inside Stanford Campus
    geofence_id=id1)

quest2 = QuestData(
    quest_name="Quest 2",
    quest_desc="Description of Quest 2",
    active_participant_list="",
    quest_state=QuestState.INACTIVE,
    quest_start_time="2023-10-01T00:00:00Z",
    quest_end_time="2023-10-31T23:59:59Z",
    latitude=37.4260,
    longitude=-122.1670,  # Inside Stanford Campus
    geofence_id=id1)

quest3 = QuestData(
    quest_name="Quest 3",
    quest_desc="Description of Quest 3",
    active_participant_list="",
    quest_state=QuestState.INACTIVE,
    quest_start_time="2023-10-01T00:00:00Z",
    quest_end_time="2023-10-31T23:59:59Z",
    latitude=37.4250,
    longitude=-122.1650,  # Inside Stanford Campus
    geofence_id=id1)

qd1 = store_quest(quest1, False)
qd2 = store_quest(quest2, False)
qd3 = store_quest(quest3, False)

# Creare 2 users
# Mock participant data
# Create two participants
participant1 = ParticipantData(
    participant_id="user1",
    is_joined=False,
    owned_assets=",".join(user1owned_assets),  # User1 owns some assets
    collected_assets="",  # Start with no assets
    quest_state=QuestState.INACTIVE,
    active_quest="",  # Assigned to quest1
    completed_quests="",
    userlocation="37.4260,-122.1650"  # Location within Stanford Campus
)

participant2 = ParticipantData(
    participant_id="user2",
    is_joined=False,
    owned_assets=",".join(user2owned_assets),  # User2 owns some assets
    collected_assets="",
    quest_state=QuestState.INACTIVE,
    active_quest="", # Also assigned to quest1
    completed_quests="",
    userlocation="37.4265,-122.1655"  # Different location within Stanford Campus
)

# Store participants in database # Similar to registration
p1 = store_participant(participant1, False)
p2 = store_participant(participant2, False)