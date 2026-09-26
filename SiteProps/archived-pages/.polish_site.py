from pathlib import Path
from html import escape, unescape
import re
import textwrap
import math
import struct
import wave

ROOT = Path(__file__).parent
old_games = (ROOT / "games.html").read_text(encoding="utf-8")
old_about = (ROOT / "about.html").read_text(encoding="utf-8")
old_reserve = (ROOT / "reserve.html").read_text(encoding="utf-8")
old_media = (ROOT / "media.html").read_text(encoding="utf-8")

games = [
    ("resident-evil-2", "Resident Evil 2", "PlayStation", "1998", "Survival Horror", "1", "$2.99", "Available", "81Ei9ikAiWL._AC_UF1000,1000_QL80_.jpg"),
    ("metal-gear-solid", "Metal Gear Solid", "PlayStation", "1998", "Stealth Action", "1", "$2.99", "Available", "Metal-Gear-Solid-NTSC-PSX-FRONT.jpg"),
    ("tekken-3", "Tekken 3", "PlayStation", "1998", "Fighting", "1–2", "$2.99", "Available", "61Xr894A3-L.jpg"),
    ("final-fantasy-vii", "Final Fantasy VII", "PlayStation", "1997", "Role-Playing Game", "1", "$2.99", "Available", "Final_Fantasy_VII_Box_Art.jpg"),
    ("silent-hill-2", "Silent Hill 2", "PlayStation 2", "2001", "Survival Horror", "1", "$3.99", "Available", "Silent_Hill_2.jpg"),
    ("gta-3", "Grand Theft Auto III", "PlayStation 2", "2001", "Action", "1", "$3.99", "Available", "GTA3boxcover.jpg"),
    ("gran-turismo-3", "Gran Turismo 3: A-Spec", "PlayStation 2", "2001", "Racing", "1–2", "$3.99", "Available", None),
    ("super-mario-64", "Super Mario 64", "Nintendo 64", "1996", "Platform", "1", "$2.99", "Out on loan", None),
    ("goldeneye-007", "GoldenEye 007", "Nintendo 64", "1997", "First-Person Shooter", "1–4", "$2.99", "Available", None),
    ("sonic-adventure-2", "Sonic Adventure 2", "Dreamcast", "2001", "Platform", "1–2", "$2.99", "Available", "Sonic_adv_2_battle_box.png"),
    ("tony-hawks-pro-skater-2", "Tony Hawk’s Pro Skater 2", "Dreamcast", "2000", "Sports", "1–2", "$2.99", "Available", "Tony_Hawk's_Pro_Skater_2_cover.png"),
    ("halo", "Halo: Combat Evolved", "Xbox", "2001", "First-Person Shooter", "1–4", "$3.99", "Available", "Halo_-_Combat_Evolved_(XBox_version_-_box_art).jpg"),
    ("max-payne", "Max Payne", "PC", "2001", "Action", "1", "$2.99", "Available", "Maxpaynebox.jpg"),
    ("diablo-ii", "Diablo II", "PC", "2000", "Role-Playing Game", "1–8", "$2.99", "Available", "Diablo_II_Coverart.png"),
]
by_slug = {game[0]: game for game in games}


def indentation(text, spaces):
    return textwrap.indent(textwrap.dedent(text).strip(), " " * spaces)


def img(name, alt="", extra=""):
    return f'<img src="images/drawings/{name}.png" alt="{escape(alt)}"{extra}>'


def header():
    return indentation("""
        <header class="site-header">
            <div class="brand-row">
                <h1><img src="images/drawings/logo_pixel_rentals.png" alt="Pixel Rentals" loading="eager"></h1>
                <img src="images/drawings/face_1.png" alt="" class="brand-face">
                <p><strong>YOUR WEEKEND STARTS HERE.</strong><br>Open since 1996. Ask what is back today.</p>
            </div>
            <nav class="store-nav" aria-label="Main navigation">
                <img src="images/drawings/long_box_1_wavy.png" alt="">
                <div class="nav-links">
                    <a href="index.html">Home</a>
                    <a href="games.html">Games</a>
                    <a href="about.html">About</a>
                </div>
                <img src="images/drawings/arrow_curved_extra.png" alt="" class="nav-arrow">
            </nav>
        </header>
    """, 12)


