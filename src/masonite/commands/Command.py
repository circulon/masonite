import warnings

from cleo import Command as BaseCommand

from ..utils.console import AddCommandColors


class Command(BaseCommand, AddCommandColors):
    def __init__(self, *args, **kwargs):
        # cleo 0.8 passes re.split() maxsplit positionally when parsing command
        # signatures, raising a DeprecationWarning on Python 3.13+. Nothing is
        # actionable on our side until cleo is upgraded, so keep craft output
        # clean. Re-asserted here (not at import time) so it stays in front of
        # any filters libraries may have prepended during application boot.
        warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"cleo\.")
        super().__init__(*args, **kwargs)
