import os
from pathlib import Path
from typing import IO

import click
import httpx


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--tf-api-token", required=True)
@click.option("--tf-organization", required=True)
@click.option("--tf-workspace", required=True)
def get_tf_workspace_id(
    tf_api_token: str, tf_organization: str, tf_workspace: str
) -> None:
    response = httpx.get(
        f"https://app.terraform.io/api/v2/organizations/{tf_organization}/workspaces/{tf_workspace}",
        headers={
            "authorization": f"Bearer {tf_api_token}",
            "content-type": "application/vnd.api+json",
        },
    )
    response.raise_for_status()
    workspace_id = response.json()["data"]["id"]

    click.echo(f"Workspace id: {workspace_id}")

    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as f:
        print(f"workspace_id={workspace_id}", file=f)


@cli.command()
@click.option("--tf-api-token", required=True)
@click.option("--tf-workspace-id", required=True)
@click.argument("tf_variables_file", type=click.File("r"))
def update_tf_variables(
    tf_api_token: str, tf_workspace_id: str, tf_variables_file: IO
) -> None:
    response = httpx.get(
        f"https://app.terraform.io/api/v2/workspaces/{tf_workspace_id}/vars",
        headers={
            "authorization": f"Bearer {tf_api_token}",
            "content-type": "application/vnd.api+json",
        },
    )
    response.raise_for_status()
    variables_by_key = {v["attributes"]["key"]: v for v in response.json()["data"]}

    for line in tf_variables_file.readlines():
        if not line.strip():
            continue
        key, _, value = line.partition("=")
        variable = variables_by_key.get(key)
        if variable is None:
            msg = f"Variable {key} not found"
            raise click.ClickException(msg)
        variable_id = variable["id"]
        variable["attributes"]["value"] = value
        response = httpx.patch(
            f"https://app.terraform.io/api/v2/workspaces/{tf_workspace_id}/vars/{variable_id}",
            headers={
                "authorization": f"Bearer {tf_api_token}",
                "content-type": "application/vnd.api+json",
            },
            json={
                "data": {
                    "id": variable_id,
                    "type": variable["type"],
                    "attributes": {**variable["attributes"], "value": value},
                }
            },
        )
        response.raise_for_status()
        click.echo(f"Updated variable {key}")


@cli.command()
@click.option("--tf-api-token", required=True)
@click.option("--tf-workspace-id", required=True)
@click.option("--gh-repo-name", required=True)
def trigger_tf_run(tf_api_token: str, tf_workspace_id: str, gh_repo_name: str) -> None:
    response = httpx.post(
        "https://app.terraform.io/api/v2/runs",
        headers={
            "authorization": f"Bearer {tf_api_token}",
            "content-type": "application/vnd.api+json",
        },
        json={
            "data": {
                "type": "runs",
                "attributes": {
                    "message": (
                        "Triggered from Github Actions workflow"
                        f" in {gh_repo_name} repository"
                    ),
                    "auto-apply": True,
                },
                "relationships": {
                    "workspace": {"data": {"type": "workspaces", "id": tf_workspace_id}}
                },
            }
        },
    )
    response.raise_for_status()


if __name__ == "__main__":
    cli()
