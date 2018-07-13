"""
battle.py

Battle Intents and Configurations
"""
# Std Lib imports
import os
import enum
import random
import logging

# DartBattle imports:
import database
import playlists
import responses
import teams

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EventCategories(enum.Enum):
    """The category types for soundtrack events, used for tokens."""
    Intro = 0
    InCount = 1
    Soundtrack = 2
    CeaseFire = 3
    ExclusiveShot = 4
    HoldOn = 5
    LayDown = 6
    PairUp = 7
    Protect = 8
    Reset = 9
    Resupply = 10
    Retreat = 11
    SpecificTarget = 12
    Shelter = 13
    SplitUp = 14
    TagFeature = 15
    TagInOrder = 16
    TagManyToOne = 17
    TagOneToOne = 18
    TagOneToMany = 19
    ZeroEliminations = 20
    OutCount = 21
    Outtro = 22
    Tail = 23
    Promo = 24


class Scenarios(enum.Enum):
    """The major scenarios available; used for tokens and playlist generation."""
    NoEvents01 = 0
    Arctic = 1
    OldWest = 2
    # Battlefield = 2
    # Forest = 3
    # Island = 4
    # Jungle = 5
    # Laboratory = 6
    # Persia = 7
    # Space = 8
    # Urban = 9
    # Warehouse = 10



