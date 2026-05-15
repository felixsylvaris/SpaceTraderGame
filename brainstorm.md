### This is file for my brainstorm, or at breeze.
Ideas that pop up one day, so write them down, maybe one day they will feel code. Like in 3 months or something. AI dont code it yet, you absolute madman. 


### Invest in Stonks
On Planet Promende add Invest location. This allows to buy farmland on location. 
You can buy up to 20 farmlands of each good on planet. The price of farmland depends on base price of produced good. Some farmland could be very expensive. 
We can sell our farmland, but we get only half price that way. 
Each farmland adds 10 production on planet during harvest. 
Each month we get 1 sell price of good per farmland we have on planet. 

### Industrial goods
Industrial goods do not have harvest, they are produced constantly. 
For starter we have Minerals on Zeta9 and Tools on Terra. Minerals are cheap. Tools are medium. 
If we have 50% supply minerals we produce double Tools. If we have 80% minerals we produce tripple. 
If we have 50% tools we produce double minerals. If we have 80% tools we produce tripple minerals. 
Literally 0 means no production. 
Below 20% means half production. 
For starter we produce and move tools and minerals from Zeta9 to Terra. 

### Black Jack in Cantina
We like games, so we put games into games to game when we game inside the game. 
There is a card game black jack, or 21. So we can play a card game and bet money on our win. There are different players of different difficulty. Sample: Mad Alice (tents to overdraw) Sketchy Samus (plays lowball) Savy Tom (is damm good)
We bet money, and we play, if we win we get double. 
Maybe put it into separete file, and even directory /data/ since it is module, we write once, test once, never see again. 

### More random event
During space voyage we could encounter rare events, one in the lifetime events. Like Encounter Space Whale. Hermit on the edge of event horziont. Friendly pirate. Lost freightmen. meteor Shower. 

### Galaxy Timeline
There could be Galaxy Timeline, and chain of events, which happen on specific turns, and generete newsfeed, and change galaxy. 
The story is generally about dominion fleet and colonial rebels. And also pirates. Actually there should be several plotlines happening at the same time. So it will interlock. 

### Expedition
We put games in our games to game while gaming. 
On Void Colony Promenade there is Expedicion Center. We can check our expedition status there, and buy expedicion upgrades like: Land Cruiser, Handguns, Personal Armour, Mercenary Bodyguard, Medic bot, Scientist, Mechanist. Scout probe. Jetpack.  Drill equipment. 
And we embark on adventure into the jungle. During Expedition we have healthbar. And success rate. We can also exit expedition. 
The expedition has form of paragraph minigame. Like You see ruin on horizont how you gonna get there? a) Fly with ship (pay fuel) b) A nice walk c) Use landcruiser (if we have landcruiser). 
->b) You pick stroll through jungle, you encounter Trex. What you gonna do? a) I still have landcruiser so drive away b) I have mercenary and guns, kill the beast (+1 Success) c) Run for life (loose health) 
You get to Ruins, nobody is home, how to get inside a) use jet pack to find gaps b) Mechanics could breach the door c) Drill baby drill. d) Sent the drone e) If we walk long enought we will end somewhere. 
and so on. 
-> Your encounter with Trex leave you mortal wounded, a) it is a scratch (suffer loss of health) b) Medic Medic! (req medic) 
-> Good job you are inside Temple, now what? a) ask scientist for tips b) I have journal of crazy archeologist c) It is about journey not destination. 
Resolution: 
Count success points acquired during expedition. If we get good we get artifacts. If we got very good we receive ancient lasergun which pimps our ship weapons. 

### New Goods
Potencial new goods:
Tools
Microchip
Chemicals
Datacube


### Independent Trader
Independent traders happens late in month cycle. It happens late in the cycle after price and stockpile adjustment. 
There is parameter ind_tr_chance=0.5 which means chance to trigger intedepend trader. 
Independent Trader scans all pairs of planets. Each time there is 50% to skip. Could also pick half pairs from pool of planets (that could be quicker). 
For each planet it checks which good has highest difference on planets. It compares mean prices and dont care about sell/buy. 
And for that good it performs a trade according to the stockpile. it goes like (high price) 10/20/40 (low price).
Independent trader cant negative stockpile, or overstockpile. 
Of course trader takes from low price planet, and moves to high price planet. 
Trader will take max possible from low price, even if at end journey there is no space. 

# StartUp Production
Each month we produce hast map of all goods and sum of stockpile in galaxy for each good. Remove void peppers from the list.  From this we get:
good_min_stock  good name
good_max_stock  good name
It recounts its value each month. 
While good_min_stock or  good_max_stock not empty:
we scan plannets in order Nexus, Terra, Zetta9, Agri, Void Colony and check:
Is there any of them good?  
If there is min stock good add +50 and set good_min_stock as none. Overflow protection. 
If there is max stock good drop -50 and set good_min_stock as none. Negative protection. 
Te purpose is that we balance galaxy if there was too much or too listle of goods. 








