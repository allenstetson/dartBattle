import sys
import random

sys.path.insert(0, "y:/home/2018_01_18_AlexaDartBattle")

import battle
import teams

#------------------------------------------------------------------------------
# Test Data
#------------------------------------------------------------------------------
inputJson = {
    "version": "1.0",
    "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.f3772c2b-97b9-435c-9192-1582af783dde",
        "application": {
            "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
        },
        "user": {
            "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
        }
    },
    "context": {
        "AudioPlayer": {
            "playerActivity": "IDLE"
        },
        "Display": {
            "token": ""
        },
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
            },
            "user": {
                "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
            },
            "device": {
                "deviceId": "amzn1.ask.device.AFWG7Y6Z66Q75MPHOH6C7OQR7NR5THCVYDUIIURUVVWV7HXT5ZQBEXQONV5PS6OLH3D6WBHJOSMZQP6QMLM2EQROSAOMD4UCGQJJMQ3PNCCNY7MVQOAMEAEUWLQFNHFSFJ5IWMJ5JZERM3TKYTBAY6CWIJZEJWY24BQVMDT4HXGQ6USNXRPQU",
                "supportedInterfaces": {
                    "AudioPlayer": {},
                    "Display": {
                        "templateVersion": "1.0",
                        "markupVersion": "1.0"
                    }
                }
            },
            "apiEndpoint": "https://api.amazonalexa.com",
            "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUxNzcxMDE0OSwiaWF0IjoxNTE3NzA2NTQ5LCJuYmYiOjE1MTc3MDY1NDksInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUZXRzdZNlo2NlE3NU1QSE9INkM3T1FSN05SNVRIQ1ZZRFVJSVVSVVZWV1Y3SFhUNVpRQkVYUU9OVjVQUzZPTEgzRDZXQkhKT1NNWlFQNlFNTE0yRVFST1NBT01ENFVDR1FKSk1RM1BOQ0NOWTdNVlFPQU1FQUVVV0xRRk5IRlNGSjVJV01KNUpaRVJNM1RLWVRCQVk2Q1dJSlpFSldZMjRCUVZNRFQ0SFhHUTZVU05YUlBRVSIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFIUkRUMlBZQVdGQkZSVk1FVVROVlVIVEhGRFJSVjIzVDM1Mk5FTEc3TU5MTFAyNVo0TkVQWFFCS01YNjYyWk1LM1BDNVZWQUdYQUFDQjRXSUM1UVlQSllMRFA0VFJEQ1NSSDdORkIzVDJJSzdONVNXU1hSTEVaVEhBNlZEQkg0U0xMQks1V1pSWVdCM1NXRkxUWTNYVTRITExYRUE3TFpISEVaN1NGVFVIRVlIUlpXVFkyRjNUT0JMNUQyMkxIVFBHTEpPUU1NQTdFUllWUSJ9fQ.de3pPeF8pckvLUGnP06PJwL0Y4RyvdYDsw8ZWXYW3jMela8kFfSvzKBOkQ7JSwRPoVm2EIs8iXQuOjXtQd_ChTYRaDBd2WECnE5ZT1Ea0RenmEeBMWGmptouQmqEnmkniv6d1LiibD26JpeLYA0bliPZL38TUsxKUA2nToB0I2vdU6s1TXpfiyiigC7nePKHjfyTrTZk9OQuNEP13j8pZy1jsKqlFK9ebxz4Hd6PfFVr9kvLqxdqZ7vxqGVv4oTgDsiawDR8CZHep4ztUPLHJRNWrO4IbEC7iiPxmQRyQVCwTTRcSNGaFSLEwjBjaix8iEQKVURCcL7dz-ohHT_fzA"
        }
    },
    "request": {
        "type": "LaunchRequest",
        "requestId": "amzn1.echo-api.request.91c160ab-73dd-48a6-b456-25406845f693",
        "timestamp": "2018-02-04T01:09:09Z",
        "locale": "en-US"
    }
}

