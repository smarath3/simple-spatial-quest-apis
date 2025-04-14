from flask import Flask, request
from server.api.spacial_quest import SpatialQuestAPI

app = Flask(__name__)

# Initialize the SpatialQuestAPI with the app and any required services
quest_service = None  # Replace with your actual quest service
spatial_quest_api = SpatialQuestAPI(quest_service)

# Example route to call quest_discovery
@app.route('/quest_discovery', methods=['GET'])
def quest_discovery():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if lat is None or lon is None:
        return {'error': 'Missing required parameters: lat and lon'}, 400
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return {'error': 'Invalid lat or lon values: must be numbers'}, 400
    
    return spatial_quest_api.quest_discovery(lat, lon)


@app.route('/quest_join', methods=['POST'])
def quest_join():
    print("quest_join is called...")
    qid = request.args.get('questId')
    print(qid)
    if qid is None:
        return {'error': 'Missing required parameter: questId'}, 400
    uid = request.args.get('userId')
    print(uid)
    if uid is None:
        return {'error': 'Missing required parameter: userId'}, 400
    
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    print(lat, lon)
    if lat is None or lon is None:
        return {'error': 'Missing required parameters: lat and lon'}, 400
    try:
        lat = float(lat)
        lon = float(lon)
        questid = int(qid)
        participantid = str(uid)
    except ValueError:
        return {'error': 'Invalid values: must be numbers and string'}, 400

    return spatial_quest_api.quest_join(questid, participantid, lat, lon)

@app.route('/quest_leave', methods=['POST'])
def quest_leave():
    print("quest_leave is called...")
    qid = request.args.get('questId')
    print(qid)
    if qid is None:
        return {'error': 'Missing required parameter: questId'}, 400
    uid = request.args.get('userId')
    print(uid)
    if uid is None:
        return {'error': 'Missing required parameter: userId'}, 400
    
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    print(lat, lon)
    if lat is None or lon is None:
        return {'error': 'Missing required parameters: lat and lon'}, 400
    try:
        lat = float(lat)
        lon = float(lon)
        questid = int(qid)
        participantid = str(uid)
    except ValueError:
        return {'error': 'Invalid values: must be numbers and string'}, 400

    return spatial_quest_api.quest_leave(questid, participantid, lat, lon)

#    def collect_asset(self, questid, userid, assetid, lat, lon):
@app.route('/collect_asset', methods=['POST'])
def collect_asset():
    print("collect_asset is called...")
    qid = request.args.get('questId')
    print(qid)
    if qid is None:
        return {'error': 'Missing required parameter: questId'}, 400
    uid = request.args.get('userId')
    print(uid)
    if uid is None:
        return {'error': 'Missing required parameter: userId'}, 400

    aid = request.args.get('assetId')
    print(aid)
    if aid is None:
        return {'error': 'Missing required parameter: assetId'}, 400

    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    print(lat, lon)
    if lat is None or lon is None:
        return {'error': 'Missing required parameters: lat and lon'}, 400
    try:
        lat = float(lat)
        lon = float(lon)
        questid = int(qid)
        participantid = str(uid)
        assetid = int(aid)

    except ValueError:
        return {'error': 'Invalid values: must be numbers and string'}, 400

    return spatial_quest_api.collect_asset(questid, participantid, assetid, lat, lon)

@app.route('/create_asset', methods=['POST'])
def create_asset():
    print("create_asset is called...")
    try:
        aname = str(request.args.get('asset_name'))
        print(aname)
        if aname is None:
            return {'error': 'Missing required parameter: asset_name'}, 400

        aid = request.args.get('assetId')
        print(aid)
        if aid is None:
            return {'error': 'Missing required parameter: assetId'}, 400

        uid = str(request.args.get('userId'))
        print(uid)
        if uid is None:
            return {'error': 'Missing required parameter: userId'}, 400

        asrc = str(request.args.get('asset_src'))
        print(asrc)
        if asrc is None:
            return {'error': 'Missing required parameter: asset_src'}, 400

        ulat = float(request.args.get('user_lat'))
        ulon = float(request.args.get('user_lon'))

        dlat = float(request.args.get('dest_lat'))
        dlon = float(request.args.get('dest_lon'))

        print(ulat, ulon, dlat, dlon)
        if ulat is None or ulon is None or dlat is None or dlon is None:
            return {'error': 'Missing required parameters: user and/or destination lat and lon'}, 400

    except ValueError:
        return {'error': 'Invalid values: must be numbers and string'}, 400

    return spatial_quest_api.create_asset(aid, aname, uid, asrc, ulat, ulon, dlat, dlon)


if __name__ == '__main__':
    app.run(debug=True)