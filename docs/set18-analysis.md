# Set 18 Enchanted Wilds: units and traits

Set 18 went live on August 25, 2026 with patch 18.1. A balance patch landed on September 1 and patch 18.2 is due September 10. It is also the first set on the Unreal engine. Everything below comes from Riot's own game files (Community Dragon, live patch) plus the live meta sources wired into the tracker. Regenerate the tables with `python scripts/build_analysis_tables.py` after a patch.

## The shape of the set

- 65 shop units: 14 one-costs, 13 two-costs, 14 three-costs, 14 four-costs, 10 five-costs.
- 36 traits: 13 origins (counting Rival), 12 classes, 11 unique single-unit traits. Eclipse is a hidden thirteenth origin effect that turns on at Solar 3 plus Lunar 3.
- 20 emblems. 8 need a Spatula (Blackthorn, Blossom, Elderwood, Fae, Inferno, Lunar, Primal, Sprykin), 8 need a Frying Pan (Brawler, Executioner, Hunter, Invoker, Rapidfire, Ravager, Spellweaver, Vanguard), and 4 only drop from augments, Tome of Traits or carousel (Coven, Defender, Flora Fatalis, Juggernaut).
- No emblem at all for Riftbeast, Solar, Adaptor and Summoner. You can only push those traits with bodies.
- Wisps replace charms: a single-use buy in the rightmost shop slot every other shop. Blossom is the trait that scales Wisps, so Blossom boards are also economy boards.

## How breakpoints read

Each trait lists breakpoints as count then tier. Bronze is the first tier, then silver, gold, and prismatic. A unique trait is on as soon as its one unit is on the board. The planner and the tracker use the same tiers, so "Blossom 7 gold" means the same thing everywhere.

## Origins

**Blossom (3 / 5 / 7 / 9 / 11, prismatic at 11).** Karma, Yorick, Yunara, Master Yi, Ahri, Sett, Ashe, plus Lux. Blossom champions gain AD, AP and 10% health. The breakpoints are about Wisps: upgraded Wisps at 3, Wisps in every shop at 5, gold refund at 7, two Wisps per round at 9. It has eight bodies, so 7 is realistic with an emblem and 9 needs Lux plus an emblem. In the live meta Blossom is the spine of the Master Yi Adaptor board, the best-placing common comp right now.

**Elderwood (3 / 5 / 7 / 9 / 11, prismatic at 11).** Ornn, Xayah, Alistar, LeBlanc, Hecarim, Ezreal, Gnar, plus Lux. Elderwood does not buff stats; it gives you placeable plants. A Stonebark Tree and a Lifebloom at 3, a second tree at 5, the Deepwood Protector at 7, plants star up at 9 and 11. Seven bodies plus Lux plus a craftable emblem makes 9 reachable, and the data shows Elderwood 5 boards placing near 1 when someone hits it. Treat it as a tank-line trait: the plants take aggro so the Ezreal or Xayah carry can work.

**Riftbeast (3 / 5 / 7 / 10).** Cinderling, Pebbles, Gromp, Murkwolf, Scuttlecrab, Krug, Mama Beak, Sentinel, Brambleback, Elder Dragon. The Alpha Mark at 3 gives one Riftbeast its personal buff. At 5 your shop gets overrun with Riftbeasts every few combats, which makes the reroll version self-feeding. At 7 they grow every 5 seconds in combat. At 10 you get two extra team slots. Elder Dragon takes two slots but counts as three Riftbeasts, so 10 means Elder Dragon plus seven others. There is no emblem, so 10 is a level 9 to 10 project. The Chinese Master+ data shows a Riftbeast 3 Elder Dragon board as the most played comp on that server.

**Coven (3 / 4 / 5 / 7).** Camille, Caitlyn, Elise, Cassiopeia, Morgana, plus Lux. Coven is an economy loop: kills and lost fights give Essence, and you cash Essence for rewards. Only five natural bodies, so 7 needs Lux and an emblem, and the emblem is not craftable. Play it as a 3 or 4 that pays for your real board.

**Sprykin (3 / 5 / 7).** Kobuko, Veigar, Teemo, Rammus, Tristana, Gnar. You get a Big Furry Friend and pick a Rider by dropping a Sprykin on it. The Rider gets health and attack speed; at 5 and 7 half or all of the friend's ability spreads to your Sprykins. Six bodies plus a craftable emblem makes 7 a real option, and the Sprykin Veigar reroll board is one of the better-placing lines this week.

**Blackthorn (2 / 4 / 6).** Rek'Sai, Veigar, Warwick, Azir, Malphite, plus Lux. Before combat the unit on the Blackthorn hex is sacrificed and your team gains health; Blackthorn units get extra stats based on what you fed them. Five bodies plus Lux plus a Spatula emblem reaches 6. Note the cdragon files still call it Blackthorn while some early guides say Eldritch; the in-game name is Blackthorn.

**Inferno (2 / 3 / 5 / 7).** Akali, Varus, Shen, Amumu, Kennen, plus Lux. Inferno damage burns and wounds. The economy hook starts at 3: after combat, shop slots without an Inferno unit ignite and roll one cost tier higher. Five bodies, Lux, and a Spatula emblem give you 7. The Ezreal Draven board that tops the win-rate table sits on Inferno 3 for that shop upgrade.

**Solar (3 only, gold at 3).** Leona, Kayle, Sejuani, plus Lux. Solar is a flat gold trait with exactly three natural bodies and no emblem. Your team gets a max-health shield and bonus magic damage, and every unique 3-star champion makes it bigger. At 3, 5 and 8 three-stars you unlock attack speed and resists, true damage, and periodic ascension to 4-star. That makes Solar the reroll-lord origin: it rewards boards that three-star many cheap units. Pair Solar 3 with Lunar 3 for Eclipse, which kills the lowest-health enemy after 10 seconds and repeats every 3.5 seconds.

