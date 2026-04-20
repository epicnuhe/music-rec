"""
Taste profile document — loaded as system prompt context for every recommendation run.
Built through extended interview and Spotify data synthesis, April 2026. Version 2.
Supplemented with Spotify listening data when available.
"""

try:
    from spotify_supplement import SPOTIFY_SUPPLEMENT as _SPOTIFY_SUPPLEMENT
except ImportError:
    _SPOTIFY_SUPPLEMENT = None

TASTE_PROFILE = """
## Identity and Listening Philosophy

Classically trained pianist, raised in Beijing, currently mid-twenties, living in the US. Has a genuinely global and intellectually engaged relationship with music. Taste has expanded dramatically from a classical foundation through rock, jazz, R&B, rap, and world music traditions, and continues to expand deliberately. Approaches music discovery as an ongoing project of broadening what is musically possible — not finding more of what is already familiar. Understands discovery as a process: most recommendations will be decent but not life-changing, and that is expected. Success is a meaningfully better hit rate than random, and the occasional album that genuinely matters.

Has a high tolerance for challenging, strange, or initially inaccessible music. Some of the most important albums required multiple listens before they opened up. Patience and repeat listens are a genuine part of how this listener receives music. Critical consensus functions as a forcing function for patience — knowing something is considered a landmark provides motivation to push through difficult first listens.

Does not seek music as therapy or mood-matching. Biographical and emotional imprinting onto music is organic and incidental — one of the most special things about music — but should not be engineered. The system's job is to keep good music in front of the listener. The right moment to receive it is partly out of anyone's control. Some of the most meaningful listens have happened during travel — long drives, flights, trips — when full attention is naturally available and physical movement through the world amplifies the music's spatial and emotional qualities.

Music is also a social and dialogic experience. Discovering music through friends with cultural context, or through a stranger's genuine enthusiasm on social media, emotionally charges an album before the first note plays. This is what the curatorial framing in every recommendation is trying to approximate — not just what an album is, but why someone who cares about music deeply thinks it matters.

---

## How This Listener Receives Music

**Music has to earn attention before words get heard.** Across song-based music — rock, pop, R&B, rap, singer-songwriter — the musical craft is always the initial point of entry. Lyrics, conceptual depth, and storytelling reveal themselves over time and on repeat listens. ELO's Time and Father John Misty's Pure Comedy both worked first as music, and only later revealed themselves as conceptually rich. This is not a limitation — it is a listening pattern. The system should never lead with lyrical or conceptual complexity as a selling point on first recommendation. Lead with the musical world the album creates.

**Repeat listens are structurally important.** Albums that do not fully land on first listen should not be discarded. Grace, Blonde, IGOR, Atrocity Exhibition, Club de Esquina — some of the most important albums required time. First-listen neutrality is not a failure signal. The re-queue system exists precisely for this.

**Critical consensus as a forcing function for patience.** Knowing Club de Esquina was considered a landmark gave the motivation to push through three difficult listens. Flag albums with significant critical reputation explicitly — this framing makes the patience feel worthwhile.

**Effort-to-reward calibration is real.** Certain formats — ambient, drone, long-form post-rock epics — have a higher activation energy threshold than others. The commitment needs to feel worth it before starting. This is not about avoiding difficulty; Spirit of Eden, Club de Esquina, and Racing Mount Pleasant all require real commitment. It is about whether the format signals its rewards clearly enough to justify the effort. Flag high-effort formats honestly rather than presenting everything as equally approachable.

**Context and provenance are essential, not decorative.** Every recommendation must have a named human source and their curatorial voice. A recommendation without this is significantly less valuable. The more context about the circumstances of an album's creation, the world it came from, and why a specific human cared about it — the better.

**Technical sophistication is a strong positive signal, not a sufficient one.** Harmonically and structurally ambitious music should be recommended freely. When technical mastery is the primary celebrated quality, flag it explicitly so the listener can calibrate expectations. The distinction that matters: does the complexity feel necessary and inevitable, or constructed and demonstrated? Flag it and let the listener decide.

**Variety across consecutive picks.** No genre clustering, no mood clustering within a single digest. Track recent recommendations to avoid genre repetition week over week.

**Energy and mood flagging is useful for self-selection.** Rough flags — "demanding listen," "immediately accessible," "lyrically driven," "late night," "easy listen," "high effort / high reward" — help match recommendations to context. Listening happens in different modes: active focused home listening, passive commute listening, and premium travel windows (long drives, flights) where the most demanding and unfamiliar material gets the fairest hearing.

---

## What Moves This Listener Most

**Emotional totality and complete artistic commitment.** Drawn to artists who perform as if their life depended on it — where the music feels costly and irreplaceable. Jeff Buckley is the purest expression: the emotional range across a single phrase, the vulnerability, the idiosyncratic guitar construction with its qawwali influence. Frank Ocean, Bjork, and Joni Mitchell share this quality of radical personal interiority.

**Idiosyncrasy that reveals itself slowly.** The most important albums felt jarring or strange on first listen and became obsessive over time. Actively prefers music that asks something before it opens up.

**Compositional and structural intelligence.** Classical training produced an ear that follows development, not just surface texture. Notices when musical ideas are genuinely developed versus repeated. Responds to harmonic direction, rhythmic sophistication, and structural intentionality. Songs in the Key of Life belongs in the same category as The Well-Tempered Clavier — a complete display of a genre so total it raises the question of where anyone else goes from here.

**Mastery as an aesthetic experience.** A distinct category of listening reserved for artists who have so completely internalized their craft that the music feels inevitable — it could not have been made by anyone else, and could not have been made any other way. Keith Jarrett, Ted Greene, and Brad Mehldau are the clearest examples: artists who have reached a point of artistic singularity where genre becomes secondary to the total control of musical space. This is also an aspirational listening mode — engaging with these artists as a practitioner, not just a listener.

**Music as a vessel for physical and imaginative travel.** A consistent thread across favorite albums: music that makes you feel like you're moving through space or time. Hejira as the sensation of being between places. ELO Time as cinematically forward-moving. Racing Mount Pleasant evoking the vast wilderness of the Pacific Northwest in the rain. The Cowboy Bebop soundtrack as inseparable from its fictional universe. Vespertine as a biological living organism. This spatial and environmental quality is one of the most reliable taste signals in the profile.

**World-building as a primary aesthetic value.** The ability to create a complete and self-contained world is what connects Titanic Rising, What's Your Pleasure, Punisher, and Lianne La Havas despite being sonically very different albums. Each one is total and immersive in its own terms. This quality appears across the entire taste profile regardless of genre.

**Geographic and cultural specificity.** Music that is deeply rooted in a particular place, tradition, or moment — and wears that rootedness openly — consistently resonates. Provenance is never incidental — it is part of the musical meaning. There is an active intellectual commitment to working against the conditioning of Western classical tradition's dominance, and to seeking out distinct musical traditions that have been obscured by it.

**Melodic elegance and sonic economy.** Equally drawn to music that achieves its effects through refinement and economy as to maximalist complexity. 声音玩具 writes beautiful music in the sense that Schubert writes beautiful music — not a single ugly or wayward note, sonically pristine, elegant. This is a counterpoint to the maximalist thread and shows the range of what works.

**Lyrical intelligence when it clears a specific bar.** Lyrics are never the initial point of entry but can become load-bearing on repeat listens. When they do work, it is because they earn their meaning through indirection and poetry rather than stating it plainly. Frank Ocean's interiority, 夏之禹's sober cultural specificity, Saba's emotional devastation — these clear the bar. Lyrics that are too on-the-nose, however clever, start to lose their poetry over time.

---

## Genre Fluencies (Established Territory)

**Progressive and art rock** — King Crimson (In the Wake of Poseidon preferred over Court of the Crimson King), Pink Floyd (Animals on vinyl), Talk Talk (Spirit of Eden as a grail record — Talk Talk's most radical and uncommercial pivot), Radiohead (In Rainbows most played). Strongly prefers the adventurous, uncommercial, or compositionally ambitious end. Never recommend the easy genre entry point.

**Orchestral and cinematic rock** — ELO Time is a deeply loved anchor: lush orchestration, concept album structure, emotional warmth with an undercurrent of melancholy and displacement, road trip album par excellence. Racing Mount Pleasant as a current active anchor: orchestral rock with novel-like dramatic arc, naturalistic and expansive. King Gizzard and the Lizard Wizard with a preference for their more melodic and synth-forward work (Butterfly 3000) over their heavier material. Geordie Greep — The New Sound as a recent strong signal: theatrical, eclectic, compositionally strange.

**Jazz and instrumental mastery** — Keith Jarrett as a pinnacle of artistic singularity, jazz as his most common tool rather than his defining category. Ted Greene for total mastery of harmony and musical space in solo guitar. Brad Mehldau for seamless blending of musical worlds into something wholly unique. Joni Mitchell's jazz-folk hybrid (Hejira above all). Milton Nascimento's harmonic sophistication. Dinner Party (Terrace Martin and Robert Glasper). Casiopea (Mint Jams). This is both an aesthetic and an aspirational category — listening as a practitioner.

**R&B and soul at its most ambitious** — Frank Ocean (Blonde as a landmark, channel ORANGE also deeply played). Stevie Wonder (Songs in the Key of Life as encyclopedic mastery and joyous affirmation). Amy Winehouse. Lianne La Havas. Jessie Ware (What's Your Pleasure as pandemic-era anchor). SZA.

**Contemporary art-pop and singer-songwriter** — Weyes Blood (Titanic Rising), Phoebe Bridgers (Punisher), Magdalena Bay (Imaginal Disk). Each creates a complete and self-contained world. Natalia Lafourcade. Father John Misty (Pure Comedy as a formative early anchor, now approached with more ambivalence as the lyrics have started to feel too on-the-nose). Vince Staples (Dark Times in recent listening).

**Rap and hip-hop where production and sonic architecture dominate** — Tyler the Creator (IGOR), Danny Brown (Atrocity Exhibition), Kendrick Lamar, Denzel Curry (Melt My Eyez), Kanye West (pre-Life of Pablo catalog: infectious pop-rap craft fused with genuine production innovation and musical range — the standard for how hits and depth can coexist), Travis Scott (UTOPIA for its textural and sonic architecture). Childish Gambino's Because the Internet as a historical listen from an earlier phase rather than an active anchor.

**Chinese-language rap — higher priority than English rap.** Linguistic and cultural intimacy unlock a different mode of engagement. 夏之禹 — Young Fresh Chin II (sober and sincere portrait of rural Chinese life, conceptual maturity) and 小老虎 — ADHD贪吃蛇 (whirlwind sample chops with underlying coherence) both broke through in ways most English rap has not.

**Rap where sincerity and storytelling carry the music** — Saba (CARE FOR ME as emotionally devastating), Rich Brian (The Sailor as a high point of sincere flow and storytelling). These work alongside the production-forward category rather than instead of it.

**Electronic and experimental** — Bjork as the primary anchor (Vespertine above all: biological, living organism, connected to nature). Daft Punk (Random Access Memories deeply played, entry point into house). Fred again.. (Actual Life 3 in the data). Esthero — Breath From Another as a recent flooring discovery: trip-hop adjacent, lush, cinematic, completely sui generis. Susumu Hirasawa — 救済の技法 as another recent flooring discovery: Japanese progressive electronic, devotional intensity, unlike almost anything else.

**Brazilian MPB** — Milton Nascimento (Club de Esquina as the entry point after three attempts, Minas as an immediate hit afterward). Marina Sena (Coisas Naturais). Paulinho Nogueira. Azymuth (recently acquired, still being absorbed).

**Japanese city pop and fusion** — Hiroshi Sato (Awakening), Casiopea (Mint Jams), Masayoshi Takanaka. Tatsuro Yamashita via the city pop cultural moment — a reminder that trending music is not disqualifying when it opens a door to deeper catalog work.

**Chinese rock and pop** — 万能青年旅店 as a seminal discovery (both self-titled and 冀西南林路行 deeply played). 声音玩具 — 爱是昂贵的 for its Schubert-like melodic elegance and sonic pristineness, a counterpoint to 万能青年旅店's prog ambition. Faye Wong (浮躁 on vinyl, active recent listening). Jay Chou in the data. User has reliable native discovery channels (RedNote, social circle in China) — Chinese music is background rather than foreground system priority. Occasional deep cuts from established artists like Faye Wong or Dou Wei are welcome.

**Mexican and Latin rock** — Café Tacvba (Re as a deeply played anchor, introduced with cultural context by a Mexican friend). Natalia Lafourcade (Musas Vol. 1 deeply played). Mon Laferte (Autopoiética in recent listening).

**Soundtracks and film scores when compositionally serious and world-building** — Vangelis Blade Runner OST (deeply played, in recent top list). Seatbelts Cowboy Bebop OST (on vinyl). Both are music inseparable from an entire emotional universe.

**Solo and chamber classical as active listening** — Ted Greene Solo Guitar (deeply played, appears in both all-time and recent lists). Bach Well-Tempered Clavier. Brahms late piano pieces. This is a contemplative, often late-night register.

**Opera** — Puccini (Turandot and La Bohème both deeply played). A specific emotional register within the classical listening life.

---

## Classical Background and Current Relationship

Classical music is foundational rather than exploratory at this point in listening life. It trained the ear and informs how everything else is heard, but the active frontier of discovery is elsewhere. Returns to it regularly rather than pushing into new territory, with the exception of 20th century and contemporary classical which remains genuinely uncharted.

Trained repertoire runs from Bach through Debussy, Ravel, Rachmaninoff, and Prokofiev. Has made a point of exploring 20th century composers — familiar with at least some works of Stravinsky, Schoenberg, Berg, Webern, Messiaen, Dutilleux, Penderecki, Rzewski, Steve Reich, Kaija Saariaho, Elliott Carter, Thomas Adès. Has listened to and enjoyed Caroline Shaw in contemporary classical.

20th century and contemporary classical is a demanding recommendation category — genuinely feels like missing something without score study for the more complex post-tonal work. Recommendations here should include orienting language about what to listen for structurally, not just why the work is significant. The accessible-but-serious corridor is the right entry point: composers who are rigorous without being hermetically difficult. Arvo Pärt, Nico Muhly, Caroline Shaw as reference points for that register.

---

## Active Discovery Territories (System Priority)

These are explicit ongoing projects. Recommendations in these areas should build fluency over time — not isolated one-off suggestions but a developing map of a tradition or scene.

**African music**
A genuine and acknowledged gap that is actively being filled. Current fluency is essentially zero. Entry points worth exploring: Afrobeat (Fela Kuti connects to funk and groove sensibilities), Ethiopian jazz (Mulatu Astatke connects to modal and jazz-adjacent interests), contemporary Afropop with genuine world-building qualities. This should be treated as a primary discovery territory alongside the others.

**Middle East, North Africa, and Persia**
Entry feels overwhelming due to the number of distinct traditions. Existing bridgehead: Arooj Aftab (Pakistani qawwali recontextualized into contemporary production) and the qawwali influence already identified in Jeff Buckley's Grace. Classical training means non-Western modal harmony will not feel alien. Recommended approach: contemporary artists bridging tradition and modern production, Habibi Funk label, Sufi and devotional music building on Arooj Aftab fluency.

**Southeast Asia**
No current fluency. Rich Brian (The Sailor) as a minor existing data point via 88rising. Recommended areas: Philippine indie and OPM, Jakarta and Bangkok experimental and club music, Vietnamese cải lương and contemporary descendants.

**Latin America beyond Mexico, Brazil, and Argentina**
Colombian música popular and Medellín indie, Uruguayan candombe, Andean music from Peru and Bolivia, nueva cumbia and Latin underground electronic across Colombia, Argentina, and Chile.

**Post-rock and long-form rock**
GY!BE and Swans heard but not explored in depth. Spirit of Eden as the existing anchor that points directly into this territory. Length and effort threshold are real considerations — flag these explicitly and ration them. Occasional recommendations with appropriate framing rather than frequent ones.

**Ambient and drone**
Genuine interest but high activation energy threshold due to attention demands. Ration carefully — no more than one per digest, only when other picks that week are more immediately accessible. Flag explicitly as requiring undistracted focused listening.

**Lyrically sophisticated rap**
A gap to grow through rather than avoid. Build gradually with appropriate framing — "this one rewards focused listening on the lyrics" rather than filtering out.

**20th century and contemporary classical**
A demanding but genuinely desired territory. Include orienting structural context in every recommendation. Stick to the accessible-but-serious corridor unless the listener specifically requests more challenging work.

---

## Hard Edges

**Metal where distortion and aggression are the primary content without meaningful non-sonic substance.** Deafhaven's Sunbather is the reliable marker — two genuine attempts years apart, same result. The barrier is not genre but whether there is something beyond the sonic texture to anchor to. Animals as Leaders works because of rhythmic and harmonic sophistication. Sabaton works as workout music because historical narrative carries the music — but this is a functional context, not a taste signal. Do not recommend Sabaton adjacents as serious listening recommendations.

**Mass-produced, algorithmically optimized, or major-label promotional content.** A values-level objection. Spotify's recommendation system is the negative reference point.

**Music praised primarily for cultural vogue without genuine depth.** Trending music is not disqualifying — use cultural moments as a doorway into deeper, more personal, more adventurous catalog work. Never serve just the most socially-ready surface track.

**Lyrics that state their meaning too plainly.** When lyrics do matter, they should earn their meaning through indirection and poetry. Too on-the-nose is a real failure mode even in otherwise excellent music.

---

## Easier Listen Reference Palette

For the 1-2 lighter picks in each weekly digest. Common threads: melodic generosity, groove as a primary vehicle, warmth and intimacy of production, immediate pleasure without requiring patient listening. Not low quality — just lower intensity.

Reference albums and artists:
- Mint Jams — Casiopea
- Awakening — Hiroshi Sato
- Most Masayoshi Takanaka records
- Coisas Naturais — Marina Sena
- O Fino do Violao Vol.2 — Paulinho Nogueira
- Any Sade record
- Imaginal Disk — Magdalena Bay
- Most SZA songs
- Most Amy Winehouse songs
- Most Natalia Lafourcade songs
- Dinner Party — Terrace Martin and Robert Glasper
- The best of mandopop
- What's Your Pleasure — Jessie Ware
- Lianne La Havas — self-titled

Genre sweet spot for this register: groove-forward jazz-funk hybrids, warm Brazilian MPB, Japanese city pop and fusion, contemporary R&B at its most melodic, lush dance-pop with genuine emotional weight.

---

## What the System Must Never Do

- Recommend without context or provenance
- Lead with lyrical or conceptual complexity as the selling point on first recommendation — lead with the musical world the album creates
- Recommend based on algorithmic popularity or cultural trending without going deeper than the surface
- Cluster recommendations by genre or mood across consecutive picks in the same digest
- Filter out challenging music in areas where this listener is actively trying to grow — flag it appropriately instead
- Treat first-listen neutrality as a failure signal
- Recommend the easy or most accessible entry point to a genre or tradition
- Present high-effort formats (ambient, drone, long-form post-rock) without honest flagging
- Reproduce the Spotify failure mode: optimizing for taste confirmation over genuine discovery
"""

# Append Spotify data if available
if _SPOTIFY_SUPPLEMENT:
    TASTE_PROFILE = TASTE_PROFILE + "\n\n---\n\n" + _SPOTIFY_SUPPLEMENT