class ScenePlaylist(object):
    """
    Obj representing playlist for battle scenes with logic to determine the
    pattern for given durations, and for choosing appropriate events based on
    sceneAttributes.

    Args:
        name: (str)
            The name of the scene to be built (arctic, jungle, urban, etc)

        sessionAttributes: (dict)
            Attributes as would be passed via Alexa representing scene
            properties and configuration.

    Raises:
        N/A

    """
    def __init__(self, name, sessionAttributes):
        self._availableEvents = None
        #self._playlist = {}
        self._protectedCategories = [
            EventCategories.Intro,
            EventCategories.InCount,
            EventCategories.Soundtrack,
            EventCategories.OutCount,
            EventCategories.Outtro,
            EventCategories.Tail
            ]
        self._randomEvents = []
        self.eventsChosen = {}
        self._intro = ""
        self._introVariant = ""
        self._playerRank = None
        self.name = name
        self.sessionAttributes = sessionAttributes
        self.useSfx = 1
        self.useSoundtrack = 1
        self.variant = "standard"

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def availableEvents(self):
        """Determines and returns the events appropriate for the Scenario,
        team status, and roles.

        Args:
            N/A

        Raises:
            N/A

        Returns:
            list
                The list of appropriate event track URLs.

        """
        # Cache
        if self._availableEvents:
            return self._availableEvents

        # Determine valid list
        if self.name == "Arctic":
            tracklist = playlists.Arctic().getEventsForRank(self.playerRank)
        else:
            tracklist = []

        available = []
        for trackPath in tracklist:
            track = trackPath[:-4]  # remove ".mp3"
            trackRoles = track.split("_")[6].split(".")
            if "_Team_" in track and not self.usingTeams:
                continue
            if "_NoTeam_" in track and self.usingTeams:
                continue
            if self.roles and not all([x in self.roles for x in trackRoles]):
                if not trackRoles == ["{:02d}".format(teams.PlayerRoles.any.value)] and \
                        not trackRoles == ["{:02d}".format(teams.PlayerRoles.none.value)]:
                    continue
            available.append(trackPath)

        # print("{} are valid tracks.".format(len(available)))
        self._availableEvents = available
        return available


    @property
    def availableEventCategories(self):
        """The list of event categories distilled from appropriate events.

        Args:
            N/A

        Raises:
            N/A

        Returns:
            list
                String names of distilled category names.

        """
        cats = set()
        # for track in self._randomEvents:
        tracklist = self.availableEvents
        for track in tracklist:
            cats.add(track.split("_")[3])
        return list(cats)

    @property
    def intro(self):
        """The introductory track; first track."""
        if self._intro:
            return self._intro
        if self.name == "Arctic":
            (self._introVariant, self._intro) = self.getIntro()
            return self._intro
        return None

    @property
    def introVariant(self):
        """The introductory track variant (A-Z)."""
        if self._introVariant:
            return self._introVariant
        if self.name == "Arctic":
            self._introVariant, self._intro = self.getIntro()
            return self._introVariant

    @property
    def inCountdown(self):
        """The countdown to the start of the battle; second track."""
        if self.name == "Arctic":
            return playlists.Arctic().inCount
        return None

    @property
    def outCountdown(self):
        """The countdown to the end of the battle. "Battle ends in 3, 2, 1." """
        if self.name == "Arctic":
            return playlists.Arctic().outCount
        return None

    @property
    def outtro(self):
        """The cease fire notification, end of battle instructions."""
        if self.name == "Arctic":
            if self.usingTeams:
                print("Outtro is using teams. Returning team.")
                return playlists.Arctic().outtroTeams
            else:
                print("Outtro is NOT using teams. Returning NoTeam.")
                return playlists.Arctic().outtro
        elif self.name == "NoEvents01":
            if self.usingTeams:
                return playlists.NoEvents01().outtroTeams
            else:
                return playlists.NoEvents01().outtro

    @property
    def playerRank(self):
        """Enum of the rank achieved by the player; 01 = Private, etc."""
        if self._playerRank:
            return self._playerRank
        if 'playerRank' in self.sessionAttributes:
            self._playerRank = self.sessionAttributes['playerRank']
        else:
            self._playerRank = '00'
        return self._playerRank
    @playerRank.setter
    def playerRank(self, newVal):
        self._playerRank = newVal

    @property
    def promo(self):
        """The countdown to the start of the battle; second track."""
        if self.name == "Arctic":
            return playlists.Arctic().promo
        return None

    @property
    def roles(self):
        """Enums of the roles currently in use by the teams"""
        if not 'playerRoles' in self.sessionAttributes:
            return []
        allRoles = []
        for team in self.sessionAttributes['playerRoles']:
            allRoles.extend(self.sessionAttributes['playerRoles'][team])
        return list(set(allRoles))

    @property
    def soundtrack(self):
        """The generic soundtrack for the battle, prior to duration formatting."""
        if self.name == "Arctic":
            return playlists.Arctic().soundtrack
        elif self.name == "NoEvents01":
            return playlists.NoEvents01().soundtrack

    @property
    def tail(self):
        """Very last thing to play; useful for advertising & announcements."""
        if self.name == "Arctic":
            return playlists.Arctic().tail
        return None

    @property
    def usingEvents(self):
        """Boolean indicating whether teams are in use for the session."""
        usingEvents = self.sessionAttributes.get('usingEvents', "True")
        if usingEvents == "True":
            return True
        return False

    @property
    def usingTeams(self):
        """Boolean indicating whether teams are in use for the session."""
        usingTeams = self.sessionAttributes.get('usingTeams', "False")
        if usingTeams == "True":
            return True
        return False

    #--------------------------------------------------------------------------
    # Private methods
    #--------------------------------------------------------------------------
    def _getPatternForDuration(self, duration):
        """Given a time duration, returns a pattern of events and sndtrk to fit.

        Args:
            duration : (int)
                The duration in minutes that the pattern should fulfill.

        Raises:
            N/A

        Returns:
            list
                The pattern of events and sndtrk tracks.

        """
        duration = int(duration)
        numAvailableEvents = len(self.availableEvents)
        if not self.usingEvents:
            numAvailableEvents = 0
        # Events are 30s so that should be subtracted from the duration,
        # and then divided by the number of events to achieve the optimal num.
        if numAvailableEvents:
            while (duration - (30 * numAvailableEvents)) / numAvailableEvents < (numAvailableEvents * 30):
                numAvailableEvents -= 1
        #Now we have the proper num of availableEvents.
        durationWithoutEvents = duration - (30 * numAvailableEvents)
        segmentLength = int(durationWithoutEvents / (numAvailableEvents+1)/30) * 30
        segmentLength = segmentLength or 30
        if segmentLength > 120: #120s is the longest clip that we have
            segmentLength = 120
        pattern = []
        eventsUsed = 0
        while duration >= segmentLength:
            if pattern and isinstance(pattern[-1], int) and eventsUsed < numAvailableEvents:
                pattern.append('e')
                eventsUsed += 1
                duration -= 30
            else:
                if pattern and isinstance(pattern[-1], int) and pattern[-1] + segmentLength <= 120:
                    last = pattern.pop()
                    pattern.append(last + segmentLength)
                    duration -= last + segmentLength
                else:
                    pattern.append(segmentLength)
                    duration -= segmentLength
        if duration > 0:
            pattern.append(duration)
        return pattern

    #--------------------------------------------------------------------------
    # Public methods
    #--------------------------------------------------------------------------
    def buildPlaylist(self, duration):
        """Given a duration, this builds a playlist string token.

        Args:
            duration : (int)
                The duration of the battle that the playlist should take.

        Raises:
            N/A

        Returns:
            str
                Token representing the playlist.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)

        """
        print("------------ building {} ---------------".format(self.name))
        numEventsChosen = 0
        trackNum = 1

        # Session Attributes:
        if not 'playerRank' in self.sessionAttributes:
            rank = '00'
        else:
            rank = self.sessionAttributes['playerRank']
        self.playerRank = rank
        if self.sessionAttributes['usingTeams'] == "True":
            teams = '1'
        else:
            teams = '0'
        newToken = "session_{}.{}.{}.".format(
            rank,
            Scenarios[self.name].value,
            teams
        )
        if self.sessionAttributes['sfx'] == "True":
            sfx = 1
        else:
            sfx = 0
        if self.sessionAttributes['soundtrack'] == 'True':
            soundtrack = 1
        else:
            soundtrack = 0
        newToken += "{}.{}_track_01_playlist".format(sfx, soundtrack)


        # -- INTRO --
        if self.intro:
            newToken += "_{:02d}.{:02d}.{}".format(
                trackNum,
                EventCategories.Intro.value,
                self.introVariant
            )
            trackNum += 1

        # -- IN COUNT --
        if self.inCountdown:
            newToken += "_{:02d}.{:02d}".format(
                trackNum,
                EventCategories.InCount.value
            )
            trackNum += 1

        # -- SNDTRK & EVENT --
        pattern = self._getPatternForDuration(duration)
        print("Pattern: {}".format(pattern))
        for item in pattern:
            if item == 'e':
                # --- event ---
                newToken += "_{:02d}.{}".format(trackNum, self.chooseEvent())
                numEventsChosen += 1
            else:
                # --- soundtrack ---
                newToken += "_{:02d}.{:02d}.{:02d}".format(
                    trackNum,
                    EventCategories.Soundtrack.value,
                    int(item)
                )
            trackNum += 1

        if self.outCountdown:
            newToken += "_{:02d}.{:02d}".format(
                trackNum,
                EventCategories.OutCount.value
            )
            trackNum += 1

        if self.outtro:
            newToken += "_{:02d}.{:02d}".format(
                trackNum,
                EventCategories.Outtro.value
            )
            trackNum += 1

        if self.tail:
            newToken += "_{:02d}.{:02d}".format(
                trackNum,
                EventCategories.Tail.value
            )


        return newToken

    def chooseEvent(self):
        """
        Randomly select event track, ensure a unique choice, ensure
        compatibility with session, keep track of events chosen, generate token
        of [category.title.roles].

        Track should be named
        event_[Scene]_[Rank]_[Category]_[Title]_[Team]_[Roles].mp3
        ( event_Arctic_09_ExclusiveShot_DugIn_Team_05 )

        Args:
            N/A

        Raises:
            N/A

        Returns:
            str
                An appropriate event token which can be mapped to a file.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)


        """
        tracklist = self.availableEvents
        track = os.path.basename(random.choice(tracklist))

        # remove ".mp3":
        track = track[:-4]
        category = track.split("_")[3]
        title = track.split("_")[4]
        roles = track.split("_")[6].split(".")

        # Generate token
        token = "{}.{}.{}".format(
            "{:02d}".format(EventCategories[category].value),
            title,
            "".join(roles)
        )

        # Ensure Unique
        if category in self.eventsChosen:
            # We've already used this category.
            if not len(self.eventsChosen.keys()) == len(self.availableEventCategories):
                # There are still more options, pick a new one
                token = self.chooseEvent()
                return token
            else:
                # Nuts we ran out of categories. Are there other tracks within
                # this category that we can use?
                if token in self.eventsChosen[category]:
                    token = self.chooseEvent()
                    return token
        else:
            print("Category {} is new.".format(category))

        # Keep track of choice
        if not category in self.eventsChosen:
            self.eventsChosen[category] = []
        self.eventsChosen[category].append(token)
        return token

    def getFirstTrackFromToken(self, token):
        """Given a string token, determine the first track to play.

        Args:
            token : (str)
                The token to parse.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)


        Raises:
            N/A

        Returns:
            str
                The token that was passed in.

            str
                The URL to the first track.

        """
        head = "_".join(token.split("_")[:3])
        tail = "_".join(token.split("_")[4:])
        trackNum = 1
        newToken = head
        newToken += '_{:02d}_'.format(trackNum)
        newToken += tail
        filename = self.getTrackFromToken(newToken)
        if not filename:
            return (None, None)
        return (newToken, filename)

    def getIntro(self, variant=None):
        if not variant:
            if self.name == "Arctic":
                return playlists.Arctic().getIntro(rank=self.playerRank)
            elif self.name == "NoEvents01":
                return playlists.NoEvents01().getIntro(rank=self.playerRank)
        else:
            if self.name == "Arctic":
                return playlists.Arctic().getIntro(rank=self.playerRank, variant=variant)
            elif self.name == "NoEvents01":
                return playlists.NoEvents01().getIntro(rank=self.playerRank, variant=variant)

    def getNextFromToken(self, token):
        """Given a string token, determine the next track to play.

        Args:
            token : (str)
                The token to parse.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)


        Raises:
            N/A

        Returns:
            str
                Token indicating that next track is now current track.

            str
                The URL to the next track.

        """
        head = "_".join(token.split("_")[:3])
        trackInfo = token.split("_")[3]
        tail = "_".join(token.split("_")[4:])
        trackNum = int(trackInfo) + 1
        newToken = head
        newToken += '_{:02d}_'.format(trackNum)
        newToken += tail
        filename = self.getTrackFromToken(newToken)
        if not filename:
            return (None, None)
        return (newToken, filename)

    def getPrevFromToken(self, token, double=True):
        """Given a string token, determine the previous track.

        Args:
            token : (str)
                The token to parse.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)

            double=True : (bool)
                The reported token is always the next one in the queue, meaning it is one track ahead
                of the actual current track. In order to fetch previous track, we must subtrack TWO
                from the current token, not just one.


        Raises:
            N/A

        Returns:
            str
                Token indicating that previous track is now current track.

            str
                The URL to the previous track.

        """
        head = "_".join(token.split("_")[:3])
        trackInfo = token.split("_")[3]
        tail = "_".join(token.split("_")[4:])
        if double:
            trackNum = int(trackInfo) - 2
        else:
            trackNum = int(trackInfo) - 1
        if trackNum < 0:
            trackNum = 0
        newToken = head
        newToken += '_{:02d}_'.format(trackNum)
        newToken += tail
        if trackNum == 0:
            (newToken, filename) = self.getFirstTrackFromToken(newToken)
        else:
            print("Fetching track for previous token: {}".format(newToken))
            filename = self.getTrackFromToken(newToken)
        if not filename:
            filename = self.getTrackFromToken(token)
            return (token, filename)
        return (newToken, filename)

    def getTrackFromToken(self, token):
        '''Given a token like
        "session_10.1.1_track_01_playlist_01.00.A_02.02.120_03.05.Avalanche.00_04.02.120_05.03.IceBreak.00_06.02.120_07.02.120_0",
        retrieve track like 'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_OneToOne_Intel_Team_07.mp3'

        Args:
            token : (str)
                The token to parse.

        Raises:
            N/A

        Returns:
            str
                URL to the requested track.

        '''
        sessionInfo = token.split("_")[1]
        trackNum = token.split("_")[3]
        playlist = token.split("_")[5:]
        print("Token is {}".format(token))
        print("Session Info is {}".format(sessionInfo))
        print("Track Info is {}".format(trackNum))
        print("Playlist is {}".format(playlist))

        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = Scenarios(int(scenarioEnum)).name
        self.name = scenarioName

        if not 'usingTeams' in self.sessionAttributes:
            if teams == '1':
                self.sessionAttributes['usingTeams'] = 'True'
        print("Current track is {}".format(trackNum))
        currentTrack = None
        for track in playlist:
            if track.startswith(trackNum):
                currentTrack = track
                break
        if not currentTrack:
            print("No current track determined.")
            return None
        trackType = currentTrack.split(".")[1]
        if int(trackType) == EventCategories.Promo.value:
            return self.promo
        elif int(trackType) == EventCategories.Intro.value:
            variant = currentTrack.split(".")[2]
            return self.getIntro(variant=variant)[1]
        elif int(trackType) == EventCategories.InCount.value:
            return self.inCountdown
        elif int(trackType) == EventCategories.OutCount.value:
            return self.outCountdown
        elif int(trackType) == EventCategories.Outtro.value:
            return self.outtro
        elif int(trackType) == EventCategories.Tail.value:
            print("Returning Tail of {}".format(self.tail))
            return self.tail
        elif int(trackType) == EventCategories.Soundtrack.value:
            path = "https://s3.amazonaws.com/dart-battle-resources/"
            duration = currentTrack.split(".")[2]
            if int(sfx) == 1:
                sfx = "Sfx"
            else:
                sfx = "NoSfx"
            if int(soundtrack) == 1:
                soundtrack = "Music"
            else:
                soundtrack = "NoMusic"
            if scenarioName == "NoEvents01":
                scenarioName = "Arctic" # Reusing sndtrk from Arctic to save storage space
            filename = "sndtrk_{}_{}_{}_{}s.mp3".format(
                scenarioName,
                soundtrack,
                sfx,
                duration
            )
            return path + filename

        #Looks like we have an event
        filename = 'event'
        filename += '_{}'.format(scenarioName)
        filename += '_{}'.format(playerRank)
        filename += '_{}'.format([x.name for x in EventCategories if x.value == int(trackType)][0])
        trackTitle = currentTrack.split(".")[2]
        filename += '_{}'.format(trackTitle)
        if teams == '1':
            filename += '_Team'
        else:
            filename += '_NoTeam'
        roles = currentTrack.split(".")[3:]
        filename += '_{}'.format(".".join(roles))
        filename+= '.mp3'

        if scenarioName == "Arctic":
            tracklist = playlists.Arctic().events
        else:
            return "https://s3.amazonaws.com/dart-battle-resources/errorBattle_01.mp3"

        matchingTracks = [x for x in tracklist if x.endswith(filename)]
        if not matchingTracks:
            #Maybe it's an 'Any' type:
            filename = filename.replace('_NoTeam_', '_Any_')
            filename = filename.replace('_Team_', '_Any_')
            matchingTracks = [x for x in tracklist if x.endswith(filename)]
        if not matchingTracks:
            # Maybe it's an Any rank
            # event_Arctic_04_TagFeature_AirstrikeCancel_Any_02.mp3
            zeroFilename = filename.split("_")[0]
            zeroFilename += "_{}".format(filename.split("_")[1])
            zeroFilename += "_00_"
            zeroFilename += "_".join(filename.split("_")[3:])
            matchingTracks = [x for x in tracklist if x.endswith(zeroFilename)]
            if not matchingTracks:
                #Maybe team specific
                if teams == '1':
                    token = 'Team'
                else:
                    token = 'NoTeam'
                zeroFilename = zeroFilename.replace("_Any_", "_{}_".format(token))
                matchingTracks = [x for x in tracklist if x.endswith(zeroFilename)]
        #TODO: The above is ATROCIOUS. Split into methods that can be called, no duplicate code!
        if not matchingTracks:
            # raise ValueError("No track named {} in track list".format(filename))
            print("No track named {} or {} in track list".format(filename, zeroFilename))
            return "https://s3.amazonaws.com/dart-battle-resources/errorBattle_01.mp3"
        return matchingTracks[0]

