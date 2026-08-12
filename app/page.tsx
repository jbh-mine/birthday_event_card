"use client";

import { useMemo, useRef, useState } from "react";

const reasons = [
  "당신이 웃으면 집 안의 공기가 달라져요.",
  "언제나 가족의 마음을 먼저 살펴줘서 고마워요.",
  "평범한 하루도 당신과 함께라면 기념일이 돼요.",
  "내가 흔들릴 때 가장 단단한 내 편이 되어줘요.",
  "당신의 다정함은 오래 남는 온기를 만들어요.",
  "사소한 이야기도 진심으로 들어주는 사람이에요.",
  "당신 덕분에 ‘우리’라는 말이 참 좋아졌어요.",
  "힘든 날에도 다시 웃을 이유를 찾아줘요.",
  "누군가를 사랑하는 법을 매일 보여줘요.",
  "당신의 솔직함까지도 사랑스러워요.",
  "나보다 나를 더 잘 알아봐 주는 순간이 있어요.",
  "함께 걷는 길에서는 서두르지 않아도 돼요.",
  "당신이 만든 추억은 시간이 갈수록 더 빛나요.",
  "작은 행복을 발견하는 눈을 가졌어요.",
  "당신 곁에서는 나도 더 좋은 사람이 되고 싶어요.",
  "기쁜 일은 두 배로, 슬픈 일은 반으로 만들어줘요.",
  "나의 서툰 마음까지 이해해 주려고 해요.",
  "우리 가족의 중심에는 늘 당신의 사랑이 있어요.",
  "당신과 나눈 농담은 몇 번을 떠올려도 웃겨요.",
  "오늘의 우리를 여기까지 데려와 줬어요.",
  "매일 다른 모습으로 또 사랑하게 해요.",
  "당신의 용기는 주변 사람까지 용감하게 만들어요.",
  "무엇이 중요한지 잊지 않게 해줘요.",
  "당신과 함께한 계절은 모두 특별해졌어요.",
  "말없이 건네는 눈빛에도 마음이 담겨 있어요.",
  "내일을 함께 상상할 수 있는 사람이에요.",
  "수많은 선택 끝에 서로를 선택한 일이 자랑스러워요.",
  "당신의 꿈을 듣는 시간이 좋아요.",
  "지친 날에도 따뜻함을 잃지 않아요.",
  "우리만 알아듣는 말들이 하나씩 늘어가요.",
  "변해가는 모습까지 함께 사랑할 수 있어요.",
  "당신의 하루를 가장 가까이에서 응원할 수 있어 행복해요.",
  "가끔은 아이처럼, 가끔은 누구보다 현명해요.",
  "내 인생의 가장 좋은 장면들엔 늘 당신이 있어요.",
  "당신의 이름은 내게 ‘집’과 같은 뜻이에요.",
  "함께 늙어간다는 약속이 기대돼요.",
  "마흔의 당신은 지금까지 중 가장 아름다워요.",
  "앞으로의 당신도 분명 눈부실 거예요.",
  "이번 생에 당신을 만난 건 가장 큰 행운이에요.",
  "그리고 마지막 이유는—그냥, 당신이 당신이라서.",
];

