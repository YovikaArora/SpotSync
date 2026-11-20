from types import SimpleNamespace

from app.services import navigation_service


class Node(dict):
    def __init__(self, element_id, labels, **properties):
        super().__init__(properties)
        self.element_id = element_id
        self.labels = labels


class FakeSession:
    def __init__(self, entrance, target, edges):
        self.entrance = entrance
        self.target = target
        self.edges = edges

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def run(self, query, **params):
        if "MATCH (e:Entrance" in query:
            return SimpleNamespace(single=lambda: {"e": self.entrance})

        if "MATCH (p:ParkingSpace" in query:
            return SimpleNamespace(single=lambda: {"p": self.target})

        if "MATCH (a)-[r:PATH]->(b)" in query:
            return self.edges

        raise AssertionError("Unexpected Neo4j query")


class FakeDriver:
    def __init__(self, session):
        self.fake_session = session

    def session(self, **kwargs):
        return self.fake_session


def make_edge(source, destination, distance, travel_time=1, accessible=True):
    return {
        "a": source,
        "r": {
            "distance_m": distance,
            "travel_time_s": travel_time,
            "accessible": accessible,
        },
        "b": destination,
    }


def run_route(monkeypatch, edges):
    entrance = Node("entrance", ["Entrance"], key="ENTRANCE_MAIN")
    target = Node("target", ["ParkingSpace"], pg_id=1)

    session = FakeSession(entrance, target, edges)

    monkeypatch.setattr(
        navigation_service, "validate_slot_exists", lambda slot_id: {}
    )
    monkeypatch.setattr(
        navigation_service,
        "_get_driver",
        lambda: FakeDriver(session),
    )

    return navigation_service.get_route_details(1)


def test_navigation_selects_shortest_weighted_route(monkeypatch):
    entrance = Node("entrance", ["Entrance"])
    middle = Node("middle", ["Ramp"])
    target = Node("target", ["ParkingSpace"])

    result = run_route(
        monkeypatch,
        [
            make_edge(entrance, target, 20, 8),
            make_edge(entrance, middle, 4, 2),
            make_edge(middle, target, 6, 3),
        ],
    )

    assert result["distance_m"] == 10
    assert result["travel_time_s"] == 5
    assert [node["properties"] for node in result["route"]] == [
        {},
        {},
        {},
    ]
    assert result["requires_ramp"] is True
    assert result["accessible"] is True
    assert result["route_data_status"] == "SIMULATED_DEMO"
    assert result["topology_status"] == "UNVERIFIED_PLACEHOLDER"


def test_navigation_does_not_invent_reverse_paths(monkeypatch):
    entrance = Node("entrance", ["Entrance"])
    target = Node("target", ["ParkingSpace"])

    result = run_route(
        monkeypatch,
        [make_edge(target, entrance, 5)],
    )

    assert result is None


def test_navigation_ignores_invalid_distance_weights(monkeypatch):
    entrance = Node("entrance", ["Entrance"])
    target = Node("target", ["ParkingSpace"])
    middle = Node("middle", ["Corridor"])

    result = run_route(
        monkeypatch,
        [
            make_edge(entrance, target, float("inf")),
            make_edge(entrance, target, -2),
            make_edge(entrance, target, True),
            make_edge(entrance, middle, 3),
            make_edge(middle, target, 4),
        ],
    )

    assert result["distance_m"] == 7


def test_navigation_marks_incomplete_time_and_accessibility(monkeypatch):
    entrance = Node("entrance", ["Entrance"])
    middle = Node("middle", ["Corridor"])
    target = Node("target", ["ParkingSpace"])

    result = run_route(
        monkeypatch,
        [
            make_edge(entrance, middle, 3, travel_time=2, accessible=True),
            make_edge(middle, target, 4, travel_time=None, accessible=False),
        ],
    )

    assert result["distance_m"] == 7
    assert result["travel_time_s"] is None
    assert result["accessible"] is False
    assert result["requires_ramp"] is False
