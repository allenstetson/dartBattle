# dartBattle
Amazon Alexa skill for augmented play with foam-based weaponry.

![](./dartBattleLogo_512x512.png "Dart Battle Logo")

* [Summary](#summary)
* [Features](#features)
  * [Introduction & Help](#introduction-&-help)
  * [Commands](#commands)
  * [Rich Media](#rich-media)
  * [Teams](#teams)
  * [Roles](#roles)
  * [Battles](#battles)
  * [Events](#events)
  * [Rank](#rank)
  * [Victories](#victories)
  * [Rules](#rules)
  * []()

### Summary
Dart Battle is a fully featured game companion built for Amazon Alexa, which provides players using foam-based projectile weapons with features such as timed battles, soundtracks, vivid scenarios with dialog and sound effects, rules, score keeping, premium DLC, team building, team role assignments, rank advancement, and random events mid-game with a variety of objectives.

### Features

#### Introduction & Help
Dart Battle utilizes Amazon's DynamoDB to maintain an awareness of a user's history with the game, and is therefore capable of detecting when a user is new to Dart Battle. Upon a user's first visit, they will be greeted with a special message from the "Commander" and given the option to listen to the help information.

The help information is available at any time to anyone by invoking Alexa's standard Help Intent ("Alexa, help" or similar). This feature playsa short audio clip from the Commander asking your "Tactical Computer" to list available commands. Following that, Alexa's voice simulator walks the user through the numerous available commands.

#### Commands
Commands available to the user are:
* TEAMS
  * "Setup teams"
  * "Tell me the teams"
  * "Shuffle teams"
  * "Clear the teams"
* BATTLES
  * "Start a battle"
  * "Start a _ minute battle", where the user specifies the number of desired minutes
  * "Enable events"
  * "Disable events"
* RANK
  * "What rank am I"
* VICTORIES
  * "Record a victory"
  * "Tell me the victories"
  * "Clear all victories"
  * "Clear victories for _", where the user specifies the name of the team or player for which to clear victories
* PROTOCOLS
  * "Enable protocol _", where the user specifies the name of a protocol (a secret code) to unlock exclusive game content
  * "Disable protocol _", where the user specifies the name of a protocol (a secret code) to turn off exclusive game content
* AUDIO DIRECTIVES
  * Most standard Amazon audio directives are supported, including: "Pause", "Start over", "Stop", "Resume", "Previous", "Next", "Skip"
  * Some standard Amazon audio directives are disabled, including: "Loop", "Shuffle", "Repeat"
* OTHER
  * "How do I play"
  * "More Options"

#### Rich Media
Dart Battle supports Alexa devices with screens, and will display cards with images and text whenever a response is provided. During the battle, Amazon's audio player is displayed along with the Dart Battle artwork and standard playback controls.

#### Teams
Dart Battle supports the creation of two or more teams, randomly assigning individuals to teams, designating a captain, and assigning random combat roles to other team members. When forming a team, Dart Battle asks for the number of players, and then for each player's name (optionally, a user may provide player numbers or nicknames). That list is divided by the number of teams desired, ensuring that team sizes are as consistent as possible (the code contains checks to prevent a user asking for more teams than there are available players). The result is then read aloud to the user.

At any point, the user may ask for Dart Battle to "Tell me the teams" at which place the existing teams and roles are read aloud to the user.

The user may request to "Shuffle the teams" which will use the existing list of players and desired number of teams to form new teams with new captains and new roles.

The user may elect to "Clear the teams" returning Dart Battle to an individual, or "everyone for themselves" mode.

Some random events are only applicable to teams. Therefore, playing Dart Battle in team mode will result in a more unpredictable battle with the potential for more varied objectives. Roles are only applicable to team play.

#### Roles
Players who join teams will be assigned roles to enrich their imaginative gameplay and to potentially give them exclusive tasks through events.  Each team needs a captain, so one member of the team will receive that role always. Additional roles are:
* Communication Specialist (available through a secret code, aka. "protocol", provided to users who complete challenges on https://dartbattle.fun)
* Computer Specialist
* Electrician
* Explosives Expert
* Heavy Weapons Expert
* Intelligence Officer
* Mechanic
* Medic
* Pilot
* Science Officer
* Scout
* Sniper
* Special Forces Operative

Roles not only give players some imaginative prompts to help them play out fantasies on the battlefield, but may also enable specific members of the team to earn points for their team by completing objectives exclusive to their role through random [events](#events).

#### Battles
Battles provide players with a framework within which to carry out their competitive gameplay at home. They provide a clear beginning and end to the battle, helping to reduce conflict between players, and provide rich imaginative play through music, characters, and dialog which are themed to different locations, conditions, and eras in history. Battles are comprised of sections of music which can be as short as 30 seconds and as long as 2 minutes. By specifying a duration for a battle, the user causes the code to divide the user's requested number of minutes into smaller chunks, allowing the insertion of one or more events, and using the available sections of music to form a battle of the desired length.  The default battle length is 5 minutes which allows for two events during the battle.

Once the battle is formed, an introduction unique to the randomly-chosen scenario is prepended, along with a clear countdown until the start of battle. This allows players to get into their starting positions, behind cover or in strategic positions, before battle begins.

Once the battle concludes, a reminder is issued for the user to record the victory, and a "tail" may be added to the very end which might be a reminder to rate the Alexa Skill in the Skill Store, or to visit Dart Battle on Facebook, or to visit https://dartbattle.fun, or similar.

Due to limitations imposed by Amazon on apps that trigger audio playback using the Audio Directives, the skill exits after a battle, and the user is free to start Dart Battle again or to reinvoke Dart Battle by saying "Alexa, tell Dart Battle to _", such as "record a victory" or "start a battle".

#### Events
Events provide interruptions during battle, issuing new objectives to players, thereby changing the dynamics of gameplay for players and using dialog and sound effects to reinforce the theme of the chosen scenario.  Each scenario has unique events with unique dialog and sound effects, but they all fall into the following categories:

* Cease Fire
  * For the reminder of the event, no one is allowed to discharge their weapon, or they suffer negative points. This allows players to reposition, regroup, or resupply safely without the fear of being hit.
* Drop And Roll
  * For scenarios including fire, this forces players to drop and roll, or else suffer negative points. This forces people in strategic nests to leave their cover momentarily, giving opponents a chance to hit them.
* Duel
 * This scenario pits two opposing team members against one another, allowing one to be a hero by scoring bonus points for their team.
* Exclusive Shot
 * For the remainder of the event, this event gives one and only one player the ability to fire, while all others are restricted from discharging their weapon under penalty of negative points.
* Hold On
 * For scenarios including earthquakes, large explosives, etc., this event forces players to run to a fixed object and hold on for the duration of the event. This might draw some opponents out of hiding.
* Lay Down
 * All players must lay prone on the ground for the remainder of the event. This may render opponents more or less vulnerable, depending on their position.
* Pair Up
 * For team play, this event forces teams to find a buddy with whom to pair before the end of the event, or risk suffering negative points.
* Protect
 * For team play, this event forces members of a team to protect one specified member. The team suffers negative points if the specified member is hit.
* Reset
 * This event forces players to return to their starting locations, and it wipes out the score thus far in battle. This can be a real game changer, allowing an underdog team the chance at a surprise victory.
* Resupply
 * This event restricts any discharge of weapons until a player has acquired the specified number of additional foam projectiles. This gives teams a chance to reload weapons without fear of being hit.
* Retreat
 * This event forces teams to regroup behind their lines, and may significantly change the battlefield during battle.
* Specific Target
 * This event specifies a single opposing team member that must be hit before the end of the event. Teams have the chance to score bonus points if that specified member is hit.
* Shelter
 * This event forces players to find an enclosed space or a space that provides cover from above until the end of the event.
* Split Up
 * This event forces team members to maintain a minimum distance between friendly team members until the conclusion of the event, potentially breaking up strategic nests or partnerships for a time.
* Tag Feature
 * This event requires team members to reach a specified target before the conclusion of the event. This target might be a light, a door, a plant, etc. This has the potential to break up teams and close the distance with opponents.
* Tag In Order
 * This event specifies multiple targets that must be reached in a particular order. These targets are likely team members from youngest to oldest, shortest hair to longest, etc. This has the potential to introduce confusion, chatter, and hopefully laughter in the midst of battle.
* Tag Many To One
 * This event forces team members to tag one specific team member before the conclusion of the event. For instance, everyone must reach the team captain under penalty of negative points.
* Tag One To Many
 * This event forces one team member to reach as many friendly team members as possible before the conclusion of the event. For instance, the medic must reach as many team mates as possible, with bonus points for each one reached.
* Zero Eliminations
 * This rare event rewards teams who have protected at least one team member from any eliminations by allowing the team to halve all points against them at the end of the battle.

Events can be turned off, if players prefer just music while they play, without any dialog, sound effects, or random events. To do this, players simply ask Dart Battle to "disable events". They can be re-enabled by asking Dart Battle to "enable events".

#### Rank


#### Victories
#### Rules

