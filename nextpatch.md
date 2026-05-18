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

*0)* is a key of choice to go back. But .md knows better. 

### 2) Shop
We can buy some upgrades for out character, Character sheets stays pernament over game. Including other expeditions or character story. Each equipment could be bouht only once. 
1) Guns 1000c (Power +1)
2) Body Armor 2000c (Power +1, Health +2)
3) Med Kit 2000c (Medicine +2, Science +1)
4) ScoutDrone 3000c (Perception +3)
5) Hire Bodyguard 5000k (Power+3, Health +3, Agility +1, Perception+1)
6) Jet Pack 2000c (Agility +2)
0) Let me out.

Shop stays open, mission or not.  
Upgrades are pernament on our charaacter sheet, so it should sit in parameters, and could be used among missions, and also personall story one day. 

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

# Adventure Easy Job
We need easyjobtoken to start it. 
We need 5000c or more in bank, otherwise msg "You need 5000c to seal the deal."
We ise our token. 
We generete exphp=[health,health] exphp[0] is temp health, and is quite important if it reach 0, we yeet out of mission, but we are still alive, maybe. exphp[1] is max hp, probably useless. But maybe we use max hp to limit healing. But exphp[0] is generally used.

We copy our character sheet, and list of upgrades as temp. Maybe we will upgrade it later. 

**Adventure model:** We travel paragraphs like it was dungeon with rooms, doors, pathways. Some pathways lead to optional rooms. Many pathways have some test or req. Inside rooms there is fluff text and test for optional fluff text (background check). Some would say it is copy of DiscoElisium. 
Easy Job grapph: Get quest -> Maybe do research od city ->Meet outside city -> It is a TRAP ->Fight or run -RESOLUTION-> We bleed in the alley OR we can get goods and money.   
So linear.  

**Fluff test** sometimes we make in background stat check and show more fluff text. 

### 1.Start <ejx01>
Print: *You aggreed to meet with drug dealer Vex, who really wants to sell you 20 bags of Void Peppers for just 5000c. On Nexus it will be worth twice as much, or even more. This is one of this easy jobs, in and out, before sector security snatche you from street. And back of the planet. *
[Test if Medicine>=1] Print: *You know about attempts to produce Void Pepper substitute from local bugs on Agrica, but herding giantic bugs is not easy task. And clients are hesitant to accept experimental product. No wonder it is cheap. *
[Test if Power>=2] Print: *You are armed to the teeth, as if you plan to raid bugs' hive. You hope Vex and his gang will not scare away.*
Print: *The Vex wants to meet outside the city walls at night, far from bystraider eyes. You still have some time to kill. What you gonna do?*
1) Cantina is the place i go. <ejx01x1>
2) Ask around about the Vex guy.   <ejx01x2>
0) Back to promenade.

#### 1.1 Cantina <ejx01x1>
Print: *You drink some delicious drink, and chill out. Event without trying you learned that Vex is leader of the gang "Punkbusters", but he is too low shot, to have any stories worth telling about him.*
1) Go to meeting at night.  -> <ejx02>
0) Back to promenade

#### 1.2 Ask around <ejx01x2>
[You loose 1 temp health]
Print: *You ask around, walk around city and promenade. You get into fight with local robbers. All this to learn that Vex is leading the small gang of poser "Punkbusters", and despite pretending otherwise they mean little, and are always short of money. But they have ambition. And are tried to raid lab on bug farm for synthetic void.*
[Test if Perception>=1] Print: *You learned that Vex tries to sell synth Void regullary, but the last man who made deal with Vex disappeared, and was never seen again on Agrica.*
[Test if Agility>=1] Print: "You sneak behind someone who could be member of Punkbusters gang, they trace to Spaceport, and talk with other freighter, port logs suggest it is departing tomorrow.*
Print: *You are not sure if nosebleed was worth it.*
1) Time to seal the deal. (continue and use token) -><ejx02>
9) Too much risk, abandon mission (Promenade and use token)
0) Back to promenade

### 2. Meet the Vex <ejx02>
Print: *It is night, but lights from spaceport brighten the sky. It even look good from distance. The jungle life makes noise, and bugs crunch in reeds. Green wall smells with wetlands and rotting leaves. What a nice night. Only mosquitos bite your hands, and fly all in front your ace all the time.  
The Vex comes with the bags and his gang, there are like 5 people of them carring the boxes. They are well armed.  
- Good to see you, was thinking you would chiken out. - he started.
- I just came here for the drugs. - You want to have this over as soon as possible.
- Ah yes the trade, you see, i need money, and i get better deal how to ship the goods out of planet without little helper. - his crew unholster guns and point at you.
- Give me the money and fuck off before i blast you. - this escaleted quickly, it is no longer a drug trade, but robbery. You should call the police, except it is hard to explain the drugs.
What you gonna do now?
1) Ok, ok take the money, no trouble. (hand over 5000c) <ejx02x01>
2) Run for the money. (attempt exit) <ejx02x02>
3) Over my dead body (fight) <ejx02x03>