inputJson2 = {
    "version": "1.0",
    "session": {
        "new": False,
        "sessionId": "amzn1.echo-api.session.f3772c2b-97b9-435c-9192-1582af783dde",
        "application": {
            "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
        },
        "attributes": {
            "duration": "120",
            "recentSession": "False",
            "rank": "03"
        },
        "user": {
            "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
        }
    },
    "context": {
        "AudioPlayer": {
            "playerActivity": "IDLE"
        },
        "Display": {
            "token": ""
        },
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
            },
            "user": {
                "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
            },
            "device": {
                "deviceId": "amzn1.ask.device.AFWG7Y6Z66Q75MPHOH6C7OQR7NR5THCVYDUIIURUVVWV7HXT5ZQBEXQONV5PS6OLH3D6WBHJOSMZQP6QMLM2EQROSAOMD4UCGQJJMQ3PNCCNY7MVQOAMEAEUWLQFNHFSFJ5IWMJ5JZERM3TKYTBAY6CWIJZEJWY24BQVMDT4HXGQ6USNXRPQU",
                "supportedInterfaces": {
                    "AudioPlayer": {},
                    "Display": {
                        "templateVersion": "1.0",
                        "markupVersion": "1.0"
                    }
                }
            },
            "apiEndpoint": "https://api.amazonalexa.com",
            "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUxNzcxMDI3MywiaWF0IjoxNTE3NzA2NjczLCJuYmYiOjE1MTc3MDY2NzMsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUZXRzdZNlo2NlE3NU1QSE9INkM3T1FSN05SNVRIQ1ZZRFVJSVVSVVZWV1Y3SFhUNVpRQkVYUU9OVjVQUzZPTEgzRDZXQkhKT1NNWlFQNlFNTE0yRVFST1NBT01ENFVDR1FKSk1RM1BOQ0NOWTdNVlFPQU1FQUVVV0xRRk5IRlNGSjVJV01KNUpaRVJNM1RLWVRCQVk2Q1dJSlpFSldZMjRCUVZNRFQ0SFhHUTZVU05YUlBRVSIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFIUkRUMlBZQVdGQkZSVk1FVVROVlVIVEhGRFJSVjIzVDM1Mk5FTEc3TU5MTFAyNVo0TkVQWFFCS01YNjYyWk1LM1BDNVZWQUdYQUFDQjRXSUM1UVlQSllMRFA0VFJEQ1NSSDdORkIzVDJJSzdONVNXU1hSTEVaVEhBNlZEQkg0U0xMQks1V1pSWVdCM1NXRkxUWTNYVTRITExYRUE3TFpISEVaN1NGVFVIRVlIUlpXVFkyRjNUT0JMNUQyMkxIVFBHTEpPUU1NQTdFUllWUSJ9fQ.jvsQ2HTzk7u5Gz_rolCJCenYkp606Xdd43O1ohLGZK_amAMGcIXiQY2zUZ75LLx-HmNtNsuooK1x1n8SWH7hbom_q-dtHgwha_PFpoifDBVBfiK5PvEnQOAugZzU4fdUwaQZ057mduQIvTLnsoEmC4sjHimUm6HnVX60fvIF5a7eWe0MOSjBEs5Bf8FRIua1uKs_FxGTTiuH8u_v8WaCf_hVYzDqPfeDLuiRN_wG9tFvKI-9lSXL4Xzyx2DojPrmWj21CMgcXoa9ELQL_Ed5B-1z1Y7ZnYyD4qwWQOZUfFAof477XPx5uulWK8OZTBKcNI3YFrHbX1uWwV3J7vSfAQ"
        }
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "amzn1.echo-api.request.817f62db-9e52-4edc-8abc-eb642156e1fe",
        "timestamp": "2018-02-04T01:11:13Z",
        "locale": "en-US",
        "intent": {
            "name": "SetupTeamsIntent",
            "confirmationStatus": "NONE",
            "slots": {
                "PLAYERSIX": {
                    "name": "PLAYERSIX",
                    "confirmationStatus": "NONE"
                },
                "PLAYERNUM": {
                    "name": "PLAYERNUM",
                    "confirmationStatus": "NONE"
                },
                "PLAYERONE": {
                    "name": "PLAYERONE",
                    "confirmationStatus": "NONE"
                },
                "TEAMNUM": {
                    "name": "TEAMNUM",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTWO": {
                    "name": "PLAYERTWO",
                    "confirmationStatus": "NONE"
                },
                "PLAYERFIVE": {
                    "name": "PLAYERFIVE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTWELVE": {
                    "name": "PLAYERTWELVE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERNINE": {
                    "name": "PLAYERNINE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERELEVEN": {
                    "name": "PLAYERELEVEN",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTHREE": {
                    "name": "PLAYERTHREE",
                    "confirmationStatus": "NONE"
                },
                "PLAYEREIGHT": {
                    "name": "PLAYEREIGHT",
                    "confirmationStatus": "NONE"
                },
                "PLAYERSEVEN": {
                    "name": "PLAYERSEVEN",
                    "confirmationStatus": "NONE"
                },
                "PLAYERFOUR": {
                    "name": "PLAYERFOUR",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTEN": {
                    "name": "PLAYERTEN",
                    "confirmationStatus": "NONE"
                }
            }
        },
        "dialogState": "STARTED"
    }
}

roles = {1:[
    '01',
    '{:02d}'.format(random.randint(2, 15)),
    '{:02d}'.format(random.randint(2, 15)),
    '{:02d}'.format(random.randint(2, 15))
    ], 2:[
    '01',
    '{:02d}'.format(random.randint(2, 15)),
    '{:02d}'.format(random.randint(2, 15)),
    '{:02d}'.format(random.randint(2, 15))
    ]}

teamJson = {
    "version": "1.0",
    "session": {
        "new": False,
        "sessionId": "amzn1.echo-api.session.f3772c2b-97b9-435c-9192-1582af783dde",
        "application": {
            "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
        },
        "attributes": {
            "duration": "600",
            "recentSession": "False",
            "rank": "10",
            "roles": roles,
            "sfx": "True",
            "soundtrack": "True",
            "usingTeams": "True"
        },
        "user": {
            "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
        }
    },
    "context": {
        "AudioPlayer": {
            "playerActivity": "IDLE"
        },
        "Display": {
            "token": ""
        },
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"
            },
            "user": {
                "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
            },
            "device": {
                "deviceId": "amzn1.ask.device.AFWG7Y6Z66Q75MPHOH6C7OQR7NR5THCVYDUIIURUVVWV7HXT5ZQBEXQONV5PS6OLH3D6WBHJOSMZQP6QMLM2EQROSAOMD4UCGQJJMQ3PNCCNY7MVQOAMEAEUWLQFNHFSFJ5IWMJ5JZERM3TKYTBAY6CWIJZEJWY24BQVMDT4HXGQ6USNXRPQU",
                "supportedInterfaces": {
                    "AudioPlayer": {},
                    "Display": {
                        "templateVersion": "1.0",
                        "markupVersion": "1.0"
                    }
                }
            },
            "apiEndpoint": "https://api.amazonalexa.com",
            "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUxNzcxMDI3MywiaWF0IjoxNTE3NzA2NjczLCJuYmYiOjE1MTc3MDY2NzMsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUZXRzdZNlo2NlE3NU1QSE9INkM3T1FSN05SNVRIQ1ZZRFVJSVVSVVZWV1Y3SFhUNVpRQkVYUU9OVjVQUzZPTEgzRDZXQkhKT1NNWlFQNlFNTE0yRVFST1NBT01ENFVDR1FKSk1RM1BOQ0NOWTdNVlFPQU1FQUVVV0xRRk5IRlNGSjVJV01KNUpaRVJNM1RLWVRCQVk2Q1dJSlpFSldZMjRCUVZNRFQ0SFhHUTZVU05YUlBRVSIsInVzZXJJZCI6ImFtem4xLmFzay5hY2NvdW50LkFIUkRUMlBZQVdGQkZSVk1FVVROVlVIVEhGRFJSVjIzVDM1Mk5FTEc3TU5MTFAyNVo0TkVQWFFCS01YNjYyWk1LM1BDNVZWQUdYQUFDQjRXSUM1UVlQSllMRFA0VFJEQ1NSSDdORkIzVDJJSzdONVNXU1hSTEVaVEhBNlZEQkg0U0xMQks1V1pSWVdCM1NXRkxUWTNYVTRITExYRUE3TFpISEVaN1NGVFVIRVlIUlpXVFkyRjNUT0JMNUQyMkxIVFBHTEpPUU1NQTdFUllWUSJ9fQ.jvsQ2HTzk7u5Gz_rolCJCenYkp606Xdd43O1ohLGZK_amAMGcIXiQY2zUZ75LLx-HmNtNsuooK1x1n8SWH7hbom_q-dtHgwha_PFpoifDBVBfiK5PvEnQOAugZzU4fdUwaQZ057mduQIvTLnsoEmC4sjHimUm6HnVX60fvIF5a7eWe0MOSjBEs5Bf8FRIua1uKs_FxGTTiuH8u_v8WaCf_hVYzDqPfeDLuiRN_wG9tFvKI-9lSXL4Xzyx2DojPrmWj21CMgcXoa9ELQL_Ed5B-1z1Y7ZnYyD4qwWQOZUfFAof477XPx5uulWK8OZTBKcNI3YFrHbX1uWwV3J7vSfAQ"
        }
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "amzn1.echo-api.request.817f62db-9e52-4edc-8abc-eb642156e1fe",
        "timestamp": "2018-02-04T01:11:13Z",
        "locale": "en-US",
        "intent": {
            "name": "SetupTeamsIntent",
            "confirmationStatus": "NONE",
            "slots": {
                "PLAYERSIX": {
                    "name": "PLAYERSIX",
                    "confirmationStatus": "NONE"
                },
                "PLAYERNUM": {
                    "name": "PLAYERNUM",
                    "confirmationStatus": "NONE"
                },
                "PLAYERONE": {
                    "name": "PLAYERONE",
                    "confirmationStatus": "NONE"
                },
                "TEAMNUM": {
                    "name": "TEAMNUM",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTWO": {
                    "name": "PLAYERTWO",
                    "confirmationStatus": "NONE"
                },
                "PLAYERFIVE": {
                    "name": "PLAYERFIVE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTWELVE": {
                    "name": "PLAYERTWELVE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERNINE": {
                    "name": "PLAYERNINE",
                    "confirmationStatus": "NONE"
                },
                "PLAYERELEVEN": {
                    "name": "PLAYERELEVEN",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTHREE": {
                    "name": "PLAYERTHREE",
                    "confirmationStatus": "NONE"
                },
                "PLAYEREIGHT": {
                    "name": "PLAYEREIGHT",
                    "confirmationStatus": "NONE"
                },
                "PLAYERSEVEN": {
                    "name": "PLAYERSEVEN",
                    "confirmationStatus": "NONE"
                },
                "PLAYERFOUR": {
                    "name": "PLAYERFOUR",
                    "confirmationStatus": "NONE"
                },
                "PLAYERTEN": {
                    "name": "PLAYERTEN",
                    "confirmationStatus": "NONE"
                }
            }
        },
        "dialogState": "STARTED"
    }
}

data_battle_ScenePlaylist_availableEvents = {
			"soundtrack": "True",
			"lastRun": "2018.04.19 04:06:55",
			"sfx": "True",
			"teams": {
				"1": {
					"Riley": "scout",
					"Owen": "communications_specialist",
					"Jonah": "captain"
				},
				"2": {
					"ralph": "special_forces_operative",
					"Hannah": "captain",
					"Asher": "communications_specialist"
				}
			},
			"playerRank": "02",
			"playerRoles": {
				"1": [
					"01",
					"12",
					"02"
				],
				"2": [
					"01",
					"02",
					"14"
				]
			},
			"recentSession": "True",
			"battleDuration": "360",
			"numBattles": "7",
			"usingTeams": "True",
			"userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ"
		}

data_teams_countVictories = {
    "Allen": ["2018.01.18 17:22:21"],
    "Brandy": [],
    "Cassie": ["2017.12.24 05:22:21", "2018.02.07 06:12:22"]
}

data_teams_ReciteTeamRoles = {
    "1": {
        "Riley": "scout",
        "Owen": "communications_specialist",
        "Jonah": "captain"
    },
    "2": {
        "ralph": "special_forces_operative",
        "Hannah": "captain",
        "Asher": "communications_specialist"
    }
}

data_battle_GetTrackFromToken = {
    "version": "0.1",
    "sessionAttributes": {
        "battleDuration": "240",
        "currentToken": "session_04.1.1.1.1_track_01_playlist_01.00.A_02.02.60_03.06.HeatSignature.00_04.02.60_05.03.Yeti.00_06.02.60_07.22",
        "lastRun": "2018.05.25 04:23:34",
        "numBattles": "49",
        "offsetInMilliseconds": "0",
        "recentSession": "False",
        "playerRank": "04",
        "playerRoles": {
            "1": [
                "01",
                "12"
            ],
            "2": [
                "01",
                "05"
            ]
        },
        "sfx": "True",
        "soundtrack": "True",
        "teams": {
            "1": {
                "frank": "captain",
                "Lena": "scout"
            },
            "2": {
                "Alan": "captain",
                "chris": "explosives_expert"
            }
        },
        "userId": "amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ",
        "usingTeams": "True",
        "240": "240"
    },
    "response": {
        "directives": [
            {
                "type": "AudioPlayer.Play",
                "playBehavior": "REPLACE_ALL",
                "audioItem": {
                    "stream": {
                        "token": "session_04.1.1.1.1_track_01_playlist_01.00.A_02.02.60_03.06.HeatSignature.00_04.02.60_05.03.Yeti.00_06.02.60_07.22",
                        "url": None,
                        "offsetInMilliseconds": 0
                    }
                }
            }
        ],
        "outputSpeech": {
            "type": "PlainText",
            "text": "4 minute arctic team battle commencing."
        },
        "card": {
            "type": "Standard",
            "title": "Start a Battle",
            "text": "4 minute arctic team battle commencing.",
            "image": {
                "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_720x480.jpg",
                "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_1200x800.jpg"
            }
        },
        "shouldEndSession": True
    }
}

data_get_next_from_token_02 = {'version': '1.0', 'context': {'AudioPlayer': {'offsetInMilliseconds': 68, 'token': 'session_02.1.1.1.1_track_07_playlist_01.00.B_02.02.60_03.07.Blizzard.00_04.02.60_05.08.KeyMember.11_06.02.60_07.22', 'playerActivity': 'PLAYING'}, 'System': {'application': {'applicationId': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}, 'user': {'userId': 'amzn1.ask.account.AHRDT2PYAWFBFRVMEUTNVUHTHFDRRV23T352NELG7MNLLP25Z4NEPXQBKMX662ZMK3PC5VVAGXAACB4WIC5QYPJYLDP4TRDCSRH7NFB3T2IK7N5SWSXRLEZTHA6VDBH4SLLBK5WZRYWB3SWFLTY3XU4HLLXEA7LZHHEZ7SFTUHEYHRZWTY2F3TOBL5D22LHTPGLJOQMMA7ERYVQ'}, 'device': {'deviceId': 'amzn1.ask.device.AFWG7Y6Z66Q75MPHOH6C7OQR7NRZAQEU5375YQ7XCB43BUJRDZ2SMA6OO3HM3FLJE4RYMXEIOFCW2DFRCEGUPBOO4O6MN37LVCAMIC445RRPOU3OIQ5P3OVCBKRFO34GTM2DS3VQFVBEANGOT4G76SSJIOYA', 'supportedInterfaces': {'AudioPlayer': {}}}, 'apiEndpoint': 'https://api.amazonalexa.com', 'apiAccessToken': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUyNzY5NDg3NSwiaWF0IjoxNTI3NjkxMjc1LCJuYmYiOjE1Mjc2OTEyNzUsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUZXRzdZNlo2NlE3NU1QSE9INkM3T1FSN05SWkFRRVU1Mzc1WVE3WENCNDNCVUpSRFoyU01BNk9PM0hNM0ZMSkU0UllNWEVJT0ZDVzJERlJDRUdVUEJPTzRPNk1OMzdMVkNBTUlDNDQ1UlJQT1UzT0lRNVAzT1ZDQktSRk8zNEdUTTJEUzNWUUZWQkVBTkdPVDRHNzZTU0pJT1lBIiwidXNlcklkIjoiYW16bjEuYXNrLmFjY291bnQuQUhSRFQyUFlBV0ZCRlJWTUVVVE5WVUhUSEZEUlJWMjNUMzUyTkVMRzdNTkxMUDI1WjRORVBYUUJLTVg2NjJaTUszUEM1VlZBR1hBQUNCNFdJQzVRWVBKWUxEUDRUUkRDU1JIN05GQjNUMklLN041U1dTWFJMRVpUSEE2VkRCSDRTTExCSzVXWlJZV0IzU1dGTFRZM1hVNEhMTFhFQTdMWkhIRVo3U0ZUVUhFWUhSWldUWTJGM1RPQkw1RDIyTEhUUEdMSk9RTU1BN0VSWVZRIn19.KV6aEtGU8gBjlvz9InZ0hbdzdcsbN2osAMZfDUOv0sJpt_qiITCFRV42QyR21bYpy0oscDWSZ6KpkK5ufnQr7Pi4YyuWa68nZzjWe2FykgsdawJirokMVAjmf-MRQERIWGCj1crrag8hHt4Y7ZSFCWhDzgNbfyXZyB-Fo_INkkKvi4lsD9DvZfogsCmzc9D2BZqdRkHgiJ5eoJO0GqUWcVm3zLaM59t8BBYID19f2OEzkNs0opT8DRIouX_rbJecrTB3OwiqqOmOfpMnnOTalwpAlEriiNOBnGMs8Ho1gBIAMSFTHP2-rEXvdX_ID6r2XNQm61fb_A63oQat7-D_gA'}}, 'request': {'type': 'AudioPlayer.PlaybackNearlyFinished', 'requestId': 'amzn1.echo-api.request.083ab0a6-d98a-4eb2-821e-bc6b8b7f2fc0', 'timestamp': '2018-05-30T14:41:15Z', 'locale': 'en-US', 'token': 'session_02.1.1.1.1_track_07_playlist_01.00.B_02.02.60_03.07.Blizzard.00_04.02.60_05.08.KeyMember.11_06.02.60_07.22', 'offsetInMilliseconds': 68}}

#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
def test_teams_assignTeamsAndRoles():
    print("running test_teams_assignTeamsAndRoles...")
    teamAssignments, playerAssignments = teams.assignTeamsandRoles(
        2, ['Allen', 'Brenda', 'Cameron', 'Dave', 'Edward', 'Felicia']
    )
    teamOne = list(playerAssignments.keys())[0]
    assert isinstance(teamAssignments, dict)
    assert isinstance(playerAssignments, dict)
    assert len(teamAssignments.keys()) == 2
    assert len(playerAssignments.keys()) == 2
    assert len(playerAssignments[teamOne]) == 3
    print("test_teams_assignTeamsAndRoles complete\n")

def test_teams_countVictories():
    print("running test_teams_countVictories...")
    todayVix, lifetimeVix = teams.countVictories(data_teams_countVictories)
    assert todayVix == {}
    assert len(lifetimeVix.keys()) == 2
    print("test teams_countVictories complete\n")

def test_teams_reciteTeamRoles():
    print("running test_teams_reciteTeamRoles...")
    speech = str(teams.reciteTeamRoles(data_teams_ReciteTeamRoles))
    expected = "Team 1. Riley is your scout. Owen is your communications specialist. " +\
    "Jonah is your captain. Team 2. ralph is your special forces operative. " +\
    "Hannah is your captain. Asher is your communications specialist. "
    assert speech.encode('ascii') == expected.encode('ascii')
    print("test teams_reciteTeamRoles complete\n")

def test_battle_ScenePlaylist_availableEvents():
    print("running test_battle_ScenePlaylist_availableEvents...")
    scenePlaylist = battle.ScenePlaylist("arctic",
                                         data_battle_ScenePlaylist_availableEvents)
    assert len(set(scenePlaylist.roles).intersection(['01', '02', '12', '14'])) == 4
    print("test_battle_ScenePlaylist_availableEvents complete\n")

def test_battle_GetTrackFromToken():
    print("Running get track from token...")
    token = "session_04.1.1.1.1_track_01_playlist_01.00.A_02.02.60_03.06.HeatSignature.00_04.02.60_05.03.Yeti.00_06.02.60_07.22"
    scenePlaylist = battle.ScenePlaylist("arctic",
                                         data_battle_GetTrackFromToken['sessionAttributes'])
    output = scenePlaylist.getTrackFromToken(token)
    print(output)
    print("test_battle_GetTrackFromToken complete\n")

def test_battle_GetNextFromToken():
    print("Running get next from token...")
    token = "session_04.1.1.1.1_track_01_playlist_01.00.A_02.02.60_03.06.HeatSignature.00_04.02.60_05.03.Yeti.00_06.02.60_07.22"
    token = "session_02.1.1.1.1_track_07_playlist_01.00.B_02.02.60_03.07.Blizzard.00_04.02.60_05.08.KeyMember.11_06.02.60_07.22"
    scenePlaylist = battle.ScenePlaylist("arctic",
                                         data_battle_GetTrackFromToken['sessionAttributes'])
    output = scenePlaylist.getNextFromToken(token)
    print(output)
    print("test_battle_GetNextFromToken complete\n")

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
if __name__ == "__main__":
    #test_teams_assignTeamsAndRoles()
    #test_teams_countVictories()
    #test_teams_reciteTeamRoles()
    #test_battle_ScenePlaylist_availableEvents()
    test_battle_GetTrackFromToken()
    test_battle_GetNextFromToken()

