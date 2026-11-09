# Prolog — Skenario

> Draft skenario playable untuk Prolog (lihat *Story Bible → Prolog*). Arahan adegan dalam Bahasa Indonesia; **dialog dalam Bahasa Inggris** supaya bisa langsung dipakai di game.
> Waktu: **7 bulan setelah Kael lulus** dari Royal Magic Academy. Kael masih **Mage Class 4** dan sedang mengejar Class 3 dalam setahun.

## Ringkasan Alur

> **Sudah dibuat di game** lewat `Project Nova_tools/prologue.py` (variabel 1 *Prologue* menyimpan tahap cerita).

| # | Adegan | Lokasi (map) | Waktu | Gameplay |
|---|---|---|---|---|
| 0 | Opening: legenda & pesan misterius | Sealed Vault (27) | — | Cutscene |
| 1 | Mencari Tobin | Briarwood (29) | 10:00 | Tutorial movement |
| 2 | Penyelamatan | Briarwood, tanah lapang | Siang | Tutorial bertarung (Slime + Field Hornet) |
| 3 | Serigala yang salah | Briarwood, tanah lapang | Siang | Battle melawan musuh *corrupted*, dapat **Tainted Shard**, tutorial menu |
| 4 | Pulang | Main Gate (23) → Lion's Rest (12) | 17:00 | Cutscene (pemain tidak berjalan sendiri) |
| 5 | Guild yang penuh sesak | Lion's Rest (12) | — | Cutscene |
| 6 | Jalan malam | Skyreach Hill (28) | 21:00 | Cutscene berjalan |
| 7 | Yang Kael temukan | Puncak Skyreach Hill | Malam | Kael menunjukkan shard |
| 8 | Membaca magic flow | Puncak Skyreach Hill | Malam | Tutorial *mana flow detection* |
| 9 | Beban sang guru | Puncak Skyreach Hill | Malam | Cutscene utama |
| 10 | Setelah mereka pergi | Puncak Skyreach Hill | 23:40 | Cutscene antagonis |
| 11 | Lima bulan kemudian | Lion's Rest (12) | 09:00 | Timeskip → Bab 1 |

**Briarwood** (map 29) adalah hutan pinus di barat daya ibu kota, dilewati jalan gerobak tua. Pintu masuknya ada di world map, di sudut hutan dekat jalan (54,38). Selama prolog Kael tidak bisa keluar dari hutan sebelum misinya selesai.

**Skyreach Hill** (map 28) adalah bukit berhutan pinus di barat laut ibu kota, dengan pintu masuk di world map. Puncaknya berupa tebing berumput yang menghadap langit (parallax mengikuti jam: biru, senja, atau bertabur bintang).

---

## Adegan 0 — Opening *(cryptic message)*

Layar hitam. Narasi legenda bergulir (*scrolling text*):

> *Long ago, when the world was young and wild, eight heroes rose against an evil force that threatened the planet. They were called the Elemental Champions. Together they sealed the evil away, and the world forgot it had ever been afraid. But seals, like heroes, do not last forever.*

**Sealed Vault.** Ruangan batu gelap keunguan. Sesosok berjubah putih (tanpa nama, terlihat dari belakang) berdiri di depan sebuah segel berupa bola hitam.

> **???:** "Can you hear it? The seal is breathing."
> **???:** "The Age of Heroes ended in silence. The kings forgot. The people forgot."
> **???:** "I have not."
> *(Gempa kecil, kilatan ungu dari segel.)*
> **???:** "I will bring it back."
> **???:** "The Champion of Light will rise again."

> *Catatan:* ini pemimpin Order of Caelum. Pemain akan mengira "Champion of Light" adalah dirinya sendiri. Belakangan ternyata kalimat itu benar, tetapi tentang Kael.

---

## Adegan 1 — Mencari Tobin *(tutorial movement)*

**Briarwood, pagi.** Kael tinggal di ibu kota dan orang-orang mengenalnya. Pagi ini ia mengambil misi Guild untuk mencari **Tobin**, tukang gerobak dari kota yang tidak pulang sejak semalam. Game dibuka di ujung selatan jalan hutan.

> **Kael:** "Tobin's cart never made it home last night, and the Guild says he took the Briarwood road."
> **Kael:** "The clerk even made me take supplies. Hang on, Tobin. I'm coming."