def footer():
    return indentation("""
        <footer>
            <img src="images/drawings/divider_wavy.png" alt="" loading="lazy">
            <p><strong>PIXEL RENTALS</strong> — Games out. Good times in.</p>
            <p><a href="index.html">Home</a> · <a href="games.html">Games</a> · <a href="about.html">About &amp; reservations</a></p>
            <p><small>© Pixel Rentals · A fictional neighborhood rental store</small></p>
            <p><a href="#top">Back to top ↑</a></p>
        </footer>
    """, 12)


def page(title, main, body_class=""):
    body_attribute = f' class="{body_class}"' if body_class else ""
    return f'''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="style.css">
        <title>{escape(title)} | Pixel Rentals</title>
    </head>
    <body{body_attribute}>
        <div class="site-shell" id="top">
{header()}

            <main>
{indentation(main, 16)}
            </main>

{footer()}
        </div>
    </body>
</html>
'''


def cover_card(slug, home=False):
    slug, title, platform, year, genre, players, price, status, filename = by_slug[slug]
    if not filename:
        return ""
    loading = "eager" if home or slug in ("resident-evil-2", "metal-gear-solid", "tekken-3") else "lazy"
    button = "Read game notes" if not home else "See game notes"
    return indentation(f'''
        <article class="cover-card">
            <a href="games.html#note-{slug}"><img class="game-cover" src="images/games/{escape(filename, quote=True)}" alt="{escape(title, quote=True)} cover art" loading="{loading}"></a>
            <h3>{escape(title)}</h3>
            <p class="game-meta">{escape(platform)} · {year}</p>
            <p class="rental-price">{price} <small>/ 3 days</small></p>
            <a class="button" href="games.html#note-{slug}">{button}</a>
        </article>
    ''', 0)


def extract_section(source, start, end):
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), source, re.S)
    if not match:
        raise ValueError("Missing source section: " + start)
    return match.group(1)


def list_items(source):
    return [unescape(re.sub(r"<[^>]+>", "", item)).strip() for item in re.findall(r"<li>(.*?)</li>", source, re.S)]


def list_html(items, tag):
    return "<" + tag + ">\n" + "\n".join("    <li>" + escape(item) + "</li>" for item in items) + "\n</" + tag + ">"


def game_note(game):
    slug, title, platform, year, genre, players, price, status, filename = game
    source = (ROOT / "games" / (slug + ".html")).read_text(encoding="utf-8")
    if "<h3>About the Game</h3>" in source:
        description = list(re.findall(r"<p>(.*?)</p>", extract_section(source, "<h3>About the Game</h3>", "<h3>Rental Options</h3>"), re.S))
        intro = unescape(re.sub(r"<[^>]+>", "", description[0])).strip()
        features = list_items(extract_section(source, "<h3>Features</h3>", "<h3>How to play / objectives</h3>"))
        play = extract_section(source, "<h3>How to play / objectives</h3>", "<h3>Game Information</h3>")
        steps = list_items(play)
        play_intro = re.search(r"<p>(.*?)</p>", play, re.S)
        play_intro = unescape(re.sub(r"<[^>]+>", "", play_intro.group(1))).strip() if play_intro else ""
        facts = {}
        for key in ("Developer", "Publisher", "Age rating"):
            match = re.search(r"<th scope=\"row\">" + re.escape(key) + r"</th>\s*<td>(.*?)</td>", source, re.S)
            if match:
                facts[key] = unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        extra = "<p>" + escape(intro) + "</p>\n"
        extra += "<p>" + " · ".join("<strong>" + escape(k) + ":</strong> " + escape(v) for k, v in facts.items()) + "</p>\n"
        extra += "<h4>Features</h4>\n" + list_html(features, "ul") + "\n"
        extra += "<h4>How to play</h4>\n<p>" + escape(play_intro) + "</p>\n" + list_html(steps, "ol")
    else:
        features = list_items(extract_section(source, "<h3>What to try</h3>", "<h3>How to play</h3>"))
        steps = list_items(extract_section(source, "<h3>How to play</h3>", '<p><img src="../images/drawings/divider_wavy.png"'))
        extra = "<h4>What to try</h4>\n" + list_html(features, "ul") + "\n"
        extra += "<h4>How to play</h4>\n" + list_html(steps, "ol")
    result = f'''
        <details class="game-note" id="note-{slug}">
            <summary>{escape(title)} <small>— {escape(platform)}, {year} · {price} for 3 days</small></summary>
            <div class="note-text">
                {indentation(extra, 16).strip()}
            </div>
        </details>
    '''
    return indentation(result, 0)