#### 2.1 You loose some <ejx02x01>
Print: *You hand over money to Vex. What a stupid outcome. You wonder if you could avoid this. Sometimes the only way to win is to not play. You go back to spaceport. At least you still can afford rest in cantina.*
-> Back to promenade. 

#### 2.2 Jungle run <ejx02x02>
Print: * You run thought jungle as your life depends on it. Good thing you dont have drugs to carry and worry about.*
[Take 5-agility temp hp wounds] 
Print: *They shot and you, and you take the hit. This looks bad. *
[Test if Medicine>=1, if yes heal Medicine wounds] Print: *You take some wounds, but you have seen worse, you patch yourself with fast solid foam and fake skin. The pain is agonizing, but you will not bleed out in the woods.*

[If hp>0] Print: *You Escaped. What a night. But you still have cash and your life. Never again.* 
-> back to promenade <end of mission>
[if hp <=0] Print: *You tried your best but it wasnt enought. The catched you. And got all they wanted.* 
-> Sad ending <ej05>

#### 2.3 Law of the jungle <ejx02x03>
Print *Anyway, you started blasting. Crunched behind fallen tree trunk you shot your laser pistol at Punkbusters.*
[If bodyguard=True] Print *Your hired mercenary murmurs "It always ends like this, never trust criminals." But beside complains, he pulls his minigang from under trenchcoat, and start raining fire over the jungle, scaring off local wildlife.* 

[If power>=2, loose max(4-power,0) hp] Print: *You put some good fight, they warent expecting such resitance. Maybe outgunned but never outmatched. Vex and his punk got busted tonight.* 
-> Upper Hand <ejx03>

[If power<2, lose 3 health] Print: *You tried, you failed again. Too many guns, too many enemies, you never asked for this. Soon you fall in the mud, wondering if this is the end of your journey. At best you loose your money. Maybe even life.*
->sad ending <ej05>

### 3. Upper hand <ejx03>
Print: *You ware victorious. Vex thugs fall from your blaster fire. And now criminal begs for mercy. 
- Dont be stingy, i will give you drugs and all. Just trade cash and it is yours.
Now he want to trade. We Could start with that!
Vex is ready to trade now, but maybe you have other plans.*
1) Deal is the deal (get 20 Void Peppers, pay 5000c) <ejx03x01>
2) I need to cover medical expenses (get 20 Void Peppers, keep cash) <ejx03x02>
3) I am done with you (walk away without the trade) <ejx03x03>
4) You dont deserve to live (get 20 Void Peppers, kill Vex) <ejx03x04>

#### Deal is deal <ejx03x01>
Print: *You throw credits at lying Vex. - Take that, you dont deserve it.* But you got your Peppers, and soon can sell them for much more. 
[Get 20 Void Peppers, pay 5000c. Back to Promenade. End mission]

#### Medical cost <ejx03x02>
Print: *- Now you are talking? You tried to kill me you madman. I should take your life, but Peppers are enought this time. If you ever cross me again, i would not show mercy. * You pack the drugs and walk away.*
[Get 20 Void Peppers, back to promenade, end mission]

#### I never asked for this <ejx03x03>
Print: *After all this effort you no longer feel like life of criminal drug lord is for you. You leave vex and his drugs bleeding in the jungle. Maybe bugs will eat him. One way or another, he is not your problem anymore.*

#### No lose ends <ejx03x04>
Print: * - Look who got busted, Punk - You mock bleeding Vex waving your laser pistol. - Now you want to talk? So listen. I need drugs. I need money. I dont need you. Nobody betrayes me. You bring it upon yourself. I am the sword  of justice. - You kill the sucker with cold blood. Now drugs are all yours. Better get out jungle, before someone comes to ask quesitions about corpses and shoting.*
[Get 20 Void peppers, back to promenade, vex dead, no money lost,  end mission]

### 5. Bleeding Out <ej05>
Print: *You lose your credits. Your blood. Your dignity. And dont even made drug deal. What a waste of time. You slowly crawled back to spaceport. Where bartender finds you, at least you get free drink and ice pack. *
[lose 5000c, end of mission]
We only lose 5000c in whole mission once one way or another. Bleeding out should should be place where we lose money if we fail run or fight aproach. There is also handle cash but it should not lead to bleed out. 


### End notes:
.md sometimes knows better with numeration and i generally want 0) as back to promenade there could be 9) to exit and also abandon mission completly. 
Fix grammar and spelling like loose lose ends somewhere. 
You can expand fluff text to make it richer, more detailed, and more gritty cyberpunk night run. 
We only move 5000c in easy job mission, 5000k is mistake (should be 5000c) 























