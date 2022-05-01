from src.python.config.appConfig import app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)


class TwoLineElement(db.Model):
    tle0 = db.Column(db.String, primary_key=True)
    tle1 = db.Column(db.String)
    tle2 = db.Column(db.String)
    updated = db.Column(db.DateTime)

    @staticmethod
    def insertRow(tle0, tle1, tle2, updated):
        return TwoLineElement(tle0=tle0, tle1=tle1, tle2=tle2, updated=updated)


db.close_all_sessions()
