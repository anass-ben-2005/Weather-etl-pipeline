"""Smoke tests for the main.py CLI."""

from main import build_parser


def test_build_parser_parses_lat_lon():
    parser = build_parser()
    args = parser.parse_args(["--lat", "33.57", "--lon", "-7.59"])

    assert args.lat == 33.57
    assert args.lon == -7.59


def test_build_parser_defaults_db_path():
    parser = build_parser()
    args = parser.parse_args(["--lat", "33.57", "--lon", "-7.59"])

    assert args.db == "weather.db"
