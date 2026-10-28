# Login and safety

## Opening the library
1. `navigate` the built-in browser to the config `login_url` (or any database `entry`; it redirects to login).
2. Tell the user, in one short line, that the browser pane is open and they need to log in (account,
   password, captcha). Wait for them to say they are logged in. Do not read or fill the form.
3. Verify by opening one database `entry` and checking the page (e.g. Cochrane shows
   "Access provided by: National Defense Medical University (NDMU)").

If a page later shows the login form again, the session expired (NDMU: 30 min idle). Ask the user to log in again;
do not retry in a loop.

## Things that look like they need credentials — use these routes instead
| Platform says | Do this instead |
|---|---|
| EBSCO "若要建立匯出結果，請登入 MyEBSCO 帳戶" | Pull records through the JSON search API (`databases/cinahl.md`) |
| Embase "Sign in to export more than 500 records" | Split the result set by publication year so each part ≤ 500 (`databases/embase.md`) |
| Built-in browser download fails (ERR_ABORTED) | Fetch the file content inside the page and dump it in chunks (`03-browser-data-out.md`) |
| Browser cannot reach localhost | Same chunk-dump route; do not try local receivers |

## Cookie banners and pop-ups
- Choose 全部拒絕 / Reject all when offered (Embase OneTrust).
- Airiti's banner only offers 我知道了 (= accept). Leave it; it does not block typing or fetches.
- Dismiss survey pop-ups (Embase "UX research" → Dismiss).

## Other proxy systems (when the user's library is not flysheet)
| System | How it looks | What to record in the config |
|---|---|---|
| EZproxy | `https://login.ezproxy.<univ>.edu.tw/login?url=<target>`; proxied hosts become `www-embase-com.ezproxy.<univ>.edu.tw` | the `login?url=` prefix and the host suffix |
| flysheet (台灣多校) | portal `/er/geter/DBP000xxxxx/` → `*.mhdla.flysheet.com.tw:8443` or IP-authenticated original host | each database's DBP code |
| WebVPN | `https://webvpn.<univ>/https/<encoded host>/...` | the WebVPN base URL |
| IP authentication (campus/VPN) | original publisher host, banner "Access provided by …" | nothing — note that the user must be on campus or VPN |
Always start from the user's actual portal link for each database; the landing host tells you which pattern applies.
The database recipes (Cochrane, Embase, EBSCO, Airiti) are the same behind every proxy; only relative URLs change.

## Claude in Chrome instead of the built-in browser
If the user prefers their own Chrome (already logged in, saved sessions), the same JavaScript recipes work through the
Claude in Chrome tools. Downloads then go to the user's Downloads folder and each one needs their permission, so the
in-page fetch + chunk-dump route is still the simplest way to get records to disk.

## Tabs
The pane allows a limited number of tabs. Close tabs you opened when a database is done; never close a tab
another agent is using.
