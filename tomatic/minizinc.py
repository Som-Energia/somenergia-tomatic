import asyncio
from tomato_cooker.grill import GrillTomatoCooker
from tomato_cooker.models import TomaticProblem, tomatic


def main():
    # define a problem
    tomatic_problem_params = dict(
        nPersones=32,
        nLinies=8,
        nSlots=4,
        nNingus=2,
        nDies=5,
        maxTorns=6,
        nTorns=[
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
        ],
        indisponibilitats=[
            {1}, {1}, {1}, {1}, {1},
            {2}, {2}, {2}, {2}, {2},
            {3}, {3}, {3}, {3}, {3},
            {4}, {4}, {4}, {4}, {4},
            {1}, {2}, {3}, {4}, {1},
            {2}, {3}, {4}, {1}, {2},
            {3}, {4}, {1}, {2}, {3},
            {4}, {1}, {2}, {3}, {4},
            {4}, {3}, {2}, {1}, {4},
            {2}, {1}, {3}, {4}, {2},
            {1}, {2}, {3}, {4}, {1},
            {2}, {3}, {4}, {1}, {2},
            {3}, {4}, {1}, {2}, {3},
            {4}, {1}, {2}, {3}, {4},
            {4}, {3}, {2}, {1}, {4},
            {2}, {1}, {3}, {4}, {2},
            {1}, {1}, {1}, {1}, {1},
            {2}, {2}, {2}, {2}, {2},
            {3}, {3}, {3}, {3}, {3},
            {4}, {4}, {4}, {4}, {4},
            {1}, {2}, {3}, {4}, {1},
            {2}, {3}, {4}, {1}, {2},
            {3}, {4}, {1}, {2}, {3},
            {4}, {1}, {2}, {3}, {4},
            {4}, {3}, {2}, {1}, {4},
            {2}, {1}, {3}, {4}, {2},
            {1}, {2}, {3}, {4}, {1},
            {2}, {3}, {4}, {1}, {2},
            {3}, {4}, {1}, {2}, {3},
            {4}, {1}, {2}, {3}, {4},
            {4}, {3}, {2}, {1}, {4},
            {2}, {1}, {3}, {4}, {2},
        ],
    )
    tomatic_problem = TomaticProblem(**tomatic_problem_params)

    # choose a list of minizinc solvers to user
    solvers = ["chuffed", "coin-bc"]

    # create an instance of the cooker
    tomato_cooker = GrillTomatoCooker(tomatic.MODEL_DEFINITION_PATH, solvers)

    # Now, we can solve the problem
    solution = asyncio.run(tomato_cooker.cook(tomatic_problem))
    print(solution)