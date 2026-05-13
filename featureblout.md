# Balance
Festival price inpact. Recode it to [low 25, mid 35, high 50] so much lower from present values 50-100. Festivals are good, too good for now. 

### Stockpiles
Planets and markets get stockpiles of good. Size of stockpile depends on price class. 
Low price = 500 mid price =300 high price =100
The starting game value is half for everyone. But make it some list in parameters, maybe will hand mod it for some spicy opprotunities. So 250/500 150/300 50/100

## Player interaction with stockpile
When we buy on planet we take away from local stockpile. There need to be a blockade limit that we cant buy more than there is. There is already info of max buy, so there will be min(money/price, cargo empty, stockpile) 
When Player sell it adds to local stockpile, with similar logic, we cant sell to exeed local stockpile limit. 

## Stockpile impact on prices
During monthly price adjustment after random walk and other festival, harvest impact, we check for stockpile. 
If present stockpile<20% of max, the price rise by 5,10,20. 
If stockpile>80% the price drops by 5/10/20 depending on good price class. 
So if palnet is starving for cinamone it will pay more. And if has too much it will drop price. 
There are still max price ,and absolute min price. 

## Production
There need to be a production cycle, ideally before price adjustment. 
Production happens during harvest on all planets where good exist. 
Production happens in quantity of 16/32/64. But if planet has production of good it produces x3 times more. 
If local Stockpile is literally 0 when we start computacion, we produce x1.5 goods. So if we drain planet completly there will be generous harvest. 
We simulate independent farmers here and random traders. 

## Consumption
If good exist on planet market it is consumed after production phase. 
The consumption rate is equal to 2/4/7. 
If Planet has Demand on that good it consumes x2 og good. 
If stockpile is at least 80% full the consumption happens at x2 rate. It stacks with default demand, so we can x4 consumption if demand consumption is overflowing. 

### Void pappers
Produce 30 Void pappers on Void Colony in 10th month. and we consume 2 on void colony and 4 on Nexus. 

---
### Future Feature (dont code yet this)
Somewhen in the future there could be extra optio ot invest in local farmland and catgirl cafes. So Player can burn money to alter local production and consumption. In exchange for some passive profit at low rate. 
So it will bever happen that we can flood or starve galaxy from goods. But not now. 





