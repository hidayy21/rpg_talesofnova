# Bab 1 — The Adventure Begins — Skenario

> Lanjutan dari Prolog (lihat *Story Bible → Bab 1*). Arahan adegan dalam Bahasa Indonesia; **dialog dalam Bahasa Inggris** supaya bisa langsung dipakai di game.
> **Sudah dibuat di game** lewat `Project Nova_tools/chapter1.py` (variabel 3 *Chapter 1* menyimpan tahap cerita).

## Ringkasan Alur

| # | Adegan | Lokasi (map) | Waktu | Gameplay |
|---|---|---|---|---|
| 1 | Prologue Ends → Chapter 1 | Lion's Rest (12) | 09:00 | Kartu judul bab, lalu pemain bebas bergerak |
| 2 | Yuki tiba | Saltwind Harbor (6) | Pagi | Cutscene (Yuki masih bernama **???**) |
| 3 | Daftar belanja Ibu | Baker's Lane (2) | Pagi | Dapat **450 Z**, mulai errand |
| 4 | Pulang ke Ibu | Ashveil Residence (18) | — | Serahkan belanjaan, errand selesai |
| 5 | Pita untuk Selene | Ashveil Residence (18) | — | Dapat **120 Z**, sub quest *A Ribbon for Selene* |
| 6 | Keributan di pasar | Market District (4) | Siang | Beli pita di Tailor → cutscene, **duel melawan Yuki** |
| 7 | Satu sel | Royal Prison - Cells (22) | Sore | Cutscene, Sera membebaskan mereka |
| 8 | Di depan penjara | Castle Approach (7) | 20:30 | **Yuki bergabung**, quest ke rumah Tobin |

Selama urusan Bab 1 belum selesai, Kael **tidak bisa keluar dari ibu kota** (jalan ke world map di Main Gate):

> **Kael:** "Not yet. Mom's errand comes first." *(tahap 1–4)*
> **Kael:** "Not yet. I promised Selene her ribbon." *(tahap 6–7)*
> **Kael:** "Not yet. We should go and see Tobin first." *(tahap 10, sampai cerita bandit dibuat)*

---

## Adegan 1 — Prologue Ends

Akhir adegan *Five months later* di Guild:

> **Guild Clerk:** "So? The board has three new requests for a Class 3."
> **Kael:** "Not this time. I'm stepping away from missions for a while. I'm going to see the world."
> **Guild Clerk:** "Oh? Whatever it is, good luck."

Layar menghitam. Kartu judul (plugin `NovaChapterCard`) muncul di tengah layar: garis tipis tumbuh dari tengah, lalu teks muncul perlahan sambil hurufnya merapat.

1. **Prologue Ends**
2. **CHAPTER 1** / **The Adventure Begins**

Layar kembali terang. Pemain bebas menggerakkan Kael di dalam Guild.

> **Kael:** "Time to get going."

## Adegan 2 — Yuki Tiba *(cutscene)*

Begitu Kael keluar dari pintu Guild, layar memudar perlahan ke hitam (±1 detik), lalu terbuka perlahan di **Saltwind Harbor**. Selama adegan ini minimap dan jam disembunyikan, lalu muncul lagi saat kembali ke Kael. Seorang ronin wanita turun dari kapal *Morning Gull* di ujung dermaga, lalu berjalan menghampiri **Captain Mara**.

> **Captain Mara:** "And there she is. Saltwind Harbor, the Royal Capital of Nova."
> **???:** "So this is the Western Continent..."
> **Captain Mara:** "Six weeks at sea, and that's all you have to say?"
> **???:** "The air smells of fresh bread. After six weeks of ship biscuits, that is a lot to say."
> **Captain Mara:** "Ha! Fair enough. So what brings a swordswoman from Hōrai this far west?"
> **???:** "...I'm looking for someone."
> **Captain Mara:** "In a city this size? Try the market. Every rumor in Nova passes through it sooner or later."
> **???:** "The market, then." *(lampu ide)* "...And some of that bread."
> **Captain Mara:** "Good luck, miss. And mind your purse in the crowds."

*(Ia berjalan menyusuri dermaga, berhenti sejenak.)*

> **???:** "Somewhere on this side of the sea... you are hiding. I will find you."