class MasterPlaylist(object):
    """Playlist obj serving as the broker between requestor and a scene or other playlist.

    Args:
        duration : (int)
            The duration in minutes of the requested playlist.

        sessionAttributes : (dict)
            Session attributes served by Alexa API.

    """
    def __init__(self, duration, sessionAttributes):
        self.duration = duration
        self.scene = None
        self.sessionAttributes = sessionAttributes
        arctic = ScenePlaylist('Arctic', sessionAttributes)
        noEvents01 = ScenePlaylist('NoEvents01', sessionAttributes)
        # TODO: Check for entitlements:
        self.scenes = {'Arctic': arctic}
        self.scenesNoEvents = {'NoEvents01': noEvents01}

    def getPromo(self):
        """Pulls up a promotional track, should one exist."""
        return self.scenes[self.scene].promo

    def getIntroAudio(self):
        """Generates a playlist token, extracts the intro.
        Args:
            N/A

        Raises:
            N/A

        Returns:
            str
                The token representing the playlist that was generated.

            str
                The URL to the intro audio track.

        """
        self.scene = random.choice(list(self.scenes.keys()))
        # TODO: Check for SFX/Music
        # Check to see if user has events enabled:
        usingEvents = self.sessionAttributes.get("usingEvents", "True")
        # print("-------- sessionAttr: --------------\n{}".format(self.sessionAttributes))
        if usingEvents == "False":
            self.scene = random.choice(list(self.scenesNoEvents.keys()))
            sceneObj = self.scenesNoEvents[self.scene]
        else:
            sceneObj = self.scenes[self.scene]

        token = sceneObj.buildPlaylist(self.duration)
        #print("Token received: {}".format(token))
        track = sceneObj.getTrackFromToken(token)
        #print("Track determined: {}".format(track))
        return (token, track)

    def getFirstTrackFromToken(self, token):
        """Given a playlist token, extract the first track and return its URL.

        Args:
            token : (str)
                The playlist token to parse.

        Raises:
            N/A

        Returns:
            str
                Token indicating that first track is current track.

            str
                URL to the first track.

        """
        sessionInfo = token.split("_")[1]
        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = Scenarios(int(scenarioEnum)).name
        try:
            sceneObj = self.scenes[scenarioName]
        except KeyError:
            sceneObj = self.scenesNoEvents[scenarioName]
        (firstToken, firstTrack) = sceneObj.getFirstTrackFromToken(token)
        return (firstToken, firstTrack)

    def getNextFromToken(self, prevToken):
        """Given a playlist token, extract the next track and return its URL.

        Args:
            prevToken : (str)
                The playlist token to parse.

        Raises:
            N/A

        Returns:
            str
                Token indicating that next track is current track.

            str
                URL to the next track.

        """
        sessionInfo = prevToken.split("_")[1]
        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = Scenarios(int(scenarioEnum)).name
        try:
            sceneObj = self.scenes[scenarioName]
        except KeyError:
            sceneObj = self.scenesNoEvents[scenarioName]
        (nextToken, nextTrack) = sceneObj.getNextFromToken(prevToken)
        return nextToken, nextTrack

    def getPreviousFromToken(self, currToken):
        """Given a playlist token, extract the previous track and return its URL.

        Args:
            currToken : (str)
                The playlist token to parse.

        Raises:
            N/A

        Returns:
            str
                Token indicating that previous track is current track.

            str
                URL to the previous track.

        """
        sessionInfo = currToken.split("_")[1]
        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = Scenarios(int(scenarioEnum)).name
        try:
            sceneObj = self.scenes[scenarioName]
        except KeyError:
            sceneObj = self.scenesNoEvents[scenarioName]
        (prevToken, prevTrack) = sceneObj.getPrevFromToken(currToken)
        return prevToken, prevTrack


