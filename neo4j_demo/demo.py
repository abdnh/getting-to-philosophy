from typing import Any
from neo4j import GraphDatabase

from web_crawler import go_to


class WikipediaLinksGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query: str, **params) -> Any:
        with self.driver.session() as session:
            ret = session.write_transaction(
                lambda tx, params: tx.run(query, params), params
            )
            return ret

    def add_path(self, origin_title: str, target_title: str):
        path = go_to(origin_title, target_title)
        for i, link in enumerate(path[:-1]):
            self.run_query(
                "MERGE (a1:Article {title: $title1})"
                "MERGE (a2:Article {title: $title2})"
                "MERGE (a1)-[l:LINKS_TO]-(a2);",
                title1=link,
                title2=path[i + 1],
            )


def main():
    graph = WikipediaLinksGraph("bolt://localhost:7687", "neo4j", "wiki")
    titles = ["Logic", "Ontology", "Foobar"]
    for title in titles:
        graph.add_path(title, "Philosophy")
    graph.close()


if __name__ == "__main__":
    main()