home_main = f'''
    <!-- Welcome and featured rentals -->
    <section class="hero">
        <div class="drawing-frame">
            {img("long_box_2_frame")}
            <h2>Games for the weekend.</h2>
        </div>
        <div class="hero-intro">
            {img("arrow_1")}
            <p>Pick a game. Bring it back when you're done. Ask what's on the shelf today.</p>
            <a class="button" href="games.html">Browse every game →</a>
        </div>
    </section>

    <!-- New arrivals are on the homepage now. -->
    <section id="new" class="home-section">
        <div class="section-intro">
            {img("new_this_week", "New this week")}
            <p>Just back from the returns desk. Ask us to hold a copy at the counter.</p>
            {img("eyes_looking_down")}
        </div>
        <div class="cover-row">
{indentation(cover_card("gta-3", True), 12)}
{indentation(cover_card("halo", True), 12)}
{indentation(cover_card("max-payne", True), 12)}
        </div>
    </section>

    <!-- Console notes moved from the old consoles page. -->
    <section id="systems" class="home-section">
        <div class="section-heading">
            <h2>Browse by system</h2>
            {img("arrow_3")}
        </div>
        <p>Ask which controllers and memory cards come with your rental.</p>
        <ul class="system-list">
            <li><a href="games.html#ps1"><strong>PlayStation</strong></a><br>Sony · 1994 · RPGs, stealth, horror, and fighting. Four games.</li>
            <li><a href="games.html#ps2"><strong>PlayStation 2</strong></a><br>Sony · 2000 · Horror, city driving, and racing. Three games.</li>
            <li><a href="games.html#n64"><strong>Nintendo 64</strong></a><br>Nintendo · 1996 · Four controller ports, if we can find the pads. Two games.</li>
            <li><a href="games.html#dreamcast"><strong>Dreamcast</strong></a><br>Sega · 1999 · Arcade games look right at home. Two games.</li>
            <li><a href="games.html#xbox"><strong>Xbox</strong></a><br>Microsoft · 2001 · Halo is our Xbox shelf pick. One game.</li>
            <li><a href="games.html#pc"><strong>PC</strong></a><br>Windows 95/98/XP era · RPGs and a rainy crime story. Two games.</li>
        </ul>
    </section>

    <!-- Staff pick and the weekly deal -->
    <section class="home-section two-notes">
        <article>
            <div class="drawing-frame note-frame">
                {img("square_box_1_taped_note")}
                <div>
                    <h2>Tony's pick</h2>
                    <p><a href="games.html#note-metal-gear-solid"><strong>Metal Gear Solid</strong></a></p>
                    <p><em>“Read the codec calls.”</em><br>— Tony</p>
                </div>
            </div>
            {img("employee_pick", "Employee Pick")}
            <p>The stealth missions are good, and the story gets a little weird.</p>
        </article>
        <article>
            <div class="drawing-frame note-frame">
                {img("square_box_2_yellow_frame")}
                <div>
                    <h2>This weekend</h2>
                    <p><strong>Rent 2 games, get 1 free.</strong></p>
                    <p>The free rental is the lowest-priced game.</p>
                </div>
            </div>
            {img("dollar_face")}
            <details>
                <summary>Other deals at the counter</summary>
                <ul>
                    <li>Wednesday: 50% off the second standard rental. The lower-priced game gets the discount.</li>
                    <li>Horror Night: rent two horror games and take 50 cents off the second one.</li>
                    <li>Tuesday: one-day PlayStation and N64 rentals cost $1.99.</li>
                </ul>
                <p>Return all three games together for the three-for-two offer.</p>
            </details>
        </article>
    </section>

    <!-- Lists and a real HTML price table -->
    <section class="home-section shop-news">
        <div>
            <h2>Most rented this month</h2>
            <ol>
                <li>Silent Hill 2</li>
                <li>Halo: Combat Evolved</li>
                <li>Grand Theft Auto III</li>
                <li>Metal Gear Solid</li>
                <li>Resident Evil 2</li>
            </ol>
        </div>
        <div>
            <h2>A few house rules</h2>
            <ul>
                <li>Bring the case back with the disc.</li>
                <li>Return it by closing on the due date.</li>
                <li>No blowing into cartridges. We have a cleaning kit.</li>
                <li>Late fee: $1 per day.</li>
            </ul>
        </div>
        <div class="drawing-frame overdue-frame">
            {img("square_box_3_star_frame")}
            <div>
                <h2>Most overdue</h2>
                <p><a href="games.html#note-super-mario-64">Super Mario 64</a></p>
                <p>Still out on loan.</p>
            </div>
        </div>
    </section>

    <section class="home-section prices">
        {img("face_2")}
        <div>
            <h2>Rental prices</h2>
            <table>
                <caption>Prices in US dollars</caption>
                <thead><tr><th scope="col">Rental</th><th scope="col">1 day</th><th scope="col">3 days</th><th scope="col">7 days</th></tr></thead>
                <tbody>
                    <tr><th scope="row">Standard game</th><td>$1.99</td><td>$2.99</td><td>$4.99</td></tr>
                    <tr><th scope="row">New release</th><td>$2.99</td><td>$3.99</td><td>$5.99</td></tr>
                </tbody>
            </table>
            <p><small>New-release prices apply to games marked as new on the shelf.</small></p>
        </div>
        <a class="button" href="about.html#reservation">Ask us to hold a game →</a>
    </section>

    <section class="home-section media-preview">
        <img src="images/screenshots/gta3.jpg" alt="Grand Theft Auto III street scene" loading="lazy">
        <div>
            <h2>Media corner</h2>
            <p>Watch the game demo space and hear our little jukebox tune.</p>
            <a class="button" href="about.html#media">Visit the media corner →</a>
        </div>
        {img("face_3")}
    </section>
'''


