from enum import Enum

class RegChannelSetupError(BaseException):
    pass

# class AdvanceError(Enum):
#     NOT_FOUND = 0 # player not in tournament
#     CONFLICT = 1 # player's matchup has already been advanced (opponent was advanced)
#     SELF_CONFLICT = 2 # player has already been advanced
#     ELIM = 3 # player already eliminated
#     OUT_OF_BOUNDS = 4

# ADVANCE_ERROR_MAP = {
#     AdvanceError.NOT_FOUND: "player doesn't exist",
#     AdvanceError.CONFLICT: "player's opponent has already been advanced",
#     AdvanceError.SELF_CONFLICT: "player has already been advanced",
#     AdvanceError.ELIM: "player is not in current round",
#     AdvanceError.OUT_OF_BOUNDS: "player number doesn't exist"
# }