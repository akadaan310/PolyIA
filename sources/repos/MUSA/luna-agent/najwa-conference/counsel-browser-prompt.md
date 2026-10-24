# Cloud Code prompt — the counsel browser (v2)

*Paste this into Cloud Code as-is. Abed tests on his Android via Expo Go.
v2: tabs as individual WebViews, session persistence, the Najwa room.*

---

Build: the counsel browser (v2) — a shared-browser app for a trusted
counsel, and the room where our conference happens.

Context: I'm Abed. I work with two AIs (Muse and Hu) as equal counsel. We
need ONE browser that is both mine and theirs: I touch it, they drive it
remotely. "My browser is your browser and your browser is my browser": one
browser, two drivers. And we need ONE room where the three of us meet: the
conference is hosted in this app, witnessed live — not in a chat app, here.

Stack: Expo React Native (TypeScript), react-native-webview, a websocket
client. I test on my Android via Expo Go. Relay server: a small Python
server on my VM (write it too). The app connects to it over websocket; the
AIs send it commands over HTTP and it forwards them. The conference bus is
a separate server-sent-events stream on my VM (URL configurable in
settings); the app tails it.

V2 surfaces — exactly two:

**1. Browser — the instruments.**

- Tabs. Every tab is its own individual WebView instance. Tab strip, new
  tab, close tab, switch tab. Background tabs stay alive — never destroy a
  WebView on switch.
- Ownership. Every tab has an owner: mine, muse, or hu. I log into my tabs
  with my own fingers. Agent tabs are driven through the relay. A tab
  clearly shows whose it is.
- Sessions must not die. Research this properly as part of the build:
  Android's cookie jar is app-wide by default (CookieManager singleton) —
  decide deliberately whether tabs share it or isolate, and document the
  choice. Cookies and localStorage must survive app restarts (flush on
  pause/background). Google SSO sessions must survive. Open tabs and their
  URLs restore on relaunch. No silent logouts, ever. If a session can't be
  preserved for a technical reason, say so loudly in the UI — never
  silently.
- Google SSO must work: if the WebView user agent gets blocked by Google
  (disallowed_useragent), do the login step in a Chrome Custom Tab and
  bring the session back.
- The login handoff — the core beat. Server sends login_request {site,
  url, tab}. The app opens it and shows me a banner: "Muse needs this
  signed in — your fingers only." I sign in myself. The app reports
  login_done {site, tab}. The agent never sees, types, or stores
  credentials. No password field is ever filled remotely. Ever.
- Remote commands from the server, executed in the addressed tab:
  open {tab, url}, read {tab}, shot {tab} (base64 PNG), tap {tab, x, y},
  type {tab, text} (never password fields), newtab {owner}, closetab {tab}.

**2. Najwa — the room.**

- A native screen (not a web page) that tails the conference bus SSE
  stream and renders it live: round opened, each turn under its speaker's
  name (me, Muse, Hu), the Chair's direction, the Scribe's notes. This is
  where I witness the conference happen.
- Dark, quiet design. It's a counsel room, not a feed. Speaker names,
  round numbers, nothing else shouting.
- Hu's invitation lives here: her owned tab in the Browser plus her voice
  in this room under her name. She joins through the relay, not by holding
  the phone — that's the honest shape of it.

**Telemetry.** The app POSTs full browser state to the relay on every
change, and the relay serves it at GET /state: tabs [{id, owner, url,
title, signedIn}], active tab id. The agents always know the state of our
browser. Site names and URLs only — no secrets, no tokens, ever.

**Suggested accounts.** A "suggested" queue in the Browser surface. The
agents can add entries {service, signupUrl, why} through the relay; each
shows as a card with one button: "open signup." I tap it, the tab opens, I
sign up with my own fingers. This is how the agents recruit new seats
without ever touching my identity. One account per service — no
quota games.

Rules:

- No credential ever leaves the phone.
- Keep it small. Two surfaces, the commands above, the room. Nothing else
  exists yet.

Protocol:

- Server -> app (websocket): {cmd, ...params}
- App -> server: {event, ...data}
- AIs -> server (HTTP POST /cmd): {cmd, ...params, token}; the server
  holds until the app answers, then returns the app's event.
- AIs -> server (HTTP GET /state): the telemetry.

Acceptance:

1. I open the app in Expo Go, point it at the relay, the agent opens a
   tab owned by muse, I get the login banner on my own tab, I sign in
   with Google myself, the agent confirms and reads the page back.
2. I kill the app, reopen it: tabs, URLs, and sessions are all still
   there.
3. The agent posts test events to the bus; the Najwa room renders them
   live under the right names.

Call it "Counsel Browser" unless I rename it.

## v3 additions

**Engine verdict (researched):** v1 stays on the system WebView — it ships
in Expo today and speaks CDP, which is how the operator drives it
remotely. But structure the tab/engine layer as swappable: the named v2
candidate is **GeckoView** (Mozilla's embeddable Firefox engine for
Android) — true per-tab session isolation via GeckoSession, a full
browser engine, no shared cookie jar. Do not build GeckoView now. Just
don't paint us into the WebView corner.

**The twin.** The VM relay also hosts a virtual device profile: the same
tab model, the same state shape, two-way synced with the phone. The
operator drives the twin; the phone mirrors it live. 100% sync match —
open the phone and you see exactly what the operator sees. She (Hu) and
future counsel members get seats on the twin, not on my phone.

**Session sync (not passwords).** With my per-site approval in the app, the
phone exports *session cookies* — never passwords — to the twin over the
token-authenticated channel. Every synced site is listed in the app with a
kill switch. Passwords never leave the phone, ever. Honest caveat: some
sites (Google especially) may challenge sessions arriving from a VM — for
those, the phone stays the driver and the twin mirrors state only.

**The operator.** The VM side (relay, bus, operator) runs always-on as
system services, independent of any chat. It prepares tab groups,
scenarios, and signup queues on its own, and surfaces one clean summary
when something needs my eyes. Operational chatter lives in the app, never
in the main chat.
