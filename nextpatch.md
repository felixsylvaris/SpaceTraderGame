# If you quit you cant get back
Rekey 0 as universal go back key. If there is conflick we will look for some other keys. 
make "q" literally quit game key.
Since 0 back ->0 quite game, could be sad trader without the save. 
Sometimes 9 key is go back, so make it 0

# Randomize game start
Keep starting price/stockpile table in parameters for edit. 
But at game start (only once with new game) perform randomize price and stockpile action. 
For each planet and each good:
stockpile is  (random(25% stockpile, 75% stockpile)+parameter stockpile)/2 
Price is (random(minimal price, 2x default price)+parameter price)/2
With price and stockpile we need to do legality check, like stockpile cant be negative, or about max stockpile. Price needs to be in 30%,300% default price. 
The idea is that we have random element then add starting parameter from the table. And then we take mean of that. So there will be randomness, but also default setup matters. 


# Fleet Supply Depo
On Terra Promenade new location dropped. Fleet Supply Depo keybind "s". In is only there, unique location. 
It buys everything on fixed prices, has no stockpile, if it buys it disappears from game. 
The prices are min price + buy spread(from vendors) +5c. So we can buy goods on lowest price possible in galaxy, ship it here and get some profit. 
Cinamone is special, since it is produced on Terra so we only need to lorry it from farmland. Somone has to do it. So depo price 21 (max vendor buy is 20) 
If galaxy ever floods in spice, we can dump it into fleet. 
The fleeddepo price table should be an object in parameters. Maybe i will alter it later. 
Cinnamon	21
Turmeric	28
Paprika	31
Ginger	39
Clove	42
Vanilla	45
Cardamom	48
Allspice	56
Saffron	65
Nutmeg	62
Void Pepper	170
Only sell to depo. We cant buy from depo. 

# Songs.json and songs.py
This project is too small for us two. 
Remove reference to songs.json and creation, and all trace for it, and check, and try. 
songs.py remain, and is refernced and is place where song is load. 



