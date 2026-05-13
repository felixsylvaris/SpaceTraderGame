Request for v10:

## File split
I want 4 files from one, and content shouldnt duplicate between them too much.
1) game
2) parameters
3) library
4) songs

# Game
This file is main file.It contains calls to other files. 
It contains actual scripts, game engine, functions. 

# Parameters
This file contains data with numbers. Like intial price setup. Ship upgrade list. Could be list of festivals. Tables of seasonal prices adjustment (harvest), initial price setup is important one. 
Generally if there is variable which is set up even before game start, this should be here. Price spread list here. Planet fuel cost matrxi here. 
This could be file with parameters which could be changed for balance. 

# Libraries
This is file which contains mostly text chunks. 
Bartender advice. 
Ideally text messege templates. 
Like infobroker could have tables could have text temple here. and just suck data from parameters. 
Could be messege templates for newsfeed, since {festival name} or {good} could be called from other list. 
In future there could be stuff like "planet description" if i have one. 

# Songs
So far only 1 song, event horizon, with and art. 
