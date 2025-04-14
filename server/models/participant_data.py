from sqlalchemy import Column, Integer, Boolean, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from server.models.quest_data import QuestState
from sqlalchemy import Enum
import enum
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

Base = declarative_base()

# Create a SQLAlchemy engine 
engine = create_engine(database_url)

class ParticipantData(Base):
    __tablename__ = 'participant_data'

    id = Column(Integer, primary_key=True)
    participant_id = Column(String(255), nullable=False)  # Unique ID for the participant
    is_joined = Column(Boolean, default=False)
    owned_assets = Column(String, nullable=True)  # Owned asset Ids stored as comma-separated string
    collected_assets = Column(String, nullable=True)  # Collected asset Ids stored as comma-separated string - Cross check with Active Quest. Applicable only to quest type assets
    quest_state = Column(Enum(QuestState), nullable=True)
    active_quest = Column(String, nullable=True)  # Store current inpursuit quest ID
    completed_quests = Column(String, nullable=True)  # Store completed quest IDs as comma-separated string
    userlocation = Column(String(255)) # lat, long coordinates stored as string 

    def __repr__(self):
        return f"<ParticipantData(participant_id={self.participant_id}, is_joined={self.is_joined}, location=({self.latitude}, {self.longitude})>"
    
# Create all tables
Base.metadata.create_all(engine)
print("--------------------------_Created ParticipantData--------------------")
# Create a SQLAlchemy session 
Session = sessionmaker(bind=engine) 
session = Session()

def store_participant(p, is_update=False) -> Integer:
    try:
        if not is_update:
            existing_participant = session.query(ParticipantData).filter(ParticipantData.participant_id == p.participant_id).first()
            if existing_participant:
                print(f"Participant with ID {p.participant_id} already exists.")
                return False
            session.add(p)
        else:
            # For update: Directly merge the changes
            session.merge(p)
 
        session.commit()
        return p.participant_id
    # Return the ID of the newly created asset 

    except Exception as e:
        print(f"Error storing quest: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        # Close the session to release resources

def get_all_participants() -> list:
    try:
        participants = session.query(ParticipantData).all()
        return [participant for participant in participants]
    except Exception as e:
        print(f"Error retrieving quests: {e}")
        return []
    finally:
        session.close()
        # Close the session to release resources

def get_participant_by_id(participant_id: str) -> ParticipantData:
    try:
        participant = session.query(ParticipantData).filter(ParticipantData.participant_id == participant_id).first()
        if participant:
            return participant
        else:
            print(f"No participant found with ID {participant_id}")
            return None
    except Exception as e:
        print(f"Error retrieving participant: {e}")
        return None
    finally:
        session.close()
        # Close the session to release resources