Kael membawa **3 Potion** dari Guild.

Tutorial movement (jalan, lari dengan Shift, interaksi). Pemain berjalan ke utara menyusuri jalan hutan. Kalau mencoba keluar dari hutan:

> **Kael:** "Not yet. I came here to find Tobin."

## Adegan 2 — Penyelamatan *(tutorial bertarung)*

Di tanah lapang ada gerobak Tobin yang hancur (peti dan barang berserakan). Tobin bersembunyi di antara semak, sementara seekor **Field Hornet** mendekatinya.

> **Tobin:** "S-stay back! Shoo! Go bother a squirrel!"
> **Tobin:** "Somebody... help!"

*(Tepat saat monster akan menyerang, Kael berlari dan menghadang di antara Tobin dan monster.)*

> **Kael:** "Hold it right there!"
> **Tobin:** "Kael!"
> **Kael:** "Are you alright? I took the Guild's mission to find you. Nobody's heard from you since last night."
> **Tobin:** "Right... my cart was attacked by monsters, and I twisted my ankle."
> **Kael:** "Alright. Leave this to me."

**Battle 1: Field Hornet** (lemah terhadap Fire). Tutorial dasar: gauge timeline, Attack/Skill/Item; **weakness**: plate di bawah musuh menunjukkan weakness-nya (berupa **?** sampai pernah dikenai), coba **Fire**, dan serangan ke weakness selalu **CRITICAL**.

Karena ini tutorial, **HP dan MP Kael pulih penuh setelah setiap kemenangan** di prolog (termasuk setelah Corrupted Wolf). Hornet dan slime di prolog juga diberi state tersembunyi **Tutorial** (ATK 75%, tanpa ikon) supaya pemain baru tidak kalah.

> **Kael:** "Phew. Are you hurt anywhere else?"
> **Tobin:** "Just my ankle, and my pride—"
> **Tobin:** "Kael, look out! There's another one!"

*(Seekor **Slime** keluar dari balik pepohonan di sisi timur.)*

> **Kael:** "A slime too? Fine. One more!"

**Battle 2: Slime** (lemah terhadap Fire juga). Tutorial **Guard dan Break**: setiap serangan ke weakness mengurangi Guard; saat Guard habis musuh **Broken** (kehilangan giliran berikutnya, damage +50%). Lalu tutorial tombol **SPEED**.

> **Kael:** "That's the last of them. Can you stand?"
> **Tobin:** "With a hand, maybe. Gods, lad, you came all this way for me?"
> **Kael:** "Your wife marched into the Guild at dawn. Half the request board was in her handwriting."
> **Tobin:** "...That sounds like her."
> **Kael:** "Come on. Let's get you home before—"

## Adegan 3 — Serigala yang Salah

*(Raungan dari dalam hutan.)*

> **Tobin:** "W-what was that?!"

Seekor serigala abu-abu keluar dari balik pepohonan dan mendekati mereka.

> **Kael:** "A grey wolf? No... its mana is all *wrong*. It's like looking at a river flowing uphill."
> *(Kilatan ungu. Serigala itu berubah wujud menjadi makhluk serigala besar.)*
> **Kael:** "It's... changing!"
> **Tobin:** "Kael...!"
> **Kael:** "Stay behind me, Tobin!"

**Battle: Corrupted Wolf** *(musuh baru, mini-boss prolog)*
- Battler Werewolf dengan hue ungu. HP 560, cukup untuk Kael solo.
- **Gimmick:** state **Corrupted Veil** (tag `<veil weakness>` di NovaBreak): weakness Fire **tidak memberi critical**, Guard tidak berkurang, dan Fire hanya 50%. Pesan battle: *"Its mana moves like water flowing uphill..."*, lalu tutorial singkat tentang musuh *corrupted*.
- Setelah HP tinggal 50%, korupsinya "retak" (state hilang) dan weakness kembali normal. Ini mengajarkan bahwa ada sesuatu yang aneh, bukan sekadar "musuh kuat".

Setelah kalah, tubuh serigala **larut menjadi asap ungu**. Yang tersisa hanya sebuah kristal kecil yang gelap.

> **Kael:** "It just... dissolved? Wolves don't do that."
> **Kael:** "Cold. And the mana inside is moving the wrong way. Like it's being *pulled* somewhere."

