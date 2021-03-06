Procuratie
############


Doel
======
Verscheidene functionarissen van het museum mogen bestellingen of opdrachten plaatsen voor een beperkt doel (kostenplaats) en bedrag. Bij overschrijding van het maximale bedrag moet een hogere functionaris accoorderen. Het kan ook zijn, dat het bedrag ook de procuratielimiet van die hogere functionaris overstijgt en dan moet er een nog hogere functionaris accoorderen.


Werkwijze OpenERP
===================
Bepaalde gebruikers kunnen inkoop-offertes aanmaken. Als de offerte is voltooid, wordt deze bevestigd en onstaat een inkooporder. Per product kan een kostenplaats worden gekozen.

Aanpassing Purchase_procuration_multi_level
===================
Per functionaris kan een procuratieregel worden gemaakt met een limiet en een kostenplaats. Voor sommige functionarissen zal er een aantal regels nodig zijn. Per regel wordt aangegeven welke manager bij overschrijding van de limiet kan worden aangesproken.

De inkoop-offertes krijgen nu als de procuratielimiet wordt overschreden de een status wacht op bevestiging. Pas als een bovengeschikte functionaris met een voldoende hoge limiet de offerte heeft bevestigd ontstaat de inkooporder.
Functionarissen kunnen eenvoudig de te bevestigen offertes selecteren.


Inrichten
=============

********************
Procuratielimieten
********************
Definieer de limieten. Deze staan in een aparte tabel, zodat ze eenvoudig kunnen worden opgetrokken.
Ga naar Instellingen / Procuratielimieten en voer de limieten in. 

Bijvoorbeeld:

+------------------------+------------------------------------------------+
|500,00                  |standaard                                       |
+------------------------+------------------------------------------------+
|2500,00                 |opdrachten, uitvoeringsgerelateerd              |
+------------------------+------------------------------------------------+
|5000,00                 |inkopen                                         |
+------------------------+------------------------------------------------+
|5000,00                 |investeringen                                   |
+------------------------+------------------------------------------------+
|5000,00                 |opdrachten, projectgerelateerd                  |
+------------------------+------------------------------------------------+
|10000,00                |opdrachten afdelingshoofd,uitvoeringsgerelateerd|   
+------------------------+------------------------------------------------+
|100000,00               |volledige bevoegdheid                           |
+------------------------+------------------------------------------------+
|10000000,00             |ongelimiteerd                                   |
+------------------------+------------------------------------------------+


*************************   
Gebruikersprocuratie
*************************
Voer per gebruiker voor elke gewenste kostenplaats een regel in.
Ga naar Instellingen / Gebruikersprocuratie en voer de regels in. 

Werk top-down, eerst de functionaris met de hoogste procuratie, in dat geval wordt geen manager ingevoerd. Voor elke andere regel wordt een manager verlangd en er wordt gecontroleerd of die een hogere procuratielimiet heeft voor dezelfde kostenplaats.

Bijvoorbeeld:
 
+------------------------+---------+------------------------+----------+------------+
|Raad van t              |Projecten|Ongelimiteerd           |10.000.000|            |    
+------------------------+---------+------------------------+----------+------------+
|Directeur               |Projecten|Voll. bevoegdheid       |100.000   |Raad van t  |      
+------------------------+---------+------------------------+----------+------------+
|Piet                    |Projecten|Opdr. proj.gerelateerd  |5.000     |Directeur   |                     
+------------------------+---------+------------------------+----------+------------+
|Jan                     |Projecten|Opdr. proj.gerelateerd  |5.000     |Directeur   |
+------------------------+---------+------------------------+----------+------------+
|Raad van t              |Jaarplan |Ongelimiteerd           |10.000.000|            |
+------------------------+---------+------------------------+----------+------------+
|Directeur               |Jaarplan |Voll. bevoegdheid       |  100.000 |Raad van t  | 
+------------------------+---------+------------------------+----------+------------+
|Afd. hoofd              |Jaarplan |Afd.hoofd, Opdr. uitv.ge|10.000    |Directeur   |         
+------------------------+---------+------------------------+----------+------------+
|Sec.hoofd J             |Jaarplan |Opdr. uitv.gerelateerd  |2.500     | Afd. hoofd |       
+------------------------+---------+------------------------+----------+------------+
|Medew. 1                |Jaarplan |Standaard               |500       |Sec. hoofd  | 
+------------------------+---------+------------------------+----------+------------+





Inkopen
===========

***********
Offerte
***********
Ga naar Inkoop/offertes (of /inkooporders) klik [Aanmaken]
In afwijking op standaard OpenERP wordt de kostenplaats per order bepaald. De gebruiker kan alleen kiezen uit de kostenplaatsen, waarvoor hij procuratie heeft.
Nadat de orderregels zijn ingevoerd kan de leverancier eerst om een offerte worden gevraagd, waarna de offerte in het systeem kan worden aangepast. 
Als de offerte vaststaat kan deze worden bevestigd: klik [Order goedkeuren].

Nu worden de procuratieregels toegepast.
De offerte wordt een inkooporder tenzij de gebruiker onvoldoende procuratie heeft. In dat geval bepaalt het programma wie de hogere in lijn is en de offerte verschijnt in diens lijstje 'goed te keuren'. Bij afwezigheid kan ook diens manager de offerte goedkeuren.

**************
Autorisatie
**************

Tabellen
Nieuw
Res_procuration_limit
Res_procuration_limit_user
Purchase_approval

Aangepast
Res_users
Purchase_order
Purchase_order_line

Groepen
Nieuw
Procuration_manager

Aangepast
Purchase_user
   
   
