def init_db():
    try:
        from db import engine, Base
        from Analytics.model_interactions import Item, Interaction
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