const characterSeries = [
  {
    series: "플레이모빌",
    slug: "playmobil",
    characters: [
      ["탐험가", "explorer"], ["신부", "bride"], ["신랑", "groom"], ["셰프", "chef"], ["의사", "doctor"],
      ["우주비행사", "astronaut"], ["소방관", "firefighter"], ["정원사", "gardener"], ["뮤지션", "musician"], ["공주", "princess"],
    ],
  },
  {
    series: "귀멸의 칼날",
    slug: "demon-slayer",
    characters: [
      ["탄지로", "tanjiro"], ["네즈코", "nezuko"], ["젠이츠", "zenitsu"], ["이노스케", "inosuke"], ["렌고쿠", "rengoku"],
      ["시노부", "shinobu"], ["기유", "giyu"], ["미츠리", "mitsuri"], ["무이치로", "muichiro"], ["텐겐", "tengen"],
    ],
  },
  {
    series: "주술회전",
    slug: "jujutsu-kaisen",
    characters: [
      ["고죠 사토루", "gojo"], ["이타도리 유지", "yuji"], ["후시구로 메구미", "megumi"], ["쿠기사키 노바라", "nobara"], ["옷코츠 유타", "yuta"],
      ["젠인 마키", "maki"], ["판다", "panda"], ["이누마키 토게", "inumaki"], ["나나미 켄토", "nanami"], ["스쿠나", "sukuna"],
    ],
  },
  {
    series: "나의 히어로 아카데미아",
    slug: "my-hero-academia",
    characters: [
      ["데쿠", "deku"], ["바쿠고", "bakugo"], ["토도로키", "todoroki"], ["우라라카", "uraraka"], ["올마이트", "all-might"],
      ["츠유", "tsuyu"], ["이이다", "iida"], ["키리시마", "kirishima"], ["아이자와", "aizawa"], ["호크스", "hawks"],
    ],
  },
] as const;

const cardCharacters = Array.from({ length: 40 }, (_, index) => {
  const group = characterSeries[index % characterSeries.length];
  const characterIndex = Math.floor(index / characterSeries.length);
  const [name, characterSlug] = group.characters[characterIndex];
  return {
    name: `${group.series} ${name}`,
    src: `./characters/${group.slug}-${String(characterIndex + 1).padStart(2, "0")}-${characterSlug}.webp`,
  };
});

const catMoments = [
  {
    kicker: "A TINY GUEST",
    copy: "첫 번째 고양이도 당신의 마흔을 축하하러 왔어요.",
    photos: [
      { src: "./cats/cat-01-orange-tabby.webp", alt: "동그란 눈으로 올려다보는 아기 치즈 고양이" },
      { src: "./cats/cat-02-tuxedo.webp", alt: "버건디 나비넥타이를 한 턱시도 고양이" },
    ],
  },
  {
    kicker: "PAWSE & SMILE",
    copy: "마음을 열다가 잠깐, 고양이 눈빛 한 번 보고 가요.",
    photos: [
      { src: "./cats/cat-03-ragdoll.webp", alt: "파란 눈의 복슬복슬한 랙돌 아기 고양이" },
      { src: "./cats/cat-04-british-shorthair.webp", alt: "앞발을 살짝 들어 인사하는 회색 고양이" },
    ],
  },
  {
    kicker: "ONE MORE MEOW",
    copy: "마지막 열 장을 앞두고 작은 응원을 보냅니다.",
    photos: [
      { src: "./cats/cat-05-calico.webp", alt: "편안하게 몸을 말고 누운 삼색 아기 고양이" },
      { src: "./cats/cat-06-black-kitten.webp", alt: "금빛 리본을 한 까만 아기 고양이" },
    ],
  },
] as const;

const catSoundSources = [
  "./sounds/cat-meow-soft.wav",
  "./sounds/cat-meow-curious.wav",
  "./sounds/cat-chirp.wav",
] as const;

const catSoundCards = new Map([
  [4, 0],
  [13, 1],
  [22, 2],
  [31, 0],
]);

const sparkles = Array.from({ length: 28 }, (_, index) => ({
  id: index,
  left: `${(index * 37 + 11) % 100}%`,
  top: `${(index * 53 + 7) % 92}%`,
  delay: `${(index % 9) * 0.42}s`,
  size: `${2 + (index % 4)}px`,
}));