catalogue = extract_section(old_games, '<h3 id="ps1">', '<h3>Most rented this month</h3>')
catalogue = '<h3 id="ps1">' + catalogue
catalogue = re.sub(r'href="games/([^"]+)\.html"', lambda m: 'href="#note-' + m.group(1) + '"', catalogue)
catalogue = re.sub(r'<table class="catalog-table" border="1" cellpadding="4">', '<table class="catalog-table">', catalogue)
catalogue = re.sub(r'<h3 id="([^"]+)">', r'<h3 class="shelf-title" id="\1">', catalogue)
catalogue = textwrap.dedent(catalogue).strip()

covers = "\n".join(cover_card(g[0]) for g in games if g[-1])
plain_games = "\n".join(f'<li><a href="#note-{g[0]}">{escape(g[1])}</a> · {escape(g[2])} · {g[3]}</li>' for g in games if not g[-1])
notes = "\n\n".join(game_note(g) for g in games)

games_main = f'''
    <section class="page-title">
        <div class="drawing-frame title-frame">
            {img("long_box_3_ribbon")}
            <h2>Games on the shelf</h2>
        </div>
        <p>Real covers from the rental shelf. Click a cover for game tips, then ask at the counter what is back today.</p>
    </section>

    <!-- Eleven real covers; three other titles remain in the catalogue below. -->
    <section class="catalog-covers">
        <h2>Browse the covers</h2>
        <div class="cover-row">
{indentation(covers, 12)}
        </div>
        <h3>More on the shelf</h3>
        <ul class="other-games">
{indentation(plain_games, 12)}
        </ul>
    </section>

    <section class="catalogue">
        <div class="section-heading">
            <h2>Full rental catalogue</h2>
            {img("arrow_2")}
        </div>
        <p>Jump to a shelf: <a href="#ps1">PlayStation</a> · <a href="#ps2">PlayStation 2</a> · <a href="#n64">Nintendo 64</a> · <a href="#dreamcast">Dreamcast</a> · <a href="#xbox">Xbox</a> · <a href="#pc">PC</a></p>
        <p>Prices are for three days. Copies come and go, so check availability at the counter.</p>
{indentation(catalogue, 8)}
    </section>

    <section class="rental-notes">
        <h2>Notes from the game counter</h2>
        <p>Open a title for its original shelf tips, features, and playing steps.</p>
{indentation(notes, 8)}
    </section>
'''