def startBattleDurationIntent(intent, session):
    """Triggered when a user asks for a battle of a given duration, comply.

    Args:
        intent : (dict)
            Intent data as provided by Alexa API, with slot for duration.

        session : (dict)
            Session data as provided by Alexa API.

    Raises:
        N/A

    Returns:
        dict
            Response dict as required by Alexa API.

    """
    sessionAttributes = session['attributes']

    if 'slots' in intent and 'DURATION' in intent['slots']:
        duration = intent['slots']['DURATION']['value']
        duration = int(duration) * 60
        if duration < 120:
            duration = 120
        sessionAttributes['battleDuration'] = str(duration)
        database.updateRecordDuration(sessionAttributes)
        response = startBattleStandardIntent(intent, session, duration=duration)
        return response

def startBattleStandardIntent(intent, session, duration=None):
    """Triggered when a user asks for a battle, comply; may specify duration.

    Args:
        intent : (dict)
            Intent data as provided by Alexa API, with slot for duration.

        session : (dict)
            Session data as provided by Alexa API.

        duration=None : (int)
            Number of seconds requested by user as the duration of the battle.

    Raises:
        N/A

    Returns:
        dict
            AudioPlayer Response dict as required by Alexa API.

    """
    speech = ""
    sessionAttributes = session['attributes']

    if not duration:
        if 'battleDuration' in sessionAttributes:
            duration = int(sessionAttributes['battleDuration'])
        else:
            duration = 120
    sessionAttributes[duration] = str(duration)

    isTeam = ""
    if sessionAttributes['usingTeams'] == "True":
        isTeam = "team"

    playlist = MasterPlaylist(duration, sessionAttributes)
    (token, track) = playlist.getIntroAudio()
    durMin = int(duration/60)
    sceneName = playlist.scene
    numBattles = int(sessionAttributes['numBattles'])
    numBattles += 1
    sessionAttributes['numBattles'] = str(numBattles)
    sessionAttributes['currentToken'] = str(token)
    sessionAttributes['offsetInMilliseconds'] = "0"

    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "

    if database.isActive():
        database.updateRecord(sessionAttributes)

    promo = playlist.getPromo()
    if promo:
        speech += '<audio src="{}" /> '.format(promo)

    if sceneName == "NoEvents01":
        text = "{} minute {} battle commencing with no events. ".format(durMin, isTeam)
        choice = random.randint(0, 5)
        if choice == 0:
            text += "If you'd like to hear events and scenarios, ask Dart Battle to turn on events. "
        speech += text
    else:
        text = "{} minute {} {} battle commencing. ".format(durMin, sceneName, isTeam)
        speech += text
    title = "Start a Battle"
    output =  {
        "version": os.environ['VERSION'],
        "sessionAttributes": sessionAttributes,
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": token,
                            "url": track,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ],
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_1200x800.jpg"
                }
            },
            "shouldEndSession": True
        }
    }
    logger.info("startBattle intent finished. Returning: {}".format(output))
    return output


