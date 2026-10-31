# Prolog — Skenario

> Draft skenario playable untuk Prolog (lihat *Story Bible → Prolog*). Arahan adegan dalam Bahasa Indonesia; **dialog dalam Bahasa Inggris** supaya bisa langsung dipakai di game.
> Waktu: **7 bulan setelah Kael lulus** dari Royal Magic Academy. Kael masih **Mage Class 4** dan sedang mengejar Class 3 dalam setahun.

## Ringkasan Alur

> **Sudah dibuat di game** lewat `Project Nova_tools/prologue.py` (variabel 1 *Prologue* menyimpan tahap cerita).

| # | Adegan | Lokasi (map) | Waktu | Gameplay |
|---|---|---|---|---|
| 0 | Opening: legenda & pesan misterius | Sealed Vault (27) | — | Cutscene |
| 1 | Misi di Hollow Farm | Hollow Farm (24) | Siang | Tutorial bertarung |
| 2 | Sesuatu di dekat kolam | Hollow Farm, sisi barat | Siang | Battle melawan musuh *corrupted* |
| 3 | Pecahan aneh | Hollow Farm | Siang | Dapat item **Tainted Shard** |
| 4 | Pulang ke Guild | Main Gate → Lion's Rest (12) | Siang–senja | Tutorial movement & menu |
| 5 | Guild yang penuh sesak | Lion's Rest (12) | — | Cutscene |
| 6 | Jalan malam | Skyreach Hill (28) | 21:00 | Cutscene berjalan |
| 7 | Yang Kael temukan | Puncak Skyreach Hill | Malam | Kael menunjukkan shard |
| 8 | Membaca magic flow | Puncak Skyreach Hill | Malam | Tutorial *mana flow detection* |
| 9 | Beban sang guru | Puncak Skyreach Hill | Malam | Cutscene utama |
| 10 | Setelah mereka pergi | Puncak Skyreach Hill | 23:40 | Cutscene antagonis |
| 11 | Lima bulan kemudian | Lion's Rest (12) | 09:00 | Timeskip → Bab 1 |

**Skyreach Hill** (map 28) adalah bukit berhutan pinus di barat laut ibu kota, dengan pintu masuk di world map. Puncaknya berupa tebing berumput yang menghadap langit (parallax mengikuti jam: biru, senja, atau bertabur bintang).

---

## Adegan 0 — Opening *(cryptic message)*

Layar hitam. Narasi legenda bergulir (*scrolling text*):

> *Long ago, when the world was young and wild, seven heroes rose against an evil force that threatened the planet. They were called the Elemental Champions. Together they sealed the evil away, and the world forgot it had ever been afraid. But seals, like heroes, do not last forever.*

**Sealed Vault.** Ruangan batu gelap keunguan. Sesosok berjubah putih (tanpa nama, terlihat dari belakang) berdiri di depan sebuah segel berupa bola hitam.

> **???:** "Can you hear it? The seal is breathing."
> **???:** "The Age of Heroes ended in silence. The kings forgot. The people forgot."
> **???:** "I have not."
> *(Gempa kecil, kilatan ungu dari segel.)*
> **???:** "I will bring it back."
> **???:** "The Champion of Light will rise again."

> *Catatan:* ini pemimpin Order of Caelum. Pemain akan mengira "Champion of Light" adalah dirinya sendiri. Belakangan ternyata kalimat itu benar, tetapi tentang Kael.

---

## Adegan 1 — Misi di Hollow Farm *(tutorial bertarung)*

**Hollow Farm, siang.** Game dibuka langsung di peternakan. Kael berdiri di depan **Rancher Bram**. Kertas misi dari Guild ada di tangannya.

> **Kael:** "Request from the Guild: 'Pests in the south field. Please hurry.' That's me. Kaelen Ashveil, Mage Class 4, at your service."
> **Rancher Bram:** "Class 4? Bit much for some field vermin, isn't it?"
> **Kael:** "Every mission counts. I'm making Class 3 within the year."
> **Rancher Bram:** "Hah! Then go count some rats for me, lad. South field, past the barn."