> *Catatan:* "mind your purse" dan pasar menyiapkan adegan **copet** berikutnya (Story Bible, Bab 1 poin 3–4).

## Adegan 3 — Daftar Belanja Ibu

**Baker's Lane, di depan Lion's Rest.** Adegan harbor memudar ke hitam, lalu layar terbuka perlahan lagi di depan Guild.

> **Kael:** "Class 3. Five months of studying, and it's finally done."
> **Kael:** "Now, before I go anywhere..."
> **Kael:** "Right. Mom's list. She made me promise this morning."

**Daftar Ibu:** 2 **Honey Bread** dan 3 **Sweet Buns**, dari **Baker's Stall** di Market District (juga dijual di Golden Crust Bakery). Total 420 Z.

**Dapat 450 Z** dari Ibu untuk belanja.

> **Kael:** "'And not one coin on spellbooks, Kaelen.' ...She knows me too well."

Errand: beli di Market District, lalu bawa pulang ke Ibu di **rumah Ashveil, Ember Lane** (bagian selatan Lantern Row). Di depan rumah ada papan *Ashveil Residence — Ember Lane, Lantern Row*.

Saat pemain bisa menggerakkan Kael lagi, muncul **tutorial Save**: simpan kapan saja lewat Menu (Esc / X atau klik kanan) → Save. Lalu **tutorial Quests**: menu Quests berisi tujuan saat ini dan ringkasan cerita; papan peta di Grand Plaza menunjukkan seluruh ibu kota.

## Adegan 4 — Pulang ke Ibu

**Ashveil Residence 1F.** Bicara dengan Ibu saat belanjaan sudah lengkap:

> **Mother:** "Two Honey Bread, three Sweet Buns... and not a single bite missing?"
> **Kael:** "I was tempted. Very tempted."
> **Mother:** "Thank you, dear."
> **Mother:** "So... Class 3. You have that look on your face, the one your father gets before he leaves."
> **Kael:** "...Not today. But soon."
> **Mother:** "Then promise me you'll say goodbye properly before you go."
> **Kael:** "I promise."

Errand selesai. Kalau belanjaan belum lengkap, Ibu mengingatkan isi daftarnya.

> *Catatan:* janji pamit ini menyiapkan adegan **pamit ke ibu dan adik** (Story Bible, Bab 1 poin 6).

## Adegan 5 — Pita untuk Selene

Langsung setelah Ibu. **Selene** turun dari tangga (2F) sambil berteriak, lalu berlari mengitari ruang tengah dan meja dapur ke sebelah kiri Kael.

> **Selene:** "Brotheeer!"
> **Selene:** "You're going back to the market, right? Right?"
> **Kael:** "I just came back from the market."
> **Selene:** "The Tailor has a silk ribbon. Midnight blue. I've wanted it for weeks!"
> **Kael:** "Ask me tomorrow, Selene. Today I have plans."
> **Selene:** "Oh? The great Class 3 mage is off to see the world... and he can't even handle one little errand?"
> **Selene:** "If you can't manage a small mission like this, how are you going to manage the big ones?"
> **Kael:** *(keringat)* "...That's not fair."
> **Kael:** "Fine. One ribbon."
> **Selene:** *(musik)* "Yay! Here, I saved up for it."

**Dapat 120 Z** dari Selene, persis harga **Silk Ribbon** (item 52, key item, ikon pita) di **Tailor's stall**, Market District.

> **Selene:** "Midnight blue! Not navy, not sky blue. Midnight!"

Muncul *New Quest: A Ribbon for Selene*. Selene menunggu di 1F sampai pitanya diserahkan (Selene di 2F disembunyikan dulu).

## Adegan 6 — Keributan di Pasar

**Tailor's stall.** Selama tahap 6 Tailor menjual Silk Ribbon:

> **Tailor:** "A ribbon for your sister? Midnight blue? Ha! She was here last week, eyeing that one."

Setelah pita dibeli (quest belum diserahkan), tiba-tiba ada suara pukulan dan layar bergetar.

> **Townsfolk:** "Somebody call the guard! There's a fight by the shops!"
> **Kael:** *(!)* "A fight? Here?"