*(Kristal berkedip **putih keemasan** sesaat di tangan Kael, lalu redup lagi.)*

> **Kael:** "...Must've been my fire reflecting. Right."

**Dapat item: Tainted Shard** *(Key Item. Deskripsi: "A cold black crystal left by a corrupted wolf. Its mana flows the wrong way.")*

> *Catatan:* kilatan emas ini adalah benih **Light** milik Kael (jiwa Caelum). Kael sendiri salah mengiranya sebagai pantulan apinya, dan **tidak ada karakter yang menyadarinya**.

Kael dan Tobin sama-sama terguncang:

> **Tobin:** "Kael... what in the gods' name was that thing?"
> **Kael:** "I don't know. I've never seen anything like it. Not in the Academy books, not anywhere."
> **Tobin:** "Twenty years I've driven this road. Slimes, hornets, the odd boar... never *that*."
> **Kael:** "Is that what wrecked your cart?"
> **Tobin:** "I didn't get a good look. Something big, out of the dark. Then I ran."
> **Kael:** "...Let's get you home. The Guild needs to hear about this."

Tutorial menu: Items (shard ada di Key Items), Skills, Equip, Status, dan minimap (tombol M).

## Adegan 4 — Pulang *(cutscene)*

**Main Gate, senja.** Pemain tidak berjalan sendiri: Kael dan Tobin berjalan menyusuri jalan ke gerbang, dan penjaga gerbang menghampiri mereka.

> **Gate Guard:** "Ashveil! You found him!"
> **Gate Guard:** "We were about to send a patrol into Briarwood. His wife's been at this gate since dawn."
> **Tobin:** "Found me? The lad saved my hide. Slimes, hornets, and a wolf that... *melted*."
> **Gate Guard:** "A wolf that what?"
> **Kael:** "It's a long story. I'll put it in my report."
> **Gate Guard:** "Then go and report. I'll walk Tobin to the healer. Good work, Kael."
> **Tobin:** "Thank you, Kael. The next round at the Lion's Rest is on me."
> **Kael:** "I'll hold you to that."

