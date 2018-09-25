"""
battle.py

Battle Intents and Configurations
"""
# Std Lib imports
import os
import enum
import random
import logging

# Amazon Imports:
from ask_sdk_model.ui.image import Image
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, AudioPlayerState)
from ask_sdk_model.interfaces import display

# DartBattle imports:
import database
import playlists
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
    DropAndRoll = 25
    Duel = 26


class Scenarios(enum.Enum):
    """The major scenarios available; used for tokens and playlist generation."""
    NoEvents01 = 0
    Arctic = 1
    Prospector = 2
    # Battlefield = 2
    # Forest = 3
    # Island = 4
    # Jungle = 5
    # Laboratory = 6
    # Persia = 7
    # Space = 8
    # Urban = 9
    # Warehouse = 10


class Scenario(object):
    """
    Obj representing playlist for battle scenes with logic to determine the
    pattern for given durations, and for choosing appropriate events based on
    sceneAttributes.

    Args:
        userSession: (session.DartBattleSession)
            The session object derived from incoming Alexa data.
        name: (str)
            The name of the scene to be built (arctic, jungle, urban, etc)

    Raises:
        N/A

    """
    def __init__(self, userSession, name=None):
        self.userSession = userSession
        self._availableEvents = None
        if not name:
            name, playlist = random.choice(self.availablePlaylists)
            self.name = name
            self._playlist = playlist
        else:
            self.name = name
            self._playlist = [x[1] for x in self.availablePlaylists if x[0] == name][0]

        self._randomEvents = []
        self.eventsChosen = {}
        self._intro = ""
        self._introVariant = ""
        self._playerRank = None
        self.useSfx = 1
        self.useSoundtrack = 1
        self.variant = "standard"

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
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
        tracklist = self.playlist.getEventsForRank(self.playerRank)  # FIXME: This breaks when usingEvents is False

        # TODO: Think about moving this logic into the Playlist
        available = []
        try:
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
        except Exception as e:
            print("Exception caught processing track {}".format(track))
            raise e

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
    def availablePlaylists(self):
        allPlaylists = {
            "Arctic": playlists.Arctic(),
            "NoEvents01": playlists.NoEvents01(),
            "Prospector": playlists.Prospector()
        }
        return [(x, allPlaylists[x]) for x in allPlaylists.keys() if allPlaylists[x].isActive(self.userSession)]

    @property
    def intro(self):
        """The introductory track; first track."""
        if self._intro:
            return self._intro
        self._introVariant, self._intro = self.getIntro()
        return self._intro

    @property
    def introVariant(self):
        """The introductory track variant (A-Z)."""
        if self._introVariant:
            return self._introVariant
        self._introVariant, self._intro = self.getIntro()
        return self._introVariant

    @property
    def inCountdown(self):
        """The countdown to the start of the battle; second track."""
        return self.playlist.inCount

    @property
    def outCountdown(self):
        """The countdown to the end of the battle. "Battle ends in 3, 2, 1." """
        return self.playlist.outCount

    @property
    def outtro(self):
        """The cease fire notification, end of battle instructions."""
        if self.usingTeams:
            print("Outtro is using teams. Returning team.")
            return self.playlist.outtroTeams
        else:
            print("Outtro is NOT using teams. Returning NoTeam.")
            return self.playlist.outtro

    @property
    def playerRank(self):
        """Enum of the rank achieved by the player; 01 = Private, etc."""
        if self._playerRank:
            return self._playerRank
        self._playerRank = self.userSession.playerRank
        return self._playerRank

    @playerRank.setter
    def playerRank(self, newVal):
        self._playerRank = newVal

    @property
    def playlist(self):
        if self._playlist:
            return self._playlist
        match = [x[1] for x in self.availablePlaylists if x[0] == self.name]
        if not match:
            raise NameError("Name {} not found in available playlists.".format(self.name))
        self._playlist = match[0]
        return self._playlist

    @property
    def prettyName(self):
        return self.playlist.prettyName

    @property
    def promo(self):
        """The countdown to the start of the battle; second track."""
        return self.playlist.promo

    @property
    def roles(self):
        """Enums of the roles currently in use by the teams"""
        allRoles = []
        for team in self.userSession.playerRoles:
            allRoles.extend(self.userSession.playerRoles[team])
        return list(set(allRoles))

    @property
    def soundtrack(self):
        """The generic soundtrack for the battle, prior to duration formatting."""
        return self.playlist.soundtrack

    @property
    def tail(self):
        """Very last thing to play; useful for advertising & announcements."""
        return self.playlist.tail

    @property
    def usingEvents(self):
        """Boolean indicating whether teams are in use for the session."""
        usingEvents = self.userSession.usingEvents
        if usingEvents == "True":
            return True
        return False

    @property
    def usingTeams(self):
        """Boolean indicating whether teams are in use for the session."""
        usingTeams = self.userSession.usingTeams
        if usingTeams == "True":
            return True
        return False

    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def _chooseEvent(self):
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
                token = self._chooseEvent()
                return token
            else:
                # Nuts we ran out of categories. Are there other tracks within
                # this category that we can use?
                if token in self.eventsChosen[category]:
                    token = self._chooseEvent()
                    return token
        else:
            print("Category {} is new.".format(category))

        # Keep track of choice
        if not category in self.eventsChosen:
            self.eventsChosen[category] = []
        self.eventsChosen[category].append(token)
        return token

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
        # Now we have the proper num of availableEvents.
        durationWithoutEvents = duration - (30 * numAvailableEvents)
        segmentLength = int(durationWithoutEvents / (numAvailableEvents+1)/30) * 30
        segmentLength = segmentLength or 30
        if segmentLength > 120:  # 120s is the longest clip that we have
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

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------
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
        # print("------------ building {} ---------------".format(self.name))
        numEventsChosen = 0
        trackNum = 1

        # Session Attributes:
        rank = self.userSession.playerRank
        self.playerRank = rank
        if self.userSession.usingTeams == "True":
            teams = '1'
        else:
            teams = '0'
        newToken = "session_{}.{}.{}.".format(
            rank,
            Scenarios[self.name].value,
            teams
        )
        if self.userSession.sfx == "True":
            sfx = 1
        else:
            sfx = 0
        if self.userSession.soundtrack == "True":
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
                newToken += "_{:02d}.{}".format(trackNum, self._chooseEvent())
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
            return None, None
        return newToken, filename

    def getIntro(self, variant=None):
        print("playlist: {}".format(self.playlist))
        variant, intro = self.playlist.getIntro(rank=self.playerRank, variant=variant)
        print("variant: {}, intro: {}".format(variant, intro))
        return self.playlist.getIntro(rank=self.playerRank, variant=variant)

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
            return None, None
        return newToken, filename

    def getPrevFromToken(self, token, double=True):
        """Given a string token, determine the previous track.

        Args:
            token : (str)
                The token to parse.
                ("session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22",
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro, 2:sndtrk90s,
                3:event14, 4:sndtrk30s, 5:outtro)

            double : (bool)
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
            return token, filename
        return newToken, filename

    def getTrackFromToken(self, token):
        """Given a token like
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

        """
        sessionInfo = token.split("_")[1]
        trackNum = token.split("_")[3]
        playlist = token.split("_")[5:]
        print("Token is {}".format(token))
        # print("Session Info is {}".format(sessionInfo))
        # print("Track Info is {}".format(trackNum))
        # print("Playlist is {}".format(playlist))

        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = Scenarios(int(scenarioEnum)).name
        self.name = scenarioName

        if teams == '1':
            self.userSession.usingTeams = 'True'
        else:
            self.userSession.usingTeams = 'False'
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
            path = self.playlist.soundtrack
            duration = currentTrack.split(".")[2]
            path = path.format(duration)
            if int(sfx) == 0:
                path = path.replace("Sfx", "NoSfx")
            if int(soundtrack) == 0:
                path = path.replace("Music", "NoMusic")
            return path

        # Looks like we have an event
        if teams == '1':
            teamToken = 'Team'
        else:
            teamToken = 'NoTeam'
        roles = currentTrack.split(".")[3:]
        roles = ".".join(roles)
        kwargs = {
            "rank": playerRank,
            "eventCategory": [x.name for x in EventCategories if x.value == int(trackType)][0],
            "eventTitle": currentTrack.split(".")[2],
            "teamToken": teamToken,
            "roles": roles
        }
        track = self.playlist.getEventWithProperties(**kwargs)
        if not track:
            return "https://s3.amazonaws.com/dart-battle-resources/errorBattle_01.mp3"

        return track


def startBattleDurationIntent(userSession):
    """Triggered when a user asks for a battle of a given duration, comply.

    Args:
        userSession : (session.DartBattleSession)
            Session derived from incoming Alexa data.

    Raises:
        N/A

    Returns:
        str, str, str, ask_sdk_model.ui.image.Image, ask_sdk_model.interfaces.audioplayer.PlayDirective
            Response data to construct an Alexa response.
            speech, title, text, cardImage, directive

    """
    duration = userSession.request.slots["DURATION"]["value"]
    duration = int(duration) * 60
    if duration < 120:
        duration = 120
    userSession.battleDuration = str(duration)
    return startBattleStandardIntent(userSession)


def startBattleStandardIntent(userSession):
    """Triggered when a user asks for a battle, comply; may specify duration.

    Args:
        userSession : (dict)
            Session data derived from incoming Alexa data.

    Raises:
        N/A

    Returns:
        str, str, str, ask_sdk_model.ui.image.Image, ask_sdk_model.interfaces.audioplayer.PlayDirective
            Response data to construct an Alexa response.
            speech, title, text, cardImage, directive

    """
    speech = ""
    duration = int(userSession.battleDuration)

    isTeam = ""
    if userSession.usingTeams == "True":
        isTeam = "team"

    playlist = Scenario(userSession)
    token = playlist.buildPlaylist(duration)
    track = playlist.getTrackFromToken(token)

    durMin = int(duration/60)
    sceneName = playlist.prettyName
    numBattles = int(userSession.numBattles)
    numBattles += 1
    userSession.numBattles = str(numBattles)
    userSession.currentToken = str(token)
    userSession.offsetInMilliseconds = "0"

    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "

    database.updateRecord(userSession)

    promo = playlist.promo
    if promo:
        speech += '<audio src="{}" /> '.format(promo)

    if userSession.usingEvents == "False":
        text = "{} minute {} battle commencing with no events. ".format(durMin, isTeam)
        choice = random.randint(0, 5)
        if choice == 0:
            text += "If you'd like to hear events and scenarios, ask Dart Battle to turn on events. "
        speech += text
    else:
        text = "{} minute {} {} battle commencing. ".format(durMin, sceneName, isTeam)
        speech += text
    title = "Start a Battle"
    largeImg = "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_1200x800.jpg"
    smallImg = "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_720x480.jpg"
    cardImage = Image(
        small_image_url=smallImg,
        large_image_url=largeImg
    )

    directive = PlayDirective(
        play_behavior=PlayBehavior.REPLACE_ALL,
        audio_item=AudioItem(
            stream=Stream(
                expected_previous_token=None,
                token=token,
                url=track,
                offset_in_milliseconds=0
            ),
            metadata=AudioItemMetadata(
                title=title,
                subtitle=text,
                art=display.Image(
                    content_description=title,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                ),
                background_image=display.Image(
                    content_description=title,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                )
            )
        )
    )

    return speech, title, text, cardImage, directive


def continueAudioPlayback(userSession):
    """Triggered by PlaybackNearlyFinished event, plays next."""
    prevToken = AudioPlayerState.token

    sessionInfo = prevToken.split("_")[1]
    (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
    scenarioName = Scenarios(int(scenarioEnum)).name
    (nextToken, nextTrack) = Scenario(userSession, name=scenarioName).getNextFromToken(prevToken)
    userSession.currentToken = nextToken
    if nextToken:
        database.updateRecordToken(userSession)
    largeImg = "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_1200x800.jpg"

    directive = PlayDirective(
        play_behavior=PlayBehavior.ENQUEUE,
        audio_item=AudioItem(
            stream=Stream(
                expected_previous_token=prevToken,
                token=nextToken,
                url=nextTrack,
                offset_in_milliseconds=0
            ),
            metadata=AudioItemMetadata(
                title=scenarioName,
                subtitle="",
                art=display.Image(
                    content_description=scenarioName,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                ),
                background_image=display.Image(
                    content_description=scenarioName,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                )
            )
        )
    )
    return directive


def reverseAudioPlayback(session):
    """Triggered when user asks for next track, plays previous."""
    # Request was triggered by a user asking for Previous track.
    session = database.getSessionFromDB(session)
    sessionAttributes = session["attributes"]

    # currentToken is always one ahead of the one that's playing.
    currentToken = sessionAttributes['currentToken']

    sessionInfo = currentToken.split("_")[1]
    (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
    scenarioName = Scenarios(int(scenarioEnum)).name
    (previousToken, previousTrack) = Scenario(sessionAttributes, name=scenarioName).getPrevFromToken(currentToken)

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
    session = database.getSessionFromDB(session)
    sessionAttributes = session["attributes"]

    currentToken = sessionAttributes['currentToken']

    sessionInfo = currentToken.split("_")[1]
    (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
    scenarioName = Scenarios(int(scenarioEnum)).name
    (firstToken, firstTrack) = Scenario(sessionAttributes, name=scenarioName).getFirstTrackFromToken(currentToken)
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
    session = database.getSessionFromDB(session)
    sessionAttributes = session["attributes"]
    # currentToken is always one ahead of the one that's playing,
    # courtesy of playbackNearlyFinished; just return the recorded token:
    nextToken = sessionAttributes['currentToken']
    playBehavior = "REPLACE_ALL"
    generic = Scenario(sessionAttributes)
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
