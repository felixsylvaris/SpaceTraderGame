# Terra, Fleet Supply Depo and industrial good
Terra, Fleet Supply Depo now accepts industrial goods them goods:
Minerals
Alloys
Weapons
Soybeans
Medicine
Robots
The logic is same. Only buy from player, price is min price+spread+5. Check if supply price is +5 over min sell price potencial. 
In Case of robots, and gubs it is just +1 over min, since we just lorry from factory to depo, production on Terra. 


# Independent Trader

Independent traders happens late in month cycle. It happens late in the cycle after price and stockpile adjustment. There is parameter ind_tr_chance=0.3 which means chance to trigger intedepend trader. Independent Trader scans all pairs of planets. Each time there is 30% to skip. Could also pick half pairs from pool of planets (that could be quicker). For each planet it checks which good has highest difference on planets. It compares mean prices and dont care about sell/buy. And for that good it performs a trade according to the stockpile. it goes like (high price) 10/20/40 (low price). So Cinamone is 40units void peppers is 10. This need to be in parameters.  Independent trader cant negative stockpile, or overstockpile. Of course trader takes from low price planet, and moves to high price planet. Trader will take max possible from low price, even if at end journey there is no space.
Independent trader operation couse price rise by +5 on low side, and price drop on high side (destination) by -5. 

# Mining Operation 
To Mine we need Mining Laser installed, we can get one in engineering bay on Zeta 9. 
On first month each year asteroid fields spawn in Zeta 9 and Void Colony. In quantity 10-100 each. It rerolls each year, if we dont mine it, someone else do. 
We can acces asteroid fields from spaceport in Zeta 9 and Void Colony under key "a". For each respective asteroid field. 
So we can embark to mine from spacepor. There is a menu:
1 Mine a little (1 mont passes, we mine 10 minerals from field)
2 Mine for several months. (will ask us how long we want to mine, each month is 10 minerals, we need cargo hold) 
3 Mine it all (we keep mining untill field is depleted, 1 leftover ore is still full mont, we will only mine untill we have space in cargo hold.)  
0- Back to Spaceport  

### New equipment: Mining Drones
In Engineering Bay on Zeta 9, only there, there are Mining Drones 10000c. They allow to mine it all in 1 month, no matter the field. They will mine it all fast and clean. We still need place in cargo. 
Mining drones do not fight. 





