# DartBattle imports:
import database


class DartBattleSession(dict):
    def __init__(self, session=None):
        if not database.isActive():
            session = dict()
            userId = session['context']['System']['user']['userId']
            session["attributes"] = database.getDefaultSessionAttrs(userId)
        else:
            session = database.getSessionFromDB(session)
        for key in session:
            self[key] = session[key]

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def attributes(self):
        return self["attributes"]

    @attributes.setter
    def attributes(self, value):
        self["attributes"] = value

    @property
    def usingTeams(self):
        return self["attributes"]["usingTeams"]

    @usingTeams.setter
    def usingTeams(self, value):
        self["attributes"]["usingTeams"] = value
