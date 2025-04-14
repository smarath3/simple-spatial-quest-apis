from flask import jsonify
from shapely import wkt
from shapely.geometry import Polygon, Point
from server.models.geo_fence import get_all_geofences
from server.models.quest_data import get_quest_by_geofence_id
from server.models.quest_data import QuestData, QuestState
from server.models.quest_data import get_quest_by_id
from server.models.geo_fence import get_geofence_by_id
from server.models.participant_data import get_participant_by_id
from server.models.participant_data import store_participant
from server.models.quest_data import store_quest
from server.models.asset_data import AssetData, store_asset
import json


class SpatialQuestAPI:

    def __init__(self, quest_service):
        self.quest_service = quest_service

    def quest_discovery(self, lat, lon):
        quests = []
        # get polygon that emcompass the point
        #get quests for each polygons
        #return list of quests
        # Check if the user location is within the geofence polygon

        user_location = Point(lat, lon)
        # Check if the user is within the geofence
        # If the user is within the geofence, return the list of quests
        # If the user is outside the geofence, return an empty list or a message

        ##Brute Force!! SEVERE PERF HIT FOR ANYTHING SCALABLE. Use better/different data bases
        geofences = get_all_geofences()
        print(geofences)
        for geofence in geofences:
            # Convert the WKT polygon to a Shapely Polygon object
            # Create the polygon from the WKT string
            polygon = wkt.loads(geofence.polygon)

            if polygon.contains(user_location):
                print(f"User is within geofence: {geofence.name}")
                # Get quests for this geofence
                # If the user is within the geofence, get quests for this geofence
                quests = get_quest_by_geofence_id(geofence.geofence_id)
                print(f"Quest found: {quests}")
                print(type(quests))

        if quests:
            print(f"Quests found: {quests}")
            serialized_quests = [quest.serialize() for quest in quests]
            # res = json.dumps(serialized_quests)
            # return res, 200
            return jsonify(serialized_quests), 200
        
        else:
            return jsonify({"message": "No quests found for the given location"}), 404

    
    # Quest Participation API
    # Join/leave quest endpoints
    # Tracking participant status
    # Asset collection endpoint
    # Example: POST /quests/{questId}/join

    # POST /quests/{questId}/join
    def quest_join(self, questid, userid, lat, lon):

        user_location = Point(lat, lon) #latest from request; since the DB location may not be upto date

        # Check participant status
        participant = get_participant_by_id(userid)
        if not participant:
            print(f"Participant with ID {userid} not found.")
            return jsonify({"error": "Participant not found"}), 404

        if participant.active_quest is questid:
            print(f"Participant {userid} is already joined to quest {questid}.")
            return jsonify({"error": "Participant already joined"}), 400
        
        if participant.quest_state is QuestState.IN_PROGRESS:
            print(f"Participant {userid} hasn't joined Quest? Quest state is already IN_PROGRESS")
            return jsonify({"error": "Participant hasn't joined Quest? Quest state is already IN_PROGRESS"}), 400


        # Check Quest status
        quest = get_quest_by_id(questid)
        if not quest:
            print(f"Quest with ID {questid} not found.")
            return jsonify({"error": "Quest not found"}), 404
        
        # Not need to check Quest state. Whatever the state is, we will allow the user to join since there can be multiple participants in the same quest
        if quest.quest_state is QuestState.BADSTATE:
            print(f"Quest with ID {questid} is not in a valid state to join.")
            return jsonify({"error": "Quest not in a valid state to join"}), 400

        geofence = get_geofence_by_id(quest.geofence_id)
        polygon = wkt.loads(geofence.polygon)
        if polygon.contains(user_location):
            print(f"User is within geofence: {geofence.name} for the quest: {quest.quest_name} to collect assets")

            activeusers = quest.active_participant_list.split(",") if quest.active_participant_list else []
            
            if(userid is None or userid == ''):
                print(f"User ID is missing")
                return jsonify({"error": "User ID is missing"}), 400
            
            if userid in activeusers:
                print(f"User {userid} is already a participant in the quest")
                return jsonify({"error": "User already joined"}), 400
            else:
                # Add the user to the active participant list
                activeusers.append(userid)
                print(f"Active users: {activeusers}")
                quest.active_participant_list = ",".join(activeusers) if len(activeusers) > 1 else activeusers[0] if activeusers else ""
                quest.quest_state = QuestState.IN_PROGRESS  # Update the quest state to active

                # Update the quest in the database
                # Update the quest in the database with new active participant list
                store_quest(quest, True)  # True indicates an update operation

                #Update participant data
                # Update the participant's active quest
                participant.is_joined = True
                
                # Business logic question - when participant joins a quest, should we reset their collected assets?
                participant.collected_assets = ""  # Reset asset collections
                participant.quest_state = QuestState.IN_PROGRESS
                participant.active_quest = questid
                store_participant(participant, True)  # True indicates an update operation
                print(f"User {userid} joined the quest: {quest.quest_name}")
                return jsonify({"message": f"User {userid} joined the quest: {quest.quest_name}"})
        else:
            print(f"User is outside the geofence for the quest: {quest.quest_name}")
            return jsonify({"error": "User is outside the geofence"}), 400
        

    # POST /quests/{questId}/leave
    # Leave quest endpoint
    def quest_leave(self, questid, userid, lat, lon):
        user_location = Point(lat, lon) #latest from request; since the DB location may not be upto date

        # Check participant status
        participant = get_participant_by_id(userid)
        if not participant:
            print(f"Participant with ID {userid} not found.")
            return jsonify({"error": "Participant not found"}), 404

        if participant.active_quest != str(questid):
            print(f"Participant {userid} is not joined to quest {questid}.")
            return jsonify({"error": "Participant not joined"}), 400
        
        if participant.quest_state is not QuestState.IN_PROGRESS:
            print(f"Participant {userid} is not in this quest.")
            return jsonify({"error": "Participant not in this quest"}), 400

        # Check Quest status
        quest = get_quest_by_id(questid)
        if not quest:
            print(f"Quest with ID {questid} not found.")
            return jsonify({"error": "Quest not found"}), 404
        
        if quest.quest_state is not QuestState.IN_PROGRESS:
            print(f"Quest with ID {questid} is not in a valid in-progress state to leave.")
            return jsonify({"error": "Quest not in a valid in-progress to leave"}), 400

        geofence = get_geofence_by_id(quest.geofence_id)
        polygon = wkt.loads(geofence.polygon)
        if polygon.contains(user_location):
            print(f"User is within geofence: {geofence.name} for the quest: {quest.quest_name} they are trying to leave")
            
            if(userid is None or userid == ''):
                print(f"User ID is missing")
                return jsonify({"error": "User ID is missing"}), 400

            activeusers = quest.active_participant_list.split(",") if quest.active_participant_list else []

            if userid not in activeusers:
                print(f"User {userid} is not an active participant in the quest")
                return jsonify({"error": "User not an active participant in the quest"}), 400
            else:
                # Remove the user from the active participant list
                activeusers.remove(userid)
                print(f"Active users: {activeusers}")
                quest.active_participant_list = ",".join(activeusers) if len(activeusers) > 1 else activeusers[0] if activeusers else ""

                #update Participant data
                participant.is_joined = False
                participant.collected_assets = ""  # Reset asset collections
                participant.quest_state = QuestState.INACTIVE
                participant.active_quest = ""
                # participant.completed_quests = "" ; Can be retained since if participant joins later, their completed quests can be retained

                # Update the quest in the database
                store_quest(quest, True)

                #Update participant data
                store_participant(participant, True)
                print(f"User {userid} left the quest: {quest.quest_name}")
                return jsonify({"message": f"User {userid} left the quest: {quest.quest_name}"})
        else:
            print(f"User is outside the geofence for the quest: {quest.quest_name}")
            return jsonify({"error": "User is outside the geofence"}), 400        


    # Asset to collect during active quests
    def collect_asset(self, questid, userid, assetid, lat, lon):
        user_location = Point(lat, lon)

        # Check participant status
        participant = get_participant_by_id(userid)
        # Check Quest status
        quest = get_quest_by_id(questid)

        # DO all participant checks
        if not participant:
            print(f"Participant with ID {userid} not found.")
            return jsonify({"error": "Participant not found"}), 404
        
        if participant.active_quest != str(questid): 
            print(f"Participant {userid} is not in the quest {questid}. Participant active quest is {participant.active_quest}")
            return jsonify({"error": "Participant not in quest"}), 400
        
        if participant.quest_state is not QuestState.IN_PROGRESS:
            print(f"Participant {userid} is not in this quest.")
            return jsonify({"error": "Participant not in this quest"}), 400

        # check user is not trying to collect what they already have/own
        owned_assets = participant.owned_assets.split(",")  if participant.owned_assets else []
        if assetid in owned_assets:
            print(f"Participant {userid} already owns the asset {assetid}.")
            return jsonify({"error": "Participant already owns the asset"}), 400

        # Do all quest checks
        if not quest:
            print(f"Quest with ID {questid} not found.")
            return jsonify({"error": "Quest not found"}), 404

        #check if assetID to be collected is part of quest asset list
        quest_assets = quest.quest_assetids.split(",") if quest.quest_assetids else []
        print(f"Quest assets: {quest_assets}")
        if str(assetid) not in quest_assets:
            print(f"Asset {assetid} is not part of the quest {questid}.")
            return jsonify({"error": "Asset not part of the quest"}), 400
        
        if quest.quest_state is not QuestState.IN_PROGRESS:
            print(f"Quest with ID {questid} is not in a valid state to collect assets.")
            return jsonify({"error": "Quest not in a valid state to collect assets"}), 400
        
        active_participant_list = quest.active_participant_list.split(",")  if quest.active_participant_list else []
        if userid not in active_participant_list:
            print(f"Participant {userid} is not an active participant in the quest {questid}.")
            return jsonify({"error": "Participant not an active participant in the quest"}), 400
        
        # Check if the user location is within the geofence polygon
        geofence = get_geofence_by_id(quest.geofence_id)
        polygon = wkt.loads(geofence.polygon)
        if polygon.contains(user_location):
            print(f"User is within geofence: {geofence.name} for the quest: {quest.quest_name} they are trying to collect the asset")
            
            # Check if the asset is already collected
            collected_assets = participant.collected_assets.split(",") if participant.collected_assets else []
            if str(assetid) in collected_assets:
                print(f"Participant {userid} has already collected the asset {assetid}.")
                return jsonify({"error": "Participant has already collected the asset"}), 400
            
            #Check if asset is already owned
            if str(assetid) in owned_assets:
                print(f"Participant {userid} already owns the asset {assetid}.")
                return jsonify({"error": "Participant already owns the asset"}), 400
            
            # Add the asset to the participant's collected assets
            collected_assets.append(str(assetid))
            print(f"Collected assets: {collected_assets}")
            participant.collected_assets = ",".join(collected_assets) if len(collected_assets) > 1 else collected_assets[0] if collected_assets else ""


            # FINAL CHECK - Check if this was the last asset to be collected for quest to be completed
            # Check formula = colledted + owned = original asset list for the quest
            merged_assets = owned_assets + collected_assets
            quest_assets = quest.quest_assetids.split(",") if quest.quest_assetids else []
            if set(merged_assets) == set(quest_assets):
                # Mark the quest as completed for the participant
                participant.quest_state = QuestState.COMPLETED
                print(f"Participant {userid} has completed the quest {quest.quest_name}!!! YAY !!!!")
                participant.active_quest = ""
                cq = participant.completed_quests.split(",")
                cq.append(str(questid))
                print(f"Completed quests: {cq}")
                # Update the completed quests list
                participant.completed_quests = ",".join(cq) if len(cq) > 1 else cq[0] if cq else ""

                # Update the participant's collected assets to None
                participant.collected_assets = ""

                #TODO: if participant is last participant in the quest, mark the quest as completed in quest data
            else:
                # If not all assets are collected, keep the quest state as in-progress
                participant.quest_state = QuestState.IN_PROGRESS

            # Update the participant in the database
            store_participant(participant, True)

            print(f"Participant {userid} collected the asset {assetid} from quest {quest.quest_name}")
            return jsonify({"message": f"Participant {userid} collected the asset {assetid} from quest {quest.quest_name}"})
        else:
            print(f"User is outside the geofence for the quest: {quest.quest_name}")
            return jsonify({"error": "User is outside the geofence"}), 400


