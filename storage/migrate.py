import asyncio

from storage.postgres import run_migrations


def main() -> None:
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()