**Lunar (2 / 3 / 4 / 5).** Diana, Aphelios, Alune, plus Lux. Lunar champions and their neighbors gain attack speed and AP; Lunar units get double. Only three bodies, so Lunar 4 and 5 need Lux and the Spatula emblem. It is mostly played for the Aphelios carry and for Eclipse.

**Fae (2 / 4).** Rakan, Xayah, Tristana, Lillia, plus Lux. Your damage, healing and shielding attracts Pixies that give Fae units AD and AP and a heal when low. At 4 you start getting Golden Pixies for gold after seven Pixies. Four bodies and a Spatula emblem makes 4 easy. The Tristana Rengar board (Fae Hunter) is a strong low-sample line.

**Primal (2 / 4).** Vi, Nidalee, Sivir, plus Lux. Primal is a choice: pick one of four Primal Blessings at 2 and a second at 4. Three bodies plus Lux or the Spatula emblem for 4. Nidalee and Sivir are both 4-costs so Primal 4 is a late-game commitment.

**Flora Fatalis (1 / 2, gold at 2).** Fiddlesticks and Soraka. A two-unit trait: at 1 they gain mana on takedown, at 2 takedowns also heal your lowest ally. The emblem exists but is not craftable. The most played comp in the world right now is a Flora Fatalis 2 board around Malphite, Soraka and Zyra, so this small trait is carrying the meta on its back.

**Rival (1 / 2).** Kha'Zix and Rengar. At 1 Rival, only one can be fielded and it collects takedowns. Kha'Zix evolves with takedowns and permanently picks Executioner, Rapidfire, Ravager or Spellweaver. Rengar pays gold every few takedowns and gives team AD after enough. At 2 both can be fielded and they buff each other. The planner has a toggle to treat Kha'Zix as evolved.

## Classes

**Adaptor (2 / 3 / 4).** Akali, Gromp, Kog'Maw, Master Yi, Nidalee. Their abilities change form depending on whether AD or AP is higher, and they gain more of whichever is higher. No emblem. Adaptor 3 is the engine of the Master Yi board, and the tracker shows Adaptor 3 boards placing around 2.3 in Master+.

**Brawler (2 / 4 / 6).** Kobuko, Rek'Sai, Alistar, Krug, Sett, Gnar. Team max health, Brawlers get a lot more. Frying Pan emblem. The most common emblem in the Master Yi line is Brawler, usually on Master Yi himself.

**Defender (2 / 4 / 6).** Leona, Ornn, Shen, Fiddlesticks, Rammus, Lillia. Team armor and magic resist, Defenders get much more. Emblem exists but is not craftable.

**Executioner (2 / 3 / 4).** Yunara, Azir, Ezreal, Soraka, Kennen. Precision plus crit chance at 2, a bleed at 3, a bigger bleed at 4. Frying Pan emblem. Executioner 3 is the hidden reason the Malphite Soraka board works: Azir, Soraka and Kennen all carry it.

**Hunter (2 / 3 / 4 / 5).** Cinderling, Caitlyn, Tristana, Sivir, Ashe. Flat AD that grows, plus damage amp when a Hunter holds the same target for 4 seconds. Frying Pan emblem.

**Invoker (2 / 3 / 4 / 5).** Pebbles, Teemo, Kog'Maw, Sentinel, Morgana. Team mana regen, Invokers get more. Frying Pan emblem. The Ahri Morgana board uses Invoker 4 to make Ahri cast fast.

**Juggernaut (2 / 4 / 6).** Rakan, Yorick, Scuttlecrab, Sejuani, Vi, Amumu, Maokai. Team durability, Juggernauts get more. Seven bodies, emblem not craftable. Juggernaut 2 is on almost every board because Yorick and Rakan are the default one-cost frontline.

**Rapidfire (2 / 3 / 4 / 5).** Varus, Xayah, Kayle, Mama Beak, Aphelios. Team attack speed plus stacking attack speed per attack on Rapidfire units. Frying Pan emblem. This is the Aphelios and Kayle class.

**Ravager (2 / 4 / 6).** Akali, Camille, Murkwolf, Warwick, Diana, Brambleback. Omnivamp plus bonus damage that doubles on targets under half health. Frying Pan emblem.

**Spellweaver (2 / 4 / 6).** Karma, Veigar, LeBlanc, Cassiopeia, Fiddlesticks, Ahri, Alune. Team AP, Spellweavers get more and stack AP on every cast. Seven bodies and a Frying Pan emblem. It is the AP flex class.

**Summoner (2 / 3).** Yorick, Azir, Mama Beak, Zyra. Each Summoner's summons get a specific buff; at 3 every effect is 50% stronger. No emblem, but four bodies makes 3 easy, and Summoner 3 boards are placing around 2.2 when they show up.

**Vanguard (2 / 4 / 6).** Rakan, Elise, Diana, Hecarim, Sentinel, Taric. A max-health shield at combat start and again under half health; durability while shielded at 6. Frying Pan emblem.

## Unique traits