def continueAudioPlayback(session, prevToken):
    """Triggered by PlaybackNearlyFinished event, plays next."""
    # Request triggered by PlaybackNearlyFinished and has no active session.
    # Default values (not really used) #TODO: Clean up MasterPlaylist init.
    duration = 120
    userId = session['context']['System']['user']['userId']
    sessionAttributes = database.getDefaultSessionAttrs(userId)
    playBehavior = "ENQUEUE"
    playlist = MasterPlaylist(duration, sessionAttributes)
    (nextToken, nextTrack) = playlist.getNextFromToken(prevToken)
    sessionAttributes['currentToken'] = nextToken
    if nextToken:
        database.updateRecordToken(sessionAttributes)
    response = {
        "version": os.environ['VERSION'],
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": playBehavior,
                    "audioItem": {
                        "stream": {
                            "token": nextToken,
                            "expectedPreviousToken" : prevToken,
                            "url": nextTrack,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ]
        }
    }
    print("Continue Audio Finished, returning: {}".format(response))
    return response


def reverseAudioPlayback(session):
    """Triggered when user asks for next track, plays previous."""
    # Request was triggered by a user asking for Previous track.
    sessionAttributes = database.getSessionFromDB(session)
    duration = int(sessionAttributes['battleDuration'])
    # currentToken is always one ahead of the one that's playing.
    currentToken = sessionAttributes['currentToken']
    masterPlaylist = MasterPlaylist(duration, sessionAttributes)
    (previousToken, previousTrack) = masterPlaylist.getPreviousFromToken(currentToken)
    playBehavior = "REPLACE_ALL"
    sessionAttributes['currentToken'] = previousToken
    database.updateRecordToken(sessionAttributes)
    # TODO: Handle lack of next file gracefully (None, None)
    response = {
        "version": os.environ['VERSION'],
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": playBehavior,
                    "audioItem": {
                        "stream": {
                            "token": previousToken,
                            "url": previousTrack,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ]
        }
    }
    print("Skip to Next Audio Finished, returning: {}".format(response))
    return response


