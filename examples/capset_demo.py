"""Discover a cap set and watch it grow -- every step exactly verified."""

from disco import Discovery
from disco.problems import CapSet


def main() -> None:
    problem = CapSet(4)  # 81 points; best-known maximum cap = 20
    engine = Discovery(problem, islands=4, population=24, seed=0)

    def report(gen: int, best) -> None:
        print(f"gen {gen:3d}: cap size {int(best.score.value)}")

    best = engine.run(80, on_improve=report)

    print(f"\nbest cap set: {int(best.score.value)} points, "
          f"valid={problem.is_cap(best.candidate)}")
    for point in sorted(best.candidate):
        print("  ", point)


if __name__ == "__main__":
    main()
