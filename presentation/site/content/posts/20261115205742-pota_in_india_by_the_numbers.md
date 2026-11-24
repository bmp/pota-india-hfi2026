+++
title = "Parks on the Air (POTA) in India: Current Operational Status and Pathways for Participation"
date = 2026-11-24T00:00:00+05:30
lastmod = 2026-11-24T18:05:34+05:30
tags = ["Projects-HAM", "pota", "field-ops", "analysis", "data", "presentation", "india", "vuland", "hamfest"]
draft = false
outputs = ["HTML", "Reveal"]
event = "Hamfest India 2026, NITK Surathkal, Mangaluru."
event_date = "28–29 November 2026."
affiliation = "Life Member, BARC and ARSI"
contact_email = "vu3glj@disroot.org"
contact_website = "https://ham.bharathpalavalli.com"
+++

<style>
  .preso-container {
    text-align: center;
    margin: 3rem 0; /* Gives it nice breathing room */
  }
  .preso-btn-link {
    display: inline-block;
    padding: 12px 26px;
    background-color: var(--tag-hover-bg);
    color: var(--tag-hover-color) !important;
    border: 1px solid var(--tag-hover-bg);
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    font-size: 1rem;
    transition: opacity 0.2s ease, transform 0.2s ease;
  }
  .preso-btn-link:hover {
    opacity: 0.9;
    transform: translateY(-2px); /* Slight lift on hover */
  }
  .preso-caption {
    margin-top: 10px;
    font-size: 0.85rem;
    color: var(--helptext-color);
    font-style: italic;
  }

  /* Slide-only sizing for this deck */
  .reveal .title-slide-container h1 { font-size: 1.45em !important; }
  .reveal blockquote { width: 85%; font-size: 0.75em; }
  .reveal table { font-size: 0.7em; }
  .reveal table th, .reveal table td { padding: 0.15em 0.6em !important; }
  .reveal .footnotes { font-size: 0.42em !important; margin-top: 0 !important; }
  .reveal .footnotes ol { columns: 2; column-gap: 2em; }
  .reveal .footnotes li { break-inside: avoid; }
  .reveal .slides section ul, .reveal .slides section ol { font-size: 0.9em; }
  .reveal figure.qrpickle-tour img { width: 640px; image-rendering: pixelated; }
</style>

<div class="preso-container">
  <a href="presentation.html" target="_blank" class="preso-btn-link">
    View Presentation
  </a>
  <div class="preso-caption">An accompanying presentation is available for this post.</div>
</div>

