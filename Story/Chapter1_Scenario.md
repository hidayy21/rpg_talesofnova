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
| 9 | Rumah Tobin | Lantern Row (5), pintu (28,43) | 21:00 | Cutscene dengan **Greta**, gerbang kota terbuka |
| 10 | Para bandit | Briarwood - Entrance (30) → Briarwood (29) | Malam | Kristal heal & chest di Entrance, lalu clearing → cutscene, **battle bandit**, **Tainted Shard kedua** |
| 11 | Pulang lewat gerbang | Main Gate (23) | 23:00 | Cutscene, Tobin menyerahkan diri |
| 12 | Pulang tengah malam | Ashveil Residence (18) | 23:45 | Makan malam Yuki, kisah kakaknya, ajakan Kael, surat untuk Isolde |
| 13 | Pagi dan pamit | Ashveil 3F (20) → 1F (18) | 07:30 | Bangun di kamar (kasur = heal), sarapan, pita, sub quest **Souvenirs for Selene**, gerbang terbuka |

Selama urusan Bab 1 belum selesai, Kael **tidak bisa keluar dari ibu kota** (jalan ke world map di Main Gate):

> **Kael:** "Not yet. Mom's errand comes first." *(tahap 1–4)*
> **Kael:** "Not yet. I promised Selene her ribbon." *(tahap 6–7)*
> **Kael:** "Not yet. We should go and see Tobin first." *(tahap 10)*
> *(tahap 11–13: gerbang terbuka, untuk menyusul Tobin ke Briarwood)*
> **Kael:** "Not yet. Selene's still waiting for her ribbon." *(tahap 14–15; terbuka lagi dari tahap 16, setelah pamit)*

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

**Yuki bergabung** (level disamakan dengan Kael), lalu **tutorial party**: Frost Iai milik Yuki ber-elemen Ice, cek Equip/Skills di Menu; dan **tutorial Formation**: slot 1–2 baris depan, 3–4 baris belakang (melee −40%, damage fisik yang diterima −40%, Cane menyerang dengan magic), untuk sekarang berdua di depan, perintah Row di battle. *New Quest:* bawa Yuki ke **rumah Tobin**.

## Adegan 9 — Rumah Tobin

**Lantern Row, Ember Lane**, rumah di (28,43), beberapa pintu di sebelah timur rumah Ashveil. Kael mengetuk pintu. Fade singkat: Kael mundur satu langkah, Yuki di sebelah kanannya. Pintu terbuka dan **Greta**, istri Tobin, keluar ke depan pintu.

> **Kael:** "Tobin? It's Kael."
> **Greta:** "Kael? At this hour?"
> **Kael:** "Evening, Greta. Sorry it's so late. Is Tobin home?"
> **Greta:** "You just missed him. He went out a little while ago."
> **Greta:** "I watched him from the window... There were men waiting for him at the end of the lane. Men I've never seen before."
> **Kael:** *(!)* "Strangers? Where did he go with them?"
> **Greta:** "I don't know. He never tells me anymore."
> **Greta:** "These past months he's been going out at night, again and again. And when he comes home, he won't say a word about it."
> **Yuki:** "...Doesn't that sound suspicious to you?"
> **Kael:** "......"
> **Kael:** *(...)* "(Five months ago... Tobin never made it home from Briarwood that night.)"
> **Kael:** "(I never asked him what he was doing on the forest road after dark.)"
> **Kael:** "Greta. I think I know where he went."
> **Greta:** "You do?"
> **Kael:** "Briarwood. I'll bring him home. I did it once already, didn't I?"
> **Greta:** "...Then I'll wait at the Main Gate. Just like last time."
> **Greta:** "Wait. Take these. Tobin always kept a few for the road." *(dapat 3 Potion)*
> **Kael:** "Thank you, Greta."

*(Greta masuk, pintu tertutup.)*

> **Yuki:** "Briarwood?"
> **Kael:** "A forest west of the capital. The old cart road runs right through it."
> **Yuki:** "And the gate will let us out at night?"
> **Kael:** "For a Class 3 mage? It will."

*Quest Updated:* pergi ke **Briarwood** dan cari Tobin. Gerbang kota sekarang terbuka. Greta menunggu di pinggir jalan Main Gate ("Please, Kael. Bring him home.").

