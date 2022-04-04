from src.python.appConfig import db


class tle(db.Model):
    tle0 = db.Column(db.String, primary_key=True)
    tle1 = db.Column(db.String)
    tle2 = db.Column(db.String)
    updated = db.Column(db.DateTime)


# class prediction(db.Model):
#     timestamp = db.Column(db.String, primary_key=True)
#     id = db.Column(db.String)
#     rise_at = db.Column(db.DateTime)
#     set_at = db.Column(db.DateTime)
#     duration = db.Column(db.Integer)
#     interval = db.Column(db.String)
#
#     def to_dict(self):
#         return {
#             "timestamp": self.timestamp,
#             "id": self.id,
#             "rise_at": str(self.rise_at_at.strftime('%d-%m-%Y')),
#             "set_at": str(self.set_at.strftime('%d-%m-%Y')),
#             "duration": str(self.duration),
#             "interval": self.interval
#         }


def tle_create_row(tle0, tle1, tle2, updated):
    return tle(tle0=tle0, tle1=tle1, tle2=tle2, updated=updated)
