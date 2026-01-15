import argparse
import os
import re
import sys
from datetime import datetime

import gitlab
import keepachangelog
from dotenv import load_dotenv
from gitlab.v4.objects import Project, ProjectMergeRequest

if os.getenv("DEV_MODE") == "true":
    load_dotenv()
else:
    load_dotenv(os.path.expanduser("~/.gitlab_changelog_generator"))

LABEL_RELEASE = "Release"
LABELS_CHANGELOG = ["Added", "Fixed", "Changed", "Deprecated"]

REGEX_MERGE_REQUEST = r"See merge request.*!(\d+)$"


def main(args):
    try:
        changes = keepachangelog.to_dict(args.changelog)
    except FileNotFoundError:
        changes = {}

    gl = gitlab.Gitlab(
        os.environ["GITLAB_URL"], private_token=os.environ["GITLAB_PRIVATE_TOKEN"]
    )
    try:
        project: Project = gl.projects.get(args.project_id)
        print(f"Create CHANGELOG for project {project.name}")
    except Exception:
        raise Exception("Project not found!")

    release_merge_requests: list[ProjectMergeRequest] = list(
        filter(lambda mr: LABEL_RELEASE in mr.labels,
               project.mergerequests.list(state="merged", target_branch=args.branch)))
    if len(release_merge_requests) == 0:
        raise Exception("No merge requests with release label found!")

    for release_mr in release_merge_requests:
        try:
            version = re.search(r"v(\d+\.\d+\.\d+)$", release_mr.title).group(1)
        except AttributeError:
            print(f"WARNING: Could not extract version from merge request iid: {release_mr.iid}")
            continue
        print(f"Version: {version}")

        changes[version] = {
            "metadata": {
                "release_date": str(datetime.fromisoformat(release_mr.merged_at).date()),
                "version": version,
                "url": release_mr.web_url
            }
        }

        commits_with_merge_request = list(
            filter(lambda c: re.search(REGEX_MERGE_REQUEST, c.message), release_mr.commits()))
        for commit_wmr in commits_with_merge_request:
            merge_request_iid = re.search(REGEX_MERGE_REQUEST, commit_wmr.message).group(1)
            merge_request = project.mergerequests.get(merge_request_iid)
            label_changelog = next((label for label in LABELS_CHANGELOG if label in merge_request.labels), None)
            if not label_changelog:
                print(f"  WARNING: merge request {merge_request.iid} - {merge_request.title}, "
                      f"not found changelog label")
                continue

            author = merge_request.author["username"]
            title = merge_request.title

            text = f"[{merge_request.iid}]({merge_request.web_url}) {title} (@{author})"

            if label_changelog.lower() not in changes[version]:
                changes[version][label_changelog.lower()] = []
            changes[version][label_changelog.lower()].append(text)

        print(f"  Created new section: {changes[version]}")

    print("Creating new CHANGELOG.md")
    with open(args.changelog, "w") as f:
        f.write(keepachangelog.from_dict(changes))


def run():
    parser = argparse.ArgumentParser(description="Generate gitlab CHANGELOG.md")
    parser.add_argument("project_id", type=int, help="The ID of the project")
    parser.add_argument("--changelog", "-c", type=str, default="./CHANGELOG.md",
                        help="The path to the changelog file, default=./CHANGELOG.MD")
    parser.add_argument("--branch", "-b", type=str, default="main", help="The target branch, default=main")

    args = parser.parse_args()

    try:
        main(args)
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    run()