> *Catatan:* "Just like last time" menggemakan Prolog ("His wife's been at this gate since dawn").

## Adegan 10 — Para Bandit

**Briarwood, malam.** Para bandit dan Tobin sudah terlihat dari jalan: mereka duduk mengelilingi api unggun di clearing tempat gerobak Tobin hancur dulu. Begitu pemain sampai di baris jalan y19, cutscene dimulai. Kael dan Yuki berjalan ke tepi selatan clearing.

> **Bandit Leader:** "Short again, Tobin. That's the third time this month."
> **Tobin:** "I-I'll get the rest. I just need a few more days—"
> **Kael:** "Tobin!"
> **Tobin:** *(!)* "Kael? Wh-what are you doing here?"
> **Kael:** "I could ask you the same thing. What are you doing with these people?"
> *(semua bandit: !)*
> **Bandit Leader:** "Tobin, what is this? You led them straight to us?"
> **Tobin:** "No! I swear, I don't know why they're here!"
> **Yuki:** "Your friend seems quite at home with these men."
> **Kael:** "......"
> **Bandit:** "Hey, kid. Ever heard the saying? Curiosity killed the cat."
> **Tobin:** "Wait! Don't hurt them!" / "...At least don't hurt the boy."
> **Yuki:** *(keringat)* "Ouch."
> **Bandit Leader:** "Relax, Tobin. We'll only put them to sleep for a while."

Seorang bandit berjalan ke depan Kael ("Come quietly now—"). Kael menyerang balik dengan api (animasi *Fire One*, layar bergetar), bandit itu terpental dan **pingsan** (sprite `Damage2`).

> *(semua bandit dan Tobin: !)*
> **Bandit Leader:** "Why, you little—!"
> **Kael:** "Yuki, sorry. You don't have to get mixed up in this. Go."
> **Yuki:** "Heh. Not a chance. Don't keep all the fun to yourself. Besides, I have unfinished business with your friend."
> **Kael:** "Suit yourself, then."
> **Bandit Leader:** "Get them!"

**Battle: Bandit Leader + 2 Bandit Lackey** (troop 45). Disesuaikan untuk Kael dan Yuki level 2–3. Lackey lemah terhadap **Ice** (Frost Iai milik Yuki), Leader lemah terhadap **Fire** (milik Kael). Bisa kabur: tidak. Kalah: game over.

Setelah menang, semua bandit tergeletak pingsan. Kael menghampiri Tobin.

> **Kael:** "Tobin!"
> **Tobin:** "I'm sorry, Kael..."
> **Tobin:** "That night in Briarwood, five months ago... I wasn't hauling grain."
> **Tobin:** "It was their cargo. They paid me to bring it through the gate. Nobody checks an old carter's cart."
> **Tobin:** "Then that wolf came out of the dark. The cart, the crates, all of it... gone."
> **Tobin:** "And they wanted every coin of it back. With interest."
> **Kael:** "So the market..."
> **Tobin:** "...Yes. The young lady was right."
> **Kael:** "Why didn't you tell me? I'd have helped you."
> **Tobin:** "You'd just saved my life, lad. How could I tell you I'd lied to you the same day?"
> **Kael:** "......"
> **Yuki:** "I was told I have to apologize to you."
> **Yuki:** "...But I think it should be the other way around."
> **Tobin:** *(keringat)* "...I'm sorry I got you thrown in prison, miss."
> **Yuki:** "Accepted."

**Hook ke cerita utama.**

> **Yuki:** "What's in those crates, anyway? They were guarding them like treasure."

Kael membuka salah satu peti di (19,6).

> *Packed in straw: black crystals, cold to the touch.*
> **Kael:** *(!)* "These are..."
> **Kael:** "(The same as the shard from the wolf. The mana's flowing the wrong way.)"
> **Kael:** "Where did you get these?"
> **Bandit Leader:** "Ugh... Don't look at me. We just move the crates."
> **Bandit Leader:** "The client pays well and doesn't give names."
> **Kael:** "What client?"
> **Bandit Leader:** "Hooded types. Never once saw their faces. Ask all you want, kid. That's all I know."
> **Yuki:** "Kael. Do you know what those are?"
> **Kael:** "...I've seen one before. Right here, five months ago."

