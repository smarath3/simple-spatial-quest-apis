from sqlalchemy import Column, Integer, String, Float
#from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Enum
import enum
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

#from database import Base
Base = declarative_base()


# Create a SQLAlchemy engine 
engine = create_engine(database_url)

class QuestState(enum.Enum):
    INACTIVE = "inactive" # not in pursuit by any participant
    IN_PROGRESS = "inprogress" # in pursuit by atleast 1 participant
    COMPLETED = "completed" # completed by all participants
    FAILED = "failed"   # failed to complete by all participants or leaving without completion
    BADSTATE = "badstate" # Some issue with Quest, don't allow to be pursued

class QuestData(Base):
    __tablename__ = 'quest_data'


    quest_id = Column(Integer, primary_key=True)
    quest_assetids = Column(String) # Store as comma-separated string of asset IDs
    quest_name = Column(String)
    quest_desc = Column(String)
    active_participant_list = Column(String) # Store as comma-separated string of users pursuing this quest
    quest_state = Column(Enum(QuestState), nullable=False)
    quest_start_time = Column(String) # Store as ISO 8601 string
    quest_end_time = Column(String) # Store as ISO 8601 string
    latitude = Column(Float)
    longitude = Column(Float)
    geofence_id = Column(Integer) # Foreign key to GeoFence table

    def __repr__(self):
        return f"<Quest(id={self.quest_id}, name={self.quest_name}>"
    
    def serialize(self):
        return {
            'quest_id': self.quest_id,
            'quest_name': self.quest_name,
            'quest_state': self.quest_state.value,
            'quest_assetids': self.quest_assetids,
            'geofence_id': self.geofence_id,
            'active_participant_list': self.active_participant_list
    }
    
# Create all tables
Base.metadata.create_all(engine)
print("--------------------------_Created QuestData--------------------")
# Create a SQLAlchemy session 
Session = sessionmaker(bind=engine) 
session = Session()

def store_quest(qd, is_update=False) -> Integer:
    try:
        if not is_update:
            # For insert: Check if quest_id already exists
            existing_quest = session.query(QuestData).filter(QuestData.quest_id == qd.quest_id).first()
            if existing_quest:
                print(f"Quest with ID {qd.quest_id} already exists.")
                return False
            session.add(qd)
        else:
            # For update: Directly merge the changes
            session.merge(qd)
        
        session.commit()
        return qd.quest_id

    except Exception as e:
        print(f"Error {'updating' if is_update else 'storing'} quest: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_all_quests() -> list:
    try:
        quests = session.query(QuestData).all()
        return [quest.__dict__ for quest in quests]
    except Exception as e:
        print(f"Error retrieving quests: {e}")
        return []
    finally:
        session.close()
        # Close the session to release resources

def get_quest_by_id(quest_id: int) -> QuestData:
    try:
        quest = session.query(QuestData).filter(QuestData.quest_id == quest_id).first()
        if quest:
            return quest
        else:
            print(f"Quest with ID {quest_id} not found.")
            return None
    except Exception as e:
        print(f"Error retrieving quest: {e}")
        return None
    finally:
        session.close()
        # Close the session to release resources

def get_quest_by_geofence_id(geofence_id: int) -> list:
    print(f"Getting quests for geofence ID {geofence_id}")
    keys = ['quest_id', 'quest_name', 'quest_desc']

    try:
        quests = session.query(QuestData).filter(QuestData.geofence_id == geofence_id).all()
        if quests:
            # for quest in quests:
            #     # Keep only the keys we want
            #     quest.__dict__ = {key: quest.__dict__[key] for key in keys if key in quest.__dict__}
            return [quest for quest in quests]
        else:
            print(f"No quests found for geofence ID {geofence_id}.")
            return []
    except Exception as e:
        print(f"Error retrieving quests: {e}")
        return []
    finally:
        session.close()
        # Close the session to release resources