def restartAudioPlayback(session):
    sessionAttributes = database.getSessionFromDB(session)
    currentToken = sessionAttributes['currentToken']
    duration = int(sessionAttributes['battleDuration'])
    playlist = MasterPlaylist(duration, sessionAttributes)
    (firstToken, firstTrack) = playlist.getFirstTrackFromToken(currentToken)
    sessionAttributes['currentToken'] = firstToken
    database.updateRecordToken(sessionAttributes)
    return {
        "version": os.environ['VERSION'],
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": firstToken,
                            "url": firstTrack,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ]
        }
    }


def skipToNextAudioPlayback(session):
    """Triggered when user asks for next track, plays next."""
    # Request was triggered by a user asking for Next track.
    sessionAttributes = database.getSessionFromDB(session)
    duration = int(sessionAttributes['battleDuration'])
    # currentToken is always one ahead of the one that's playing,
    # courtesy of playbackNearlyFinished; just return the recorded token:
    nextToken = sessionAttributes['currentToken']
    playBehavior = "REPLACE_ALL"
    generic = ScenePlaylist('generic', sessionAttributes)
    nextTrack = generic.getTrackFromToken(nextToken)  # TODO: Make this a classmethod so no args are required
    sessionAttributes['currentToken'] = nextToken
    database.updateRecordToken(sessionAttributes)
    # TODO: Handle lack of next file gracefully (None, None)
    response = {
        "version": os.environ['VERSION'],
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": playBehavior,
                    "audioItem": {
                        "stream": {
                            "token": nextToken,
                            "url": nextTrack,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ]
        }
    }
    print("Skip to Next Audio Finished, returning: {}".format(response))
    return response
