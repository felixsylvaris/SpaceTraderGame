### This is file for dropping feature in progress discussion. 

Adding patchnotes at top of file is actually useful. As i can copy it to readme history. 

## Date and Calendar
Add global variable month and year. And also turn. 
Turn is invisible to player and starts at 1 and just keep going. We will use later (maybe). 
Month will increase by 1 each time we leave planet, we need succesfully leave planet to count. 
Year has 10 months and we start at 2201year
We have 10 months we start at 1st. 
Months name: Ianu, Febu, Mari, Aprix, Maiu, Iuin, Septr, Octo, Nova, Dedl
Also Cantine option "Stay for a while" moves date by 1 month and 1 turn. 

## Extra goods
To each planet add 1 or 2 good from already existing. So each good will exist on 3 planets if possible. 
The price need to be similar to what already existing. With counting that production halves cost locally. And Demand is like +50%
We avoid perfect pairs (can travel back and fort for oscilation trade). 

## Death and taxes
Adding taxes will definetly make game better. 
Each time we sell goods we pay 2% of sale value in taxes. so 10x35=350 income, and 7c tax. We get information about tax paid. And it is removed from our account. minimal tax is 1. It is rounded up to full credit. 

## And now inflation
Each time a turn passes, either in cantine, or leave planet options, the price drift and adjust. 
Produce and Demand prices are stable for now. 
Prices could drift by 1-10 up and 1-9down with 50% on each. It is calculated for each planet+good pair. So yes there is a chance that each 2 months there will be +1c price on each. 
Also add block, that price cant drop below 10. 

## Galaxy Harvest Season
Each good has harvest month. Maybe some good have not like void papers. Lets assume Void pappers are sublime drug which is not harvested for now. Each good different month of harvest. 
In month of harvest price drop but in 5 months there is antiharvest month when galaxy prices are overall higher. We assume that independed traders move some harvest spice around. 
Somple good price adjuster by season: -20,-15,-5,0,+5,+10,+20,+15,+10,0. So Ianu is harvest, Septr is antiharvest. Maybe it dont need to be perfect 5 gap. Can just rotate this templete by 1 for each good. 
So we have galaxy harvest change + random drift. The exact amptitude depends on good initial price, it could be max -20, or could be -30. Actually - prices are risky. Due to negative price. 
The +price could be much more generous. 

## Pumpkin latte Festival
Each planet has one month and one good (which is traded on planet) which is used in Festival. This makes price go crazy for that month. 
So Terra Cinamone Roll Festival could add +50c for month, but the next month it drops hard -50. It is annual same month. 
The festival should always happen after harvest, but could be some time. 
Generete 5 fluff text for bartender advice game, which would mention Planet + Good + Month +fesitval Name + funny detail. Like we fill dummy of tentacle monster with papricas and beat it with plasma hammers to release prize. 
And add it to bartender advice list. 

## Engineering Bay
Engineering Bay is place where we can upgrade our ship. 
Options
1)Fuel Uo
2) Drain Fuel
3) Upgrades
### Fuel Up 
We can tank 100, 200, 500, 1000, all up fuel to our tank. Fuel cost 1c per 1 fuel. 
Make global variable fuelpr=1. Maybe we get ALAXY OPEC crisis in future. 
### Drain fuel
We actually can drain the fuel from our tank. in case if we end with 2000fuel and 0 credits due to some pirates. 
Drain works in similar patter as fuel up. 100,200,500,1000, 90%. And we gain credits. We cant sold out all fuel. 
Add logic we need like 50 fuel to leave the port. Maybe it already is there. 


### Upgrades
Each upgrade we can buy once. And they are BOUGHT. But there is some repeticion. Some Upgrades exist only on 1 planet. 
Ship properties:
Weapons=0
BrokLic=No
pasquotinst=No Also slot for actual content pasquota=[] 

list of uprgades:
- Kinetic Launcher [2000c] Weapon+1
- Mining Lasser [1000c] Weapon+1 [only Zeta-9]
- Void Torpedo [5000c] Weapon+1 [only Void Colony]
- Stern tank 1000c +200 fuel cap
- Portside tank 2000c +300fuel cap
- Cylindrical Tank 3000c +500Fuel cap
- Small Hold 1000c 1000c +100 cargo
- Side Hold 1000c 2000c +100 cargo [only Terra]
- Grain Silo 3000c +200cargo [only Agrica]
- BrokerLicense 1000c unlock peek price [Only Nexus]
- Passanger Quoters 1000c unlock 1 passanger slot
- Long Range Radar 3000c [Only Terra] We reduce chance for pirates by 15%

  ### Galactic Broker License
  There is option to peek prices on all prices. At start of the game it shows "You need to buy Galactic Broker License. Go to Nexus to get one. Maybe sell the ship to afford it."
  After Broker License is installed we can peek at prices from all planets.

  ## Passanger mechanic
  To pick passangers we need to upgrade passanger quoters on our ship.
  Each time we visit planet there is 20% chance the passanger will spawn. Also if we stay in cantina and wait a while. (month passes) Just avoid if looking into cantina again, and again will spawn traveler.
  There is extra option in cantina 3) Traveler <EMPTY> which informs us about presence of traveler ready.
  Each traveler has stats Destination, Shortname, FullName, CantinaText,ExistText.
  Destination is fancy, since it is random, but not planet we are on.
  We can pick traveler from cantina, or not. If we pick when we already have, we kick old one out.
  If we have traveler, and we visit planet they desire, we get +300c and exittext will show.

  There will be many travelers in future, for now 1 is enought
  Whitemain, Pride Mercenary, This large lionlike mercenary with two laserguns hanging on his back is seeking his lost cub. The little furball is always on another planet. // Whitemaine is grateful for end of voyage. He admits he hates hyperlines and teleportacion. Happy pays to leave the ship as soon as possible.
  Or maybe invent some extra passanger type fallowing the type. So there will be a list to pick one. Ideally already made it some form of list, so i can add more in future.

  ## Pirates Encounters
  Global piratangs=10
  global piratbribe=100
  
  When we leave planet there is 25% chance we get pirate encounter.
  Each time we encounter pirate they get +1 piratangst
  Options with pirates
  1) Fight +2piratangst
  2) Flight (pay 20 fuel*pirate agresion) we need to have that.
  3) Bribe 100, but +100 each time, they get greedy, but early game we have get from jail card. Pirateangst-3
  4) Drop cargo - we loose half of each cargo type round up min 1 of each. Pirates let us go. Pirateangst-2
  5) Bluff Out - we claim we are empty. If our total cargo less than 11 we autopass. Otherwise 50% to bluff pass if we failed piratangst+2 and this option is off in this encounter.
  6) Surrender - we surrender our ship, and we are sold as crypto miner on Zeta 9. GAME OVER
 
  ### 1) Fight Pirates
  We estimate pirate power. Max(1, angst%20) and compare it to our weapons. Options
  We are weaker < we loose half of our cargo anyway as panic button.But we continue voyage. Month dont pass extra. 
  We are equal == We scare off pirate away from this porcupine.
  We are superior > We destroyed pirate scum And get 100*pirateangst bounty. Pirateangst+3. We continue our journey

  



