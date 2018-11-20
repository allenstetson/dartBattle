# Std lib imports:
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from botocore.exceptions import ClientError
import boto3
DB_ACTIVE = True
# DB_ACTIVE = False #THIS DISABLES DB WHILE IT IS UNSTABLE. COMMENT FOR TESTING.

"""
try:
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError
    import boto3
    DB_ACTIVE = True
    # DB_ACTIVE = False #THIS DISABLES DB WHILE IT IS UNSTABLE. COMMENT FOR TESTING.
    logger.info('DB Import successful')
except ImportError as e:
    logger.info(e.message + "\n" + e.args)
    logger.info("DB Import failed. Falling back to defaults.")
    DB_ACTIVE = False
"""

def isActive():
    return DB_ACTIVE


def clearRecordVictory(userSession, victor=None):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update victories attr for user ID {}.".format(myId))
    if victor:
        try:
            response = table.get_item(
                TableName="DartBattle",
                Key={
                    'userId': myId
                }
            )
        except ClientError as e:
            logger.info("ClientError received!")
            logger.error(e.response['Error']['Message'])
            return False, None, None
        if not 'Item' in response:
            return False, None, None
        victories = response['Item']['victories']
        victories[victor] = []
    else:
        victories = {}
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
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def getDefaultSessionAttrs(userId):
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
        dynamodb = boto3.resource(
            'dynamodb',
            region_name='us-east-1',
            endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
        )
        myId = session.userId
        table = dynamodb.Table('DartBattle')
        logger.info("Attempting to retrieve item for user ID {}.".format(myId))
        item = None
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
            logger.info("ClientError received!")
            logger.error(e.response['Error']['Message'])
            newUser = True
        if newUser:
            logger.info("get_item for userId failed, new user.")
            sessionAttributes = getDefaultSessionAttrs(myId)
            table.put_item(Item=sessionAttributes)
        else:
            logger.info("get_item for userId succeeded.")

            # Look for recent session
            lastRun = datetime.datetime.strptime(item['lastRun'], "%Y.%m.%d %H:%M:%S")
            now = datetime.datetime.now()
            delta = now-lastRun
            logger.info("Lapse between lastRun ({}) and now({}) is {} days.".format(lastRun, now, delta.days))
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
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to get victories attr for user ID {}.".format(myId))
    try:
        response = table.get_item(
            TableName="DartBattle",
            Key={
                'userId': myId
            }
        )
    except ClientError as e:
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return None
    if not 'Item' in response:
        return None
    victories = response['Item']['victories']
    return victories


def updateRecordProtocol(userSession):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    protocolCodes = userSession.protocolCodes

    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update protocol attr for user ID {}.".format(myId))
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set protocolCodes=:p",
            ExpressionAttributeValues={
                ':p': protocolCodes
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def updateRecordDuration(userSession):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update battleDuration attr for user ID {}.".format(myId))
    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set battleDuration=:d",
            ExpressionAttributeValues={
                ':d': userSession.battleDuration
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def updateRecordTeams(userSession):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update teams attr for user ID {}.".format(myId))
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
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def updateRecordToken(userSession):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update currentToken attr for user ID {}.".format(userSession.userId))
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
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def updateRecordVictory(userSession, victor):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update victories attr for user ID {}.".format(myId))
    try:
        response = table.get_item(
            TableName="DartBattle",
            Key={
                'userId': myId
            }
        )
    except ClientError as e:
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
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
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False, None, None


def updateRecord(session):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = session.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update item for user ID {}.".format(myId))
    updateCmd = "SET"
    updateVals = {}
    lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    for i, attr in enumerate(session.attributes):
        updateCmd += " {} = :val{}".format(attr, i)
        updateVals[":val{}".format(i)] = session.attributes[attr]

    try:
        table.update_item(
            TableName="DartBattle",
            Key={'userId': myId},
            UpdateExpression="set numBattles=:n, lastRun=:r, playerRank=:k",
            ExpressionAttributeValues={
                ':n': session.attributes['numBattles'],
                ':r': lastRun,
                ':k': session.attributes['playerRank']
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False


def updateToggleEvents(userSession):
    enabled = userSession.usingEvents

    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        endpoint_url="http://dynamodb.us-east-1.amazonaws.com"
    )
    myId = userSession.userId
    table = dynamodb.Table('DartBattle')
    logger.info("Attempting to update usingEvents attr for user ID {} to {}.".format(myId, enabled))
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
        logger.info("ClientError received!")
        logger.error(e.response['Error']['Message'])
        return False
