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

Independent traders happens late in month cycle. It happens late in the cycle after price and stockpile adjustment. There is parameter ind_tr_chance=0.5 which means chance to trigger intedepend trader. Independent Trader scans all pairs of planets. Each time there is 50% to skip. Could also pick half pairs from pool of planets (that could be quicker). For each planet it checks which good has highest difference on planets. It compares mean prices and dont care about sell/buy. And for that good it performs a trade according to the stockpile. it goes like (high price) 10/20/40 (low price). So Cinamone is 40units void peppers is 10. This need to be in parameters.  Independent trader cant negative stockpile, or overstockpile. Of course trader takes from low price planet, and moves to high price planet. Trader will take max possible from low price, even if at end journey there is no space.
Independent trader operation couse price rise by +5 on low side, and price drop on high side (destination) by -5. 



