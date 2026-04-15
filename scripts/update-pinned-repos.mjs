import fs from "node:fs";

const USERNAME = "Modracx";
const README_PATH = "README.md";
const START = "<!-- PINNED-REPOS:START -->";
const END = "<!-- PINNED-REPOS:END -->";
const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;

if (!TOKEN) {
  throw new Error("GITHUB_TOKEN or GH_TOKEN is required.");
}

const query = `
  query($login: String!) {
    user(login: $login) {
      pinnedItems(first: 6, types: REPOSITORY) {
        nodes {
          ... on Repository {
            name
            description
            url
            homepageUrl
            stargazerCount
            forkCount
            primaryLanguage {
              name
            }
          }
        }
      }
    }
  }
`;

const response = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${TOKEN}`,
    "Content-Type": "application/json",
    "User-Agent": "modracx-readme-updater",
  },
  body: JSON.stringify({
    query,
    variables: { login: USERNAME },
  }),
});

if (!response.ok) {
  throw new Error(`GitHub GraphQL request failed: ${response.status} ${response.statusText}`);
}

const payload = await response.json();

if (payload.errors?.length) {
  throw new Error(payload.errors.map((error) => error.message).join("; "));
}

const repos = payload.data?.user?.pinnedItems?.nodes?.filter(Boolean) ?? [];
const section = renderRepos(repos);
const readme = fs.readFileSync(README_PATH, "utf8");

if (!readme.includes(START) || !readme.includes(END)) {
  throw new Error(`README markers ${START} and ${END} are required.`);
}

const updated = readme.replace(
  new RegExp(`${escapeRegExp(START)}[\\s\\S]*?${escapeRegExp(END)}`),
  `${START}\n${section}\n${END}`,
);

fs.writeFileSync(README_PATH, updated);

function renderRepos(items) {
  if (items.length === 0) {
    return "_No pinned repositories found._";
  }

  const rows = [];

  for (let index = 0; index < items.length; index += 2) {
    const left = renderCell(items[index]);
    const right = items[index + 1] ? renderCell(items[index + 1]) : '    <td valign="top" width="50%"></td>';
    rows.push(`  <tr>\n${left}\n${right}\n  </tr>`);
  }

  return `<table>\n${rows.join("\n")}\n</table>`;
}

function renderCell(repo) {
  const language = repo.primaryLanguage?.name;
  const languageBadge = language ? `${badge(language, "", languageLogo(language))}\n        ` : "";
  const starsBadge = badge("stars", repo.stargazerCount, "github", `Stars ${repo.stargazerCount}`);
  const liveLink = repo.homepageUrl ? ` · <a href="${escapeHtml(repo.homepageUrl)}">Live</a>` : "";

  return `    <td valign="top" width="50%">
      <h3><a href="${escapeHtml(repo.url)}">${escapeHtml(repo.name)}</a></h3>
      <p>${escapeHtml(cleanDescription(repo.description))}</p>
      <p>
        ${languageBadge}${starsBadge}
        <a href="${escapeHtml(repo.url)}">Repository</a>${liveLink}
      </p>
    </td>`;
}

function badge(label, message = "", logo = "", alt = label) {
  const safeLabel = encodeBadgePart(label);
  const safeMessage = encodeBadgePart(message);
  const text = safeMessage ? `${safeLabel}-${safeMessage}` : safeLabel;
  const logoPart = logo ? `&logo=${encodeURIComponent(logo)}` : "";

  return `<img alt="${escapeHtml(alt)}" src="https://img.shields.io/badge/${text}-0d1117?style=flat-square${logoPart}&logoColor=c8860a"/>`;
}

function languageLogo(language) {
  const logos = {
    JavaScript: "javascript",
    TypeScript: "typescript",
    PHP: "php",
    Vue: "vue.js",
    HTML: "html5",
    CSS: "css3",
  };

  return logos[language] ?? "";
}

function cleanDescription(description) {
  if (!description) {
    return "Pinned repository from my GitHub profile.";
  }

  const trimmed = description.replace(/\s+/g, " ").trim();
  return trimmed.length > 160 ? `${trimmed.slice(0, 157).trim()}...` : trimmed;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function encodeBadgePart(value) {
  return String(value).replaceAll("-", "--").replaceAll(" ", "%20");
}
