from ._argv import build_configuration


def main() -> int:
    config = build_configuration()  # noqa
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
