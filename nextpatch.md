# Industrial Goods

*New Goods:* 
- Minerals
- Alloys
- Weapons
- Soybeans
- Medicine
- Robots   


Industrial Goods have no harvest, are produced every month.
Industrial goods stockpiles 100small, 300 mid, 500 large
Industrial goods price spread 5/10/15
Price range 30% defaut min. 300% defaut max. 


## Parameter table 

Good ; Planets (P-production here) ; Stockpile ; Price ; Price Class

Minerals; Void Colony (P), Zeta9 ; 500; 80c low
Alloys; Zeta9 (P), Terra, Nexus; 300; 120c mid
Weapons; Terra(P), Void Colony, Agri; 100; 200c High
Soybeans; Agri(P), Zeta9, Nexus; 500, 60c Low
Medicine; Nexus(P), Void Colony, Terra, 100, 300c High
Robots; Terra(P), Void Colony, Zeta9, Agri, 300, 160c High

Parameter default table: Price in table is default price. Stockpile in table is half max stockpile. 

#### Starting Game Set Up
Stockpile is (Random(25%,75%)of max stockpile + table stockpile)/2
Price is (Random(min, 200% default) + parameter table)/2
Logic: We take random state of good add parameter table value and avg from that. So i can mod starting state a little, but also there is some randomness. 

## Consumption
If good exists on planet is is consumed. 
-1 Medicine, Weapons
-2 Alloys
-4 Minerals, Soybeans

If stockpile below 20% consumption /2 up, but at least 1. 
If stockpile above 80% consumption *2. 

### Price stockpile influence
If price is 20% stockpile or below, price change UP by 5/10/20 a month depending on price class. 
If price is 80% or above, price change DOWN by  5/10/20 a month. 


## Production
Medicine +2 Only Nexus
Weapons +2 Only Terra
Soybeans +8 Only Agri
Minerals +8 Only Void Colony
Alloys +4 Only Zeta 9
Robots +4 Only Terra

If minerals stockpile > 50%, production of alloys *2
If alloys  stockpile > 50%, production of weapons *2
If weapons  stockpile > 50%, production of soybeans *2 (kill more bugs to chopchop forrest)
If robots stockpile>50%, production of soybeans *2
If robots stockpile>50%, production of minerals *2
If robots stockpile>50%, production of alloys *2