*Kael wraps one of the crystals in a cloth and slips it into his pocket.* **Dapat Tainted Shard kedua** (total 2).

> **Yuki:** "You're keeping one?"
> **Kael:** "Someone I know will want to see it. And I'd rather it didn't go missing on the way to the gate."
> **Kael:** "Come on. Let's take these three to the gate. The guard can deal with them. And with the crates."
> **Tobin:** "I'm coming too. It's time I told the guard everything."
> **Kael:** "...Alright."

> *Catatan:* kliennya adalah Order of Caelum (para "hooded types"), tapi belum ada yang tahu. Kebohongan Tobin di Prolog ("I didn't get a good look") kini terjawab.

## Adegan 11 — Pulang Lewat Gerbang

**Main Gate, 23:00.** Kael, Yuki, dan Tobin berjalan naik dari ujung jalan, ketiga bandit di belakang mereka. Penjaga gerbang menghampiri.

> **Gate Guard:** "Ashveil? At this hour? And who are... these?"
> **Kael:** "Bandits. We caught them in Briarwood. They've been running crates through this gate in Tobin's cart."
> **Gate Guard:** "Tobin's cart?"
> **Tobin:** "It's true. Every word. I carried their cargo. And when I lost it, I picked pockets in the market to pay them back."
> **Tobin:** "I'll answer for it."
> **Greta:** *(!)* "Tobin!" *(berlari ke Tobin)*
> **Greta:** "You fool... Why didn't you tell me?"
> **Tobin:** "I'm sorry, Greta."
> **Gate Guard:** "Picking pockets is a matter for the magistrate. But a man who walks a bandit crew to the gate himself... that will count for something."
> **Kael:** "I'll speak to Sera too. She'll hear the whole story."
> **Gate Guard:** "Sir Seraphine? Ha. Then he's in good hands."
> **Gate Guard:** "And those crates in the clearing... we'll send a patrol for them at first light."

*The guards lead the bandits through the gate.*

> **Tobin:** "Kael. Miss Yuki. Thank you."
> **Tobin:** "The next round at the Lion's Rest is on me... ...once I can afford it."
> **Kael:** "I'll hold you to that. Again."
> **Yuki:** "Make it two rounds."

Fade, 23:30. Yuki kembali menjadi follower.

> **Kael:** "...What a day."
> **Yuki:** "Is it always like this in your country?"
> **Kael:** "No. Usually it's quieter. I think."
> **Kael:** "Come on. Selene's still waiting for her ribbon. And you need somewhere to sleep tonight."

*Quest Updated:* bawa Silk Ribbon pulang ke Selene.

## Adegan 12 — Pulang Tengah Malam

**Ashveil Residence 1F, 23:45.** Ibu masih terjaga di ruang tengah, dekat pintu. Ia maju selangkah, Kael dan Yuki juga.

> **Mother:** "Kaelen Ashveil." / "Do you have any idea what time it is?"
> **Kael:** "...Late?"
> **Mother:** "Selene waited for you all evening. She went to bed an hour ago."
> **Kael:** "(The ribbon... It'll have to wait until morning.)"
> **Mother:** "And who is this?"
> **Yuki:** "Good evening. My name is Ryuzetsu Yuki. I've come from Hōrai. Forgive me for calling so late."
> **Kael:** "She's only just arrived in the capital, Mom. She's got nowhere to stay tonight."
> **Mother:** "Then she stays here, of course." / "From Hōrai... You have come a long way, Yuki. Have the two of you eaten?"
> *(Kael dan Yuki: ...)*
> **Mother:** "I thought not." / "Sera came by for supper tonight. She waited for you as long as she could."
> **Kael:** *(keringat)* "(Sera was here...? I hope she didn't mention the prison.)"
> **Mother:** "I kept your bowl aside, Kaelen, and there's just enough left for one more." / "Sit down, both of you. The stew is still warm."

Di meja dapur: **makanan Benua Barat pertama Yuki** (Story Bible, Bab 1 poin 6). Di Hōrai juga ada stew, tapi rasanya lain.