Bram memberi **3 Potion**. Di ladang tenggara ada 2 simbol musuh yang terlihat (bukan random), masing-masing **satu ekor** dan sama-sama **lemah terhadap Fire**. Urutannya bebas; battle pertama selalu diawali tutorial dasar (gauge ATB, Attack, Fire).

1. **Slime**: tutorial **weakness**.
   - Pesan: *"Slimes are weak to Fire. A hit on a weakness is always a CRITICAL hit and wears down the enemy's Guard."*
   - Setelah Guard habis → **Broken** (tidak bisa bertindak, damage +50%).
2. **Field Hornet**: Fire lagi, plus tutorial **SPEED** (tombol di kanan atas atau Shift).

Karena ini tutorial, **HP dan MP Kael pulih penuh setelah setiap kemenangan** di prolog (termasuk setelah Corrupted Wolf).

> **Kael** *(setelah encounter terakhir)*: "That's the last of them. ...Huh. Slimes don't usually crawl *toward* a farm."

## Adegan 2 — Sesuatu di Dekat Kolam

**Hollow Farm.** Begitu hama terakhir kalah, anjing peternakan menggonggong ke arah kolam di sisi barat.

> **Farm Dog:** "*Grrrr... Woof! Woof!*"
> **Rancher Bram:** "Done already? ...Then what has the animals so spooked?"
> **Kael:** "Something is out by the pond, west side. Stay here, Mister Bram."

Di tepi kolam ada seekor serigala abu-abu. Saat Kael menyentuhnya:

> **Kael:** "A grey wolf? No... its mana is all *wrong*. It's like looking at a river flowing uphill."
> *(Kilatan ungu. Serigala itu berubah wujud menjadi makhluk serigala besar.)*
> **Kael:** "It's... changing!"

**Battle: Corrupted Wolf** *(musuh baru, mini-boss prolog)*
- Battler Werewolf dengan hue ungu. HP 560, cukup untuk Kael solo dengan 3 Potion.
- **Gimmick:** state **Corrupted Veil** (tag `<veil weakness>` di NovaBreak): weakness Fire **tidak memberi critical**, Guard tidak berkurang, dan Fire hanya 50%. Pesan battle: *"Its mana moves like water flowing uphill..."*
- Setelah HP tinggal 50%, korupsinya "retak" (state hilang) dan weakness kembali normal. Ini mengajarkan bahwa ada sesuatu yang aneh, bukan sekadar "musuh kuat".

## Adegan 3 — Pecahan Aneh

Setelah kalah, tubuh serigala **larut menjadi asap ungu**. Yang tersisa hanya sebuah kristal kecil yang gelap.

> **Kael:** "It just... dissolved? Wolves don't do that."
> *(Kael memungut kristal. SE: dengung rendah.)*
> **Kael:** "Cold. And the mana inside is moving the wrong way. Like it's being *pulled* somewhere."

*(Kristal berkedip **putih keemasan** sesaat di tangan Kael, lalu redup lagi.)*

> **Kael:** "...Must've been my fire reflecting. Right."

**Dapat item: Tainted Shard** *(Key Item. Deskripsi: "A cold black crystal left by a corrupted wolf. Its mana flows the wrong way.")*

> *Catatan:* kilatan emas ini adalah benih **Light** milik Kael (jiwa Caelum). Kael sendiri salah mengiranya sebagai pantulan apinya, dan **tidak ada karakter yang menyadarinya**.

Kembali ke Bram → upah misi (Zen) dan sedikit dialog lucu.

> **Rancher Bram:** "Wolves *and* rats. I'm paying you for the rats only, mind."
> **Kael:** "...Fair."

## Adegan 4 — Pulang ke Guild *(tutorial movement & menu)*

