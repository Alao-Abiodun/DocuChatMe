from lib.prisma_lib import prisma


def transaction():
    """Services open a transaction through this so they never import prisma directly.

    Pass the yielded client into repository calls as `client=tx`.
    """
    return prisma.tx()
