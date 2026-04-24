"""Integration tests for the cli."""

from __future__ import annotations
from pathlib import Path

import pytest

from cli import main


def _store(tmp_path: Path) -> str:
    """Return a fresh JSON store path inside ``tmp_path``."""
    return str(tmp_path / "splitpy.json")


def test_cli_end_to_end_equal_split(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test a full user -> group -> expense -> settle flow via the CLI."""
    store = _store(tmp_path)

    # arrange: create users and group
    for uid, name in [("alice", "Alice"), ("bob", "Bob"), ("carol", "Carol")]:
        assert main(["--store", store, "add-user", "--id", uid, "--name", name]) == 0
    assert (
        main(
            [
                "--store",
                store,
                "add-group",
                "--id",
                "trip",
                "--name",
                "Beach",
                "--members",
                "alice",
                "bob",
                "carol",
            ]
        )
        == 0
    )

    # act:
    assert (
        main(
            [
                "--store",
                store,
                "add-expense",
                "--group",
                "trip",
                "--description",
                "Dinner",
                "--amount",
                "90.00",
                "--paid-by",
                "alice",
                "--split",
                "equal",
                "--participants",
                "alice",
                "bob",
                "carol",
            ]
        )
        == 0
    )

    # act: run settle
    assert main(["--store", store, "settle", "--group", "trip"]) == 0
    out = capsys.readouterr().out

    # assert
    assert "bob -> alice: 30.00" in out
    assert "carol -> alice: 30.00" in out


def test_cli_balances_reports_net_positions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that the balances command reports the ledger."""
    # arrange
    store = _store(tmp_path)
    for uid, name in [("a", "A"), ("b", "B")]:
        main(["--store", store, "add-user", "--id", uid, "--name", name])
    main(
        [
            "--store",
            store,
            "add-group",
            "--id",
            "g",
            "--name",
            "G",
            "--members",
            "a",
            "b",
        ]
    )
    main(
        [
            "--store",
            store,
            "add-expense",
            "--group",
            "g",
            "--description",
            "Lunch",
            "--amount",
            "10.00",
            "--paid-by",
            "a",
            "--split",
            "equal",
            "--participants",
            "a",
            "b",
        ]
    )

    # act
    main(["--store", store, "balances", "--group", "g"])
    out = capsys.readouterr().out

    # assert
    assert "a: 5.00" in out
    assert "b: -5.00" in out


def test_cli_shares_split(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the shares split flag produces a 2:1 ratio."""
    # arrange
    store = _store(tmp_path)
    for uid, name in [("a", "A"), ("b", "B")]:
        main(["--store", store, "add-user", "--id", uid, "--name", name])
    main(
        [
            "--store",
            store,
            "add-group",
            "--id",
            "g",
            "--name",
            "G",
            "--members",
            "a",
            "b",
        ]
    )
    main(
        [
            "--store",
            store,
            "add-expense",
            "--group",
            "g",
            "--description",
            "Rent",
            "--amount",
            "30.00",
            "--paid-by",
            "a",
            "--split",
            "shares",
            "--participants",
            "a",
            "b",
            "--values",
            "2",
            "1",
        ]
    )

    # act
    main(["--store", store, "balances", "--group", "g"])
    out = capsys.readouterr().out

    # assert
    assert "a: 10.00" in out
    assert "b: -10.00" in out


def test_cli_shares_split_requires_matching_values(
    tmp_path: Path,
) -> None:
    """Test that shares split rejects a values/participants mismatch."""
    # arrange
    store = _store(tmp_path)
    main(["--store", store, "add-user", "--id", "a", "--name", "A"])
    main(["--store", store, "add-user", "--id", "b", "--name", "B"])
    main(
        [
            "--store",
            store,
            "add-group",
            "--id",
            "g",
            "--name",
            "G",
            "--members",
            "a",
            "b",
        ]
    )

    # act and assert
    with pytest.raises(ValueError, match="must match"):
        main(
            [
                "--store",
                store,
                "add-expense",
                "--group",
                "g",
                "--description",
                "X",
                "--amount",
                "10.00",
                "--paid-by",
                "a",
                "--split",
                "shares",
                "--participants",
                "a",
                "b",
                "--values",
                "1",
            ]
        )
