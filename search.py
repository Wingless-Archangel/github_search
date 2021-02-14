import requests
import os
import click
from typing import *
import json
import re

URL = "https://api.github.com/search/code"
PAGE = 1
TOKEN = os.getenv("github_token", "")


@click.command()
@click.option("--query", default="ptt", help="Github Search query")
@click.option("--token", default=TOKEN, help="Github Token")
def main(query, token) -> None:
    github_token = f"token {token}"
    querystring = {"q": query, "page": PAGE, "per_page": 100}
    headers = {"authorization": github_token}
    result = call_api(headers, querystring)
    print(json.dumps(result, indent=4, sort_keys=True))


def call_api(headers: dict, querystring: dict) -> json:
    result = {}
    url = URL
    while True:
        print(f"current url is {url} and page is {querystring['page']}")
        response = requests.request("GET", url, headers=headers, params=querystring)
        res_header = response.headers
        response_json = response.json()
        link_header = re.split(", ", res_header["Link"])
        link_dict = link_header_parser(link_header)

        for item in response_json["items"]:
            name = item["name"]
            html_url = item["html_url"]
            result[name] = html_url

        if "next" not in link_dict:
            break
        else:
            querystring["page"] += 1

    return result


def link_header_parser(link_header: list) -> dict:
    link = {}
    for elem in link_header:
        m = re.match(
            r"<(?P<link>https://api.github.com/.*)>; rel=\"(?P<name>.*)\"", elem
        )
        name = m.group("name")
        url = m.group("link")
        link.update({name: url})

    return link


if __name__ == "__main__":
    main()