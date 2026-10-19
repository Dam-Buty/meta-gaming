# Lore

Poursuivis par la garde pour une rixe dans une taverne (qui n'était pas du tout leur faute !) nos deux aventuriers se glissent dans une chatière et s'engoufrent dans les Catacombes de Paris. Trouveront-ils la sortie ?

# Plan des catacombes

```
##################   #########                               
#     E          #####       #                               
#                #   # 1     #   ############                
##################   #       #   #          #       #######  
                     #       #####    2     #########  $  #  
                     #       #   #          #       #######  
                     #########   ############                
                                      #                      
                                      #                      
                                   ##########                
                 ############      #        #                
                 #          #      #    3   #    ############
                 #       5  ########        ######     4    #
                 #          #      #        #    #          #
                 ############      ##########    ############
                       #                #                     
                       #                #                     
                       #             #######                        
                   ###########       #  $$ #                  
                   #    *    #       #######                        
                   ###########              
```


E: Entrée
1: 1 rat (facile à battre)
2: 2 rats
$: Récompense : arme plus puissante
3: 1 slime (difficile sans l'arme plus puissante, faisable avec)
4: 2 slimes (impossible sans l'arme plus puissante, facile avec l'armure plus puissante)
$$: Récompense : armure plus puissante
5: 1 Boss Difficile stuffé mais faisable
*: Sortie

Plan compréhensible pour un LLM :
E=>1
1=>2
2=>$
2=>3
3=>4
3=>$$
3=>5
5=>*

# Mécaniques :

ATK - DEF - HP

Dégats = ATK(attaquant) + Bonus d'arme - DEF(défenseur) - Bonus d'armure
Le défenseur a <Bonus d'armure>% de chance d'esquiver

Tour de jeu : héros attaquent chacun son tour, puis les monstres un par un puis retour aux héros


