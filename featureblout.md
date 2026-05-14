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