- Avatar (Lux, 5-cost). Lux arrives as one of nine origins: Blackthorn, Blossom, Coven, Elderwood, Fae, Inferno, Lunar, Primal, Solar. Her chosen origin counts twice, so Lux is worth two bodies for that trait, and holding her transforms every other Lux in your shop to the same origin. This is the single most important fact for the emblem planner: Lux plus one emblem is a plus three.
- Apex Predator (Elder Dragon, 5-cost). Takes two slots, adds two to Riftbeast.
- Attuned (Alune, 5-cost). Cycles the moon each cast; your team alternates between durability and damage amp.
- Bounty Seeker (Draven, 5-cost). Pick a bounty, complete it with Draven, choose another.
- Caustic (Kog'Maw, 3-cost). His damage shreds and sunders for 4 seconds. Kog'Maw is the most common 3-cost in the game because of this.
- Emerald Aspect (Taric, 5-cost). Drag an ally onto Taric to pair them for bonuses from his ability.
- Greenfather (Ivern, 5-cost). Seeds grow hexes that buff whoever stands there.
- Monolith (Malphite, 4-cost). Armor and magic resist per enemy targeting him. The premier main tank of the set.
- Old Growth (Maokai, 5-cost). Permanent max health whenever a nearby enemy dies.
- Thornmaiden (Zyra, 4-cost). Team durability, more while her plants live.
- Eclipse (hidden). Active at Solar 3 and Lunar 3.

## Units that connect traits

Fourteen units carry three traits, and they are the glue of every flex board: Akali, Rakan, Veigar, Xayah, Yorick, Azir, Diana, Fiddlesticks, Kog'Maw, Mama Beak, Tristana, Sentinel, Alune, Gnar. Rakan and Yorick are one-costs that each turn on Juggernaut with a second trait, which is why they are on almost every early board.

Only five origin and class pairs repeat across two units (Blossom Spellweaver, Sprykin Brawler, Riftbeast Invoker, Elderwood Brawler, Riftbeast Ravager). Everything else is a unique combination, so most units are the only bridge between their two traits. When the planner suggests an odd unit, it is usually because that unit is the only bridge.

## Emblem strategy in one paragraph

An emblem is worth the most on a unit that does not already have the trait and that you want to play anyway. The biggest jumps are Lux plus emblem (plus three), Elder Dragon for Riftbeast (plus three for two slots), and any Spatula emblem on a vertical with eight or more bodies (Blossom, Elderwood). Traits with no emblem (Riftbeast, Solar, Adaptor, Summoner) cannot be forced, so plan bodies for them first and use emblems for the traits around them. The current Master+ data has Juggernaut, Rapidfire and Brawler as the most commonly held emblems, and Brawler on Master Yi as the most common single emblem placement.

## What is climbing right now

The tracker's dashboard has the live numbers. The snapshot tables below were generated at build time and cover the global Master+ sample, the region leaders, and the China Master+ groups. The short version on patch 18.1d:

- Flora Fatalis Malphite Soraka is the most played board everywhere and is still rising, but it places mid-table. It is a safe top-4 line, not a win line.
- Blossom Master Yi (Adaptor 3 with Kog'Maw, Vi, Rengar, Nidalee) is the best-placing common comp and the one Chinese Master+ players push to Brawler 4.
- Solar Kayle Xayah is popular but slipping; the Solar Akali Camille reroll version is the one gaining share.
- China Master+ favors Elderwood 3 Solar 3 Kayle and Executioner Summoner Malphite over the Nidalee Sivir Primal board that is common in the West.
- Riftbeast comes in two forms: the reroll Krug Pebbles version and the Elder Dragon 5-cost version. The reroll version places better in Master+.

## Trait table

| Trait | Kind | Breakpoints | Units | Emblem |
|---|---|---|---|---|
| Blackthorn | origin | 2 bronze / 4 silver / 6 gold | Rek'Sai (1), Veigar (1), Warwick (2), Azir (3), Malphite (4), Lux (5, counts twice) | Spatula + Giant's Belt |
| Blossom | origin | 3 bronze / 5 silver / 7 gold / 9 gold / 11 prismatic | Karma (1), Yorick (1), Yunara (2), Master Yi (3), Ahri (4), Sett (4), Ashe (5), Lux (5, counts twice) | Spatula + Needlessly Large Rod |
| Coven | origin | 3 bronze / 4 silver / 5 silver / 7 gold | Camille (1), Caitlyn (2), Elise (2), Cassiopeia (3), Morgana (4), Lux (5, counts twice) | not craftable |
| Elderwood | origin | 3 bronze / 5 silver / 7 gold / 9 gold / 11 prismatic | Ornn (1), Xayah (1), Alistar (2), LeBlanc (2), Hecarim (3), Ezreal (4), Gnar (5), Lux (5, counts twice) | Spatula + Chain Vest |
| Fae | origin | 2 bronze / 4 gold | Rakan (1), Xayah (1), Tristana (3), Lillia (4), Lux (5, counts twice) | Spatula + B.F. Sword |
| Flora Fatalis | origin | 1 bronze / 2 gold | Fiddlesticks (3), Soraka (4) | not craftable |
| Inferno | origin | 2 bronze / 3 silver / 5 gold / 7 gold | Akali (1), Varus (1), Shen (2), Amumu (4), Kennen (5), Lux (5, counts twice) | Spatula + Recurve Bow |
| Lunar | origin | 2 bronze / 3 silver / 4 silver / 5 gold | Diana (3), Aphelios (4), Alune (5), Lux (5, counts twice) | Spatula + Tear Of The Goddess |
| Primal | origin | 2 bronze / 4 gold | Vi (3), Nidalee (4), Sivir (4), Lux (5, counts twice) | Spatula + Sparring Gloves |
| Riftbeast | origin | 3 bronze / 5 silver / 7 gold / 10 gold | Cinderling (1), Pebbles (1), Gromp (2), Murkwolf (2), Scuttlecrab (2), Krug (3), Mama Beak (3), Brambleback (4), Sentinel (4), Elder Dragon (5); Elder Dragon adds +2 | none |
| Rival | origin | 1 gold / 1 bronze / 2 gold | Kha'Zix (3), Rengar (3) | none |
| Solar | origin | 3 gold | Leona (1), Kayle (2), Sejuani (2), Lux (5, counts twice) | none |
| Sprykin | origin | 3 bronze / 5 silver / 7 gold | Kobuko (1), Veigar (1), Teemo (2), Rammus (3), Tristana (3), Gnar (5) | Spatula + Negatron Cloak |
| Adaptor | class | 2 bronze / 3 silver / 4 gold | Akali (1), Gromp (2), Kog'Maw (3), Master Yi (3), Nidalee (4) | none |
| Brawler | class | 2 bronze / 4 silver / 6 gold | Kobuko (1), Rek'Sai (1), Alistar (2), Krug (3), Sett (4), Gnar (5) | Frying Pan + Giant's Belt |
| Defender | class | 2 bronze / 4 silver / 6 gold | Leona (1), Ornn (1), Shen (2), Fiddlesticks (3), Rammus (3), Lillia (4) | not craftable |
| Executioner | class | 2 bronze / 3 silver / 4 gold | Yunara (2), Azir (3), Ezreal (4), Soraka (4), Kennen (5) | Frying Pan + Sparring Gloves |
| Hunter | class | 2 bronze / 3 silver / 4 silver / 5 gold | Cinderling (1), Caitlyn (2), Tristana (3), Sivir (4), Ashe (5) | Frying Pan + B.F. Sword |
| Invoker | class | 2 bronze / 3 silver / 4 silver / 5 gold | Pebbles (1), Teemo (2), Kog'Maw (3), Morgana (4), Sentinel (4) | Frying Pan + Tear Of The Goddess |
| Juggernaut | class | 2 bronze / 4 silver / 6 gold | Rakan (1), Yorick (1), Scuttlecrab (2), Sejuani (2), Vi (3), Amumu (4), Maokai (5) | not craftable |
| Rapidfire | class | 2 bronze / 3 silver / 4 silver / 5 gold | Varus (1), Xayah (1), Kayle (2), Mama Beak (3), Aphelios (4) | Frying Pan + Recurve Bow |
| Ravager | class | 2 bronze / 4 silver / 6 gold | Akali (1), Camille (1), Murkwolf (2), Warwick (2), Diana (3), Brambleback (4) | Frying Pan + Negatron Cloak |
| Spellweaver | class | 2 bronze / 4 silver / 6 gold | Karma (1), Veigar (1), LeBlanc (2), Cassiopeia (3), Fiddlesticks (3), Ahri (4), Alune (5) | Frying Pan + Needlessly Large Rod |
| Summoner | class | 2 bronze / 3 gold | Yorick (1), Azir (3), Mama Beak (3), Zyra (4) | none |
| Vanguard | class | 2 bronze / 4 silver / 6 gold | Rakan (1), Elise (2), Diana (3), Hecarim (3), Sentinel (4), Taric (5) | Frying Pan + Chain Vest |
| Apex Predator | unique | 1 unique | Elder Dragon (5) | none |
| Attuned | unique | 1 unique | Alune (5) | none |
| Avatar | unique | 1 unique | Lux (5) | none |
| Bounty Seeker | unique | 1 unique | Draven (5) | none |
| Caustic | unique | 1 unique | Kog'Maw (3) | none |
| Eclipse | unique |  |  | none |
| Emerald Aspect | unique | 1 unique | Taric (5) | none |
| Greenfather | unique | 1 unique | Ivern (5) | none |
| Monolith | unique | 1 unique | Malphite (4) | none |
| Old Growth | unique | 1 unique | Maokai (5) | none |
| Thornmaiden | unique | 1 unique | Zyra (4) | none |

## Unit table

| Cost | Unit | Traits | Range | Mana | Ability |
|---|---|---|---|---|---|
| 1 | Akali | Inferno, Adaptor, Ravager | 1 | 0/30 | Kunai Strike: Adaptor AD: Throw a volley of kunai at the target, dealing X ADAP physical damage. If the target is Burning, deal an additional X AD damage. Adaptor AP: If the Ability ki |
| 1 | Camille | Coven, Ravager | 1 | 0/25 | Defensive Sweep: Slice the target for X ADAP physical damage and gain X Shield for X seconds. |
| 1 | Cinderling | Riftbeast, Hunter | 4 | 0/50 | Razor Leaves: Summon five razor-sharp leaves that converge on the current target, dealing a total of X ADAP physical damage and applying X% Wound and X% Burn for X seconds. Scarlet Buf |
| 1 | Karma | Blossom, Spellweaver | 4 | 0/40 | Karmic Bond: Tether the current target, dealing X AP magic damage over X seconds. Then release a burst of power around them, dealing X AP magic damage to all enemies in a X Hex radius |
| 1 | Kobuko | Sprykin, Brawler | 1 | 30/90 | Dance of Life: Restore X HPAP Health over X seconds. The next attack is replaced with a bash that deals X HPAP magic damage. |
| 1 | Leona | Solar, Defender | 1 | 40/100 | Shield Bash: Passive: Start combat with X AP bonus Armor and Magic Resist that decays over X seconds. Active: Bash the current target, dealing X Armor magic damage and Stunning them f |
| 1 | Ornn | Elderwood, Defender | 1 | 40/100 | Bellows Breath: Active: Gain X AP Shield for X seconds and deal X AP magic damage to enemies in a cone. Quest: Each player combat, Ornn stores damage blocked as Forge Power, doubled at 3 |
| 1 | Pebbles | Riftbeast, Invoker | 4 | 25/65 | Azure Laser: Begin consuming X max Mana per second and channeling a laser on the target. Each second while casting, deal X AP magic damage to them and reduce their Magic Resist by X.  |
| 1 | Rakan | Fae, Juggernaut, Vanguard | 1 | 35/105 | Entrancing Dance: Gain X AP Shield for X seconds. Then grant the ally who has dealt the most damage this combat X AP decaying Attack Speed for X seconds. |
| 1 | Rek'Sai | Blackthorn, Brawler | 1 | 40/100 | Uproot: Passive: Restore X HP Health each second, tripled for X seconds after casting. Active: Lunge out of the ground, Stunning adjacent enemies for X second and dealing X AP ma |
| 1 | Varus | Inferno, Rapidfire | 4 | 30/120 | Piercing Arrow: Wind up, then fire an arrow at the most enemies in line with the target. It deals X ADAP physical damage to enemies hit, reduced by X for each enemy it passes through (mi |
| 1 | Veigar | Blackthorn, Sprykin, Spellweaver | 4 | 0/30 | Primordial Burst: Launch a giant blast at the target that deals X AP magic damage, increased to X AP if they're below X max Health. If they die, permanently gain X% Ability Power. Current  |
| 1 | Xayah | Elderwood, Fae, Rapidfire | 4 | 0/50 | Deadly Plumage: Gain X Attack Speed for the next X attacks. These attacks are replaced with feathers that deal X AD physical damage and reduce Armor by X AP. |
| 1 | Yorick | Blossom, Juggernaut, Summoner | 1 | 50/110 | Last Rites: Passive: On death, spawn a Spirit Walker with X HP max Health which immediately taunts, forcing enemies to attack it. Active: Restore X AP Health and strike the target, d |
| 2 | Alistar | Elderwood, Brawler | 1 | 30/90 | Triumphant Roar: Roar, restoring X HPAP Health, cleansing disables, and healing the two lowest percent Health allies for X AP. Then slam the current target, dealing X AP magic damage and  |
| 2 | Caitlyn | Coven, Hunter | 4 | 0/3 | Headshot: Passive: Every third attack is replaced with a Headshot that deals X ADAP physical damage. |
| 2 | Elise | Coven, Vanguard | 1 | 20/70 | Spider Queen: Transform into a spider and gain X max Health. Attacks while in Spider Form deal X AP bonus magic damage and heal for X AP. Subsequent casts grant X decaying Attack Speed |
| 2 | Gromp | Riftbeast, Adaptor | 4 | 0/45 | Belchy Bubble: Adaptor AP: Belch a noxious bubble at the current target that explodes on the first enemy hit, dealing X AP magic damage. Enemies within a 1 hex radius of the explosion t |
| 2 | Kayle | Solar, Rapidfire | 4 | 0/0 | Solar Judgement: Passive: Kayle ascends based on her star level, granting her stacking bonuses. 1st Ascension: Attacks deal X AP bonus magic damage. 2nd Ascension: Attacks X% Shred enemie |
| 2 | LeBlanc | Elderwood, Spellweaver | 4 | 0/40 | Mirror Image: Passive: After player combat, your strongest LeBlanc has a X chance to create a copy of an ally on your board, increased by X per takedown. Active: Launch a mirror image  |
| 2 | Murkwolf | Riftbeast, Ravager | 1 | 0/40 | Rending Claws: Leap to the lowest Health enemy within X Hexes and deal X ADAP physical damage. The next X attacks gain X Attack Speed and deal X AD bonus physical damage. Grey Buff: Gai |
| 2 | Scuttlecrab | Riftbeast, Juggernaut | 1 | 40/100 | Can You Dig It?: Passive: Attacks are replaced by a dance that deals X AD physical damage to all adjacent enemies. Active: Burrow underground, gaining X Durability for X seconds and heali |
| 2 | Sejuani | Solar, Juggernaut | 1 | 40/100 | Sun's Wrath: Gain X HPAP Shield for X seconds. Then cleave in a cone, dealing X AP magic damage and strike in a line, dealing X AP magic damage to enemies hit. |
| 2 | Shen | Inferno, Defender | 1 | 30/90 | Ki Barrier: Grant X AP Shield to Shen and X AP Shield to a nearby damaged ally for X seconds. Both of their next X attacks gain X Attack Speed and deal X AP bonus magic damage. |
| 2 | Teemo | Sprykin, Invoker | 4 | 0/50 | Fungus Among Us: Throw 2 clusters of mushrooms that deal X AP magic damage to the X nearest enemies. Then hurl a giant mushroom that deals X AP magic damage to the target. Each cast has a |
| 2 | Warwick | Blackthorn, Ravager | 1 | 0/40 | Jaws of The Beast: Bite the current target, dealing X AD physical damage and healing for X AP of the damage dealt. Gain X Attack Speed for the rest of combat. |
| 2 | Yunara | Blossom, Executioner | 4 | 0/35 | Cultivation of Spirit: Dash, then launch an orb at the current target that deals X ADAP physical damage and splits, dealing X ADAP physical damage to X nearby enemies. |
| 3 | Azir | Blackthorn, Executioner, Summoner | 4 | 0/35 | Arise!: Gain X Attack Speed and summon X soldiers for the next X attacks. These attacks are replaced by commands which direct each soldier to deal X AP magic damage per attack. |
| 3 | Cassiopeia | Coven, Spellweaver | 4 | 0/30 | Noxious Blast: Poison the target and the nearest non-poisoned enemy, dealing X AP magic damage over X seconds. Poisons stack. |
| 3 | Diana | Lunar, Ravager, Vanguard | 1 | 0/40 | Pale Barrier: Gain X shield for X seconds and send out X moonlight orbs spread among enemies within 2 hexes, each dealing X AP magic damage. |
| 3 | Fiddlesticks | Flora Fatalis, Defender, Spellweaver | 1 | 30/90 | Harvest: Reduce the Magic Resist of the X nearest enemies by X. Then drain life from them over X seconds, healing for X AP Health and dealing X AP magic damage to each over the du |
| 3 | Hecarim | Elderwood, Vanguard | 1 | 30/110 | Spirit of Dread: Gain X Armor and Magic Resist for 3 seconds and restore X AP Health over the duration. Launch spectral riders at the X nearest enemies, dealing X AP magic damage and Stun |
| 3 | Kha'Zix | Rival | 1 | 0/25 | Taste Their Fear: Leap to the farthest enemy within X Hexes, dealing X AP magic damage. If they have no adjacent allies, deal X AP magic damage instead and gain X mana.{Augment.Variant.Riv |
| 3 | Kog'Maw | Caustic, Adaptor, Invoker | 4 | 15/55 | Raining Artillery: Adaptor AD: Launch acid at the target and the other nearest enemy, dealing X ADAP physical damage. Enemies below X max Health take X ADAP physical damage instead. Adaptor |
| 3 | Krug | Riftbeast, Brawler | 1 | 80/135 | Rock and Roll: Passive: On death, split into two Kruglettes with X HP Health which immediately taunt, forcing enemies to attack them. Active: Gain X AP max Health, then roll into the ta |
| 3 | Mama Beak | Riftbeast, Summoner, Rapidfire | 4 | 20/60 | Flock Family: Summon 4 untargetable Tiny Beaks nearby for X AP seconds. Whenever Mama Beak attacks, Tiny Beaks attack the same enemy, dealing X AD physical damage. Orange Buff: Dealing |
| 3 | Master Yi | Blossom, Adaptor | 1 | 0/3 | Wuju Style: Passive: Every third attack is a Double Strike. On takedown, gain a burst of movement speed. Adaptor AD: Double Strikes grant X AP stacking Attack Speed. Adaptor AP: Doub |
| 3 | Rammus | Sprykin, Defender | 1 | 30/80 | Defensive Ball Curl: Taunt, forcing enemies to attack this champion. For X seconds, gain X AP Shield and X Armor and Magic Resist. When the Shield breaks, deal X ArmorMR physical damage to en |
| 3 | Rengar | Rival | 1 | 10/50 | Savagery: Jump to the lowest percent Health enemy within X hexes and stab them, dealing X AD physical damage. Then heal for X AP, increased to up to X AP based on their missing Hea |
| 3 | Tristana | Fae, Sprykin, Hunter | 4 | 0/60 | Explosive Charge: Attach an explosive charge to the target that lasts X seconds. While active, gain infinite range and X AP Attack Speed. After the duration, the charge explodes and splits |
| 3 | Vi | Primal, Juggernaut | 1 | 0/60 | Furious Fists: Passive: On attack, restore X HP Health. Active: Unleash a primal roar, restoring X AP Health. Then gain X Attack Speed, X Durability, and is Unstoppable for X seconds. |
| 4 | Ahri | Blossom, Spellweaver | 4 | 20/100 | Spirit Bomb: Launch a spirit bomb at the location within X hexes that has the most surrounding enemies. It deals X AP magic damage to enemies in a X hex radius, reduced by X per hex a |
| 4 | Amumu | Inferno, Juggernaut | 1 | 30/140 | Tantrum: Passive: Every second, restore X APHP Health and deal X AP magic damage to enemies within X hex. Active: Deal X AP magic damage to enemies within X hexes and Stun them fo |
| 4 | Aphelios | Lunar, Rapidfire | 4 | 20/70 | Moonlight's Onslaught: Equip Severum and swipe the target X AS times over X seconds, each dealing X AD physical damage. After the onslaught finishes, fire a blast that deals X ADAP physical dam |
| 4 | Brambleback | Riftbeast, Ravager | 1 | 0/40 | Crimson Fury: Passive: When the target dies, leap at the next target, dealing X AD physical damage. Active: Gain X Attack Damage for X seconds. During this time ignore X AP Armor. Red  |
| 4 | Ezreal | Elderwood, Executioner | 4 | 0/30 | Forest's Flurry: Blink away from the current target, deal X AD physical damage to them, and gain X AP Attack Speed. Every 4th cast consumes the Attack Speed granted from Nature's Wrath an |
| 4 | Lillia | Fae, Defender | 1 | 40/140 | Lilting Lullaby: Restore X AP Health and send X butterflies at nearby enemies. Enemies hit take X AP magic damage and Sleep for X seconds. If they take X damage, they wake up and take an  |
| 4 | Malphite | Blackthorn, Monolith | 1 | 30/80 | Petrified Bark: Gain X AP Shield for X seconds and become petrified. When the shield breaks, unleash a wave of dark energy, dealing X APArmorMR magic damage to enemies within X hexes. |
| 4 | Morgana | Coven, Invoker | 2 | 0/60 | Withering Curse: Passive: Gain X Omnivamp. Active: Fire a dark blast at X nearby enemies, dealing X AP magic damage to them and cursing them for X seconds. Then, spawn a X Hex withering z |
| 4 | Nidalee | Primal, Adaptor | 1 | 0/40 | Javelin Toss: Adaptor AP: Gain X Attack Speed for the next X attacks. These attacks are replaced with javelins that deal X AP magic damage. The 3rd attack instead targets the furthest  |
| 4 | Sentinel | Riftbeast, Vanguard, Invoker | 1 | 60/150 | Azure Shockwave: Gain X APHP Shield for X seconds. Slam the ground, sending a fissure in the direction of the most enemies. Enemies hit are briefly knocked up, take X AP magic damage, and |
| 4 | Sett | Blossom, Brawler | 1 | 60/135 | Haymaker: Passive: Upon falling below X max Health the first time each combat, gain 100 mana. Active: Wind up a big punch, rapidly healing for X HPAP before dealing X HPAD physical |
| 4 | Sivir | Primal, Hunter | 4 | 0/40 | Boomerang Blade: Throw a large crossblade that deals X ADAP physical damage to the current target and bounces X times between nearby enemies, dealing X ADAP physical damage each bounce. W |
| 4 | Soraka | Flora Fatalis, Executioner | 4 | 0/30 | Starcall: Call down a star on the current target, dealing X AP magic damage. If a star has previously fallen on them, call down X additional stars that each deal X AP magic damage. |
| 4 | Zyra | Thornmaiden, Summoner | 4 | 0/45 | Rampant Growth: Spawn X plants around the battlefield that attack the nearest enemy X times. Each attack deals X AP magic damage. |
| 5 | Alune | Attuned, Lunar, Spellweaver | 4 | 0/35 | Moonfall: Rain X moonshards split among the X nearest enemies, dealing X AP magic damage each. If the moon is full, instead crash it onto the board, dealing X AP magic damage split |
| 5 | Ashe | Blossom, Hunter | 6 | 20/80 | Spirit Rift: Fire an arrow through the most enemies in a line that deals X AD physical damage, reduced by X per enemy hit (minimum X). The arrow leaves a trail for X seconds that deal |
| 5 | Draven | Bounty Seeker | 6 | 0/120 | Whirling Death: Passive: Attacks target random enemies in range and apply a bleed that deals X AD physical damage over X seconds. Every attack has a X AP chance to deal X bonus physical  |
| 5 | Elder Dragon | Apex Predator, Riftbeast | 2 | 20/60 | Heat Without Equal: Passive: Attacks deal X damage to enemies adjacent to the target. Active: Become invulnerable and fly into the air. On return, stun all enemies for X seconds, gain X Omni |
| 5 | Gnar | Elderwood, Sprykin, Brawler | 2 | 0/70 | Rage Gene: Passive: Gain X Rage per second and X Rage per attack. Active: Transform into Mega Gnar and leap into the largest group of enemies within X hexes. Then, deal X AD physica |
| 5 | Ivern | Greenfather | 3 | 50/80 | Triggerseed: Passive: Shields from this Ability can critically strike with Precision. Active: Grant X allies X AP%i:scaleDA% Shield and X Damage Amp for X seconds. Then deal X AP magi |
| 5 | Kennen | Inferno, Executioner | 2 | 0/40 | Firestorm: Charge up, gaining X Ability Power per Burning enemy. Then, gain X AP Shield for X seconds and rush through a nearby group of enemies, dealing X AP magic damage to each.  |
| 5 | Lux | Avatar (choose: Blackthorn, Blossom, Coven, Elderwood, Fae, Inferno, Lunar, Primal, Solar) | 6 | 20/70 | Final Spark: Passive: On cast, all allies that share a trait with Lux gain X AP mana. Active: Fire a laser towards the largest group of enemies that deals X AP magic damage, reduced b |
| 5 | Maokai | Old Growth, Juggernaut | 1 | 40/100 | Sow the Seeds: Passive: After every X damage blocked, a sapling jumps towards a nearby enemy and deals X HP magic damage. On death, X saplings jump out. Active: Deal X HP magic damage t |
| 5 | Taric | Emerald Aspect, Vanguard | 1 | 0/65 | Emerald Radiance: Passive: The first time Taric or his paired ally drops below X Health, unleash emerald energy from both of them, granting X HP Shield to allies within X Hexes for X secon |

## Trait overlap

Units carrying three traits: Akali (Inferno, Adaptor, Ravager), Rakan (Fae, Juggernaut, Vanguard), Veigar (Blackthorn, Sprykin, Spellweaver), Xayah (Elderwood, Fae, Rapidfire), Yorick (Blossom, Juggernaut, Summoner), Azir (Blackthorn, Executioner, Summoner), Diana (Lunar, Ravager, Vanguard), Fiddlesticks (Flora Fatalis, Defender, Spellweaver), Kog'Maw (Caustic, Adaptor, Invoker), Mama Beak (Riftbeast, Summoner, Rapidfire), Tristana (Fae, Sprykin, Hunter), Sentinel (Riftbeast, Vanguard, Invoker), Alune (Attuned, Lunar, Spellweaver), Gnar (Elderwood, Sprykin, Brawler)

Origin and class pairs that appear on more than one unit:
- Blossom + Spellweaver: Karma, Ahri
- Sprykin + Brawler: Kobuko, Gnar
- Riftbeast + Invoker: Pebbles, Sentinel
- Elderwood + Brawler: Alistar, Gnar
- Riftbeast + Ravager: Murkwolf, Brambleback

## Meta snapshot (Master+, patch 18.1d, 32,327 games, generated 2026-09-08T05:25 UTC)

| Comp | Share | Place | Top 4 | Win | 7-day change | Board |
|---|---|---|---|---|---|---|
| Flora Fatalis Malphite & Soraka | 12.5% | 4.61 | 48% | 8% | +1.3 pts | Yorick, Azir, Fiddlesticks, Amumu, Malphite, Soraka, Zyra, Kennen |
| Primal Nidalee & Sivir | 6.4% | 4.70 | 46% | 5% | +2.1 pts | Cinderling, Rek'Sai, Kog'Maw, Krug, Sentinel, Malphite, Nidalee, Sivir |
| Solar Kayle & Xayah | 5.5% | 4.48 | 51% | 18% | -1.2 pts | Leona, Ornn, Rakan, Xayah, Kayle, Sejuani, Hecarim, Aphelios |
| Blossom Master Yi & Vi | 5.3% | 3.69 | 64% | 22% | +1.2 pts | Yorick, Kog'Maw, Krug, Master Yi, Rengar, Vi, Nidalee, Sett |
| Riftbeast Sentinel & Aphelios | 4.8% | 4.74 | 44% | 9% | -0.9 pts | Diana, Hecarim, Mama Beak, Sentinel, Aphelios, Brambleback, Zyra, Taric |
| Blossom Ahri & Morgana | 3.7% | 4.60 | 48% | 9% | -0.1 pts | Karma, Pebbles, Krug, Ahri, Sentinel, Morgana, Sett, Taric |
| Solar Akali & Camille | 2.7% | 4.48 | 53% | 11% | +2.1 pts | Akali, Camille, Leona, Ornn, Varus, Kayle, Sejuani, Amumu |
| Flora Fatalis Cassiopeia & Fiddlesticks | 2.7% | 4.44 | 52% | 11% | -0.6 pts | Leona, Ornn, Shen, Cassiopeia, Fiddlesticks, Rammus, Lillia, Soraka |
| Riftbeast Krug & Pebbles | 1.6% | 4.40 | 53% | 9% | +0.2 pts | Cinderling, Pebbles, Murkwolf, Scuttlecrab, Krug, Sentinel, Brambleback, Gnar |
| Fae Tristana & Rengar | 1.3% | 4.60 | 46% | 18% | -0.1 pts | Kobuko, Rakan, Rammus, Rengar, Tristana, Vi, Lillia, Sivir |
| Sprykin Veigar & Rek'Sai | 1.3% | 4.54 | 48% | 10% | +0.0 pts | Kobuko, Rek'Sai, Veigar, Teemo, Fiddlesticks, Rammus, Sett, Gnar |
| Inferno Ezreal & Draven | 1.2% | 4.31 | 51% | 22% | -0.0 pts | Alistar, Amumu, Ezreal, Draven, Gnar, Ivern, Kennen, Maokai |
| Fae Aphelios & Lillia | 1.0% | 5.05 | 40% | 8% | +0.1 pts | Ornn, Xayah, Alistar, Diana, Hecarim, Aphelios, Lillia, Gnar |

Region leaders (highest play share inside each region):

- NA: Flora Fatalis Malphite & Soraka (13.1% of boards, place 4.86)
- EUW: Flora Fatalis Malphite & Soraka (12.4% of boards, place 4.63)
- EUNE: Flora Fatalis Malphite & Soraka (15.4% of boards, place 4.85)
- KR: Flora Fatalis Malphite & Soraka (12.7% of boards, place 4.66)
- JP: Flora Fatalis Malphite & Soraka (12.2% of boards, place 4.64)
- BR: Flora Fatalis Malphite & Soraka (12.3% of boards, place 4.61)
- LAN: Flora Fatalis Malphite & Soraka (16.3% of boards, place 3.71)
- LAS: Primal Nidalee & Sivir (8.5% of boards, place 3.90)
- OCE: Flora Fatalis Malphite & Soraka (14.8% of boards, place 4.79)
- TR: Flora Fatalis Malphite & Soraka (17.1% of boards, place 4.72)
- TW: Flora Fatalis Malphite & Soraka (4.5% of boards, place 5.71)
- VN: Flora Fatalis Malphite & Soraka (4.3% of boards, place 5.41)
- SEA: Flora Fatalis Malphite & Soraka (3.9% of boards, place 5.72)

China Master+ (Tencent, patch 16.17, 20260907):

| Comp | Games | Place | Top 4 | Win | Board |
|---|---|---|---|---|---|
| Elderwood 3 + Solar 3 (Kayle) | 178 | 2.00 | 93% | 47% | Leona, Ornn, Rakan, Xayah, Kayle, LeBlanc, Sejuani, Hecarim |
| Elderwood 3 + Solar 3 (Kayle) | 440 | 2.00 | 92% | 56% | Leona, Ornn, Rakan, Xayah, Elise, Kayle, LeBlanc, Sejuani |
| Blossom 3 + Invoker 3 (Ahri) | 130 | 2.50 | 92% | 25% | Pebbles, Krug, Ahri, Morgana, Sett, Sentinel, Alune, Ashe, Taric |
| Brawler 4 + Adaptor 3 (Master Yi) | 238 | 2.50 | 90% | 27% | Yorick, Master Yi, Kog'Maw, Krug, Vi, Sett, Nidalee, Gnar |
| Executioner 3 + Summoner 3 (Malphite) | 453 | 2.50 | 91% | 27% | Yorick, Azir, Fiddlesticks, Malphite, Soraka, Zyra, Amumu, Alune, Kennen |
| Executioner 3 + Summoner 3 (Malphite) | 156 | 2.70 | 83% | 24% | Yorick, Azir, Fiddlesticks, Malphite, Soraka, Zyra, Amumu, Ivern, Kennen |
| Executioner 4 + Summoner 3 (Malphite) | 325 | 2.80 | 86% | 25% | Yorick, Azir, Fiddlesticks, Ezreal, Malphite, Soraka, Zyra, Amumu, Kennen |
| Riftbeast 3 (Elder Dragon) | 1818 | 3.70 | 62% | 29% | Amumu, Sentinel, Elder Dragon, Ivern, Kennen, Maokai, Draven, Taric |
