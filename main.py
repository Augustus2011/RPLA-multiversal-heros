import os
import time
from pathlib import Path

from .scripts.analysis import Analysis_Dilemma_GROUP_CHARACTERS,Analysis_Scoring,Analysis_Canon_GROUP_CHARACTERS

def main():
    Ad=Analysis_Dilemma_GROUP_CHARACTERS(2)
    Ac=Analysis_Canon_GROUP_CHARACTERS(2)
    As=Analysis_Scoring()
    As.run()
    Ac.run()
    Ad.run()

if __name__ == "main":
    main()