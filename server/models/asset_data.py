from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

#from database import Base
Base = declarative_base()

# Create a SQLAlchemy engine 
engine = create_engine(database_url)

# Class for storing asset data - asset is a digital content placed by a user that can be a signal for another user to con'quest' 
class AssetData(Base):
    __tablename__ = 'asset_data'

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_name = Column(String, nullable=False)
    asset_source = Column(String, nullable=False)
    asset_desc = Column(String, nullable=True)
    asset_status = Column(String, nullable=False)  # Enum: 'active', 'inactive'
    asset_owner = Column(String, nullable=False)  # User ID of the asset owner
    asset_location = Column(String, nullable=False)  # Location ID where the asset is located
    asset_timestamp = Column(String, nullable=False)  # Store as ISO 8601 string
    asset_type = Column(String, nullable=False)  # Enum: 'quest', 'location'
    geofence_id = Column(Integer) # Foreign key to GeoFence table

    def __repr__(self):
        return f"<AssetData(id={self.asset_id}, name={self.asset_name}, src={self.asset_source}, loc={self.asset_location}, owner={self.asset_owner})>"
    
# Create all tables
Base.metadata.create_all(engine)
print("--------------------------_Created AssetData--------------------")
# Create a SQLAlchemy session 
Session = sessionmaker(bind=engine) 
session = Session()


def store_asset(ad, is_update=False) -> Integer:
    try:
        if not is_update:
            existing_asset = session.query(AssetData).filter(AssetData.asset_id == ad.asset_id).first()
            if existing_asset:
                print(f"Asset with ID {ad.asset_id} already exists.")
                return False 
            session.add(ad)
        else:
            # For update: Directly merge the changes
            session.merge(ad)
        session.commit()
        return ad.asset_id
    # Return the ID of the newly created asset 

    except Exception as e:
        print(f"Error storing quest: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        # Close the session to release resources

def get_all_assets() -> list:
    try:
        assets = session.query(AssetData).all()
        return [asset for asset in assets]
    except Exception as e:
        print(f"Error retrieving assets: {e}")
        return []
    finally:
        session.close()
        # Close the session to release resources

def get_asset_by_name(asset_name: str) -> AssetData:
    try:
        asset = session.query(AssetData).filter(AssetData.asset_name == asset_name).first()
        if asset:
            return asset
        else:
            print(f"Asset with name {asset_name} not found.")
    except Exception as e:
        print(f"Error retrieving asset: {e}")
        return None
    finally:
        session.close()
        # Close the session to release resources        