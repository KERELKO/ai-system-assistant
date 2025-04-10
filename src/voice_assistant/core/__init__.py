from pathlib import Path
from logging import getLogger


logger = getLogger()


ROOT = Path(__file__).parent.parent.parent.parent


__all__ = ['logger', 'ROOT']