export default function Home() {
  const [opened, setOpened] = useState<number[]>([]);
  const [finale, setFinale] = useState(false);
  const [filmStarted, setFilmStarted] = useState(false);
  const [filmPlaying, setFilmPlaying] = useState(false);
  const [filmEnded, setFilmEnded] = useState(false);
  const [catSoundEnabled, setCatSoundEnabled] = useState(true);
  const filmRef = useRef<HTMLVideoElement>(null);

  const openedSet = useMemo(() => new Set(opened), [opened]);
  const progress = Math.round((opened.length / reasons.length) * 100);

  const playCatSound = (soundIndex: number) => {
    if (!catSoundEnabled || filmPlaying) return;
    const sound = new Audio(catSoundSources[soundIndex]);
    sound.volume = 0.24;
    void sound.play().catch(() => undefined);
  };

  const reveal = (index: number) => {
    if (openedSet.has(index)) return;
    setOpened((current) => [...current, index]);
    const soundIndex = catSoundCards.get(index);
    if (soundIndex !== undefined) playCatSound(soundIndex);
  };

  const revealAll = () => {
    if (opened.length === reasons.length) return;
    setOpened(reasons.map((_, index) => index));
    playCatSound(2);
  };

  const playFilm = async () => {
    const film = filmRef.current;
    if (!film) return;
    if (filmEnded) film.currentTime = 0;
    setFilmStarted(true);
    setFilmEnded(false);
    try {
      await film.play();
    } catch {
      setFilmStarted(false);
    }
  };

  return (
    <main className="page">
      <div className="opening-scene" aria-hidden="true">
        <div className="opening-halo" />
        <p>FOR THE MOST BEAUTIFUL SEASON</p>
        <strong>40</strong>
        <span>당신을 위한 이야기가 시작됩니다</span>
      </div>

      <div className="ambient" aria-hidden="true">
        <div className="aurora aurora-one" />
        <div className="aurora aurora-two" />
        {sparkles.map((sparkle) => (
          <i
            className="sparkle"
            key={sparkle.id}
            style={{
              left: sparkle.left,
              top: sparkle.top,
              width: sparkle.size,
              height: sparkle.size,
              animationDelay: sparkle.delay,
            }}
          />
        ))}
      </div>

      <nav className="nav" aria-label="생일 편지 둘러보기">
        <a className="wordmark" href="#top" aria-label="처음으로">
          <span className="wordmark-dot" />
          OUR FORTY
        </a>
        <div className="nav-links">
          <a href="#reasons">마음 40개</a>
          <a href="#future">앞으로의 우리</a>
          <a href="#film">1분 영화</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <p className="eyebrow">A LETTER FOR YOUR 40TH BIRTHDAY</p>
        <div className="hero-number" aria-label="마흔">
          <span>4</span><span>0</span>
        </div>
        <div className="orbit orbit-one" aria-hidden="true">사랑 · 웃음 · 우리 · 오늘 ·</div>
        <div className="orbit orbit-two" aria-hidden="true">그리고 앞으로의 모든 계절 ·</div>
        <h1>
          당신의 마흔 번째 계절이<br />
          <em>눈부시게 시작되기를.</em>
        </h1>
        <p className="hero-copy">
          마흔은 지나온 날들의 끝이 아니라,<br className="mobile-break" />
          우리가 함께 써 내려갈 가장 아름다운 다음 장이에요.
        </p>
        <a className="primary-button" href="#reasons">
          <span>마음을 열어보기</span>
          <b aria-hidden="true">↓</b>
        </a>
        <p className="date-mark">1986 — 2026 · FORTY YEARS OF YOU</p>
      </section>

      <section className="prologue section-shell">
        <div className="chapter-label">CHAPTER 01 · TO YOU</div>
        <p className="giant-quote" aria-hidden="true">“</p>
        <blockquote>
          세상에는 수많은 날이 있지만,<br />
          오늘은 <strong>당신이 태어난 날</strong>이라서<br />
          내게 가장 특별한 하루예요.
        </blockquote>
        <p className="prologue-note">
          긴 시간 동안 수많은 사람에게 사랑을 건네온 당신에게,<br />
          오늘만큼은 그 사랑이 모두 돌아오기를 바라요.
        </p>
      </section>

      <section className="reasons-section section-shell" id="reasons">
        <div className="section-heading">
          <div>
            <div className="chapter-label">CHAPTER 02 · 40 REASONS</div>
            <h2>내가 당신을 사랑하는<br /><em>마흔 가지 이유</em></h2>
          </div>
          <div className="progress-card">
            <span>{opened.length.toString().padStart(2, "0")} / 40</span>
            <div
              className="progress-track"
              role="progressbar"
              aria-label="열어본 사랑의 이유"
              aria-valuemin={0}
              aria-valuemax={40}
              aria-valuenow={opened.length}
            >
              <i style={{ width: `${progress}%` }} />
            </div>
            <button onClick={revealAll} type="button" disabled={opened.length === 40}>
              {opened.length === 40 ? "모두 열었어요" : "한번에 모두 열기"}
            </button>
          </div>
        </div>

        <div className="reason-controls">
          <p className="tap-guide">반짝이는 숫자를 하나씩 눌러보세요. 몇몇 카드에는 고양이가 숨어 있어요.</p>
          <button
            className={`cat-sound-toggle ${catSoundEnabled ? "is-on" : ""}`}
            type="button"
            aria-pressed={catSoundEnabled}
            onClick={() => setCatSoundEnabled((enabled) => !enabled)}
          >
            <span aria-hidden="true">♪</span>
            고양이 소리 {catSoundEnabled ? "켜짐" : "꺼짐"}
          </button>
        </div>

        <div className="reason-collection">
          {Array.from({ length: 4 }, (_, chapterIndex) => {
            const start = chapterIndex * 10;
            const catMoment = catMoments[chapterIndex];
            return (
              <div className="reason-chapter" key={`reason-chapter-${chapterIndex + 1}`}>
                <div className="reason-grid">
                  {reasons.slice(start, start + 10).map((reason, offset) => {
                    const index = start + offset;
                    const isOpen = openedSet.has(index);
                    const character = cardCharacters[index];
                    return (
                      <button
                        className={`reason-card ${isOpen ? "is-open" : ""}`}
                        key={reason}
                        onClick={() => reveal(index)}
                        type="button"
                        aria-label={`${index + 1}번째 사랑의 이유${isOpen ? `: ${reason}. ${character.name} 캐릭터` : " 열기"}`}
                        aria-expanded={isOpen}
                      >
                        <span className="card-inner">
                          <span className="card-face card-front">
                            <span className="reason-number">{String(index + 1).padStart(2, "0")}</span>
                            <span className="reason-prompt">마음을 열어보세요</span>
                            <span className="reason-star" aria-hidden="true">✦</span>
                          </span>
                          <span className="card-face card-back">
                            {isOpen && (
                              <>
                                <span className="character-art" aria-hidden="true">
                                  <img src={character.src} alt="" loading="lazy" decoding="async" />
                                </span>
                                <span className="reason-divider" aria-hidden="true" />
                                <span className="reason-text">{reason}</span>
                              </>
                            )}
                            <span className="reason-mark" aria-hidden="true">♥</span>
                          </span>
                        </span>
                        {isOpen && (
                          <span className="card-burst" aria-hidden="true">
                            <i /><i /><i /><i /><i /><i />
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {catMoment && (
                  <aside className={`cat-interlude cat-interlude-${chapterIndex + 1}`} aria-label="고양이 축하 사진">
                    <figure className="cat-photo cat-photo-one">
                      <img src={catMoment.photos[0].src} alt={catMoment.photos[0].alt} loading="lazy" decoding="async" />
                    </figure>
                    <div className="cat-message">
                      <span>{catMoment.kicker}</span>
                      <p>{catMoment.copy}</p>
                      <i aria-hidden="true">meow · meow</i>
                    </div>
                    <figure className="cat-photo cat-photo-two">
                      <img src={catMoment.photos[1].src} alt={catMoment.photos[1].alt} loading="lazy" decoding="async" />
                    </figure>
                  </aside>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className="future section-shell" id="future">
        <div className="future-glow" aria-hidden="true" />
        <div className="chapter-label">CHAPTER 03 · THE NEXT 40</div>
        <p className="future-kicker">2046년, 어느 따뜻한 저녁</p>
        <h2>스무 해 뒤의 우리가<br /><em>오늘을 기억한다면</em></h2>
        <div className="timeline" aria-label="앞으로 함께할 시간">
          <span>40</span><i /><b>함께 걷는 중</b><i /><span>60</span>
        </div>
        <p className="future-copy">
          우리는 지금보다 조금 더 천천히 걷고, 조금 더 자주 웃고,<br />
          오늘의 걱정들이 사실은 아주 작았다고 말하겠지요.<br />
          그래도 한 가지는 지금과 똑같을 거예요.<br />
          <strong>나는 여전히 당신의 가장 가까운 편이라는 것.</strong>
        </p>
      </section>

      <section className="film-section section-shell" id="film">
        <div className="film-copy">
          <div className="chapter-label">CHAPTER 04 · A FILM FOR YOU</div>
          <p className="film-kicker">사진 없이, 마음만으로 만든 1분</p>
          <h2>당신의 마흔을 위한<br /><em>아주 작은 영화</em></h2>
          <p>
            조용한 빛과 문장, 그리고 오직 이 순간을 위해 만든 음악에<br />
            당신에게 꼭 전하고 싶었던 마음을 담았어요.
          </p>
          <div className="film-sound-note"><span aria-hidden="true">♪</span> 소리를 켜면 마음이 더 잘 들려요</div>
        </div>

        <div className={`film-frame ${filmPlaying ? "is-playing" : ""}`}>
          <video
            ref={filmRef}
            playsInline
            preload="metadata"
            poster="./birthday-film-poster.jpg"
            controls={filmStarted}
            onPlay={() => setFilmPlaying(true)}
            onPause={() => setFilmPlaying(false)}
            onEnded={() => {
              setFilmPlaying(false);
              setFilmEnded(true);
            }}
            aria-label="당신의 마흔을 축하하는 1분 생일 영화"
          >
            <source src="./birthday-film.mp4" type="video/mp4" />
          </video>

          {(!filmStarted || filmEnded) && (
            <button className="film-launch" type="button" onClick={playFilm}>
              <span className="play-orb" aria-hidden="true"><i>▶</i></span>
              <strong>{filmEnded ? "한 번 더 보기" : "1분 영화 시작하기"}</strong>
              <small>탭하면 음악과 함께 재생됩니다</small>
            </button>
          )}

          <div className="film-runtime" aria-hidden="true">
            <span>ORIGINAL BIRTHDAY FILM</span>
            <b>01:00</b>
          </div>
        </div>
      </section>

      <section className="finale section-shell">
        <div className="envelope-wrap">
          {!finale ? (
            <button className="envelope" onClick={() => setFinale(true)} type="button">
              <span className="seal">40</span>
              <span className="envelope-label">마지막 편지 열기</span>
            </button>
          ) : (
            <article className="letter">
              <p className="letter-date">오늘, 당신의 마흔 번째 생일에</p>
              <h2>사랑하는 당신에게.</h2>
              <p>
                당신과 함께한 시간 덕분에 나는 행복이 거창한 것이 아니라는 걸 알게 됐어요.
                나란히 먹는 밥, 문득 마주친 눈, 별일 없었다고 말할 수 있는 저녁.
                그 모든 평범함이 당신 때문에 내 인생의 가장 귀한 장면이 되었어요.
              </p>
              <p>
                지금까지의 사십 년을 진심으로 축하하고, 앞으로의 사십 년은 더 많이 웃게 해줄게요.
                기쁜 날에는 가장 먼저 안아주고, 힘든 날에는 가장 오래 곁에 있을게요.
              </p>
              <p className="letter-emphasis">
                태어나줘서 고마워요.<br />
                그리고 내 사람이 되어줘서, 정말 고마워요.
              </p>
              <div className="signature">영원히 당신의 편인, 남편이</div>
            </article>
          )}
        </div>
      </section>

      <section className="birthday-wish">
        <div className="wish-ring" aria-hidden="true"><span>✦</span></div>
        <p>FORTY &amp; FOREVER</p>
        <h2>생일 축하해요,<br /><em>나의 가장 아름다운 사람.</em></h2>
        <p className="wish-small">당신의 모든 계절을 사랑합니다.</p>
      </section>
    </main>
  );
}