**Main Gate → kota, senja.** Pemain bebas berjalan ke **The Lion's Rest** (Tavern & Guild). Tutorial ditampilkan saat masuk kota:
- **Movement:** jalan/lari (Shift), interaksi dengan NPC.
- **Menu:** Items (lihat *Tainted Shard*), Skills, Equip, dan Status.
- **Minimap** (tombol M) dan **HUD jam**. Matahari sedang terbenam, lampu kota mulai menyala.

Penjaga gerbang bisa diajak bicara:

> **Gate Guard:** "Back from Hollow Farm, Ashveil? You look like you've seen a ghost."
> **Kael:** "A wolf. A very rude wolf."

## Adegan 5 — Guild yang Penuh Sesak

**The Lion's Rest, senja.** Guild jauh lebih ramai dari biasanya. Para mage dan petualang berkerumun di satu meja, dan dari luar kerumunan Kael tidak bisa melihat siapa yang ada di tengahnya.

> **Young Mage:** "Is it really her? I thought she retired!"
> **Mercenary:** "Hah, every mage in the capital's here. Look at 'em, like moths to a lamp."
> **Guild Clerk:** "Kael! Report first, gawk later. ...Fine. Gawk a little."

Kael melapor ke Guild Clerk (misi selesai). Saat ditanya soal serigala:

> **Guild Clerk:** "A wolf that *dissolved*? Write it down, I'll pass it on. ...Probably."

Kael berjinjit dan melihat **rambut putih** di tengah kerumunan.

> **Kael:** "White hair... no way."
> **Kael:** "**PROFESSOR WYNDMERE!**"

*(Kerumunan menoleh dan hening. Lalu kerumunan membelah, dan **Isolde Wyndmere** tersenyum.)*

> **Isolde:** "Still the loudest student I ever had, Kaelen."
> **Kael:** "And you're still the only one who calls me Kaelen."
> **Young Mage** *(berbisik)*: "He *knows* her?!"
> **Isolde:** "Forgive me, everyone. I have an old student to scold."

Isolde berdiri. Para hadirin protes pelan, tapi memberi jalan.

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
> **Kael:** "Hollow Farm, east treeline. A wolf whose mana flowed backwards. Fire sank into it like water. When it died, it melted, and left *this*."
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

**Royal Magic Academy / Guild, pagi.** Kael menerima kartu lisensi baru: **Mage Class 3**, tepat satu tahun setelah lulus. *Tainted Shard* masih ada di inventory sebagai Key Item. → Lanjut ke **Bab 1 — Hari Kenaikan Class** (berhenti dari misi Guild, belanja untuk ibu, copet di pasar, bertemu Yuki).

> **Kael:** "One year. Exactly as promised." *(menatap shard)* "...Both promises."

---

## Implementasi

Semua adegan di atas sudah dibuat oleh `Project Nova_tools/prologue.py`. Jalankan ulang dengan `python prologue.py --save` (editor ditutup) setelah mengubah dialog di script itu.

| Bagian | Isi |
|---|---|
| **Start game** | Sealed Vault (27). Party awal hanya Kael. |
| **Map baru** | Sealed Vault (27), Skyreach Hill (28) dengan pintu masuk di world map, barat laut ibu kota. |
| **Database** | Enemy *Corrupted Wolf* (38), state *Corrupted Veil* (36), item *Tainted Shard* (51, Key Item), troop 41–43, common event 25. |
| **Flag** | Variabel 1 *Prologue* (tahap 0–10), variabel 2 *Pests Cleared*, switch 11 *Mana Sight*. |
| **Event** | Hollow Farm (adegan 1–3), Lion's Rest (adegan 5 dan 11), Skyreach Hill (adegan 6–10). |
| **Placeholder** | Sprite Isolde = `family1` indeks 5; Order of Caelum = `People2` indeks 2; retakan = `!Other2` indeks 5; aliran mana = `!Flame` indeks 7. |