> **Yuki:** "Stew... We have stew in Hōrai as well." — **Mother:** "Oh? Is it like this one?"
> **Yuki:** "...Not at all. Ours is lighter, with miso and fish. This one is rich. Heavy, in a good way."
> **Mother:** "Then have another bowl."
> **Kael:** "Wait till you try her apple pie." — **Mother:** "There is no apple pie, Kaelen. Not for boys who come home at midnight."
> **Mother:** "The guest room on the second floor is ready for you, Yuki. Goodnight, you two."

Ibu berjalan ke tangga (lewat lantai, tidak menembus dinding) sementara obrolan berlanjut. **Kisah kakak Yuki:**

> **Yuki:** "My brother. Homura. Half a year ago he left Hōrai in the night. They say he took a ship west."
> **Kael:** "Your brother? Then he'll be glad to see you." — **Yuki:** "...He won't be."
> **Yuki:** "When I find him, I will settle what he did. That is all I'll say about it tonight."
> **Kael:** "I'm going to see the world anyway. If your brother's out there, our road will cross his sooner or later. Come with me."
> **Yuki:** "You'd travel with a woman who drew her sword on you this morning?"
> **Kael:** "You'd travel with the guy who beat you?"
> **Yuki:** "Beat me? The guards stopped that fight." *(Kael: kesal)*
> **Yuki:** "Goodnight, Kael. Thank you for the stew." — **Kael:** "...Goodnight."

Kael sendirian menulis **surat untuk Isolde** (scroll text), lalu tidur.

## Adegan 13 — Pagi dan Pamit

**Ashveil 3F, 07:30.** Kael bangun di sebelah kasurnya.

> **Kael:** "Alright. Today's the day. Time to start the journey."

*Tutorial:* kasur di rumah bisa dipakai untuk istirahat (HP & MP penuh) kapan saja. Pemain turun sendiri ke lantai 1.

**1F.** Kael kesiangan: Ibu, Selene, dan Yuki sudah sarapan di meja (ada hidangan di meja). Selene dan Yuki sudah berkenalan.

> **Selene:** "Brother! You overslept!" — **Mother:** "Good morning, sleepyhead. Come and sit down. Breakfast is getting cold."
> **Selene:** "Yuki's been telling us everything. The market, the prison, the bandits!" — **Kael:** "...Everything?" — **Yuki:** "Most of it."
> **Selene:** "She says the guards had to stop your fight because you were losing." — **Kael:** *(kesal)* "That's not what happened." — **Yuki:** "Mm."
> **Kael:** "One silk ribbon. Midnight blue." *(pita diserahkan, sub quest selesai)*
> **Selene:** "It's... it's actually midnight! Not navy! Not sky blue! Thank you, Brother!"
> **Mother:** "Don't look so solemn about it. It's not as if you're leaving forever. You'll be back the moment you run out of clean clothes." *(meta-joke Story Bible)*
> **Selene:** "Then bring me something back! From every town you visit! Every. Single. One."

*New Quest: **Souvenirs for Selene*** (sub quest oleh-oleh).

> **Mother:** "Yuki, dear. Look after him for me." — **Yuki:** "I will. Someone has to."

Gerbang kota terbuka (tahap 16). Saat pemain bisa bergerak lagi, hidangan di meja sudah hilang dan Ibu kembali ke dapur.

## Briarwood - Entrance (map 30)

Hutan berdaun lebar antara World Map dan Briarwood (`map_briarwood_entrance.py`). Masuk dari bawah (dari World Map, 54,38), keluar ke Briarwood di atas; keluar dari Briarwood ke bawah juga kembali ke sini.

- **Kristal heal** (19,5), tepat sebelum Briarwood: HP & MP seluruh party penuh, bisa dipakai berkali-kali.
- **Chest** di dataran tinggi kanan (22,10), naik lewat tangga batu (21,15–16): 2 Hi-Potion, 2 Magic Water.
- Papan penunjuk di jalan masuk. Lantai hutan memakai autotile *Bush* (dibuat tidak bisa dilewati di tileset Outside).

---

## Implementasi

