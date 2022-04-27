#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.fluent.core.solver.flobject import *

from .constant import constant
from .field_name import field_name
from .option import option
from .profile_name import profile_name
from .udf import udf


class qdot(Group):
    """'qdot' child."""

    fluent_name = "qdot"

    child_names = ["option", "constant", "profile_name", "field_name", "udf"]

    option: option = option
    """
    option child of qdot
    """
    constant: constant = constant
    """
    constant child of qdot
    """
    profile_name: profile_name = profile_name
    """
    profile_name child of qdot
    """
    field_name: field_name = field_name
    """
    field_name child of qdot
    """
    udf: udf = udf
    """
    udf child of qdot
    """