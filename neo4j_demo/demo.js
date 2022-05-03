var viz;
const DEFAULT_TITLES = [
    'Foobar',
    'Philosophy'
];

const originInput = document.getElementById("origin");
const targetInput = document.getElementById("target");
const form = document.getElementById("form");
originInput.value = DEFAULT_TITLES[0];
targetInput.value = DEFAULT_TITLES[1];
form.addEventListener("submit", e => {
    const origin = originInput.value;
    const target = targetInput.value;
    viz.renderWithCypher(`
    MATCH p = (a)-[*]->(c)
    WHERE a.title = '${origin}' AND c.title = '${target}'
    RETURN *`);
    e.preventDefault();
});

function draw() {
    var config = {
        container_id: "viz",
        server_url: "bolt://localhost:7687",
        server_user: "neo4j",
        server_password: "wiki",
        labels: {
            "Article": {
                "caption": "title",
            }
        },
        relationships: {
            "LINKS_TO": {
                "caption": false
            }
        },
        initial_cypher: `MATCH p = (a)-[*]->(c)
        WHERE a.title = '${DEFAULT_TITLES[0]}' AND c.title = '${DEFAULT_TITLES[1]}'
        RETURN *`
    };

    viz = new NeoVis.default(config);
    viz.render();
}

draw();
