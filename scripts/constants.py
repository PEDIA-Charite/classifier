'''
Global Constants
'''

# Mode
TEST_MODE = 0
CV_MODE = 1
LOOCV_MODE = 2
PARAM_TEST_MODE = 3

# Graph
NO_GRAPH = 0
GRAPH = 1

# Running Mode
NORMAL_MODE = 0
SERVER_MODE = 1

# Default param C
PARAM_C = [pow(2, i) for i in range(0, 8, 2)]
PARAM_G = [pow(2, i) for i in range(-6, -1, 2)]
