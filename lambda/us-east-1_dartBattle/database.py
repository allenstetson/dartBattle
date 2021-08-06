###############################################################################
# Copyright (c) 2019 Allen Stetson, allen.stetson@gmail.com
# All rights reserved. No duplication allowed.
#
# This file is part of DartBattle.
#
# DartBattle may not be copied and/or distributed without the express
# permission of Allen Stetson.
###############################################################################
"""
database.py - Contains all logic to interact with the DynamoDB database.

The following is super helpful code to use in order to test dartbattle locally
without a connection to Dynamo.

"""
# Std lib imports:
import datetime
import logging

# =============================================================================
# GLOBALS
# =============================================================================
DBS3_URL = 'https://s3.amazonaws.com/dart-battle-resources/'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# ------------------------------------
# Conditional imports
# ------------------------------------
#  When running locally, the connection to DynamoDB is not established. These
#  conditional imports allow the code to run locally using hard-coded default
#  values for testing.
try:
    from botocore.exceptions import ClientError
    import boto3
    DB_ACTIVE = True
    # DB_ACTIVE = False #THIS DISABLES DB. UNCOMMENT FOR LOCAL TESTING.
    LOGGER.info('DB Import successful')
except ImportError as e:
    LOGGER.info("DB Import failed. Falling back to defaults.")
    DB_ACTIVE = False


__all__ = [
    "isActive",
    "clearRecordVictory",
    "getDefaultSessionAttrs",
    "getSessionFromDB",
    "getVictoriesFromDB",
    "updateRecordAttr",
    "updateRecordBattle",
    "updateRecordTeams",
    "updateRecordToken",
    "updateRecordVictory",
    "updateToggleEvents",
]


# =============================================================================
# FUNCTIONS
# =============================================================================
def isActive():
    """Convenience to determine whether or not we connected to DynamoDB.

    If the import for DynamoDB failed, this will return False, and hard-coded
    default values will be used within the code.

    Returns:
        bool: Whether or not we are actively using DynamoDB.

    """
    return DB_ACTIVE


