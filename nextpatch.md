## Galaxy Random Events Blank and Impact
So far we have random newsfeed events:
```

atmospheric_events = [
    "A rogue freighter with 10,000 units of Void Pepper vanished near Nexus. No trace.",  
    "A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.",  
    "The old Void Colony governor was arrested. The new one is friendlier to black-market deals.",  
    "The jump lanes near Terra are being taxed now. Change is coming.",  
    "The galaxy feels different lately. The old routes are shifting.",  
    "A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle.",  
    "Rumors spread of a hidden cache of Mystery Crates on Agrica.",  
    "A poet in the cantina recites a ballad about the lost spice fleets of Dedl.",  
    "The stars seem brighter tonight. Maybe it's the Void Pepper.",  
    "A traveler claims to have seen a ghost ship near the edge of the system."  
]  

```

Bu they do NOTHING. Time to change it.   
We add parameter rnd_event_split=0.2  
We add the list   
event_rnd_blank  
event_rnd_impact  
blank has atmospheric events which do nothinglike: Notorious card player Cheating Jack arrested for cheating in cardgame. or Fleet Supply HQ request citizens to donate their spice good. Come to your military before military comes to you. or "Join Terra Fleet. Travel the Galaxy. Encounter new alliens. Maybe Kill them. Healthplan Provides cybernetic prostetic. Sign up NOW!"

So here comes the list of blank events, they do nothing, just show up 80% by default. Can sit in library. 

```
"Terran scientis claim that Void Peppers are remains of ancient Space Whale. Should we protect extinct  specie?",
"Corporation Pandora on Agrica claims to bioengineer local bugs to produce Void Peppers in small quantity. Side effect is making bugs smarter. So far all speciments run away into the jungle" 
"A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years."
"The old Void Colony governor was arrested. The new one is friendlier to black-market deals."
"The jump lanes near Terra are being taxed now. Change is coming."
"The galaxy feels different lately. The old routes are shifting."
"A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle."
"Rumors spread of a hidden cache of Mystery Crates on Agrica."
"A poet in the cantina recites a ballad about the lost spice fleets of Dedl."
"The stars seem brighter tonight. Maybe it's the Void Pepper."
"A traveler claims to have seen a ghost ship near the edge of the system."
"Famout player Cheating Jack arrested in Promenade's Cantina, he was cheating in card game."
"Join Terra Fleet. Travel the Galaxy. Encounter new alliens. Maybe Kill them. Healthplan Provides cybernetic prostetic. Sign up NOW!",
"Fleet Supply HQ request citizens to donate their spice good. Come to your military before military comes to you",
"Tired of nonsence News? Buy subscribtion for Infobroker news on Promenade. No fake news. Just value.",
"Another expediction lost in the jungle on Agrica, during exploration of ancient ruins, What a loss.",
"Experimental Hyperdrive Cruise Ship >>Hindenburg<< lost without trace on first comercial flight. Oh the Humanity!",
"Senat votes the bill to limit use of AI in administrative decision making. But all artificial advisor suggest against it.",
"Excentric Googolplexier Melon Tusk tells more about his plan to trade in Cinamone Futures. >> Why move the spice around, when you could earn money by trading rights to maybe existing cinamone?<< he is asking the real questoin." 

```

Now the impact news. They should consist of tanname, fluff text, and script. But the script probably needs to be stored elsewhere, and tagname is the link. For now we can keep it in libary and parameters. Maybe will get file events later. the gagname could look like evri001 (event randdom impact 001) 
You generally need to make protection stockpile needs to be in brackets 0, stockpile for good price class. And Price need to be between min and max. 

"AGRICA DROUGHT — paprika yields expected to halve next season."

(Effect: Agrica’s Paprika stockpile -200, Paprika and Agrica price +20, need stockpile 0 protection, and price below max protectoin)


"Pirates attacked Void Colony! Stockpiles ransacked!"

(Effect: Void Colony’s Void Pepper stockpile -50, Clove stockpile -100, VC Void pper price +100, Clowe Price +50)


"Void Pepper smugglers caught on Nexus! Market flooded."

(Effect: Nexus’s Void Pepper stockpile +50, Void Pepper price on Nexus -100)


"Saffron harvest on Zeta-9 exceeds expectations!"

(Effect: Zeta-9’s Saffron stockpile +50, Saffron price on Zeta-9 -50)

"TERRA CINAMONE ORCHAND WILDFIRE - local farmers watch blazes consuming cinamone trees. It smells wonderful. But at waht cost?"
(Effect: Terra cinamone stockpil -200, Price +30, stockpile 0 protection, price max protection)

"AGRICA Farmers learned to harvest cinamone substitute from local berries. But will it compte with real thing?"
(Effect: Agrica cinamone stockpile +200, Price -30, minimal price protection, max stockpile protection) 

*NEXUS Popular pop star claims Saffron is Aphrodisiac. Demand sours in result."
(Effect Nexus Saffron Stockpile -50, price +50, protection) 

" Zeta 9, biggest importer of Tummeric goes backrupt. Who will fill the niche?"
(Effect Zeta 9, Tumeric stockpile -200, Price +30) 







