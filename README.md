# Lost-Ark-Brelshaza-Gate-6-Helper
In Lost Ark, the legion raid on Brelshaza's 6th gate can get quite chaotic so I made this helper program in order to help users 
easily keep track of the time between certain mechanics in the fight.

## Meteor Mechanic Explained
The main gimmick of this fight revolves around dropping meteors on the 3x3 grid where you fight the boss. Each tile of the grid 
has 3 HP with the exception of the center tile which has 13 HP. There are two different types of meteors that will damage the 
tiles, blue meteors that will 1 point of damage and yellow meteors that deal 3 points of damage.

- Yellow meteors drop at x188, x137, x88, and x37 HP bars remaining.  
- Blue meteors are dropped every 1 minute after a yellow meteor drops and yellow meteors reset this timer.  
- The number of blue meteors dropped starts with 2 and then alternates between dropping 3 meteors and 4 meteors.  
- Floor tiles get restored after 1 minute and 40 seconds.  

Blue meteors are small enough to only impact 1 tile if placed correctly, while yellow meteors are much larger and will impact at 
least 4 tiles if placed at the very corners of the grid. Due to this, the strategy is to keep all tiles healthy until a yellow 
meteor appears which is guaranteed to break 3 tiles.

Although the program does not currently help the user decide where to drop the meteors, the timer should allow users adequate 
time to prepare themselves for the next incoming mechanic.

## How to use
Start the program by navigating to the directory using a terminal and running the program with the command
> python helper.py
The user only needs to click on the start button when the boss fight begins and click on the corresponding buttons to tell the 
program when a yellow meteor drops and when the floor breaks.
