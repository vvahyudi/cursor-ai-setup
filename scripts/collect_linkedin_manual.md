# Manual LinkedIn Collection Protocol

LinkedIn is inconsistent for logged-out scraping and may restrict automated collection. Use this manual/compliant protocol unless you have a permitted API/vendor workflow.

## Capture fields

For each post URL in `/research/linkedin-posts/*.md`, capture:

- author
- LinkedIn post URL
- posted date/time as displayed
- capture date/time
- full post body
- media type: text, image, carousel, video, document, poll, repost/commentary
- engagement snapshot: reactions, comments, reposts if visible
- notable comments from target ICPs/practitioners
- core claim/framework
- implied playbook step

## Recommended file format

Append to the author file:

```md
### YYYY-MM-DD — Short post title

- URL:
- Captured at:
- Media type:
- Engagement snapshot:

#### Raw post text

> Keep verbatim capture for internal research only. Do not republish long excerpts externally.

#### Analyst notes

- Core claim:
- Evidence/examples:
- Playbook implication:
- Tags:
```

## Compliance notes

- Do not bypass login/access controls.
- Do not mass scrape against LinkedIn ToS.
- Prefer manual capture, exports from owned accounts, or a compliant social listening/vendor tool.
- Store raw captures in private repos unless redistribution rights are clear.
