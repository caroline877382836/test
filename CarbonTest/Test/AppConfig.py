from enum import Enum

class LateralMarginCheckMethod(Enum):
    eCenterCheck = 0           # Check the center of a voxel -- if the center is inside, make the voxel as inside.
    eCenterCheckPlus1Spot = 1  # Check the center of a voxel, add one spots laterally
    eCornerCheck = 2           # Check corners of a voxel -- if one of 8 voxels is inside, make the voxel as inside.



rayTraceResolution = 1.0   # default = 1.0 (*gridSize) line 35
