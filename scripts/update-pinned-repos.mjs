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
    const right = items[index + 1] ? renderCell(items[index + 1]) : '    <td width="50%"></td>';
    rows.push(`  <tr>\n${left}\n${right}\n  </tr>`);
  }

  return `<table>\n${rows.join("\n")}\n</table>`;
}

function renderCell(repo) {
  const repoName = encodeURIComponent(repo.name);
  const cardUrl = `https://github-readme-stats.shion.dev/api/pin/?username=${USERNAME}&repo=${repoName}&bg_color=0d1117&title_color=c8860a&text_color=c9d1d9&icon_color=c8860a&border_color=30363d&border_radius=8`;

  return `    <td width="50%">
      <a href="${escapeHtml(repo.url)}">
        <img width="100%" alt="${escapeHtml(repo.name)} repository card" src="${cardUrl}"/>
      </a>
    </td>`;
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