# #        Endpoint for placing completed digital content in real-world locations
# #        Must validate placement within allowed geo-boundaries
#     # POST /assets with location data
    def create_asset(self, assetid, asset_name, userid, asset_src, user_lat, user_lon, dest_lat, dest_lon):

        userlocation = Point(user_lat, user_lon)
        destination = Point(dest_lat, dest_lon)

        geofences = get_all_geofences()
        print(geofences)
        for geofence in geofences:
            # Convert the WKT polygon to a Shapely Polygon object
            # Create the polygon from the WKT string
            polygon = wkt.loads(geofence.polygon)

            if polygon.contains(userlocation) and polygon.contains(destination):
                print(f"User is within geofence: {geofence.name} for the asset placement")

                # check for valid owner by searching for the user in the participant data

                asset = AssetData(
                    asset_id = assetid,
                    asset_name=asset_name,
                    asset_source=asset_src,
                    asset_desc="Asset placed by User", 
                    asset_status="active",
                    asset_owner=userid,
                    asset_location=f"{dest_lat},{dest_lon}",  # Using f-string for comma separated coordinates
                    asset_timestamp="2023-10-01T00:00:00Z",  # Placeholder for actual timestamp
                    asset_type="quest",
                    geofence_id=geofence.geofence_id
                )
                id = store_asset(asset, False)  # False indicates a new asset creation
                print(f"Asset {asset_name} with id {id} created by user {userid} at location {dest_lat},{dest_lon}")
                return jsonify({"message": f"Asset {asset_name} with id {id} created by user {userid} at location {dest_lat},{dest_lon}"}), 201
            else:
                print(f"User is outside the geofence for the asset placement")
                return jsonify({"error": "User is outside the geofence"}), 400
        # If no geofence found, return an error
        return jsonify({"error": "No valid geofence found for the asset placement"}), 400