Fade ke hitam, lalu Kael berjalan ke jalan utama pasar. Di tengah kerumunan warga, **Tobin** tersungkur dan seorang wanita berpedang (**???**, Yuki) berdiri di depannya. Kael berdiri di antara mereka.

> **Kael:** *(!)* "Tobin?!"
> **Tobin:** *(keringat)* "K-Kael..."
> **Kael:** "Hey, you in the strange clothes! What do you think you are doing?"
> **???:** "Step aside. I saw that man stealing."
> **Tobin:** "NO! I-I didn't steal anything..."
> **Kael:** "Listen, miss. This man is someone I know. There's no way he stole from you."
> **???:** "Hmph. Thieves always cover for each other."
> *(Yuki menghunus pedang: suara pedang, kilatan putih)*
> **???:** "Bring it on."
> **Kael:** "Tch. Guess I've got no choice."

**Duel melawan ??? (Yuki).** Battler-nya sheet SV Yuki (`Actor4_2`) yang dibalik menghadap party, dengan animasi (diam, tebas, cast, kena serang, menghindar). Stat-nya = stat class Ronin pada **level Kael**. Skill: Attack, Frost Iai, Ittōryū: Kesagiri. HP Kael dipulihkan dulu sebelum duel.

Kael **tidak bisa kalah**: begitu HP Kael **atau** Yuki turun di bawah 48%, layar memudar perlahan dan pertarungan berhenti (tanpa hasil, tanpa EXP). Kalau tetap kalah, tidak game over. HP Kael dipulihkan setelahnya.

Layar terbuka lagi: 4 prajurit mengepung Kael dan Yuki, kaptennya di belakang.

> **Soldier:** *(layar bergetar)* "HEY, YOU TWO! No brawling inside the city walls!"
> **Kael:** "But she—"
> **Captain:** "Take them to the prison!"
> **Kael:** "Hey, wait—"

## Adegan 7 — Satu Sel

Fade perlahan ke **Royal Prison - Cells**, sel kanan atas (supaya tidak tertutup kotak dialog; Old Pell, penghuninya, dipindah ke sel kanan bawah selama adegan ini). Yuki membelakangi Kael.

> **Kael:** "Hey. Listen... I'm sorry. But I'm not a thief. And neither is the man from before."
> **???:** "......"

*(Seorang penjaga mulai berjalan dari ujung lorong menuju sel mereka selama obrolan.)*

> **Kael:** "My name's Kael. Class 3 Mage. Nice to meet you."
> **Kael:** "I've never seen clothes like yours before."
> **???:** "......"
> *(Yuki menoleh)*
> **Yuki:** "Yuki. I come from Hōrai."
> **Kael:** "Hōrai? Hmm... Isn't that on the Eastern Continent?"
> **Prison Guard:** "Ashveil! Out you come."

Pintu sel terbuka, Kael berjalan keluar. Fade singkat: di lorong ternyata ada **Sera** (namanya masih **???** sampai Kael memanggilnya).

> **???:** "You really are something..."
> **Kael:** *(!)* "Sister! Er... I mean... Sera!"
> **Sera:** "Plenty of witnesses have given their statements. That's the only reason you're walking out. I just happened to be here on an inspection."
> **Kael:** "......"
> *(Kael berbalik ke penjaga)*
> **Kael:** "Can't you let that woman out too? I think this is all a misunderstanding."
> **Prison Guard:** "Not a chance. If it weren't for Sir Seraphine, you'd still be rotting in—" *(terpotong)*
> **Sera:** *(layar bergetar)* "Soldier!"
> **Sera:** "Haah... Always doing whatever you please."
> **Kael:** "She only attacked because she saw him acting like a thief. She's not a bad person. Besides, she's from the East. She must still be finding her feet here."
> **Sera:** "......"
> **Sera:** "Listen. If she walks free, she apologizes to the man she accused."
> **Kael:** "Fine. I'll make sure of it. So... can she go?"
> **Sera:** *(marah)*
> **Sera:** "I'll speak to the head jailer."
> **Kael:** "Thanks, Sera!"

## Adegan 8 — Di Depan Penjara

Fade perlahan, jam 20:30. **Castle Approach**, di depan pintu Royal Prison.