# Keep the unique story, staff, hours, contact, glossary, form, and media examples.
story = extract_section(old_about, '<h2>About Pixel Rentals</h2>', '</td>')
story = '<h2>About Pixel Rentals</h2>' + story
staff_table = extract_section(old_about, '<table border="1" cellpadding="6">', '<h3>Store Hours</h3>')
staff_table = '<table>' + staff_table
hours = extract_section(old_about, '<h3>Store Hours</h3>', '<h3>Store Rules</h3>')
hours = '<h3>Store hours</h3>' + hours
rules = extract_section(old_about, '<h3>Store Rules</h3>', '<h3>Game Ratings</h3>')
rules = '<h3>Store rules</h3>' + rules
glossary = extract_section(old_about, '<h3>Quick game glossary</h3>', '<p><img src="images/drawings/doodle_sticker_sheet.png"')
glossary = '<h3>Quick game glossary</h3>' + glossary
form = extract_section(old_reserve, '<form action="#" method="get">', '</form>')
form = '<form action="#reservation" method="get">' + form + '</form>'
form = re.sub(r'<button type="submit">', '<button class="button" type="submit">', form)
form = re.sub(r'<button type="reset">', '<button class="button" type="reset">', form)

about_main = f'''
    <!-- The story and practical information share one page. -->
    <section class="about-intro">
        <div>
{indentation(story, 12)}
        </div>
        {img("employee_pick", "", ' loading="lazy"')}
    </section>

    <section class="about-facts">
        <div>
{indentation(staff_table, 12)}
        </div>
        <div>
{indentation(hours, 12)}
        </div>
    </section>

    <section class="about-facts">
        <div>
{indentation(rules, 12)}
            <p>Please rewind VHS tapes before returning them. Memory card saves are your responsibility, so back them up if you can.</p>
            <p>Learn more about age ratings at the <a href="https://www.esrb.org/">ESRB website</a>.</p>
        </div>
        <div>
            <h3>Contact</h3>
            <address>Pixel Rentals<br>42 Cartridge Lane<br>Springfield, USA<br>Phone: (555) 010-1996<br>Email: <a href="mailto:hello@pixelrentals.example">hello@pixelrentals.example</a></address>
            <p><small>This store and its contact details are fictional.</small></p>
{indentation(glossary, 12)}
        </div>
    </section>

    <!-- A school-project form: it does not send a reservation to the store. -->
    <section id="reservation" class="reservation">
        <div class="section-heading">
            <h2>Try a reservation</h2>
            {img("arrow_3")}
        </div>
        <p>This is a form demo. It does not reserve a copy. In the store, call (555) 010-1996 to ask what is available.</p>
{indentation(form, 8)}
    </section>

    <!-- The audio is a small original tune; video waits for a student-made clip. -->
    <section id="media" class="media-corner">
        <div class="section-heading">
            <h2>Media corner</h2>
            {img("face_3")}
        </div>
        <div class="media-pair">
            <div>
                <h3>Video demo space</h3>
                <p>Our own game clip can go here later. For now, the poster shows the GTA III shelf pick.</p>
                <video controls preload="none" poster="images/screenshots/gta3.jpg">
                    Your browser does not support the video element.
                </video>
            </div>
            <div>
                <h3>Pixel Rentals jukebox</h3>
                <p>A short original arcade-style tune.</p>
                <audio controls preload="none">
                    <source src="media/audio/pixel-rentals-jingle.wav" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <p>Pat says the door bell is too loud. Nobody has fixed it yet.</p>
            </div>
        </div>
    </section>
'''

(ROOT / "index.html").write_text(page("Home", home_main, "home-page"), encoding="utf-8")
(ROOT / "games.html").write_text(page("Games", games_main), encoding="utf-8")
(ROOT / "about.html").write_text(page("About & Reservations", about_main), encoding="utf-8")

# A simple original six-second tune makes the audio example work offline.
audio_path = ROOT / "media" / "audio" / "pixel-rentals-jingle.wav"
audio_path.parent.mkdir(parents=True, exist_ok=True)
sample_rate = 22050
notes_hz = [523.25, 659.25, 783.99, 659.25, 880.0, 783.99, 523.25, 659.25]
with wave.open(str(audio_path), "wb") as output:
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(sample_rate)
    for frequency in notes_hz:
        for index in range(int(sample_rate * 0.65)):
            t = index / sample_rate
            envelope = min(1, t * 25) * max(0, 1 - t / 0.7)
            tone = 0.26 * math.sin(2 * math.pi * frequency * t)
            tone += 0.08 * math.sin(2 * math.pi * frequency * 2 * t)
            output.writeframesraw(struct.pack("<h", int(32767 * envelope * tone)))
