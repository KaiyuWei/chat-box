import logging

from database.mysql import get_mysql_db
from models.user import User

logger = logging.getLogger(__name__)


def ensure_dummy_user():
    """
    Ensure dummy user with ID 1 exists in the database.
    This is a user for development and testing.
    TODO: Remove this after implementing a proper user auth system.
    """
    db = next(get_mysql_db())
    try:
        existing_user = db.query(User).filter(User.id == 1).first()
        if not existing_user:
            dummy_user = User(
                id=1,
                username="dummy_user",
                email="dummy@example.com",
                password_hash="dummy_hash_hash",
            )
            db.add(dummy_user)
            db.commit()
            logger.info("Created dummy user with ID 1 for development and testing")
        else:
            logger.info("dummy user with ID 1 already exists")
    except Exception as e:
        logger.error(f"Error checking/creating dummy user: {e}")
        db.rollback()
    finally:
        db.close()
