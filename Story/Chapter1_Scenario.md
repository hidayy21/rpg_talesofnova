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

Selama errand belum selesai, Kael **tidak bisa keluar dari ibu kota** (jalan ke world map di Main Gate):

> **Kael:** "Not yet. Mom's errand comes first."

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

Errand selesai, Kael boleh keluar dari ibu kota. Kalau belanjaan belum lengkap, Ibu mengingatkan isi daftarnya.

> *Catatan:* janji pamit ini menyiapkan adegan **pamit ke ibu dan adik** (Story Bible, Bab 1 poin 6).

---

## Implementasi

| Bagian | Isi |
|---|---|
| **Script** | `python chapter1.py --save` (editor ditutup, jalankan setelah `prologue.py --save`). |
| **Flag** | Variabel 3 *Chapter 1*: 1 bebas di Guild, 2 Yuki di harbor, 3 daftar Ibu, 4 errand berjalan, 5 errand selesai. |
| **Event** | Lion's Rest: pintu keluar mengarah ke harbor di tahap 1. Saltwind Harbor: Yuki dan cutscene-nya. Baker's Lane: daftar Ibu. Main Gate: jalan ke world map terkunci di tahap 1–4. Ashveil Residence: Ibu menerima belanjaan di tahap 4. |
| **Plugin** | `NovaChapterCard` (kartu judul bab, perintah `ChapterCard Chapter 1 \| The Adventure Begins`). |
| **Quest log** | Menu **Quests** (plugin `NovaQuests`, data `data/Quests.json` dari `quests.py`): *Chapter 1 - The Adventure Begins* mengikuti variabel 3, dengan tujuan saat ini dan ringkasan per tahap. Teksnya ada di `quest()` dalam `chapter1.py`. Tab *Sub Quests* sudah ada, diisi lewat `SUB_QUESTS` di `quests.py`. |
| **Papan kota** | `city_map.py --save`: papan peta di Grand Plaza (18,25) menampilkan gambar `img/pictures/Nova_CityMap.png` (dirender dari map distrik; jalankan ulang `python city_map.py` setelah map distrik berubah). Papan *Ashveil Residence* di Ember Lane (13,44). |
| **Lubang pintu** | Setiap event pintu `!Door1` di map luar punya tile lubang gelap di Outside_B (69 kotak, 71 lengkung untuk style 2/3), dipasang `town_kit` dan `door_holes.py --save`. |
| **Tes cepat** | Scene Select punya 4 titik Bab 1 (Guild, harbor, daftar Ibu, pulang ke Ibu dengan belanjaan). |
| **Placeholder** | Sprite & wajah Yuki = `Actor4` indeks 1. |
