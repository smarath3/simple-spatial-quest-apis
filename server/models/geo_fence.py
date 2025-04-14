from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

Base = declarative_base()

# Create a SQLAlchemy engine 
engine = create_engine(database_url)

class GeoFence(Base):
    __tablename__ = 'geo_fence'

    geofence_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    # Using String to store WKT representation of the polygon
    polygon = Column(String(255))

    # Using PostGIS polygon type to store lat/long coordinates
    #polygon = Column(Geometry('POLYGON'))


# Create all tables
Base.metadata.create_all(engine)
print("--------------------------_Created GeoFence--------------------")
# Create a SQLAlchemy session 
Session = sessionmaker(bind=engine) 
session = Session()

def store_geofence(name: str, wkt: str) -> bool:
    try:

        # Create new GeoFence object
        new_geofence = GeoFence(
            name=name,
            polygon=wkt
        )

        # Add to session and commit
        session.add(new_geofence)
        session.commit()
        return new_geofence.geofence_id

    except Exception as e:
        print(f"Error storing geofence: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        # Close the session to release resources
 
def get_all_geofences() -> list:
    try:
        geofences = session.query(GeoFence).all()
        return [geofence for geofence in geofences]
    except Exception as e:
        print(f"Error retrieving geofences: {e}")
        return []
    finally:
        session.close()
        # Close the session to release resources

def get_geofence_by_id(geofence_id: int) -> GeoFence:
    try:
        geofence = session.query(GeoFence).filter(GeoFence.geofence_id == geofence_id).first()
        if geofence:
            return geofence
        else:
            print(f"GeoFence with ID {geofence_id} not found.")
            return None
    except Exception as e:
        print(f"Error retrieving geofence: {e}")
        return None
    finally:
        session.close()
        # Close the session to release resources    
    