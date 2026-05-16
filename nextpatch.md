# Expedition
Expedition is the new mini game. Which is paragraph game, with character sheet, and some rolls. 
Expedition each has special file in data/exp/ they could get quite long.  
But character sheet is universal and lives in parameters.  

## Character Sheet
In parameters we gain character sheet. Which is more about our character than ship. It stays over game, and we can get bonuses. We have character sheet dict, and equipment dict (with upgrades we both). 
Stats: (if there is no base, then base 0)
- Power
- Science
- Medicine 
- Perception
- Agiity
- Health (base 3)
- Supply
- Cargo (base 1) 

## Finding Expedition
On Agrica on Promenade there is Expedition Center location under key "e", we can find there:
1) Start expedition
2) Shop
0) Back to promenade

### 2) Shop
We can buy some upgrades for out character, Character sheets stays pernament over game. Including other expeditions or character story. Each equipment could be bouht only once. 
1) Guns 1000c (Power +1)
2) Body Armor 2000c (Power +1, Health +2)
3) Med Kit 2000c (Medicine +2, Science +1)
4) ScoutDrone 3000c (Perception +3)
5) Hire Bodyguard 5000k (Power+3, Health +3, Agility +1, Perception+1)

### Expeditions avaiable
There is only one expedition to choose, we have democracy:
1) "Easy Job" (req easy_job_token)
0) Back

*EasyJobToken* In parameters there is easy_job_token=1. Which allows us one attempt for EasyJob expedition. 

->1) Fluff explanation appears:
"Local Gang offers a bit of Beetlejuice which is local slang for Void Peppers but made from Agricas Bug refining. It has similar effect and taste, but this substitute is hard to sell. We can get 20units for 5k. 
What a bargain. On Nexus we can get twice as much for this." 
1) Lets go! (start expedition) 
2) I need shop first->go to shop
3) No, never, this is not for me. (use easyjob token) 
0) Maybe another time






