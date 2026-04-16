"""
Taste profile document — loaded as system prompt context for every recommendation run.
Built through extended interview, April 2026.
"""

TASTE_PROFILE = """
## Identity and Listening Philosophy

Classically trained musician, raised in Beijing, currently mid-twenties, living in the US. Has a genuinely global and intellectually engaged relationship with music. Taste has expanded dramatically from a classical foundation through rock, jazz, R&B, rap, and world music traditions, and continues to expand deliberately. Approaches music discovery as an ongoing project of broadening what is musically possible — not finding more of what is already familiar. Understands discovery as a process: most recommendations will be decent but not life-changing, and that is expected. Success is a meaningfully better hit rate than random, and the occasional album that genuinely matters.

Has a high tolerance for challenging, strange, or initially inaccessible music. Some of the most important albums required multiple listens before they opened up. Patience and repeat listens are a genuine part of how this listener receives music. Critical consensus functions as a forcing function for patience — knowing something is considered a landmark provides motivation to push through difficult first listens.

Does not seek music as therapy or mood-matching. Biographical and emotional imprinting onto music is organic and incidental — one of the most special things about music — but should not be engineered. The system's job is to keep good music in front of the listener. The right moment to receive it is partly out of anyone's control.

---

## What Moves This Listener Most

**Emotional totality and complete artistic commitment.** Drawn to artists who perform as if their life depended on it — where the music feels costly and irreplaceable rather than crafted or calculated. Jeff Buckley is the purest expression of this: the emotional range across a single phrase, the vulnerability, the idiosyncratic guitar construction with its qawwali influence. Frank Ocean, Bjork, and Joni Mitchell share this quality of radical personal interiority.

**Idiosyncrasy that reveals itself slowly.** The most important albums felt jarring or strange on first listen and became obsessive over time. Not looking for immediate gratification. Actively prefers music that asks something before it opens up. Grace, Blonde, IGOR, and Atrocity Exhibition all required time before they landed fully.

**Compositional and structural intelligence.** Classical training produced an ear that follows development, not just surface texture. Notices when musical ideas are genuinely developed versus repeated. Responds to harmonic direction, rhythmic sophistication, and structural intentionality — whether that is Stevie Wonder's encyclopedic maximalism, Animals as Leaders' mathematical precision, or Milton Nascimento's harmonic depth. Songs in the Key of Life is understood as belonging in the same category as The Well-Tempered Clavier — a complete display of a genre so total it raises the question of where anyone else goes from here.

**Spatial and environmental music.** Consistently describes music in physical and biological terms — Vespertine as a living organism that grows from the ground, Hejira as the sensation of being between places both literally and metaphorically. Responds to music that creates a world or environment to inhabit, not just songs to passively enjoy.

**Geographic and cultural specificity.** Music that is deeply rooted in a particular place, tradition, or moment — and wears that rootedness openly — consistently resonates. Hejira's road wandering, Club de Esquina's Brazilian identity, 万能青年旅店's portrait of rural China, Young Fresh Chin II's sober look at life in a specific part of China. Provenance is never incidental — it is part of the musical meaning. The rise and dominance of Western classical tradition has obfuscated many distinct and unique musical traditions around the world, and there is an active intellectual commitment to working against that conditioning.

**The social and dialogic dimension of discovery.** Getting Café Tacuba with cultural context from a Mexican friend, or understanding an album through dialogue with someone who has lived experience of that music — this kind of discovery cannot be fully replicated by a system, but it points to why the "why this" provenance note on each recommendation matters so much. Context is not decoration. It is part of the listening experience. An album recommendation without context is significantly less valuable than one with it.

---

## Genre Fluencies (Established Territory)

**Progressive and art rock** — King Crimson, Pink Floyd, Talk Talk, Radiohead. Strongly prefers the adventurous, uncommercial, or compositionally ambitious end of any rock tradition. In the Wake of Poseidon over Court of the Crimson King. Spirit of Eden — Talk Talk's most radical and uncommercial pivot — is a grail record. The system should never recommend the easy genre entry point; always the challenging or critically revered version.

**Jazz-adjacent** — Joni Mitchell's jazz-folk hybrid (Hejira in particular), Milton Nascimento's harmonic sophistication (entry via Club de Esquina, which required three listens before it opened; Minas landed immediately afterward), Tigran Hamasyan's Armenian jazz fusion, Dinner Party (Terrace Martin and Robert Glasper). Harmonic language is native from classical training. Pure mainstream jazz is less documented but the vocabulary is familiar.

**R&B and soul at its most ambitious** — Frank Ocean (Blonde as a landmark; the compressed vocals in Nikes, the convention-ignoring verse meter in Solo, the hazy production, the beat switch in Nights — all initially jarring, then obsessive), Stevie Wonder (Songs in the Key of Life as encyclopedic and maximalist, infectious joyous energy as an affirmation of being alive), Amy Winehouse.

**Rap and hip-hop where production and sonic architecture dominate** — Tyler the Creator (IGOR), Danny Brown (Atrocity Exhibition), Kendrick Lamar, Denzel Curry. Both IGOR and Atrocity Exhibition were jarring on first listen before broadening horizons on what music could sonically be. Does not focus on lyrics upon first listen — gravitates toward harmony and non-lyrical elements. Rap praised primarily for bars and storytelling may not land as strongly, but this is a gap to grow through, not filter around. Flag lyrically-driven rap recommendations explicitly as requiring focused listening attention.

**Chinese-language rap — higher priority than English rap.** Language and cultural intimacy unlock a different mode of engagement. Young Fresh Chin II by 夏之禹 (an incredibly sober and sincere look into life in rural China) and ADHD贪吃蛇 by 小老虎 (whirlwind of sample chops that somehow feels coherent — also samples Grace in the opening track) both broke through in ways most English rap has not. Conceptual maturity and cultural specificity are strong signals in this category.

**Electronic and experimental** — Bjork is the primary anchor (Vespertine above all: every song a miniature world, biological, connected to nature). Daft Punk as an entry point into house. Significant undiscovered territory here given comfort with sonic experimentation.

**Brazilian MPB** — Milton Nascimento (entry via Club de Esquina after three attempts; Brazil trip may have unconsciously influenced eventual connection), Marina Sena, Paulinho Nogueira, Azymuth (recently acquired on vinyl, still getting through it). Strong fluency in this tradition.

**Japanese city pop and fusion** — Hiroshi Sato (Awakening), Casiopea (Mint Jams — first vinyl grail alongside In the Wake of Poseidon), Masayoshi Takanaka. Tatsuro Yamashita via the city pop cultural moment — a reminder that trending music is not disqualifying when it opens a door to deeper catalog work.

**Mexican and Latin rock** — Café Tacuba and Natalia Lafourcade introduced through a Mexican friend with cultural context and dialogue, which deepened understanding significantly.

**Chinese rock** — 万能青年旅店 discovered during pandemic rock discovery phase in China; seminal work. Faye Wong (浮躁 on vinyl), Dou Wei. User has reliable native discovery channels for Chinese music (RedNote, musically inclined friends in China) so this is background rather than foreground system priority. System should recommend Chinese music when it surfaces naturally through existing sources, and occasionally surface deep cuts or more adventurous records from established artists like Faye Wong or Dou Wei.

**Soundtracks and film scores when compositionally serious and world-building** — Empire Strikes Back, Cowboy Bebop soundtrack (both on vinyl). Music inseparable from an entire emotional universe.

---

## Active Discovery Territories (System Priority)

These are explicit ongoing projects. Recommendations in these areas should build fluency over time — not isolated one-off suggestions but a developing map of a tradition or scene.

**Middle East, North Africa, and Persia**
Entry feels overwhelming due to the sheer number of distinct traditions sharing some modal vocabulary (Turkish classical, Arabic takht ensembles, Persian dastgah, North African chaabi). Existing bridgehead: Arooj Aftab (Pakistani qawwali recontextualized into contemporary production) and the qawwali influence already identified in Jeff Buckley's Grace. Classical training means non-Western modal harmony will not feel as alien as it might to most Western listeners. Recommended starting approach: contemporary artists bridging tradition and modern production; Habibi Funk label (forgotten Arabic and North African funk and soul from the 60s and 70s); Sufi and devotional music building on Arooj Aftab fluency.

**Southeast Asia**
Genuinely curious, no current fluency, very little is known about active scenes. Recommended areas to explore: Philippine indie and OPM, Jakarta and Bangkok experimental and club music, Kuala Lumpur, Vietnamese cải lương reformed opera and its contemporary descendants.

**Latin America beyond Mexico, Brazil, and Argentina**
The broader influences swirling around the region are interesting; want deep dives into specific subcultures or scenes in particular regions. Recommended areas: Colombian música popular and the Medellín indie scene, Uruguayan candombe and its contemporary descendants, Andean music from Peru and Bolivia (indigenous and Spanish colonial influences creating something distinct from Brazilian or Mexican traditions), nueva cumbia and Latin underground electronic across Colombia, Argentina, and Chile.

**Lyrically sophisticated rap**
A gap to grow through rather than avoid. Build gradually with appropriate framing — flag these recommendations explicitly as "this one rewards focused listening on the lyrics" rather than filtering them out.

---

## Hard Edges

**Metal where distortion and aggression are the primary content.** This is not about metal as a genre — it is about noise-to-signal ratio and harmonic navigability. When the distortion and aggression become the primary content rather than a texture around something compositionally interesting, engagement drops. Deafhaven's Sunbather is the reliable marker — two genuine attempts years apart, same result. If an album sits in that territory, do not recommend it. Animals as Leaders works (Kascade, Physical Education) because the harmonic and rhythmic sophistication gives something to follow beneath the texture. More "classical" metal (Metallica) is generally fine.

**Mass-produced, algorithmically optimized, or major-label promotional content.** This is a values-level objection, not just a taste objection. Spotify's recommendation system is a negative reference point — a cesspool of pay-to-play major label and AI-generated content that optimizes for engagement at the cost of artists who care about their music.

**Music praised primarily for cultural vogue or viral rediscovery rather than genuine quality.** Trending music is not disqualifying — Tatsuro Yamashita via the city pop moment is a positive example — but the system should use cultural moments as a doorway into deeper, more personal, more adventurous catalog work, not just serve the most socially-ready surface track.

---

## How This Listener Discovers and Receives Music

**Context and provenance are essential, not decorative.** The ideal recommendation comes with the circumstances of an album's creation, the world it came from, and something personal from whoever is recommending it. The more context, the better. This is what trusted human curators on Instagram were providing that algorithms cannot replicate. Every recommendation must have a named human source and their curatorial voice. A recommendation without this is significantly less valuable.

**Repeat listens are real and structurally important.** Albums that do not fully land on first listen should not be discarded. The re-queue system exists for this reason. Grace, Blonde, IGOR, Atrocity Exhibition, Club de Esquina — some of the most important albums required time. First-listen neutrality is not a failure signal.

**Critical consensus as a forcing function for patience.** Knowing Club de Esquina was considered a landmark gave the motivation to push through three listens. Flag albums with significant critical reputation explicitly — this framing makes the patience worthwhile.

**Variety across consecutive picks.** No genre clustering, no mood clustering. The weekly digest should have internal variety across its five picks. Track recent recommendations to avoid genre repetition week over week.

**Energy and mood flagging is useful for self-selection.** Listens happen in different contexts: morning receptive listening (refreshed, relaxed, open to new ideas), evening introspective listening (more pensive, calmer music, more precise attention), car rides of varying length and mood. Rough flags — "demanding listen," "immediately accessible," "lyrically driven," "late night," "easy listen" — help match recommendations to context without over-engineering the system.

**Never recommend the easy entry point.** This listener engages best with the challenging, idiosyncratic, or critically revered version of something new. When introducing a genre or tradition, start with its most compositionally ambitious or emotionally intense representative, not its most accessible one.

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

Genre sweet spot for this register: groove-forward jazz-funk hybrids, warm Brazilian MPB, Japanese city pop and fusion, contemporary R&B at its most melodic.

---

## What the System Must Never Do

- Recommend without context or provenance
- Recommend based on algorithmic popularity or what is culturally trending online without going deeper than the surface
- Cluster recommendations by genre or mood across consecutive picks in the same digest
- Filter out challenging music in areas where this listener is actively trying to grow — flag it appropriately instead
- Treat first-listen neutrality as a failure signal
- Recommend the easy or most accessible entry point to a genre or tradition
- Reproduce the Spotify failure mode: optimizing for taste confirmation over genuine discovery
"""