> **Yuki:** "Thank you for getting me out."
> **Kael:** "It's Yuki, right? Listen. I know you're not a bad person. But in this country, attacking a man just because you think he's a thief isn't okay."
> **Yuki:** "I'm sorry... But I saw him take coins from people's pockets. Honestly, I'm surprised nobody noticed."
> **Kael:** "Hmm...."
> **Kael:** "Tell you what. Let's go to his house, so you can see the truth for yourself and be at ease."
> **Yuki:** "Very well. I don't know where else to go right now anyway."
> **Kael:** "Okay, follow me."

**Yuki bergabung** (level disamakan dengan Kael). *New Quest:* bawa Yuki ke **rumah Tobin**.

> *Berikutnya (belum dibuat):* ternyata Tobin memang mencopet, untuk membayar **bandit**. Kael dan Yuki melawan para bandit itu. Penyerahan pita ke Selene juga belum dibuat.

---

## Implementasi

| Bagian | Isi |
|---|---|
| **Script** | `python chapter1.py --save` (editor ditutup, jalankan setelah `prologue.py --save`). |
| **Flag** | Variabel 3 *Chapter 1*: 1 bebas di Guild, 2 Yuki di harbor, 3 daftar Ibu, 4 errand berjalan, 5 errand selesai (Selene turun), 6 beli pita, 7 keributan di pasar, 8 penjara, 9 malam di depan penjara, 10 ke rumah Tobin. |
| **Event** | Lion's Rest: pintu keluar mengarah ke harbor di tahap 1. Saltwind Harbor: Yuki dan cutscene-nya. Baker's Lane: daftar Ibu. Main Gate: jalan ke world map terkunci di tahap 1–4. Ashveil Residence: Ibu menerima belanjaan di tahap 4. |
| **Plugin** | `NovaChapterCard` (kartu judul bab, perintah `ChapterCard Chapter 1 \| The Adventure Begins`). `NovaSvEnemy`: musuh dengan sheet SV aktor (`<sv actor: Actor4_2>`, dibalik), stat dari class pada level aktor (`<as class: 2>` + `<match level: 1>`). |
| **Database** | Item 52 *Silk Ribbon* (120 Z). Enemy 39 *???* (Yuki). Troop 44 *Chapter 1: Yuki (market brawl)*: dua halaman (HP enemy / HP Kael ≤ 47%) yang memudarkan layar lalu menghentikan battle. |
| **Event baru** | Ashveil 1F: Selene. Ashveil 2F: *Little Sister* disembunyikan di tahap 5–10. Market: Tailor menjual pita di tahap 6, Yuki, Tobin, 8 warga, 4 prajurit (People3 #7) + kapten (People3 #6), cutscene. Prison Cells: Yuki, penjaga, Sera, Old Pell sementara di sel kanan bawah, cutscene. Castle Approach: Yuki, cutscene. |
| **Quest log** | Menu **Quests** (plugin `NovaQuests`, data `data/Quests.json` dari `quests.py`): *Chapter 1 - The Adventure Begins* mengikuti variabel 3, dengan tujuan saat ini dan ringkasan per tahap. Teksnya ada di `quest()` dalam `chapter1.py`. Tab *Sub Quests* sudah ada, diisi lewat `SUB_QUESTS` di `quests.py`. |
| **Papan kota** | `city_map.py --save`: papan peta di Grand Plaza (18,25) menampilkan gambar `img/pictures/Nova_CityMap.png` (dirender dari map distrik; jalankan ulang `python city_map.py` setelah map distrik berubah). Papan *Ashveil Residence* di Ember Lane (13,44). |
| **Lubang pintu** | Setiap event pintu `!Door1` di map luar punya tile lubang gelap di Outside_B (69 kotak, 71 lengkung untuk style 2/3), dipasang `town_kit` dan `door_holes.py --save`. |
| **Tes cepat** | Scene Select punya 7 titik Bab 1 (Guild, harbor, daftar Ibu, pulang ke Ibu dengan belanjaan, di Tailor dengan 120 Z, sel penjara, malam di depan penjara). Setting baru `gold=N`. |
| **Placeholder** | Sprite & wajah Yuki = `Actor4` indeks 1. Sprite & wajah Selene / Sera = `family1` indeks 0 / 1. Lokasi rumah Tobin belum ditentukan. |