| Bagian | Isi |
|---|---|
| **Script** | `python chapter1.py --save` (editor ditutup, jalankan setelah `prologue.py --save`). |
| **Flag** | Variabel 3 *Chapter 1*: 1 bebas di Guild, 2 Yuki di harbor, 3 daftar Ibu, 4 errand berjalan, 5 errand selesai (Selene turun), 6 beli pita, 7 keributan di pasar, 8 penjara, 9 malam di depan penjara, 10 ke rumah Tobin, 11 ke Briarwood (gerbang terbuka), 12 adegan bandit, 13 di Main Gate, 14 pulang ke Selene (gerbang terkunci lagi). |
| **Event** | Lion's Rest: pintu keluar mengarah ke harbor di tahap 1. Saltwind Harbor: Yuki dan cutscene-nya. Baker's Lane: daftar Ibu. Main Gate: jalan ke world map terkunci di tahap 1–4. Ashveil Residence: Ibu menerima belanjaan di tahap 4. |
| **Plugin** | `NovaChapterCard` (kartu judul bab, perintah `ChapterCard Chapter 1 \| The Adventure Begins`). `NovaSvEnemy`: musuh dengan sheet SV aktor (`<sv actor: Actor4_2>`, dibalik), stat dari class pada level aktor (`<as class: 2>` + `<match level: 1>`). |
| **Database** | Item 52 *Silk Ribbon* (120 Z). Enemy 39 *???* (Yuki). Troop 44 *Chapter 1: Yuki (market brawl)*: dua halaman (HP enemy / HP Kael ≤ 47%) yang memudarkan layar lalu menghentikan battle. Enemy 40 *Bandit Lackey* (220 HP, lemah Ice, battler `Rogue`), enemy 41 *Bandit Leader* (480 HP, lemah Fire, battler `Swordsman`), troop 45 *Chapter 1: Bandits (Briarwood)*. |
| **Event Bab 1 lanjutan** | Lantern Row: pintu rumah Tobin (28,43) memutar adegan Greta di tahap 10, plus Greta dan Yuki. Briarwood: api unggun (`!Flame` 2, dengan cahaya), 3 bandit (`Evil` 0/4), Bandit Leader (`Evil` 1), Tobin, Yuki, 4 pemicu di jalan y19, cutscene. Bandit pingsan memakai `Damage2` 0/1/7. Main Gate: Greta (tahap 11–13), Tobin, Yuki, 3 bandit, cutscene. Selama cutscene, follower disembunyikan dan Yuki diperankan event. |
| **Event baru** | Ashveil 1F: Selene. Ashveil 2F: *Little Sister* disembunyikan di tahap 5–10. Market: Tailor menjual pita di tahap 6, Yuki, Tobin, 8 warga, 4 prajurit (People3 #7) + kapten (People3 #6), cutscene. Prison Cells: Yuki, penjaga, Sera, Old Pell sementara di sel kanan bawah, cutscene. Castle Approach: Yuki, cutscene. |
| **Quest log** | Menu **Quests** (plugin `NovaQuests`, data `data/Quests.json` dari `quests.py`): *Chapter 1 - The Adventure Begins* mengikuti variabel 3, dengan tujuan saat ini dan ringkasan per tahap. Teksnya ada di `quest()` dalam `chapter1.py`. Tab *Sub Quests* sudah ada, diisi lewat `SUB_QUESTS` di `quests.py`. |
| **Papan kota** | `city_map.py --save`: papan peta di Grand Plaza (18,25) menampilkan gambar `img/pictures/Nova_CityMap.png` (dirender dari map distrik; jalankan ulang `python city_map.py` setelah map distrik berubah). Papan *Ashveil Residence* di Ember Lane (13,44). |
| **Lubang pintu** | Setiap event pintu `!Door1` di map luar punya tile lubang gelap di Outside_B (69 kotak, 71 lengkung untuk style 2/3), dipasang `town_kit` dan `door_holes.py --save`. |
| **Tes cepat** | Scene Select punya 9 titik Bab 1 (Guild, harbor, daftar Ibu, pulang ke Ibu dengan belanjaan, di Tailor dengan 120 Z, sel penjara, malam di depan penjara, pintu rumah Tobin, jalan Briarwood). Setting `gold=N`, serta `join=2` (aktor 2 masuk party pada level Kael) dan `level=N` (level Kael). |
| **Placeholder** | Sprite & wajah Yuki = `Actor4` indeks 1. Sprite & wajah Selene / Sera = `family1` indeks 0 / 1. Sprite Greta = `People4` indeks 7 (belum punya wajah). Rumah Tobin = rumah terkunci di Ember Lane (28,43), adegannya di depan pintu. |