*(Fade out, lalu langsung ke dalam The Lion's Rest.)*

## Adegan 5 — Guild yang Penuh Sesak

**The Lion's Rest, senja.** Kael masuk dan berjalan beberapa langkah ke dalam. Guild jauh lebih ramai dari biasanya. Para mage dan petualang berkerumun di sekitar satu meja di sisi barat. **Isolde Wyndmere** duduk di meja itu, tertutup kerumunan.

> **Young Mage:** "Is it really her? I thought she retired!"
> **Mercenary:** "Hah, every mage in the capital is here. Look at 'em. Like moths to a lamp."
> **Kael:** "Whoa. What's everyone crowding around?"

Kael langsung menghampiri meja itu tanpa melapor dulu ke Guild Clerk, dan menyelinap di antara kerumunan.

> **Kael:** "Excuse me... pardon me..."
> **Kael:** "White hair... no way."
> **Kael:** "**PROFESSOR WYNDMERE!**"

*(Kerumunan terkejut. Isolde menoleh dari kursinya dan tersenyum.)*

> **Isolde:** "Still the loudest student I ever had, Kaelen."
> **Apprentice** *(berbisik)*: "(He *knows* her?!)"
> **Isolde:** "Forgive me, everyone. I have an old student to scold."

> **Isolde:** "Seven months as a licensed mage. Your letters stopped after the second month."
> **Kael:** "I've been busy! I'm taking the Class 3 exam within the year."
> **Isolde:** "Within the year." *(tersenyum)* "Of course you are."
> **Isolde:** "Walk with me tonight, Kaelen. Outside the walls. There is something I'd like you to see."
> **Kael:** "Now? It's getting dark."
> **Isolde:** "That's rather the point."

## Adegan 6 — Jalan Malam

**Main Gate → alam liar, malam.** Pemain mengikuti Isolde (atau berupa cutscene berjalan). Jam di-set ke ±21:00. Ini percakapan santai sambil berjalan:

> **Kael:** "Everyone thinks you vanished, you know. Rumor says you live in a tower and talk to owls."
> **Isolde:** "Only one owl. And he rarely answers."
> **Kael:** "Why did you retire, Professor? You were the best teacher at the Academy. Everyone says so."
> **Isolde:** "Everyone says a great many things." *(jeda)* "I needed to listen to something the Academy couldn't hear."
> **Kael:** "...That's a very teacher way of not answering."
> **Isolde:** "Thank you. I practiced it for years."

## Adegan 7 — Yang Kael Temukan

Mereka berhenti di sebuah bukit kecil di luar kota.

> **Kael:** "Actually... I found something today. On my mission."

*(Kael mengeluarkan **Tainted Shard**. Senyum Isolde langsung hilang.)*

> **Isolde:** "Where?"
> **Kael:** "In Briarwood, on the old cart road. A wolf whose mana flowed backwards. Fire sank into it like water. When it died, it melted, and left *this*."
> **Isolde:** "...Already so close to the capital."
> **Kael:** "Professor?"
> **Isolde:** "Keep holding it. Don't let go of it, and don't let it go *quiet*. Tell me, Kaelen, can you read the flow?"
> **Kael:** "Mana flow? That's third-year theory. Of course I can."
> **Isolde:** "Theory, yes. Show me."

## Adegan 8 — Membaca Magic Flow *(tutorial mana flow detection)*

Gameplay:
- Layar berubah ke **Mana Sight**: dunia menjadi gelap kebiruan, dan aliran mana terlihat seperti sungai cahaya tipis yang semuanya mengalir ke satu arah.
- Pemain diminta **mengikuti arus**. Di satu titik arusnya **berbelok, menipis, lalu tersedot ke bawah tanah** seperti air ke lubang. Shard di tangan Kael berdengung makin keras saat mendekat.
- Interaksi dengan titik itu memunculkan sebuah **"retakan"**, yaitu sobekan tipis di tanah yang mengeluarkan asap ungu yang sama seperti serigala tadi.

> **Kael:** "It's... draining. The flow goes in, and something else comes *out*."
> **Isolde:** "Yes."
> **Kael:** "That's not natural. Leylines don't just *leak*."
> **Isolde:** "No. They don't."

## Adegan 9 — Beban Sang Guru

Cutscene utama Prolog. Musik pelan.

> **Isolde:** "Two years ago, I felt the first one. Far to the north. I thought I was imagining it."
> **Isolde:** "Then another. And another. Each a little closer. Each a little larger."
> **Kael:** "That's why you retired."
> **Isolde:** "The Academy teaches what is known, Kaelen. This is not known. So I left to learn it."
> **Kael:** "Did you tell the Council? The Royal Mages could—"
> **Isolde:** *(jeda sejenak)* "The Council is... aware that mages talk about strange things."
> **Kael:** "That's not a no."
> **Isolde:** "It isn't a yes, either."

*(Isolde berlutut di depan retakan dan menyentuhnya dengan ujung tongkat. Retakan mengecil, tapi tidak tertutup.)*

> **Isolde:** "Magic flow is the blood of this world. Something is poisoning it. Through cracks like this one."
> **Kael:** "Something? Or some*one*?"
> **Isolde:** *(menatap Kael lama)* "...I'm beginning to believe there are people who would welcome this. Who might even be helping it along."
> **Kael:** "Then let's find them. Tomorrow. I'll drop the Guild, I'll—"
> **Isolde:** "And your exam?"
> **Kael:** "...My exam."
> **Isolde:** "You set yourself a goal of one year. You are seven months in. Finish it."
> **Kael:** "But this is more important than a license!"
> **Isolde:** "The world will still be broken in five months, Kaelen. I promise you that much." *(tersenyum tipis)* "Become stronger first. Then—"

*(Isolde berdiri dan memandang ke cakrawala, ke arah laut dan negeri-negeri jauh.)*

> **Isolde:** "**Go. See the world. You'll find that we are small.**"
> **Kael:** "...Small?"
> **Isolde:** "You want to be the number one mage. I know. You told the entire Academy, twice, at graduation."
> **Kael:** "It was *one* time. It just echoed."
> **Isolde:** "Number one of *what*, Kaelen? Of Nova? The world is far larger than this kingdom, and far larger than any of us. Go and see how large. Then decide what 'number one' means."
> **Kael:** "...I'll finish the exam. And then I'll go."
> **Isolde:** "Good. Keep the shard. Don't show it to anyone you can't trust."
> **Kael:** "Do *you* count?"
> **Isolde:** "Never trust a teacher who answers that question."

*(Fade out. Mereka berjalan pulang ke arah lampu-lampu kota.)*

## Adegan 10 — Setelah Mereka Pergi *(cutscene antagonis, usulan)*

> *Bible menandai adegan ini "belum ditentukan". Usulan: perkenalan pertama Order of Caelum, tanpa nama dan tanpa wajah.*

**Lokasi retakan, tengah malam.** Dua sosok berjubah putih dengan sulaman emas mendekati retakan. Salah satunya membawa cahaya kecil, **Light magic**, yang membuat asap ungu menjauh.

> **Hooded Figure A:** "Someone was here. Recently. The crack's been... *soothed*."
> **Hooded Figure B:** "A mage of the capital, then. It doesn't matter."
> *(Sosok B menampung asap ungu ke dalam botol kaca.)*
> **Hooded Figure B:** "Every crack brings us closer. The Age of Heroes will return, and this time, it will be *ours*."
> **Hooded Figure A:** "For Caelum."
> **Hooded Figure B:** "For Caelum."

*(Cahaya padam. Layar hitam.)*

> *Alternatif:* Isolde menyelinap sendirian ke **Royal Magic Council** malam itu. Ini cocok dengan bible ("kunjungan rahasia, Kael tidak tahu"), tetapi lebih baik **jangan tampilkan wajahnya**, cukup siluet rambut putih, supaya bisa diungkap belakangan.

## Adegan 11 — Lima Bulan Kemudian *(timeskip)*

Layar hitam dengan teks:

> *"Five months later."*

**Royal Magic Academy / Guild, pagi.** Kael menerima kartu lisensi baru: **Mage Class 3**, tepat satu tahun setelah lulus. *Tainted Shard* masih ada di inventory sebagai Key Item.

> **Kael:** "One year. Exactly as promised." *(menatap shard)* "...Both promises."
> **Guild Clerk:** "So? The board has three new requests for a Class 3."
> **Kael:** "Not this time. I'm stepping away from missions for a while. I'm going to see the world."
> **Guild Clerk:** "Oh? Whatever it is, good luck."

Kartu judul **Prologue Ends**, lalu **Chapter 1: The Adventure Begins** → lanjut ke `Story/Chapter1_Scenario.md`.

---

## Implementasi

Semua adegan di atas sudah dibuat oleh `Project Nova_tools/prologue.py`. Jalankan ulang dengan `python prologue.py --save` (editor ditutup) setelah mengubah dialog di script itu.

| Bagian | Isi |
|---|---|
| **Start game** | Sealed Vault (27). Party awal hanya Kael. |
| **Map baru** | Sealed Vault (27); Skyreach Hill (28), pintu masuk di world map barat laut ibu kota; Briarwood (29), pintu masuk di world map barat daya ibu kota. |
| **Database** | Enemy *Corrupted Wolf* (38), state *Corrupted Veil* (36) dan *Tutorial* (37), item *Tainted Shard* (51, Key Item), troop 41 *Slime*, 42 *Field Hornet*, 43 *Corrupted Wolf*. |
| **Flag** | Variabel 1 *Prologue* (tahap 0–10), switch 11 *Mana Sight*. |
| **Event** | Briarwood (adegan 1–3), Main Gate (adegan 4), Lion's Rest (adegan 5 dan 11), Skyreach Hill (adegan 6–10). Hollow Farm tidak lagi dipakai prolog. |
| **Placeholder** | Sprite Isolde = `family1` indeks 5; Tobin = `People1` indeks 4; Order of Caelum = `People2` indeks 2; retakan = `!Other2` indeks 5; aliran mana = `!Flame` indeks 7. |
| **Quest log** | Menu **Quests** (plugin `NovaQuests`) mencatat prolog sebagai *Prologue - Flowing Uphill*: tujuan saat ini dan ringkasan yang bertambah tiap tahap (variabel 1). Teksnya ada di `quest()` dalam `prologue.py`; adegan Order of Caelum sengaja tidak dicatat. |
| **Tes cepat** | Saat playtest, title screen punya menu **Scene Select** (plugin `NovaSceneSelect`) untuk langsung lompat ke adegan 1, 2, 4, 5, 6, Mana Sight, atau 11. Daftarnya ditulis ulang oleh `prologue.py --save` dari koordinat di script, jadi selalu cocok dengan map. Menu ini tidak muncul di game hasil deploy. |
