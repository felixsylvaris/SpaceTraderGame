# BlackJack at Cantina
In each Cantina there is Game Table with Blackjack game as an option.  
Each time player visits new planet, we get 3 game tokens. Winning any mini game eats one token. If we win 3 times we need to move to another planet. We are too good for local scene.  

There are 3 opponents to choose from:
Skittish Tom: pass above 15, wager limit 500, entry 50
Mad Alice: pass above 18, wager limit 1000, entry 100
Lucky "Ace" Jack: pass above 17, wager limit 2000, entry 200, draws Ace of Spades as his first card from deck. 
You play one opponent at the time. You cant bet more than their limit.
We need example 500c in bank to even play Skittish Tom. 

There is deck generation. With figures and numbers. Numbers 2-10 count as value. Figures count all 10. Ace counts 1 or 11 whichever suits us. 
We can draw extra card as long as we want, but if we bust we loose the game. 
After we draw our cards we can double bet. 
AI: 21: 3 doubles, 19+:2 doubles, 17+: 1 double
If someones refuse to double we resolve the game without it. We show our cards.   
If AI bust by rng player wins. 

If we win we get our money back, and opponents money. 
If we loose we bet our bet score. 

the game sits in blackjack.py in /data/ catalogue.  