def clearRecordVictory(userSession, victor=None):
    """Clears the database record for victories for a name or for all time.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

        victor (str): The name of the team or individual for which to clear
            the victory record.

    Returns:
        bool: Whether or not we were successful.

    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update victories attr for user ID {}."
    LOGGER.info(msg.format(myId))
    # If a name was provided:
    if victor:
        try:
            response = table.get_item(
                TableName="DartBattle",
                Key={
                    'userId': myId
                }
            )
        except ClientError as e:
            LOGGER.info("ClientError received!")
            LOGGER.error(e.response['Error']['Message'])
            return False
        if not 'Item' in response:
            return False
        victories = response['Item']['victories']
        # Clear out the victories for that name:
        victories[victor] = []
    # If no name was provided, this means ALL victories:
    else:
        victories = {}
    # Update the database with the changes:
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set victories=:v",
            ExpressionAttributeValues={
                ':v': victories
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False


def getDefaultSessionAttrs(userId):
    """Gets a dict of default values for all session attributes.

    Args:
        userId (str): A very long string beginning with "amzn1.ask.account.",
                unique per user.

    Returns:
        dict: A dict of all session attributes set to default values.

    """
    lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    sessionAttributes = {
        "dateCreated": lastRun,
        "battleDuration": "240",
        "currentToken": "None",
        "lastRun": lastRun,
        "numBattles": "0",
        "recentSession": "False",
        "playerRank": "00",
        "playerRoles": [],
        "protocolCodes": {},
        "sfx": "True",
        "soundtrack": "True",
        "teams": {},
        "userId": userId,
        "usingTeams": "False",
        "victories": {}
    }
    return sessionAttributes


def getSessionFromDB(session):
    """Pulls all attributes from the database by userId, returns all attrs.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        dict: All session attributes with their values from the database.

    """
    # Connect to the DB:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    # Pull the records for this user:
    myId = session.userId
    table = dynamodb.Table('DartBattle')
    LOGGER.info("Attempting to retrieve item for user ID {}.".format(myId))
    item = None
    newUser = None
    try:
        response = table.get_item(
            TableName="DartBattle",
            Key={
                'userId': myId
            }
        )
        if not 'Item' in response:
            newUser = True
        else:
            item = response['Item']
            newUser = False
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        newUser = True

    # If this is a new user, the records will have never been created.
    #  Use defaults:
    if newUser:
        LOGGER.info("get_item for userId failed, new user.")
        sessionAttributes = getDefaultSessionAttrs(myId)
        table.put_item(Item=sessionAttributes)
        return sessionAttributes

    # Database successfully queried. Let's populate some attrs!:
    LOGGER.info("get_item for userId succeeded.")
    # Look for recent session
    lastRun = datetime.datetime.strptime(item['lastRun'], "%Y.%m.%d %H:%M:%S")
    now = datetime.datetime.now()
    delta = now-lastRun
    msg = "Lapse between lastRun ({}) and now({}) is {} days."
    LOGGER.info(msg.format(lastRun, now, delta.days))
    if delta.days >= 1:
        recentSession = "False"
    else:
        recentSession = "True"

    # Determine team status
    if recentSession:
        usingTeams = item['usingTeams']
        if usingTeams:
            roles = item['playerRoles']
        else:
            roles = []
    else:
        usingTeams = "False"
        roles = []

    # New Attrs:
    offsetInMilliseconds = item.get('offsetInMilliseconds', "0")
    usingEvents = item.get('usingEvents', "True")
    protocolCodes = item.get('protocolCodes', {})

    sessionAttributes = {
        "battleDuration": item['battleDuration'],
        "currentToken": item['currentToken'],
        "lastRun": now.strftime("%Y.%m.%d %H:%M:%S"),
        "numBattles": item['numBattles'],
        "offsetInMilliseconds": offsetInMilliseconds,
        "recentSession": recentSession,
        "playerRank": item['playerRank'],
        "playerRoles": roles,
        "protocolCodes": protocolCodes,
        "sfx": item['sfx'],
        "soundtrack": item['soundtrack'],
        "teams": item['teams'],
        "userId": myId,
        "usingEvents": usingEvents,
        "usingTeams": usingTeams
    }
    return sessionAttributes


def getVictoriesFromDB(userSession):
    """Get the victories from the database recorded under this user.

    This includes all victories for all player/team names.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        {dict}: Nested dictionaries with player names pointing to victories
            that have datetime stamps as their values.

    """
    # Connect to the database:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to get victories attr for user ID {}.".format(myId)
    LOGGER.info(msg)
    try:
        response = table.get_item(
            TableName="DartBattle",
            Key={
                'userId': myId
            }
        )
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return None
    if not 'Item' in response:
        return None

    # Database query successful, now pull the victories from that info:
    victories = response['Item']['victories']
    return victories


def updateRecordAttr(userSession, attrName, attrValue):
    """Updates a single attribute in the user record in the database..

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

        attrName (str): The name of the attribute to update in the DB

        attrValue (*): The value of the attribute to write to the DB

    Returns:
        bool: Whether or not we were successful.

    """
    # Connect to DB:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update item {} for user ID {}."
    LOGGER.info(msg.format(attrName, myId))

    try:
        # Update the user's record. Amazon's DynamoDB uses tokens in the update
        #  expression to prevent injection attacks.
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set {}=:a".format(attrName),
            ExpressionAttributeValues={
                ':a': attrValue
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False


def updateRecordBattle(userSession):
    """Updates user record with new values for attributes relevant to battle.

    These attrs include numBattles, lastRun, currentToken, and
    offsetInMilliseconds.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        bool: Whether or not we were successful.

    """
    # Connect to DB:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update battle items for user ID {}.".format(myId)
    LOGGER.info(msg)
    updateCmd = "SET"
    updateVals = {}
    lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    for i, attr in enumerate(userSession.attributes):
        updateCmd += " {} = :val{}".format(attr, i)
        updateVals[":val{}".format(i)] = userSession.attributes[attr]

    try:
        # Update the user's record. Amazon's DynamoDB uses tokens in the update
        #  expression to prevent injection attacks.
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression=("set numBattles=:n, lastRun=:r, currentToken=:t,"
                              "offsetInMilliseconds=:o"),
            ExpressionAttributeValues={
                ':n': userSession.attributes['numBattles'],
                ':r': lastRun,
                ':t': userSession.currentToken,
                ':o': userSession.offsetInMilliseconds
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False


def updateRecordTeams(userSession):
    """Updates user record with new values for attributes relevant to teams.

    These attrs include playerRoles, teams, and usingTeams.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        bool: Whether or not we were successful.

    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    LOGGER.info("Attempting to update teams attr for user ID {}.".format(myId))
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set playerRoles=:r, teams=:t, usingTeams=:u",
            ExpressionAttributeValues={
                ':r': userSession.playerRoles,
                ':t': userSession.teams,
                ':u': userSession.usingTeams
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False


def updateRecordToken(userSession):
    """Updates user record with new values for audio.

    The audio attrs include currentToken and offsetInMilliseconds.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        bool: Whether or not we were successful.

    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update currentToken/offset attr for user ID {}."
    LOGGER.info(msg.format(userSession.userId))
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': userSession.userId},
            UpdateExpression="set currentToken=:t, offsetInMilliseconds=:o",
            ExpressionAttributeValues={
                ':t': userSession.currentToken,
                ':o': userSession.offsetInMilliseconds
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False


def updateRecordVictory(userSession, victor):
    """Updates user record with new values for victories.

    This does some custom logic to insert the datetime for the victory into the
    database.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

        victor (str): The name of the victor for whom to record a victory.

    Returns:
        bool, int, int: Whether or not we were successful, the number of
            victories by this victor for today, the number of vitories for all
            time by this victor today.

    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update victories attr for user ID {}.".format(myId)
    LOGGER.info(msg)
    try:
        response = table.get_item(
            TableName="DartBattle",
            Key={
                'userId': myId
            }
        )
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False, None, None
    if not 'Item' in response:
        return False, None, None
    victories = response['Item']['victories']
    now = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    if not victor in victories:
        victories[victor] = []
    victories[victor].append(now)
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set victories=:v",
            ExpressionAttributeValues={
                ':v': victories
            },
            ReturnValues="UPDATED_NEW"
        )
        vicToday = 0
        vicTotal = len(victories[victor])
        for vicDate in victories[victor]:
            then = datetime.datetime.strptime(vicDate, "%Y.%m.%d %H:%M:%S")
            if (datetime.datetime.now() - then).days < 1:
                vicToday += 1
        return True, vicToday, vicTotal
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False, None, None


def updateToggleEvents(userSession):
    """Updates user record to toggle the state of events.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        bool: Whether or not we were successful.

    """
    enabled = userSession.usingEvents

    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    msg = "Attempting to update usingEvents attr for user ID {} to {}."
    LOGGER.info(msg.format(myId, enabled))
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set usingEvents=:e",
            ExpressionAttributeValues={
                ':e': enabled
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        LOGGER.info("ClientError received!")
        LOGGER.error(e.response['Error']['Message'])
        return False