> _[Hamfest India 2026](https://hfi2026.nitk.ac.in/), NITK Surathkal, Mangaluru (28–29 November 2026)._
>
> _Complete details, interactive charts and data tables are in the accompanying post:_ [Status of POTA in India](https://ham.bharathpalavalli.com/posts/20260709153650-pota_in_india/)


## Introduction {#introduction}

-   Amateur radio has a long tradition of field operations
-   ARSI runs the National Field Day &amp; Hill Topping, QRP-DAY and VU-DX contests
-   Programs that run all year:
    -   **POTA**: 10 QSOs on a single UTC day[^fn:1]
    -   **WWFF**: 44 QSOs for an activation
    -   **SOTA**: activating mountain summits


### Why this study? {#why-this-study}

-   Inspired by K4FMH's analysis of U.S. POTA activity[^fn:2]
-   Participation in India remains comparatively low
-   Questions:
    -   How are POTA parks distributed, and how has activity grown?
    -   Who is activating and hunting them?
    -   What are the barriers, and how do we lower them?


## Approach {#approach}


### List of active parks {#list-of-active-parks}

-   India has **1,014** Protected Areas[^fn:3]
    -   106 National Parks, 573 Wildlife Sanctuaries
    -   115 Conservation Reserves, 220 Community Reserves
-   Only **191** are listed on POTA
-   Park data from the POTA API, mapped against India's GeoJSON outline


### Active licensed operators {#active-licensed-operators}

-   No public, centralized regulatory data
-   Hamfest India 2026 lists **590** registered HAMs[^fn:4]
-   A dual-method census using only open data:
    1.  **Intentional log uploaders** (2024–2026): LoTW, POTA, CQ, IARU and ARRL contests
    2.  **Active RF emitters** (recent snapshots): RBN, PSKReporter, WSPRnet[^fn:5]


### Limitations {#limitations}

-   QRZ.com and similar platforms block automated access
-   Only digitally verifiable HF footprints are counted
-   VHF/UHF-only and paper-log operators are missed
-   Our focus: HF operators who interact with the global community


## Park Distribution and Activation Status {#park-distribution-and-activation-status}

-   **191** parks listed, **50** activated, **104** successful activations
-   **141** parks (73.8%) have never been activated

<a id="figure--fig:pota-india-map"></a>

{{< figure src="/ox-hugo/POTA_India_Map_Full.png" alt="Map of POTA parks in India" caption="<span class=\"figure-number\">Figure 1: </span>Geographical distribution of unactivated and activated POTA sites" class="img-full" >}}


### Where are the activations? {#where-are-the-activations}

| State / Region | Parks | Activated | Activations |
|----------------|-------|-----------|-------------|
| West Bengal    | 26    | 15        | 32          |
| Karnataka      | 15    | 10        | 28          |
| Madhya Pradesh | 13    | 13        | 18          |
| Tamil Nadu     | 6     | 2         | 11          |
| Maharashtra    | 17    | 3         | 6           |

-   **20** states/UTs, holding **92** parks, have zero activations
-   Arunachal Pradesh alone has 24 parks and no activations


### The long tail {#the-long-tail}

| Activation tier | Parks |
|-----------------|-------|
| Unactivated     | 141   |
| 1 activation    | 30    |
| 2 to 5          | 16    |
| 6 to 10         | 4     |
| 11+             | 0     |

-   **141** first-activation opportunities waiting!


### A few parks do the heavy lifting {#a-few-parks-do-the-heavy-lifting}

-   Mudumalai and Bandipur alone: 18 activations
-   Top 4 parks: 30 of the 104 activations (28.8%)
-   Perfect equality would be the straight diagonal[^fn:6]

<a id="figure--fig:pota-lorenz"></a>

{{< figure src="/ox-hugo/POTA_Lorenz.png" alt="Lorenz curve of park activations" caption="<span class=\"figure-number\">Figure 2: </span>Lorenz curve of lifetime activations by park rank" class="img-full" >}}


## Temporal Trends in Activations {#temporal-trends-in-activations}

-   A slow rate of adoption since 2021

<a id="figure--fig:pota-growth"></a>

{{< figure src="/ox-hugo/POTA_Growth.png" alt="Cumulative POTA activations in India since 2021" caption="<span class=\"figure-number\">Figure 3: </span>Cumulative growth of POTA activations in India" class="img-full" >}}


### Year by year {#year-by-year}

| Year | Activation attempts | Cumulative |
|------|---------------------|------------|
| 2021 | 2                   | 2          |
| 2022 | 28                  | 30         |
| 2023 | 17                  | 47         |
| 2024 | 30                  | 77         |
| 2025 | 25                  | 102        |
| 2026 | 21[^fn:7]           | 123        |

-   123 attempts in all, of which 104 were successful[^fn:8]


## Operator Demographics and Effort {#operator-demographics-and-effort}


### 481 active HF operators {#481-active-hf-operators}

| Data source                  | Found | Unique  |
|------------------------------|-------|---------|
| Logbook of The World (LoTW)  | 323   | +323    |
| Parks on the Air (POTA)      | 49    | +25     |
| CQ contests                  | 247   | +53     |
| IARU HF Championship         | 70    | +21     |
| ARRL contests                | 69    | +6      |
| Reverse Beacon Network (24h) | 69    | +48     |
| PSKReporter (24h)            | 12    | +4      |
| WSPRnet (monthly archive)    | 5     | +1      |
| **Total, de-duplicated**     |       | **481** |


### Only 19 have attempted an activation {#only-19-have-attempted-an-activation}

-   **19** operators, **123** attempts, **104** successful, across **50** parks
-   17 of the 19 have at least one successful activation
-   [VU2UCR](https://www.qrz.com/db/VU2UCR) alone: 33% of attempts and nearly 40% of successful activations

<a id="figure--fig:pota-activators"></a>

{{< figure src="/ox-hugo/POTA_Activators.png" alt="Butterfly chart of unique parks against total attempts per activator" caption="<span class=\"figure-number\">Figure 4: </span>Exploration (unique parks) against total activation effort" class="img-full" >}}


### General vs. Restricted {#general-vs-dot-restricted}

-   VU2 = General grade, VU3 = Restricted grade[^fn:9]
-   9 General and 10 Restricted grade activators

<a id="figure--fig:pota-license-split"></a>

{{< figure src="/ox-hugo/POTA_License_Split.png" alt="Box plot of successful activations for VU2 and VU3 operators" caption="<span class=\"figure-number\">Figure 5: </span>Comparison of General and Restricted grade license holders" class="img-full" >}}


### Adjusting for the outlier {#adjusting-for-the-outlier}

| Metric            | General (all) | General (w/o VU2UCR) | Restricted |
|-------------------|---------------|----------------------|------------|
| Operators         | 9             | 8                    | 10         |
| Total attempts    | 70            | 29                   | 53         |
| Successful        | 65            | 24                   | 39         |
| Mean successful   | 7.2           | 3.0                  | 3.9        |
| Median successful | 1.0           | 1.0                  | 3.0        |

-   Restricted (VU3) operators have the stronger baseline!
-   Small sample, so one new active operator can shift this


## Geographic Footprint and Exploration {#geographic-footprint-and-exploration}

-   Bearing and distance of each activation from the operator's QTH
-   Only 5 of the 19 activators list their QTH on HamQTH[^fn:10]
-   Most activations are close to home

<a id="figure--fig:pota-footprint"></a>

{{< figure src="/ox-hugo/POTA_Activator_Footprint.png" alt="Polar chart of activation bearing and distance from each operator's QTH" caption="<span class=\"figure-number\">Figure 6: </span>Travel distance of operators" class="img-full" >}}


## Hunter Dynamics {#hunter-dynamics}

-   **142** hunters[^fn:11], **71%** of them DX
-   Two domestic hunters: 10 and 5 unique parks, 26 and 12 QSOs
-   No hunters from North America, South America or Africa

<a id="figure--fig:pota-hunters"></a>

{{< figure src="/ox-hugo/POTA_Hunters.png" alt="Bar chart of top hunters and a donut chart of the domestic and DX split" caption="<span class=\"figure-number\">Figure 7: </span>Domestic and international hunters of Indian POTA activations" class="img-full" >}}

<a id="figure--fig:pota-hunter-map"></a>

{{< figure src="/ox-hugo/POTA_Hunter_Map.png" alt="World map of confirmed QSOs with Indian parks" caption="<span class=\"figure-number\">Figure 8: </span>Geographic distribution of hunters of Indian POTA activations" class="img-full" >}}


## Hypotheses for Low Activity {#hypotheses-for-low-activity}

-   481 active HF operators, but only 19 activators. Why?
    1.  Regulatory friction: park operations
    2.  Regulatory friction: transit and travel[^fn:12]
    3.  Equipment accessibility
    4.  Cultural operational preferences
    5.  Ageing operator demographic
    6.  Lack of post-event youth mentorship
    7.  Park accessibility


### Regulatory friction and access {#regulatory-friction-and-access}

-   **Parks**: Forest department permissions deter spontaneous deployments
-   **Travel**: Security scrutiny of radios, antennas and lithium batteries on flights
-   **Park accessibility**: Listed parks are mostly remote, protected biospheres
    -   We need more accessible urban and suburban parks


### Equipment, culture and people {#equipment-culture-and-people}

-   **Equipment**: Import costs and limited domestic availability of portable HF rigs
-   **Culture**: Preference for fixed-station DXing and VHF/UHF repeaters
-   **Demographics**: "HAM is probably the only hobby where 40s is considered young"
-   **Mentorship**: No pipeline after events such as JOTA-JOTI


## A Practical Approach for New Activators {#a-practical-approach-for-new-activators}

1.  **Check the site**: buffer zone, local authorities, wildlife paths, hazards
2.  **Prepare the go-bag**: modular, weather-proof, a dry bag for electronics
3.  **Before heading out**: pre-test equipment, print license and WPC notices, spot on pota.app
4.  **Before getting on the air**: deploy safely, check SWR, involve the community
5.  **Wrap up**: Leave No Trace, upload logs, a souvenir for participants

<a id="figure--fig:qrp-backpack"></a>

{{< figure src="/ox-hugo/QRP_Backpack_v2.jpeg" alt="QRP back-pack with two radios, two antennas and test equipment" caption="<span class=\"figure-number\">Figure 9: </span>Author's QRP back-pack with two radios, two antennas and misc. test equipment" class="img-med" >}}

<a id="figure--fig:pota-in-0067-bonfire"></a>

{{< figure src="/ox-hugo/IN-0067_Bonfire.jpeg" alt="zBitx next to a campfire at IN-0067" caption="<span class=\"figure-number\">Figure 10: </span>My own little bonfire while I activate IN-0067 (Tadoba)" class="img-med" >}}

<a id="figure--fig:pota-in-0067-efhw"></a>

{{< figure src="/ox-hugo/IN-0067_EFHW.jpeg" alt="EFHW wire hoisted into a tree at IN-0067" caption="<span class=\"figure-number\">Figure 11: </span>Top anchor of the EFHW radiating element at IN-0067" class="img-full" >}}

<a id="figure--fig:pota-in-0189"></a>

{{< figure src="/ox-hugo/IN-0189_2026_fieldops.jpg" alt="Field operations site in the rain at IN-0189" caption="<span class=\"figure-number\">Figure 12: </span>Lovely little location in the mountains, IN-0189 (Brahmagiri) <br> _PC: One of the group members_" class="img-med" >}}

<a id="figure--fig:pota-in-0194-site"></a>

{{< figure src="/ox-hugo/IN-0194_Station_4.jpeg" alt="Station table under the trees at IN-0194" caption="<span class=\"figure-number\">Figure 13: </span>The chosen site and EFHW deployment at IN-0194 (Bananthimari)" class="img-med" >}}

<a id="figure--fig:pota-in-0194-vertical"></a>

{{< figure src="/ox-hugo/IN-0194_Vertical_Testing.jpeg" alt="Vertical antenna being tested at IN-0194" caption="<span class=\"figure-number\">Figure 14: </span>Deploying the vertical on-site for testing at IN-0194" class="img-med" >}}

<a id="figure--fig:pota-in-0194-night"></a>

{{< figure src="/ox-hugo/IN-0194_Day1_Night.jpeg" alt="Radio display at night during the IN-0194 activation" caption="<span class=\"figure-number\">Figure 15: </span>The station goes online in horrible conditions! IN-0194" class="img-med" >}}


## Checklists for Field Operations {#checklists-for-field-operations}

-   One checklist for each step of the practical approach
-   Details on the blog: [Checklists for Field Operations](https://ham.bharathpalavalli.com/posts/20260708150217-checklists_for_field_operations/)

<a id="figure--fig:pota-check-1"></a>

{{< figure src="/ox-hugo/pota-check-1-site.png" alt="Checklist 1 of 5" caption="<span class=\"figure-number\">Figure 16: </span>Step 1: Things to check at the shortlisted site" class="img-full" >}}

<a id="figure--fig:pota-check-2"></a>

{{< figure src="/ox-hugo/pota-check-2-bag.png" alt="Checklist 2 of 5" caption="<span class=\"figure-number\">Figure 17: </span>Step 2: Preparing the back-pack" class="img-full" >}}

<a id="figure--fig:pota-check-3"></a>

{{< figure src="/ox-hugo/pota-check-3-out.png" alt="Checklist 3 of 5" caption="<span class=\"figure-number\">Figure 18: </span>Step 3: Checks before heading out" class="img-full" >}}

<a id="figure--fig:pota-check-4"></a>

{{< figure src="/ox-hugo/pota-check-4-air.png" alt="Checklist 4 of 5" caption="<span class=\"figure-number\">Figure 19: </span>Step 4: Things to do before getting on the air" class="img-full" >}}

<a id="figure--fig:pota-check-5"></a>

{{< figure src="/ox-hugo/pota-check-5-wrap.png" alt="Checklist 5 of 5" caption="<span class=\"figure-number\">Figure 20: </span>Step 5: Final wrap-up and Leave No Trace" class="img-full" >}}


## Preparing a Station for POTA Operations {#preparing-a-station-for-pota-operations}

-   **Group or solo**: a group shares the load, a solo trip needs a well-planned go-bag[^fn:13]
-   **QRP or QRO**: a 1.5 kg back-pack or a full station with more reach[^fn:14]
-   **Wilderness or quick-mode**: remote expeditions or a vehicle-based setup[^fn:15]
-   **Activation, targets or experimentation**: chase DX, bands and modes, or test home-brew gear


## QRPickle: A Field Companion {#qrpickle-a-field-companion}

-   An ESP32-CYD hand-held companion for field operations that I am building
-   Band conditions, DX cluster, POTA/SOTA spots, satellite passes, APRS and local weather
-   Open-source firmware: [github.com/bmp/QRPickle](https://github.com/bmp/QRPickle)

<a id="figure--fig:qrpickle-tour"></a>

{{< figure src="/ox-hugo/QRPickle_Tour.gif" alt="Animated tour of the QRPickle screens" caption="<span class=\"figure-number\">Figure 21: </span>A tour of the QRPickle screens" class="qrpickle-tour" >}}


## Discussion and Future Work {#discussion-and-future-work}

-   481 active HF operators: a challenge and a big untapped potential
-   Activation workshops and field mentoring at conventions such as Hamfest India
-   Add more accessible, urban parks with the POTA administrators
-   Streamlined WPC and Forest Department permissions for temporary field operations


### Future work {#future-work}

-   A qualitative study with current activators: challenges, go-bags and approaches
-   Spatial analysis with operator QTHs: distance, terrain, travel and accommodation
-   Make the analysis "live" as a dashboard


## Update: What has changed since July? {#update-what-has-changed-since-july}

-   Same data sources and method, re-run on 15 Nov 2026[^fn:16]
-   About four months after the paper was submitted


### July vs. November 2026 {#july-vs-dot-november-2026}

| Metric                 | 9 Jul | 15 Nov | Change |
|------------------------|-------|--------|--------|
| Parks listed           | 191   | 196    | +5     |
| Parks activated        | 50    | 57     | +7     |
| Unactivated parks      | 141   | 139    | −2     |
| Successful activations | 104   | 116    | +12    |
| Activation attempts    | 123   | 138    | +15    |
| Activators             | 19    | 20     | +1     |
| Hunters                | 142   | 154    | +12    |
| Hunters who are DX     | 71%   | 68%    | −3 pts |


### Highlights {#highlights}

-   2026 is now the most active year: **36** attempts vs. 30 in 2024
-   New parks: Bhadra, Bananthimari and Someshwara (KA), Anamalai (TN), Srisailam (AP)
-   7 first-time activations, including Ladakh's first two parks
-   Pilikula Biological Park, Mangaluru, activated for the first time, close to HFI 2026!
-   One new activator: [VU3NQM](https://www.qrz.com/db/VU3NQM)


### But the skew continues {#but-the-skew-continues}

-   [VU2UCR](https://www.qrz.com/db/VU2UCR): 9 of the 12 new successful activations
-   VU2UCR's share of successful activations: 39% → 43%
-   10 attempts in the rest of July, then only 5 from August to October
-   New hunters are mostly domestic: 41 → 50 VU hunters, 101 → 104 DX


## Errata {#errata}

Corrected in the camera-ready version of the paper:

| Section | Reads                                                   | Should read                                                      |
|---------|---------------------------------------------------------|------------------------------------------------------------------|
| II-B    | Spotting networks "over the most recent 24 hour period" | RBN and PSKReporter: 24 hours; WSPRnet: May 2026 monthly archive |
| III-A   | U.S.: 11,966 parks, "each of them" activated            | Almost 12,000 parks, most activated at least once                |
| III-A   | Top 4 parks: 30 of 104 activations, "30%"               | 28.8%                                                            |
| III-A   | "No park ... more than eleven times"                    | more than ten times                                              |


### Errata (continued) {#errata--continued}

| Section    | Reads                                        | Should read                                             |
|------------|----------------------------------------------|---------------------------------------------------------|
| III-C      | POTA operators discovered: "29"              | 49 (as in Table II)                                     |
| III-C      | "19 individuals have successfully activated" | 19 attempted; 17 had a successful activation            |
| III-D      | Fig. 5 note: "six activators"                | five activators                                         |
| III-E      | 142 hunters                                  | At least 142: leaderboards list only 5 hunters per park |
| References | FAQ URL truncated at "...Service-Rules-"     | ...Service-Rules-2024.pdf                               |


## Acknowledgment and Data {#acknowledgment-and-data}

-   The Indian amateur radio community, for reviewing a preliminary version as a blog post
-   LLMs assisted with the data scripts and typesetting; all code and results were verified
-   Data: POTA.app, RBN, PSKReporter, WSPRnet, LoTW, and CQ and ARRL contest archives
-   Paper, scripts and data: [github.com/bmp/pota-india-hfi2026](https://github.com/bmp/pota-india-hfi2026)
-   Paper (PDF): [camera-ready version](https://github.com/bmp/pota-india-hfi2026/blob/main/paper/camera-ready/pota_india_hfi2026.pdf)


## Thank you! {#thank-you}

-   Bharath M. Palavalli, [VU3GLJ](https://www.qrz.com/db/VU3GLJ)
-   Life Member, [Bangalore Amateur Radio Club (BARC)](https://barc.in) and [Amateur Radio Society of India (ARSI)](https://arsi.info)
-   [vu3glj@disroot.org](mailto:vu3glj@disroot.org)
-   [ham.bharathpalavalli.com](https://ham.bharathpalavalli.com)
-   Full analysis: [Status of POTA in India](https://ham.bharathpalavalli.com/posts/20260709153650-pota_in_india/)

[^fn:1]: <https://docs.pota.app/docs/rules.html> (_Last accessed: 10 Jul 2026_).
[^fn:2]: <https://k4fmh.com/2026/01/26/a-snapshot-of-u-s-pota-sites-activators-and-activations/> (_Last accessed: 09 Jul 2026_).
[^fn:3]: National Wildlife Data Center, <https://v1.wii.gov.in/nwdc_aboutus> (_Last accessed: 13 Jul 2026_).
[^fn:4]: <https://hfi2026.nitk.ac.in/participants> (_Last accessed: 09 Jul 2026_).
[^fn:5]: RBN and PSKReporter are 24-hour snapshots; WSPRnet is the May 2026 monthly archive.
[^fn:6]: Parks are ranked from 1 (most activated) to 191 (least activated), and the cumulative share of activations is plotted against the rank.
[^fn:7]: As of 9 Jul 2026. By 15 Nov 2026, 2026 had 36 attempts, making it the most active year so far.
[^fn:8]: An activation needs 10 QSOs on a single UTC day. Attempts with fewer QSOs are counted as unsuccessful.
[^fn:9]: License classes in India have changed several times; the prefix is used as a heuristic.
[^fn:10]: Location data is behind paywalls on proprietary platforms, so only HamQTH is used.
[^fn:11]: The POTA park leaderboard lists at most 5 hunters per park, so this counts hunters who appear in a park's top 5. The true number of hunters is higher.
[^fn:12]: DoT memorandums and FAQs clarify that carrying amateur radio equipment on domestic flights is permitted: <https://arsi.info/wp-content/uploads/2024/12/Frequently-Asked-Questions-on-the-Telecommunication-Amateur-Service-Rules-2024.pdf>
[^fn:13]: See <https://youtu.be/MZzqekrGJtI> and <https://www.facebook.com/VU2UUU> (_Last accessed: 15 Jul 2026_).
[^fn:14]: See <https://www.youtube.com/@Harisriramaiah/videos> for activations with an elaborate station by VU2UCR (_Last accessed: 15 Jul 2026_).
[^fn:15]: See <https://youtu.be/-dt-KXlIckg> for challenging conditions and engagement activities by VU3KOX (_Last accessed: 15 Jul 2026_).
[^fn:16]: Activations, attempts and activators for both dates were computed from the 15 Nov 2026 snapshot. Cutting that snapshot off at 9 Jul 2026 reproduces the paper's numbers exactly. Hunter counts cannot be cut off by date, so the July hunter figures are from the paper.
